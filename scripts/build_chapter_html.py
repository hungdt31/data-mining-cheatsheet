#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mở rộng main.tex (latexpand), làm sạch cấu trúc khó cho Pandoc, xuất HTML fragment
và bọc vào assets/chapter-template.html — dùng trên CI hoặc máy có latexpand + pandoc.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TITLES_PATH = ROOT / "scripts" / "chapter-titles.json"
TEMPLATE_PATH = ROOT / "assets" / "chapter-template.html"
OUT_DIR = ROOT / ".ci-html"

CHAPTER_ORDER = ["C1", "C2", "C3", "C4", "C5", "C6"]


def _chapter_pager_html(ch: str, titles: dict) -> str:
    """Sinh HTML khối prev/next để thay __CHAPTER_PAGER__."""
    idx = CHAPTER_ORDER.index(ch) if ch in CHAPTER_ORDER else -1
    prev_ch = CHAPTER_ORDER[idx - 1] if idx > 0 else None
    next_ch = CHAPTER_ORDER[idx + 1] if idx < len(CHAPTER_ORDER) - 1 else None

    def _btn(cid: str, direction: str) -> str:
        num   = cid[1:].zfill(2)
        label = "← Chương trước" if direction == "prev" else "Chương tiếp →"
        css   = f"chapter-pager__{direction}"
        title = _escape_html(titles.get(cid, cid))
        return (
            f'<a class="{css}" href="{cid.lower()}.html">'
            f'<span class="chapter-pager__dir">{label}</span>'
            f'<span class="chapter-pager__title">Chương {num} · {title}</span>'
            f'</a>'
        )

    parts = []
    parts.append(_btn(prev_ch, "prev") if prev_ch else '<span></span>')
    parts.append(_btn(next_ch, "next") if next_ch else '<span></span>')
    return '<nav class="chapter-pager" aria-label="Điều hướng chương">' + "".join(parts) + "</nav>"


def extract_document_body(flat_tex: str) -> str:
    m = re.search(r"\\begin\{document\}(.*)\\end\{document\}", flat_tex, re.DOTALL)
    if not m:
        raise ValueError("Không tìm thấy phạm vi document.")
    return m.group(1).strip()


def sanitize_body(tex: str) -> str:
    """Giảm lệnh LaTeX mà Pandoc thường đọc kém."""
    # Bỏ phần tiêu đề từ _title.tex (3 dòng đầu trang)
    tex = re.sub(r"\\newcommand\s*\{\\ChapterNum\}\s*\{[^}]*\}\s*", "", tex)
    tex = re.sub(r"\\newcommand\s*\{\\ChapterTitle\}\s*\{[^}]*\}\s*", "", tex)
    tex = _strip_first_center_env(tex)

    subs = [
        (r"\\onehalfspacing\s*", ""),
        (r"\\renewcommand\s*\{\\arraystretch\}\s*\{[^}]*\}\s*", ""),
        (r"\\newpage\s*", "\n\n"),
        (r"\\clearpage\s*", "\n\n"),
        (r"\\begin\{longtable\}", r"\\begin{tabular}"),
        (r"\\end\{longtable\}", r"\\end{tabular}"),
    ]
    for pat, repl in subs:
        tex = re.sub(pat, repl, tex, flags=re.MULTILINE)

    tex = re.sub(r"^\s*\\endhead\s*$", "", tex, flags=re.MULTILINE)
    tex = re.sub(r"\\begin\{singlespace\}", "", tex)
    tex = re.sub(r"\\end\{singlespace\}", "", tex)

    tex = strip_enumerate_optional_args(tex)
    return tex


def _strip_first_center_env(tex: str) -> str:
    """Xoá khối \\begin{center}...\\end{center} đầu tiên (tiêu đề từ _title.tex)."""
    start = tex.find(r"\begin{center}")
    if start == -1:
        return tex
    end = tex.find(r"\end{center}", start)
    if end == -1:
        return tex
    return tex[:start] + tex[end + len(r"\end{center}"):]


def strip_enumerate_optional_args(tex: str) -> str:
    """\\begin{enumerate}[...] → \\begin{enumerate} (cân bằng ngoặc [ ])."""
    token = r"\begin{enumerate}["
    parts: list[str] = []
    s = 0
    while True:
        idx = tex.find(token, s)
        if idx == -1:
            parts.append(tex[s:])
            break
        parts.append(tex[s:idx])
        bracket_pos = idx + len(token) - 1
        depth = 1
        j = bracket_pos + 1
        while j < len(tex) and depth:
            if tex[j] == "[":
                depth += 1
            elif tex[j] == "]":
                depth -= 1
            j += 1
        if depth != 0:
            parts.append(tex[idx : idx + len(token)])
            s = idx + len(token)
            continue
        parts.append(r"\begin{enumerate}")
        s = j
    return "".join(parts)


def run_latexpand(tex_dir: Path) -> str:
    with tempfile.NamedTemporaryFile(
        mode="w+", suffix=".tex", delete=False, encoding="utf-8"
    ) as tmp:
        tmp_path = Path(tmp.name)
    try:
        subprocess.run(
            ["latexpand", "-o", str(tmp_path), "main.tex"],
            cwd=tex_dir,
            check=True,
            capture_output=True,
            text=True,
        )
        return tmp_path.read_text(encoding="utf-8")
    finally:
        tmp_path.unlink(missing_ok=True)


def run_pandoc(body_tex: str) -> tuple[str | None, str]:
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".tex", delete=False, encoding="utf-8"
    ) as tmp_in:
        tmp_in.write(body_tex)
        in_path = Path(tmp_in.name)
    try:
        proc = subprocess.run(
            [
                "pandoc",
                str(in_path),
                "-f",
                "latex",
                "-t",
                "html",
                "--mathjax",
            ],
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            err = (proc.stderr or proc.stdout or "").strip() or "Pandoc không trả lời."
            return None, err[:2500]
        return proc.stdout.strip(), ""
    finally:
        in_path.unlink(missing_ok=True)


def write_stub(out_html: Path, ch: str, title: str, message: str, titles: dict | None = None) -> None:
    slug = ch.lower()
    tpl = TEMPLATE_PATH.read_text(encoding="utf-8")
    stub = (
        f'<p class="stub-note">{_escape_html(message)}</p>'
        f'<p class="stub-links"><a href="{slug}.pdf">Mở bản PDF</a></p>'
    )
    html = _fill_template(tpl, ch, title, slug, stub, titles=titles)
    out_html.write_text(html, encoding="utf-8")


def _escape_html(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _fill_template(
    tpl: str, ch: str, title: str, slug: str, body: str, titles: dict | None = None
) -> str:
    num = ch[1:].zfill(2)
    pager = _chapter_pager_html(ch, titles or {}) if titles is not None else ""
    return (
        tpl.replace("__CHAPTER_LABEL__", f"Chương {num}")
        .replace("__TITLE__", title)
        .replace("__BODY__", body)
        .replace("__PDF_HREF__", f"{slug}.pdf")
        .replace("__CHAPTER_SLUG__", slug)
        .replace("__CHAPTER_PAGER__", pager)
    )


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: build_chapter_html.py C1", file=sys.stderr)
        return 2

    ch = sys.argv[1]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_html = OUT_DIR / f"{ch}.html"
    tex_dir = ROOT / "chapters" / ch
    titles = json.loads(TITLES_PATH.read_text(encoding="utf-8"))
    title = titles.get(ch, ch)

    if not (tex_dir / "main.tex").is_file():
        write_stub(out_html, ch, title, "Không tìm thấy main.tex.", titles=titles)
        return 1

    try:
        flat = run_latexpand(tex_dir)
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        msg = "Không chạy được latexpand (cần texlive-extra-utils)."
        if isinstance(exc, subprocess.CalledProcessError) and exc.stderr:
            msg = exc.stderr.strip()[:800]
        write_stub(out_html, ch, title, msg, titles=titles)
        return 1

    try:
        raw_body = extract_document_body(flat)
    except ValueError as exc:
        write_stub(out_html, ch, title, str(exc), titles=titles)
        return 1

    body_tex = sanitize_body(raw_body)
    fragment, pandoc_err = run_pandoc(body_tex)
    if fragment is None:
        write_stub(out_html, ch, title, f"Chuyển HTML thất bại: {pandoc_err}", titles=titles)
        return 1

    tpl = TEMPLATE_PATH.read_text(encoding="utf-8")
    slug = ch.lower()
    html = _fill_template(tpl, ch, title, slug, fragment, titles=titles)
    out_html.write_text(html, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
