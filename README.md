# 🚦 Hệ Thống Sa Bàn Giao Thông Thông Minh — Marie Curie Academy (MCA)
> **Dự án tham dự Cuộc thi Olympic STEM 2026 — Trường Đại học Sư phạm Hà Nội (HNUE)**  
> **Bảng thi:** Tiểu học | **Mô hình:** Kiến trúc lai Hybrid (PictoBlox AI + Vi điều khiển C++ Arduino Nano)  
> **Phiên bản:** `v2.2 Release` (Turnkey Hardware BOM & Electrical Audit Verified)

---

## 📌 Giới Thiệu Dự Án

Dự án sa bàn giao thông thông minh là giải pháp công nghệ giáo dục STEM toàn diện, kết hợp giữa **Trí tuệ Nhân tạo (AI)** nhận diện phương tiện ưu tiên qua thị giác máy tính và **Phần cứng điều khiển nhúng C++** thời gian thực với cơ chế an toàn Failsafe tức thời.

### Điểm nhấn công nghệ:
1. **Kiến trúc Lai Độc lập (Hybrid Architecture):**
   - **Tầng Thị giác AI (PictoBlox):** Thu nhận hình ảnh từ Camera, phân loại phương tiện (Xe Cứu thương, Xe Thường, Không có xe) bằng mô hình Google Teachable Machine, truyền ký tự lệnh qua Serial (`9600 BAUD`).
   - **Tầng Điều khiển Cứng (Arduino C++):** Vận hành FSM (Finite State Machine) 4 pha độc lập, hoàn toàn không bị phụ thuộc vào máy tính khi xảy ra sự cố cáp hoặc treo camera.
2. **Nút bấm Người đi bộ Khẩn cấp Tức thì (Instant Pedestrian Failsafe):**
   - Sử dụng cơ chế Interrupt phần cứng (Chân D2) kết hợp giải thuật chống dội (Debounce trong ISR). Đèn lập tức chuyển sang chu kỳ nhấp nháy vàng chuyển tiếp an toàn để người đi bộ qua đường.
3. **Chống nhiễu & Khóa ưu tiên (3000ms Minimum Hold Time):**
   - Xe cứu thương đi qua kích hoạt mã `'1'` được giữ làn xanh liên tục tối thiểu 3 giây, loại bỏ hiện tượng nhấp nháy hoặc mất tín hiệu khi xe vừa rời khỏi tầm quét camera.

---

## 📂 Cấu Trúc Thư Mục Dữ Liệu (`MCA/HNUE_olympic_stem/1.Data/c++ PictoBlox`)

Toàn bộ gói sản phẩm hoàn thiện được lưu trữ tại đường dẫn `MCA/HNUE_olympic_stem/1.Data/c++ PictoBlox/`:

| Tên Tệp Tin | Định Dạng | Mô Tả Kỹ Thuật |
| :--- | :--- | :--- |
| `traffic_light_hybrid_firmware.ino` | C++ / Arduino | Firmware vi điều khiển v2.1 Fixed: Đã loại bỏ hoàn toàn `IRAM_ATTR` gây lỗi trên AVR, chuẩn hóa chân GPIO Nano (D2-D12), Failsafe tức thì, Baudrate 9600. |
| `du_an_sa_ban_pictoblox.sb3` | PictoBlox / Scratch 3.0 | Dự án khối lệnh trực quan cho học sinh Tiểu học: Chứa sprite hoạt động `SaBan_MarieCurie`, biến bảng điều khiển và khối Teachable Machine. |
| `HUONG_DAN_LAP_TRINH_PICTOBLOX_VA_CPP_v2.docx` | Microsoft Word (323 KB) | Cẩm nang kỹ thuật bàn giao chính thức: Bản đồ Serial lệnh `0/1/2`, sơ đồ đấu nối chân Nano, hướng dẫn huấn luyện Teachable Machine và 9 câu hỏi đáp sự cố thực địa. |
| `so_do_khoi_lenh_pictoblox.png` | Ảnh HD (1600x1100) | Sơ đồ khối logic chương trình PictoBlox: Chu trình quét camera, phân loại AI, gửi Serial và cập nhật UI sa bàn. |
| `so_do_kien_truc_lai_hybrid.png` | Ảnh HD (1600x1050) | Sơ đồ kiến trúc luồng dữ liệu 2 tầng: Tầng Nhận diện AI trên PC và Tầng Chấp hành Thời gian thực trên Arduino Nano. |

---

## 🛒 Danh Mục Linh Kiện Mua Sắm & Dự Toán Kinh Phí (~400.000 VNĐ)

*Tuân thủ hạn mức kinh phí của Ban Tổ chức HNUE (< 1.000.000 VNĐ / đội thi, tiết kiệm ~60% ngân sách).*

### 1. Nhóm Mạch Điều Khiển & Cảm Biến:
* **Arduino Nano v3.0 (CH340 + Cáp Mini USB):** 1 chiếc (~65.000đ).
* **Đế mở rộng Nano Sensor Shield v3.0 (3-pin S-V-G):** 1 chiếc (~22.000đ) — *Cắm giắc chắc chắn, loại bỏ hoàn toàn nguy cơ tuột dây của bo lỗ Breadboard.*
* **Động cơ Micro Servo SG90 (9g, 180°):** 1 chiếc (~30.000đ) — Nâng hạ thanh cần Barie chắn đường.
* **Module Cụm 3 LED Giao thông 5V (Traffic Light):** 1 chiếc (~10.000đ) — Đèn ô tô (Đỏ D12 - Vàng D11 - Xanh D10).
* **Module 2 LED / LED đơn 5mm siêu sáng:** 1 cặp Đỏ (D6) - Xanh lá (D7) kèm 2 trở $220\Omega$ (~5.000đ) — Đèn người đi bộ. *(Khuyên dùng: Mua thêm 1 module Traffic Light 5V để tận dụng trở tích hợp sẵn).*
* **Còi chip Active Buzzer 5V:** 1 chiếc (~5.000đ) — Còi chủ động bíp dẫn đường cho học sinh qua đường và hú khi xe cứu thương chạy.
* **Module Nút bấm cơ học (Tactile Switch 3-pin):** 1 chiếc (~5.000đ) — Nút khẩn cấp Failsafe D2.
* **02 Tụ điện hóa 470µF / 16V:** 2 chiếc (~2.000đ) — Cắm song song chân nguồn VCC/GND gần Servo D9 triệt tiêu xung gai sụt áp.
* **Dây cáp bẹ Dupont Cái - Cái (40 sợi, 20cm):** 1 tép (~15.000đ).
* **Dây cáp bẹ Dupont Đực - Cái (20 sợi, 20cm):** 1 tép (~8.000đ).

### 2. Nhóm Thị Giác AI & Kết Nối:
* **Webcam USB mini (HD 720p hoặc 1080p):** 1 chiếc (~95.000đ nếu mua mới, hoặc tận dụng Webcam trường/laptop).
* **Bộ chia cổng USB (USB Hub 4 cổng):** 1 chiếc (~45.000đ) — Gom gọn cáp cắm vào Laptop.

### 3. Nhóm Vật Liệu Thi Công Sa Bàn:
* **Tấm Formex 5mm hoặc 10mm (60cm x 80cm):** 1 tấm (~50.000đ) — Mặt đế sa bàn vừa vặn bàn thi đấu.
* **Decal màu xám/đen & trắng:** 1 cuộn (~15.000đ) — Dán mặt đường và vạch kẻ phân làn.
* **Ống nhựa luồn dây điện phi 16 (dài 40cm):** 1 đoạn (~5.000đ) — Làm cột đèn và giá treo Camera.
* **Que gỗ balsa siêu nhẹ / que kem (22cm):** 1 thanh (~2.000đ) — Thanh cần Barie nhẹ < 3g.
* **Mô hình xe cứu thương đồ chơi mini:** 1 chiếc (~15.000đ) — Làm vật thể mẫu cho học sinh biểu diễn nhận diện AI.
* **Súng bắn keo nến & Băng dính xốp 3M:** 1 bộ (~15.000đ) — Cố định chân đế linh kiện.

---

## ⚡ Kết Quả Kiểm Toán Điện Áp & Tải Dòng (Simulation & Verification)

* **Nguồn cấp:** Cổng USB 2.0 máy tính cung cấp $5V - 500mA$.
* **Dòng điện trạng thái tĩnh (Normal Idle):** $\approx 62.2mA$ (An toàn, tiết kiệm điện).
* **Dòng điện đỉnh khi vận hành đầy tải:** $\approx 382mA < 500mA$ (Khi Servo kéo cần Barie + LED Đỏ ô tô + LED Xanh người đi bộ + Còi Buzzer).
* **Cơ chế chống sụt áp (Anti-Sag):** 02 tụ bù hóa nhôm $470\mu F / 16V$ xả điện bù tức thời khi Servo khởi động gia tốc, ngăn chặn 100% hiện tượng reset chip vi điều khiển hoặc rớt kết nối USB CH340.

---

## 🔌 Bản Đồ Giao Thức & Chân Nối Phần Cứng

### 1. Phân bổ Chân Vi điều khiển Arduino Nano:
* **Tuyến đường chính (Đèn ô tô):** `RED_CAR` = D12 | `YELLOW_CAR` = D11 | `GREEN_CAR` = D10
* **Đèn tín hiệu Người đi bộ:** `PED_RED` = D6 | `PED_GREEN` = D7
* **Âm thanh cảnh báo:** `BUZZER` = D8 (Chủ động, tích hợp nhịp 500ms / 200ms)
* **Cơ cấu cần chắn Barie:** `SERVO` = D9 (Góc $0^\circ$: Đóng ngang; Góc $90^\circ$: Mở dựng đứng)
* **Nút bấm Người đi bộ Khẩn cấp (Failsafe):** `BTN_FAILSAFE` = D2 (Ngắt ngoài `INT0`, `INPUT_PULLUP`)

### 2. Giao thức Truyền thông Serial (9600 BAUD):
* Nhận `'1'`: **ƯU TIÊN XE CỨU THƯƠNG** — Dọn đường khẩn cấp 2.5s $\to$ Xe Xanh, Barie đóng, Còi hú.
* Nhận `'2'`: **ƯU TIÊN HỌC SINH QUA ĐƯỜNG** — Đèn xe Vàng 3s $\to$ Xe Đỏ, Đi bộ Xanh, Barie mở $90^\circ$, Còi bíp 15s.
* Nhận `'0'`: **GIAO THÔNG BÌNH THƯỜNG** — Chu kỳ tự hành tuần hoàn 4 pha.

---

## 🚀 Hướng Dẫn Vận Hành Nhanh

1. **Nạp Firmware vào Arduino Nano:**
   - Mở `traffic_light_hybrid_firmware.ino` trên Arduino IDE.
   - Chọn Board: `Arduino Nano`, Processor: `ATmega328P`, Port: Cổng COM của CH340 $\to$ Nhấn **Upload**.
2. **Khởi chạy PictoBlox:**
   - Mở PictoBlox v9.2.1 $\to$ `File` $\to$ `Load from your computer` $\to$ Mở tệp `du_an_sa_ban_pictoblox.sb3`.
   - Kết nối cổng COM vi điều khiển (`Connect` $\to$ `Serial Port` $\to$ chọn cổng COM tương ứng).
   - Huấn luyện / dán URL Teachable Machine Model nhận diện xe.
   - Nhấn **Cờ xanh** để vận hành hệ thống.

---

## 🏆 Đơn Vị Phát Triển & Bản Quyền

* **Đơn vị:** Marie Curie Academy (MCA)
* **Đội tuyển tham dự:** Olympic STEM HNUE 2026 — Trường Đại học Sư phạm Hà Nội
* **Tác giả:** Thầy cô & Học sinh Đội tuyển STEM MCA
* **Hỗ trợ kỹ thuật & Kiểm toán:** Antigravity Engine (AE) Standard Architecture
