# Khai Phá Dữ Liệu – Tài liệu ôn tập

Tổng hợp kiến thức, câu hỏi tự luận (20 câu) và trắc nghiệm (40 câu) theo từng chương môn **Khai Phá Dữ Liệu** – ĐH Bách Khoa TP.HCM.

## 📄 Tài liệu PDF

Sau mỗi lần push lên `main`, GitHub Actions tự động biên dịch LaTeX và công bố PDF lên GitHub Pages:

| Chương | Chủ đề | PDF |
|--------|--------|-----|
| C1 | Giới thiệu về Khai Phá Dữ Liệu | [c1.pdf][c1] |
| C2 | Tiền Xử Lý Dữ Liệu | [c2.pdf][c2] |
| C3 | Phân Lớp Dữ Liệu (Classification) | [c3.pdf][c3] |
| C4 | Hồi Quy và Dự Đoán (Regression) | [c4.pdf][c4] |
| C5 | Phân Cụm Dữ Liệu (Clustering) | [c5.pdf][c5] |
| C6 | Luật Kết Hợp và Thuật Toán Apriori | [c6.pdf][c6] |

> Thay `<your-github-username>` và `<repo-name>` bằng thông tin thực của bạn.

[c1]: https://<your-github-username>.github.io/<repo-name>/chapters/c1.pdf
[c2]: https://<your-github-username>.github.io/<repo-name>/chapters/c2.pdf
[c3]: https://<your-github-username>.github.io/<repo-name>/chapters/c3.pdf
[c4]: https://<your-github-username>.github.io/<repo-name>/chapters/c4.pdf
[c5]: https://<your-github-username>.github.io/<repo-name>/chapters/c5.pdf
[c6]: https://<your-github-username>.github.io/<repo-name>/chapters/c6.pdf

## 🗂️ Cấu trúc thư mục

```
.
├── .github/
│   └── workflows/
│       └── build.yml          # CI/CD: compile LaTeX → deploy GitHub Pages
├── chapters/
│   ├── _preamble.tex          # Shared: tất cả \usepackage & cấu hình
│   ├── _title.tex             # Shared: block tiêu đề (dùng \ChapterNum, \ChapterTitle)
│   ├── jasa_harvard.sty       # Bibliography style
│   ├── C1/main.tex
│   ├── C2/main.tex
│   ├── C3/main.tex
│   ├── C4/main.tex
│   ├── C5/main.tex            # ✅ Đầy đủ nội dung – Clustering
│   └── C6/main.tex            # ✅ Đầy đủ nội dung – Association Rules
└── slide/                     # Slide gốc của giảng viên (PDF)
```

## ✍️ Thêm nội dung cho chương mới

Mỗi `CX/main.tex` chỉ cần:

```latex
\documentclass[10pt]{article}
\input{../_preamble}           % kéo toàn bộ packages

\begin{document}
\onehalfspacing
\renewcommand{\arraystretch}{1.5}

\newcommand{\ChapterNum}{X}
\newcommand{\ChapterTitle}{TÊN CHƯƠNG}
\input{../_title}

% --- Nội dung kiến thức ---
% --- Câu hỏi tự luận ---
% --- Câu hỏi trắc nghiệm ---
% --- Đáp án (trang cuối) ---

\end{document}
```

Khi push lên `main`, CI/CD tự biên dịch và cập nhật PDF trên GitHub Pages.

## ⚙️ Cài đặt GitHub Pages

1. Vào **Settings → Pages** của repo (tab **Pages** bên trái).
2. Mục **Build and deployment**:
   - **Source** phải là **GitHub Actions** (không chọn “Deploy from a branch” nếu bạn dùng workflow `deploy-pages`).
3. Push lên `main` (hoặc chạy workflow thủ công: **Actions → Build & Publish… → Run workflow**).

### Nếu job “Setup GitHub Pages” báo `Not Found` / Get Pages site failed

- Nguyên nhân: repo chưa có **GitHub Pages** hoặc nguồn chưa phải **GitHub Actions** → API `GET /repos/.../pages` trả 404.
- **Cách 1 (khuyên dùng):** Settings → Pages → Source = **GitHub Actions**, lưu rồi chạy lại workflow.
- **Cách 2:** Workflow đã có `enablement: true` trong bước `configure-pages` để thử bật Pages qua API; cần quyền `pages: write` (file workflow đã cấu hình).
- Repo **private** trên tài khoản miễn phí: GitHub có thể **không** cấp GitHub Pages—cần public repo hoặc gói hỗ trợ Pages cho private.

## 📚 Tài liệu tham khảo

- Jiawei Han, Micheline Kamber, Jian Pei – *Data Mining: Concepts and Techniques*, 3rd Ed.
- David Hand, Heikki Mannila, Padhraic Smyth – *Principles of Data Mining*
