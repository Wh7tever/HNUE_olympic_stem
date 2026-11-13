# RUNBOOK.md — HNUE Olympic STEM Operating Procedures

Hướng dẫn vận hành chuẩn cho AI Agents và Đội ngũ Kỹ thuật STEM Marie Curie Academy (MCA).

---

## 1. Môi Trường & Thiết Lập Ban Đầu

1. Di chuyển vào thư mục dự án:
   ```powershell
   cd E:\Antigravity\MCA\HNUE_olympic_stem
   ```
2. Kiểm tra độ sẵn sàng của Agent Harness:
   ```powershell
   .\tools\Test-ProjectAgentReadiness.ps1
   ```
3. Cập nhật và đồng bộ bảng trạng thái:
   ```powershell
   .\tools\Sync-ProjectStatus.ps1
   ```

---

## 2. Quy Trình Nhận & Thực Thi Nhiệm Vụ (Task Execution)

Khi bắt đầu một nhiệm vụ kỹ thuật mới (ví dụ viết code, soạn thuyết minh, xây dựng sa bàn):

1. **Khởi tạo Task Work Item:**
   ```powershell
   .\tools\New-ProjectWorkItem.ps1 -TaskId "T-0002" -Title "Boc tach the le cuoc thi HNUE Olympic STEM" -Slice "VS-001" -Owner "Antigravity_Engine"
   ```
2. **Thực thi với nguyên tắc Read-Before-Write:**
   - Đọc kỹ tài liệu yêu cầu trong `docs/the-le-cuoc-thi/`.
   - Lập phương án kỹ thuật và kiểm thử đơn vị.
3. **Chạy Thẩm Định Kỹ Thuật (Operating Gate):**
   ```powershell
   .\tools\Invoke-ProjectOperatingGate.ps1 -Mode checkpoint
   ```
4. **Cập nhật trạng thái Task sau nghiệm thu:**
   ```powershell
   .\tools\Update-ProjectWorkItem.ps1 -TaskId "T-0002" -Status "done" -Evidence "AE_VALIDATION_REPORT.md"
   ```

---

## 3. Khắc Phục Sự Cố & An Toàn (Troubleshooting & Safety)

- **Lỗi cảm biến / Mất kết nối vi điều khiển:**
  - Kiểm tra cổng COM và tốc độ Baud rate (115200 bps).
  - Không nạp code khi cơ cấu chấp hành (động cơ, cánh tay robot) đang cắm pin công suất cao.
- **Sự cố xung đột git hoặc file hỏng:**
  - Không dùng `git reset --hard` khi chưa backup.
  - Sử dụng `tools\Test-ProjectDeliveryState.ps1` để kiểm tra độ nguyên vẹn.
