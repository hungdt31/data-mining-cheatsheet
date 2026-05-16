#!/usr/bin/env python3
"""Đọc dist/chapters — tạo manifest JSON + dist/index.html từ index.html gốc."""
from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def main() -> None:
    repo = os.environ["GITHUB_REPO"]
    dist_ch = ROOT / "dist" / "chapters"
    manifest: list[dict] = []
    for cid in ["C1", "C2", "C3", "C4", "C5", "C6"]:
        low = cid.lower()
        has_pdf = (dist_ch / f"{low}.pdf").is_file()
        has_html = (dist_ch / f"{low}.html").is_file()
        if has_pdf or has_html:
            manifest.append({"id": cid, "pdf": has_pdf, "html": has_html})

    blob = json.dumps(manifest, ensure_ascii=False)
    idx = (ROOT / "index.html").read_text(encoding="utf-8")
    idx = idx.replace("__GITHUB_REPOSITORY__", repo).replace("__CHAPTERS_JSON__", blob)
    (ROOT / "dist" / "index.html").write_text(idx, encoding="utf-8")


if __name__ == "__main__":
    main()
