# CONTEXT.md — HNUE Olympic STEM 2026 (Marie Curie Academy)

> **CƠ SỞ DỮ LIỆU & BỐI CẢNH THI ĐẤU CHÍNH THỨC — SẴN SÀNG CHUYỂN GIAO LAPTOP DỰ THI**  
> **Dự án:** Hệ thống Đèn Giao Thông Học Đường Thông Minh Tích Hợp AI Vision & Rào Chắn Barie Tự Động  
> **Cuộc thi:** HNUE Olympic STEM 2026 — Chủ đề: *"Future Innovators - Những nhà kiến tạo tương lai"*  
> **Đơn vị tổ chức:** Trường Đại học Sư phạm Hà Nội (136 Xuân Thủy, Cầu Giấy, Hà Nội)  
> **Đoàn dự thi:** Trường Tiểu học, THCS & THPT Marie Curie Thái Bình  
> **Bảng thi đấu:** Bảng Tiểu học Khối 4 – 5 (Dự án STEM sáng tạo)  
> **GitHub Repo:** `https://github.com/Wh7tever/HNUE_olympic_stem.git` (Branch `main`)  
> **Thời điểm cập nhật chuyển giao:** Tháng 11/2026 (Đã nghiệm thu phần cứng & nạp Firmware v2.3 Final)

---

## 1. Hồ Sơ Đội Tuyển & Cán Bộ Phụ Trách (MCA Team)

| Vai trò | Họ và Tên | Lớp / Đơn vị | Trách nhiệm chuyên môn |
| :--- | :--- | :---: | :--- |
| **Trưởng đoàn** | **Cô Ngọc & Cô Phương Anh** | Cán bộ quản lý đoàn | Quản lý học sinh, điều phối hậu cần, liên hệ Ban tổ chức HNUE |
| **Hỗ trợ kỹ thuật** | **Thầy Lê Ngọc Anh** | Giáo viên phụ trách STEM | Chỉ đạo kỹ thuật mô hình, lập trình thuật toán, huấn luyện thuyết trình |
| **Thí sinh 1 (Đội trưởng)** | **Phạm Hữu Đạt** | Lớp 4A1 | Thuyết trình ý tưởng, kiến trúc STEM, thuật toán AI & logic vận hành |
| **Thí sinh 2 (Kỹ sư cơ khí)** | **Vũ Minh Quang** | Lớp 4A1 | Thuyết minh thiết kế mô hình, vật liệu tái chế, vận hành cơ khí |
| **Thí sinh 3 (Kỹ sư thử nghiệm)**| **Vũ Ngọc An Đông**| Lớp 5A1 | Thuyết minh ý nghĩa xã hội/môi trường, dữ liệu thử nghiệm, phản biện |

---

## 2. Thông Số Phần Cứng Thực Tế & Sơ Đồ Đấu Nối (Hardware Pinout)

Hệ thống sử dụng **Arduino Nano v3.0 (ATmega328P Old Bootloader)** cắm trên **Nano Sensor Shield v3.0 (chuẩn G-V-S)**.

| Cổng Shield | Chân (S - V - G) | Linh Kiện Thực Tế | Chức Năng Hoạt Động & Quy Chuẩn |
| :---: | :---: | :--- | :--- |
| **D2** | Blue (S) | Nút bấm cơ học Failsafe (dây tím) | Ngắt ngoài INT0 (Falling edge, debounce 300ms) - Cứu hộ vỉa hè khi camera mất mạng |
| **D6** | Blue (S) & Black (G) | Cụm LED Đi bộ — Đèn ĐỎ | Sáng khi luồng xe đang chạy hoặc khi Barie đóng |
| **D7** | Blue (S) & Black (G) | Cụm LED Đi bộ — Đèn XANH | Sáng khi học sinh được phép qua đường (Chân Vàng bỏ trống đúng QCVN 41:2019) |
| **D8** | Blue (S) & Black (G) | Còi chip Active Buzzer 5V | Bíp đếm ngược 15s (12s chậm + 3s nhanh) và hú dồn dập khi xe cứu thương đến |
| **D9** | Blue (S), Red (V), Black (G) | Động cơ Servo mini SG90 | Barie tự động: 0° đóng ngang, 90° mở đứng, quét mượt phi chặn 3°/20ms |
| **D10** | Blue (S) | Cụm LED Xe Ô tô — Đèn XANH | Bật khi thông luồng xe bình thường hoặc mở ưu tiên cứu thương |
| **D11** | Blue (S) | Cụm LED Xe Ô tô — Đèn VÀNG | Báo giảm tốc 3s trước khi dừng xe; nhấp nháy 1Hz ở chế độ tự hành Watchdog |
| **D12** | Blue (S) | Cụm LED Xe Ô tô — Đèn ĐỎ | Dừng toàn bộ phương tiện khi học sinh qua đường |
| **D13** | Red (V) & Black (G) | Tụ hóa 470µF / 16V | Mắc song song nguồn 5V-GND triệt tiêu sụt áp (Brownout Reset) khi Servo quét |

> **Thông số nạp & giao tiếp:**
> - Vi điều khiển: `ATmega328P (Old Bootloader)`
> - Baudrate nạp (avrdude / Arduino IDE): `57600 baud`
> - Baudrate chạy thực tế (Serial Monitor / Web / PictoBlox): `9600 baud`
> - Giao thức lệnh: `'H'` (Heartbeat), `'0'` (Đường vắng), `'1'` (Cứu thương), `'2'` (Học sinh qua đường).

---

## 3. Kiến Trúc Phần Mềm & Thư Mục Dự Án

### 3.1. Cấu Trúc Tệp Tin Dự Án (Repository Tree)
```text
HNUE_olympic_stem/
├── 1.Data/
│   ├── 1. Huong dan & The le/          # Thể lệ, văn bản chính thức của BTC HNUE 2026
│   ├── 2. Ho so/                       # Hồ sơ văn bản nộp dự thi
│   │   ├── HO_SO_TOAN_DIEN_DU_AN_STEM_OLYMPIC_2026.docx  # Bản thuyết minh 130 trang
│   │   ├── SO_TAY_KY_THUAT_VA_NHAT_KY_THUC_HANH.docx     # Sổ tay kỹ thuật & Nhật ký 14 buổi
│   │   ├── DANH_SACH_MUA_SAM_LINH_KIEN_THUC_TE.docx      # Bảng kê tài chính Shopee
│   │   ├── CHECKLIST_DO_CAN_MUA_VA_CHUAN_BI.docx         # Checklist kiểm tra thiết bị
│   │   └── 1.Kế hoạch thi HNUE STEM OLYMPIC.docx
│   ├── 3. Phan mem & Ma nguon Hybrid/  # Phần mềm thi đấu
│   │   ├── traffic_light_hybrid_firmware.ino             # Firmware v2.3 Final chính thức
│   │   ├── test_hardware_diagnostic.ino                  # Firmware chẩn đoán tự động
│   │   └── du_an_sa_ban_pictoblox.sb3                    # Dự án PictoBlox AI Scratch
│   └── 4. Hinh anh & Ban ve 3D/        # Phác thảo phối cảnh sa bàn, thiết kế kỹ thuật
├── src/
│   ├── ai_traffic_web_controller.html  # Trạm Web Serial AI Camera góc 45°
│   ├── traffic_light_arduino.ino
│   └── test_hardware_diagnostic.ino
├── CONTEXT.md                          # Trí nhớ & Bối cảnh dự án (file này)
├── LAPTOP_MIGRATION_GUIDE.md           # Cẩm nang chuyển giao và cài đặt laptop
└── AGENTS.md                           # Hiến pháp vận hành của Antigravity Engine
```

### 3.2. Trạng Thái Dự Án Hiện Tại
- **Hồ sơ:** Đã phẫu thuật sạch 100% dòng USB Hub (không mua). Định mức sa bàn = 334.000 VNĐ; gói linh kiện thực tế kèm dự phòng = 623.614 VNĐ.
- **Phần cứng:** Đã lắp ráp đầy đủ, tụ điện 470µF đã nối an toàn, còi đã lột tem niêm phong âm lượng to rõ.
- **Firmware:** Đã nạp thành công Firmware v2.3 Final vào Arduino Nano qua cổng COM3.
- **Kịch bản thi đấu:** Đã test pass toàn bộ 5 tình huống (Đường vắng, Học sinh xin đường, Cứu thương khẩn cấp, Nút bấm vỉa hè Failsafe, Watchdog tự hành nháy vàng 1Hz).

---

## 4. Hai Phương Án Biểu Diễn AI Trên Laptop

1. **Phương án 1 (Giao diện Web Serial hiện đại):** 
   - Mở `src/ai_traffic_web_controller.html` bằng Google Chrome.
   - Bấm `🔌 Kết Nối Cổng USB Arduino` $\to$ chọn cổng COM của Arduino $\to$ Bấm `▶️ Khởi Động Camera & AI`.
2. **Phương án 2 (Kéo thả khối PictoBlox):**
   - Mở phần mềm `PictoBlox` $\to$ Mở tệp `1.Data/3. Phan mem & Ma nguon Hybrid/du_an_sa_ban_pictoblox.sb3`.
   - Kết nối cổng COM Arduino Nano và bấm cờ xanh.
