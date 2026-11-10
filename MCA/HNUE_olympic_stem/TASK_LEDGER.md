# TASK_LEDGER.md

Use this file as the project task ledger across humans, agents, and sessions.

| Task ID | Slice | Status | Owner/Agent | Scope | Files/Modules | Verification | Blocker | Evidence | Interaction Mode | Blocked By |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| T-0001 | VS-001 | done | Antigravity_Engine | Khởi tạo và thiết lập toàn diện bộ khung vận hành Antigravity Engine (AOK / RCP) cho dự án HNUE Olympic STEM | `CONTEXT.md`, `AGENTS.md`, `PROJECT_MAP.md`, `ARCHITECTURE.md`, `tools/`, `TASKS/`, `QUALITY_GATES.md` | Test-ProjectAgentReadiness PASS & Invoke-ProjectOperatingGate PASS | none | AE_VALIDATION_REPORT.md | AFK | none |
| T-0002 | VS-001 | done | Antigravity_Engine | Bóc tách thể lệ, bảng Tiểu học, danh sách 3 học sinh MCA, thang điểm 100, quy chế 5p thuyết trình + 5p phản biện và trần chi phí ≤ 1.000.000 VNĐ | `1.Data/`, `docs/the-le-cuoc-thi/`, `CONTEXT.md` | Đối soát 100% điều lệ ban tổ chức HNUE và kế hoạch trường MCA | none | `CONTEXT.md` | AFK | none |
| T-0003 | VS-002 | done | Antigravity_Engine | Thiết kế kiến trúc giải pháp kỹ thuật, mạch điều khiển, lập trình tích hợp AI (Teachable Machine) và cơ cấu chấp hành | `src/`, `assets/` | Mã nguồn Arduino Nano (`src/traffic_light_arduino.ino`) và Trạm Web AI Serial (`src/ai_traffic_web_controller.html`) | none | `src/` | AFK | T-0002 |
| T-0004 | VS-003 | todo | Antigravity_Engine | Biên soạn bản thuyết minh đề tài, poster khoa học và slide trình chiếu chuẩn Hội đồng giám khảo HNUE | `docs/thuyet-minh-de-tai/`, `assets/` | File thuyết minh .docx/.pdf và slide chuẩn thể thức hội đồng | none | TO_BE_FILLED | AFK | T-0003 |
| T-0005 | VS-001 | done | Antigravity_Engine | Xây dựng ý tưởng giải pháp STEM cụ thể cho Bảng Tiểu học theo Phương án 1 (Webcam USB rời gắn đỉnh cột), tính toán động học, sa bàn và bảng kê chi phí chi tiết ≤ 1.000.000 VNĐ | `1.Data/` | Bảng kê chi phí 295.000 VNĐ (tiết kiệm 705.000 VNĐ) và hồ sơ tính toán hoàn chỉnh | none | `1.Data/HO_SO_THIET_KE_KY_THUAT_VA_DU_TOAN_CHI_TIET.md` | AFK | T-0002 |
| T-0006 | VS-003 | todo | Antigravity_Engine | Biên soạn khung Sổ tay kỹ thuật (Engineering Notebook) ghi nhật ký 5 bước quy trình thiết kế kỹ thuật | `docs/thuyet-minh-de-tai/SO_TAY_KY_THUAT.md` | Cấu trúc đầy đủ Ask -> Imagine -> Plan -> Create -> Improve | none | TO_BE_FILLED | AFK | T-0005 |
| T-0007 | VS-003 | todo | Antigravity_Engine | Soạn thảo kịch bản thuyết trình đúng 5 phút và ngân hàng 10 câu hỏi phản biện mẫu chuẩn bị cho 3 học sinh | `docs/thuyet-minh-de-tai/KICH_BAN_THUYET_TRINH_5_PHUT.md` | Bố cục khớp 5 câu hỏi cốt lõi của BGK, khớp thời lượng 5 phút | none | TO_BE_FILLED | AFK | T-0005 |
| T-0008 | VS-002 | done | Antigravity_Engine | Kiểm toán danh mục linh kiện (Đủ - Thừa - Thiếu), phát hiện bẫy sụt áp IC AMS1117, lập kế hoạch thử nghiệm 4 giai đoạn và xuất bản firmware chẩn đoán tự động | `1.Data/`, `src/`, `scripts/` | 8 trang tài liệu PDF/DOCX, firmware chẩn đoán `test_hardware_diagnostic.ino`, code FSM 5 trạng thái đồng bộ 100% | none | `1.Data/KE_HOACH_THU_NGHIEM_VA_DANH_GIA_THIET_BI.pdf` | AFK | T-0003 |

## Status Values

- todo
- doing
- blocked
- review
- done

## Interaction Mode

- AFK: agent can continue without user input.
- HITL: human decision, private access, external action, or product judgment is required.
- unknown: not classified yet.

## Agent Rule

- Claim one task at a time unless explicitly instructed otherwise.
- Do not mark done without verification evidence.
- If blocked, record the blocker and recommended next move.
