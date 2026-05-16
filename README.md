# Khai Phá Dữ Liệu – Tài liệu ôn tập

Tổng hợp kiến thức, câu hỏi tự luận (20 câu) và trắc nghiệm (40 câu) theo từng chương môn **Khai Phá Dữ Liệu** – ĐH Bách Khoa TP.HCM.

**GitHub Pages:** https://hungdt31.github.io/data-mining-cheatsheet/

---

## Các chương

| Chương | Chủ đề | Web | PDF |
|--------|--------|-----|-----|
| C1 | Giới thiệu về Khai Phá Dữ Liệu | [Xem][c1-web] | [PDF][c1-pdf] |
| C2 | Tiền Xử Lý Dữ Liệu | [Xem][c2-web] | [PDF][c2-pdf] |
| C3 | Hồi Quy và Dự Đoán (Regression) | [Xem][c3-web] | [PDF][c3-pdf] |
| C4 | Phân Lớp Dữ Liệu (Classification) | [Xem][c4-web] | [PDF][c4-pdf] |
| C5 | Phân Cụm Dữ Liệu (Clustering) | [Xem][c5-web] | [PDF][c5-pdf] |
| C6 | Luật Kết Hợp và Thuật Toán Apriori | [Xem][c6-web] | [PDF][c6-pdf] |

[c1-web]: https://hungdt31.github.io/data-mining-cheatsheet/chapters/c1.html
[c2-web]: https://hungdt31.github.io/data-mining-cheatsheet/chapters/c2.html
[c3-web]: https://hungdt31.github.io/data-mining-cheatsheet/chapters/c3.html
[c4-web]: https://hungdt31.github.io/data-mining-cheatsheet/chapters/c4.html
[c5-web]: https://hungdt31.github.io/data-mining-cheatsheet/chapters/c5.html
[c6-web]: https://hungdt31.github.io/data-mining-cheatsheet/chapters/c6.html

[c1-pdf]: https://hungdt31.github.io/data-mining-cheatsheet/chapters/c1.pdf
[c2-pdf]: https://hungdt31.github.io/data-mining-cheatsheet/chapters/c2.pdf
[c3-pdf]: https://hungdt31.github.io/data-mining-cheatsheet/chapters/c3.pdf
[c4-pdf]: https://hungdt31.github.io/data-mining-cheatsheet/chapters/c4.pdf
[c5-pdf]: https://hungdt31.github.io/data-mining-cheatsheet/chapters/c5.pdf
[c6-pdf]: https://hungdt31.github.io/data-mining-cheatsheet/chapters/c6.pdf

---

## Cấu trúc repo

```
.
├── .github/workflows/build.yml   # CI: LaTeX → PDF + HTML → GitHub Pages
├── chapters/
│   ├── _preamble.tex             # Shared packages & cấu hình
│   ├── _title.tex                # Block tiêu đề dùng chung
│   ├── C1/main.tex  …  C6/main.tex
├── assets/
│   ├── chapter-template.html     # Template trang web từng chương
│   └── chapters.css              # CSS editorial (responsive)
├── scripts/
│   ├── build_chapter_html.py     # LaTeX → HTML (cần pandoc + latexpand)
│   ├── render_index.py           # Sinh index.html cho CI
│   ├── dev_pages.py              # Server xem trước cục bộ
│   └── chapter-titles.json       # Tiêu đề từng chương
└── index.html                    # Trang mục lục (template, CI thay placeholder)
```

---

## Xem trước cục bộ (dev)

Không cần cài thêm gì ngoài Python 3.10+:

```bash
python scripts/dev_pages.py
# → http://127.0.0.1:8765/
```

Mỗi chương có nút **«Trên web»** (nhúng PDF trực tiếp) và **«PDF»**. Dừng bằng Ctrl+C.

Tùy chọn:

```bash
python scripts/dev_pages.py --port 3000   # đổi cổng
python scripts/dev_pages.py --build-only  # chỉ tạo .web-dev/, không bật server
python scripts/dev_pages.py --no-open     # không tự mở trình duyệt
```

### Sinh HTML đầy đủ từ LaTeX (tùy chọn)

Cần **pandoc** và **latexpand** (gói `texlive-extra-utils`):

```bash
python scripts/build_chapter_html.py C5
# lặp C1..C6, sau đó rebuild dev:
python scripts/dev_pages.py --build-only
```

---

## Thêm / sửa nội dung chương

Mỗi `chapters/CX/main.tex` theo cấu trúc:

```latex
\documentclass[10pt]{article}
\input{../_preamble}

\begin{document}
\onehalfspacing
\renewcommand{\arraystretch}{1.5}

\newcommand{\ChapterNum}{X}
\newcommand{\ChapterTitle}{TÊN CHƯƠNG}
\input{../_title}

% Nội dung kiến thức
% Câu hỏi tự luận
% Câu hỏi trắc nghiệm
% Đáp án

\end{document}
```

Push lên `main` → CI tự biên dịch, sinh HTML và deploy lên GitHub Pages.

---

## Cài đặt GitHub Pages (lần đầu)

1. **Settings → Pages → Source = GitHub Actions** (không chọn "Deploy from a branch").
2. Push lên `main` hoặc chạy thủ công: **Actions → Build & Publish LaTeX PDFs → Run workflow**.

**Lỗi `Not Found` ở bước "Setup GitHub Pages":**
- Chưa bật Pages hoặc nguồn chưa đúng → làm bước 1.
- Repo private trên tài khoản miễn phí: GitHub Pages yêu cầu repo public hoặc gói trả phí.

---

## Tài liệu tham khảo

- Jiawei Han, Micheline Kamber, Jian Pei – *Data Mining: Concepts and Techniques*, 3rd Ed.
- David Hand, Heikki Mannila, Padhraic Smyth – *Principles of Data Mining*
