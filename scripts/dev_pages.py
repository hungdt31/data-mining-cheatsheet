#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Môi trường xem site giống GitHub Pages trên máy cục bộ.

Ưu tiên:
  1. Dùng .ci-html/Cn.html nếu đã sinh sẵn (cần pandoc+latexpand).
  2. Nếu không có, tự tạo trang nhúng PDF (embed) để xem ngay trong trình duyệt.

Chạy từ gốc repo:
  python scripts/dev_pages.py

Chỉ dựng file, không bật server:
  python scripts/dev_pages.py --build-only

Sinh HTML đầy đủ (cần pandoc + latexpand):
  python scripts/build_chapter_html.py C5
"""
from __future__ import annotations

import argparse
import html as _html
import json
import os
import shutil
import subprocess
import sys
import textwrap
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT   = Path(__file__).resolve().parents[1]
OUT    = ROOT / ".web-dev"
TITLES = json.loads((ROOT / "scripts" / "chapter-titles.json").read_text(encoding="utf-8"))

# ── Trang nhúng PDF ──────────────────────────────────────────────────────────

_PDF_EMBED_TMPL = textwrap.dedent("""\
<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{label} · {title}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600;1,6..72,400&family=Source+Sans+3:wght@400;600&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="chapters.css" />
  <style>
    .embed-wrap {{
      margin-top: 1.5rem;
      border-radius: 6px;
      overflow: hidden;
      box-shadow: 0 2px 12px rgba(28,28,28,.12);
    }}
    .embed-wrap embed,
    .embed-wrap iframe {{
      display: block;
      width: 100%;
      height: calc(100vh - 14rem);
      min-height: 480px;
      border: none;
    }}
    .embed-fallback {{
      padding: 2rem;
      text-align: center;
      font-style: italic;
      color: var(--ink-muted);
    }}
    .embed-fallback a {{
      color: var(--accent);
      font-weight: 600;
      text-decoration: none;
      border-bottom: 1px solid transparent;
    }}
    .embed-fallback a:hover {{ border-bottom-color: var(--accent); }}
  </style>
</head>
<body class="chapter-page">
  <div class="chapter-shell" style="max-width:64rem">
    <nav class="chapter-nav">
      <a class="chapter-nav__back" href="../index.html">← Tất cả chương</a>
      <a class="chapter-nav__pdf" href="{pdf}" target="_blank" rel="noopener">Tải PDF</a>
    </nav>
    <header class="chapter-masthead">
      <p class="chapter-masthead__kicker">{label}</p>
      <h1 class="chapter-masthead__title">{title}</h1>
    </header>
    <div class="embed-wrap">
      <embed src="{pdf}" type="application/pdf"
             title="{title}"
             onerror="this.style.display='none';
                      document.getElementById('fb').style.display='block'">
      <div id="fb" class="embed-fallback" style="display:none">
        <p>Trình duyệt không nhúng được PDF.</p>
        <p><a href="{pdf}" target="_blank">Mở PDF trong tab mới →</a></p>
      </div>
    </div>
    <footer class="chapter-footer" style="margin-top:1.5rem">
      <a href="../index.html">Danh sách chương</a>
      <span class="chapter-footer__sep">·</span>
      <a href="{pdf}" target="_blank" rel="noopener">Tải PDF</a>
    </footer>
  </div>
</body>
</html>
""")


def _make_pdf_embed_page(ch: str) -> str:
    low   = ch.lower()
    num   = ch[1:].zfill(2)
    label = f"Chương {num}"
    title = TITLES.get(ch, ch)
    return _PDF_EMBED_TMPL.format(
        label=_html.escape(label),
        title=_html.escape(title),
        pdf=f"{low}.pdf",
    )


# ── Lấy repo slug từ git remote ─────────────────────────────────────────────

def _github_slug() -> str:
    try:
        r = subprocess.run(
            ["git", "config", "--get", "remote.origin.url"],
            capture_output=True, text=True, timeout=5, cwd=ROOT, check=False,
        )
        u = r.stdout.strip()
        if u.startswith("https://github.com/"):
            parts = u.split("github.com/", 1)[1].split("/", 1)
            if len(parts) >= 2:
                return f"{parts[0]}/{parts[1].removesuffix('.git').rstrip('/')}"
        if u.startswith("git@github.com:"):
            tail = u.split(":", 1)[1].removesuffix(".git").rstrip("/")
            if "/" in tail:
                return tail
    except (FileNotFoundError, subprocess.TimeoutExpired, IndexError):
        pass
    return "local/dev"


# ── Dựng .web-dev/ ───────────────────────────────────────────────────────────

def build(*, repo_slug: str) -> list[dict]:
    OUT.mkdir(parents=True, exist_ok=True)
    chapters_dir = OUT / "chapters"
    chapters_dir.mkdir(exist_ok=True)

    shutil.copy2(ROOT / "assets" / "chapters.css", chapters_dir / "chapters.css")

    manifest: list[dict] = []
    for cid in ["C1", "C2", "C3", "C4", "C5", "C6"]:
        low      = cid.lower()
        pdf_src  = ROOT / "chapters" / cid / "main.pdf"
        html_src = ROOT / ".ci-html" / f"{cid}.html"

        has_pdf  = pdf_src.is_file()
        has_html = html_src.is_file()

        if has_pdf:
            shutil.copy2(pdf_src, chapters_dir / f"{low}.pdf")

        if has_html:
            # HTML đã sinh đầy đủ qua Pandoc
            shutil.copy2(html_src, chapters_dir / f"{low}.html")
        elif has_pdf:
            # Fallback: trang nhúng PDF trực tiếp
            (chapters_dir / f"{low}.html").write_text(
                _make_pdf_embed_page(cid), encoding="utf-8"
            )
            has_html = True   # kể là "có web"

        if has_pdf or has_html:
            manifest.append({"id": cid, "pdf": has_pdf, "html": has_html})

    # Render index.html
    idx      = (ROOT / "index.html").read_text(encoding="utf-8")
    safe_json = json.dumps(manifest, ensure_ascii=False) \
                    .replace("<", "\\u003c").replace(">", "\\u003e")
    idx = idx.replace("__GITHUB_REPOSITORY__", repo_slug)
    idx = idx.replace("__CHAPTERS_JSON__", safe_json)
    (OUT / "index.html").write_text(idx, encoding="utf-8")

    return manifest


# ── main ─────────────────────────────────────────────────────────────────────

def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except OSError:
            pass

    ap = argparse.ArgumentParser(description="Xem site Pages cục bộ (.web-dev/)")
    ap.add_argument("--port", "-p", type=int, default=8765)
    ap.add_argument("--no-open",    action="store_true", help="Không tự mở trình duyệt")
    ap.add_argument("--build-only", action="store_true", help="Chỉ tạo .web-dev/, không chạy server")
    ap.add_argument("--repo", default="", help="owner/repo (mặc định: đọc từ git remote)")
    args = ap.parse_args()

    slug     = args.repo.strip() or _github_slug()
    manifest = build(repo_slug=slug)

    # Thống kê
    n_pdf  = sum(1 for m in manifest if m["pdf"])
    n_html = sum(1 for m in manifest if m["html"])
    print(f"Đã dựng {OUT}")
    print(f"  PDF:  {n_pdf}/6 chương")
    print(f"  HTML: {n_html}/6 chương (embed PDF nếu chưa có Pandoc)")

    if not any((ROOT / "chapters" / f"C{i}" / "main.pdf").is_file() for i in range(1, 7)):
        print("\n[!] Chưa có PDF nào — hãy biên dịch LaTeX trước (latexmk -pdf)")

    has_pandoc_html = any((ROOT / ".ci-html" / f"C{i}.html").is_file() for i in range(1, 7))
    if not has_pandoc_html:
        print("\n[i] Trang \"Trên web\" hiện dùng chế độ nhúng PDF.")
        print("    Để có HTML đầy đủ: cài pandoc + latexpand rồi chạy")
        print("      python scripts/build_chapter_html.py C1  (lặp C1..C6)")

    if args.build_only:
        print(f"\nChạy server thủ công:\n  python -m http.server {args.port} --directory .web-dev")
        return 0

    os.chdir(OUT)
    server = ThreadingHTTPServer(("127.0.0.1", args.port), SimpleHTTPRequestHandler)
    url    = f"http://127.0.0.1:{args.port}/"
    print(f"\nServer: {url}  (Ctrl+C để dừng)")
    if not args.no_open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nĐã dừng.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
