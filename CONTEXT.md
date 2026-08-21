# CONTEXT.md — Workspace Root Context (`E:\Antigravity`)

Updated At: 2026-08-11
Workspace Root: `E:\Antigravity`
Host OS / Control Plane: `E:\Antigravity\Antigravity_engine`

---

## 1. Workspace Identity & Architecture

`E:\Antigravity` là thư mục làm việc cấp cao nhất (Workspace Root), chứa cỗ máy **Antigravity Engine (Host OS)** và các **Dự án thành phần (Subprojects)** độc lập.

### Danh sách 9 Subprojects:

| Subproject | Mục đích & Mô tả | Trạng Thái / Công Nghệ |
| --- | --- | --- |
| **`Antigravity_engine`** | **Host OS / Control Plane** vận hành hệ thống AI Agent (RCP, SDLC Gates, CodeGraph) | PowerShell, Python, Markdown, MCP |
| **`ExamPro`** | Ứng dụng web xử lý đề thi, trộn đề, nhận diện LaTeX/MathJax & xuất bản Word/PDF | React, Vite, Node.js, Supabase |
| **`MarieCurie_Portal`** | Cổng thông tin điện tử trường Marie Curie (Tuyển sinh, TKB, Tin tức, Văn bản, Admin) | HTML5, CSS3, JavaScript |
| **`Preschool_MCA`** | Bài giảng mầm non & tài liệu giáo dục trực quan | HTML, CSS, JavaScript |
| **`Chuan_van_ban`** | Chuẩn hóa thể thức văn bản hành chính & báo cáo SSO/HBS | Word, Automation |
| **`LMS_Support_Extension`** | Browser Extension hỗ trợ hệ thống LMS | JavaScript, HTML, CSS |
| **`MCA`** | Hệ thống giải & quản lý thời khóa biểu (TKB) | Data Processing, HTML |
| **`System admin`** | Quản trị hệ thống hạ tầng IT (Ruijie Reyee Gateway, Hikvision CCTV, Windows Tuning) | Sysadmin, PowerShell, ReyeeOS, NVR 5.0 |
| **`gdrive_downloader_extension`** | Chrome Extension hỗ trợ tự động tải dữ liệu Google Drive | Manifest v3, JavaScript |

---

## 2. Quy Tắc Giao Tiếp & Governance

1. **Host OS Governance:** `Antigravity_engine` đóng vai trò quản trị toàn bộ hoạt động của AI Agents trên mọi dự án thuộc `E:\Antigravity\*`.
2. **Cổng Lệnh (`ag.cmd`):** Mọi thao tác lập trình không hiển nhiên đều phải thông qua cổng `ag.cmd task` và `ag.cmd command`.
3. **Tính Độc Lập:** Mỗi subproject có thư mục và ngữ cảnh riêng. Cấm tự ý trộn lẫn tài liệu sysadmin hay source code giữa các subproject.
