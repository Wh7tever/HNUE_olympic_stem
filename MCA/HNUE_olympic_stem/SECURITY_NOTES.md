# SECURITY_NOTES.md — HNUE Olympic STEM Data & Security Rules

> **Cảnh báo:** Nghiêm cấm lưu trữ mật khẩu, API key, token cá nhân hoặc thông tin định danh học sinh (PII) trong mã nguồn hoặc kho lưu trữ mở.

---

## 1. Khu Vực Nhạy Cảm (Sensitive Areas)

1. **Thông tin học sinh & Đội thi (Student PII):**
   - Họ tên, ngày sinh, số điện thoại, căn cước công dân của các thành viên đội thi MCA phải được bảo mật tuyệt đối, chỉ nộp qua kênh đăng ký chính thức của Ban tổ chức HNUE.
2. **Kênh truyền thông không dây (Wireless Telemetry):**
   - Nếu robot / sa bàn sử dụng Wi-Fi hoặc Bluetooth để truyền dữ liệu, phải đặt mật khẩu mạng riêng (WPA2/WPA3) hoặc dùng token bắt tay (Handshake Token) để tránh bị can thiệp tín hiệu khi thi đấu trên sàn.
3. **Mã nguồn giải thuật độc quyền:**
   - Các giải thuật bám vạch tối ưu, mô hình nhận diện AI hoặc thiết kế cơ khí phải giữ bảo mật trước ngày thi chính thức.

---

## 2. Quy Tắc Truy Cập Của Agent (Agent Access Rules)

- Không commit các file chứa cấu hình phần cứng nhạy cảm hoặc camera streaming credentials lên repo public.
- Mọi tài liệu dự thi xuất bản dưới dạng file Word/PDF phải được rà soát bỏ metadata nhạy cảm trước khi nộp.
