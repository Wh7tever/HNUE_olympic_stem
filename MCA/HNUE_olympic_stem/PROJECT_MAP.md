# PROJECT_MAP.md — HNUE Olympic STEM (MCA)

Bản đồ cấu trúc và luồng dữ liệu của dự án Olympic STEM trường Marie Curie Academy (MCA).

## 1. Summary

- **Project name:** HNUE_olympic_stem
- **Organization:** Marie Curie Academy (MCA)
- **Target Competition:** Olympic STEM — Đại học Sư phạm Hà Nội (HNUE)
- **Project size:** Standard (Full AOK/RCP Harness)
- **Stack:** Python, C++/Arduino, Web Telemetry (HTML/CSS/JS), MarkItDown, Office Automation
- **Primary goal:** Huấn luyện đội tuyển, phát triển sản phẩm sáng tạo STEM và hoàn thiện hồ sơ dự thi Olympic STEM HNUE đạt thứ hạng cao.
- **Domain context:** Xem chi tiết tại `CONTEXT.md`

## 2. Top-Level Structure

| Đường dẫn (Path) | Mục đích & Trách nhiệm | Ghi chú & Quy ước |
| --- | --- | --- |
| `docs/` | Toàn bộ tài liệu chính thức | Thể lệ, thuyết minh, tiêu chí chấm thi, quyết định kỹ thuật |
| `docs/the-le-cuoc-thi/` | Quy chế và điều lệ thi từ BTC HNUE | Quy định sa bàn, kích thước, thể thức thi đấu |
| `docs/thuyet-minh-de-tai/` | Thuyết minh khoa học, hồ sơ kỹ thuật | Soạn thảo theo chuẩn mẫu của Hội đồng Sư phạm |
| `docs/decisions/` | Architectural Decision Records (ADRs) | Lưu vết lý do kỹ thuật chọn phần cứng/thuật toán |
| `src/` | Mã nguồn cốt lõi của giải pháp STEM | Thuật toán điều khiển, xử lý dữ liệu, giao diện giám sát |
| `tests/` | Bộ kiểm thử tự động & mô phỏng | Unit tests thuật toán bám vạch, đo khoảng cách, xử lý số liệu |
| `assets/` | Tài nguyên trực quan | Bản vẽ cơ khí, sơ đồ mạch, poster dự thi, ảnh sa bàn thực nghiệm |
| `scripts/` | Script tự động hóa | Script xuất bản tài liệu, kiểm toán format, build mô hình |
| `tools/` | Bộ công cụ vận hành Antigravity Engine | `Invoke-ProjectOperatingGate.ps1`, `Sync-ProjectStatus.ps1`, v.v. |
| `TASKS/` | Hồ sơ nhiệm vụ kỹ thuật per-task | Lưu vết chi tiết từng hạng mục công việc |
| `.aok-runtime/` | Dữ liệu runtime nội bộ của RCP | Logs, cache, báo cáo thẩm định kỹ thuật tự động |

## 3. Module Boundaries & Responsibilities

| Module | Trách nhiệm | Giao tiếp đối ngoại | Điểm cần bảo vệ |
| --- | --- | --- | --- |
| `Core Controller` | Đọc cảm biến, tính toán thuật toán, điều khiển chấp hành | Serial / GPIO / Bluetooth | Tốc độ chu kỳ điều khiển không bị trễ |
| `Sensor Pipeline` | Lọc nhiễu tín hiệu, phát hiện vật cản, nhận diện vạch | Trả dữ liệu float / boolean | Bộ lọc không tạo độ trễ pha quá lớn |
| `Mission Planner` | Điều phối các pha thi đấu trên sa bàn theo kịch bản | Gọi lệnh từ Controller API | Kịch bản chuyển pha phải có timeout an toàn |
| `Documentation Engine` | Kết xuất bản thuyết minh, slide và poster | File Word/PDF chuẩn in | Chuẩn font chữ, căn lề, hình ảnh sắc nét |

## 4. Common Workflows

| Quy trình | Lệnh khởi chạy | Nghiệm thu |
| --- | --- | --- |
| Kiểm tra trạng thái dự án | `.\tools\Test-ProjectAgentReadiness.ps1` | Ready Score >= 90 |
| Đồng bộ tiến độ | `.\tools\Sync-ProjectStatus.ps1` | `PROJECT_STATUS.md` cập nhật |
| Thẩm định kỹ thuật (Gate) | `.\tools\Invoke-ProjectOperatingGate.ps1 -Mode checkpoint` | Status = PASS |
