# 🚦 Hệ Thống Sa Bàn Giao Thông Thông Minh — Marie Curie Academy (MCA)
> **Dự án tham dự Cuộc thi Olympic STEM 2026 — Trường Đại học Sư phạm Hà Nội (HNUE)**  
> **Bảng thi:** Tiểu học | **Mô hình:** Kiến trúc lai Hybrid (PictoBlox AI + Vi điều khiển C++ Arduino Nano)  
> **Phiên bản:** `v2.1 Fixed` (Combat-Ready & Turnkey)

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
| `traffic_light_hybrid_firmware.ino` | C++ / Arduino | Firmware vi điều khiển v2.1 Fixed: Đã loại bỏ hoàn toàn `IRAM_ATTR` gây lỗi trên AVR, chuẩn hóa chân GPIO Nano (D2-D11), Failsafe tức thì, Baudrate 9600. |
| `du_an_sa_ban_pictoblox.sb3` | PictoBlox / Scratch 3.0 | Dự án khối lệnh trực quan cho học sinh Tiểu học: Chứa sprite hoạt động `SaBan_MarieCurie`, biến bảng điều khiển và khối Teachable Machine. |
| `HUONG_DAN_LAP_TRINH_PICTOBLOX_VA_CPP_v2.docx` | Microsoft Word (323 KB) | Cẩm nang kỹ thuật bàn giao chính thức: Bản đồ Serial lệnh `0/1/2`, sơ đồ đấu nối chân Nano, hướng dẫn huấn luyện Teachable Machine và 9 câu hỏi đáp sự cố thực địa. |
| `so_do_khoi_lenh_pictoblox.png` | Ảnh HD (1600x1100) | Sơ đồ khối logic chương trình PictoBlox: Chu trình quét camera, phân loại AI, gửi Serial và cập nhật UI sa bàn. |
| `so_do_kien_truc_lai_hybrid.png` | Ảnh HD (1600x1050) | Sơ đồ kiến trúc luồng dữ liệu 2 tầng: Tầng Nhận diện AI trên PC và Tầng Chấp hành Thời gian thực trên Arduino Nano. |

---

## 🔌 Bản Đồ Giao Thức & Chân Nối Phần Cứng

### 1. Phân bổ Chân Vi điều khiển Arduino Nano:
* **Tuyến đường chính (Đại lộ):**
  * `RED_1` = D4 | `YELLOW_1` = D3 | `GREEN_1` = D5
* **Tuyến đường phụ (Ngõ/Phố cắt ngang):**
  * `RED_2` = D7 | `YELLOW_2` = D6 | `GREEN_2` = D8
* **Đèn tín hiệu Người đi bộ:**
  * `PED_RED` = D9 | `PED_GREEN` = D10
* **Nút bấm Ưu tiên Người đi bộ (Failsafe):**
  * `BTN_PEDESTRIAN` = D2 (Kích hoạt ngắt ngoài `FALLING`, có điện trở kéo lên `INPUT_PULLUP`)
* **Còi báo hiệu âm thanh (Buzzer):**
  * `BUZZER` = D11 (Cảnh báo nhịp ngắt quãng khi người đi bộ qua đường)

### 2. Giao thức Truyền thông Serial (9600 BAUD):
* Nhận `'1'`: **ƯU TIÊN XE CỨU THƯƠNG** — Đèn tuyến chính chuyển Xanh ngay lập tức, tuyến phụ Đỏ, còi báo động kích hoạt.
* Nhận `'2'`: **ƯU TIÊN XE BUÝT TRƯỜNG HỌC** — Kéo dài chu kỳ xanh tuyến chính thêm 5 giây.
* Nhận `'0'`: **GIAO THÔNG BÌNH THƯỜNG** — Duy trì chu kỳ tự hành tuần hoàn 4 pha.

---

## 🚀 Hướng Dẫn Vận Hành Nhanh

1. **Nạp Firmware vào Arduino Nano:**
   - Mở `traffic_light_hybrid_firmware.ino` trên Arduino IDE (hoặc PictoBlox ở chế độ Upload).
   - Chọn Board: `Arduino Nano`, Processor: `ATmega328P` (hoặc `Old Bootloader`), Port: Cổng COM tương ứng của chip nạp CH340.
   - Nhấn **Upload**.
2. **Khởi chạy PictoBlox:**
   - Mở PictoBlox v9.2.1, chọn `File` -> `Load from your computer` -> Mở tệp `du_an_sa_ban_pictoblox.sb3`.
   - Kết nối cổng COM vi điều khiển (`Connect` -> `Serial Port` -> chọn COM).
   - Huấn luyện hoặc dán URL Teachable Machine Model nhận diện xe.
   - Nhấn **Cờ xanh** để bắt đầu vận hành hệ thống.

---

## 🏆 Đơn Vị Phát Triển & Bản Quyền

* **Đơn vị:** Marie Curie Academy (MCA)
* **Đội tuyển tham dự:** Olympic STEM HNUE 2026 — Trường Đại học Sư phạm Hà Nội
* **Tác giả:** Thầy cô & Học sinh Đội tuyển STEM MCA
* **Hỗ trợ kỹ thuật & Kiểm toán:** Antigravity Engine (AE) Standard Architecture
