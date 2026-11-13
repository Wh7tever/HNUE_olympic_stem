# 🚦 Hệ Thống Sa Bàn Giao Thông Thông Minh — Marie Curie Academy (MCA)
> **Dự án tham dự Cuộc thi Olympic STEM 2026 — Trường Đại học Sư phạm Hà Nội (HNUE)**  
> **Bảng thi:** Tiểu học | **Mô hình:** Kiến trúc lai Hybrid (PictoBlox AI + Vi điều khiển C++ Arduino Nano)  
> **Phiên bản:** `v2.6 Final Release` (Turnkey Hardware BOM & Electrical Audit Verified)

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

## 📂 Cấu Trúc Thư Mục Dữ Liệu & Hồ Sơ (`1.Data`)

Toàn bộ gói sản phẩm hoàn thiện được phân khu chuyên nghiệp tại thư mục `1.Data/` và `src/`:

### 1. `1.Data/1. Huong dan cua Ban to chuc/`
* `1272_DHPSHN_NVSP.pdf`: Công văn hướng dẫn chính thức từ Trường ĐH Sư phạm Hà Nội.
* `thông tin.docx`: Thông tin chi tiết về thể lệ, biểu mẫu và quy chế thi Olympic STEM 2026.

### 2. `1.Data/2. Ho so/` (Bộ 5 Văn Kiện Thuyết Minh Đạt Chuẩn Thẩm Định Quốc Gia)
* `HO_SO_TOAN_DIEN_DU_AN_STEM_OLYMPIC_2026.docx` (2.18 MB): Bản thuyết minh hoàn chỉnh 15 trang, chuẩn thể thức văn bản, phụ lục ảnh thực tế sa bàn và ma trận rủi ro.
* `HUONG_DAN_LAP_TRINH_PICTOBLOX_VA_CPP_v2.docx` (526 KB): Cẩm nang kỹ thuật chuyển giao, bản đồ mã Serial, 9 câu hỏi đáp và kịch bản thuyết trình phân vai 5 phút.
* `SO_TAY_KY_THUAT_VA_NHAT_KY_THUC_HANH.docx` (51 KB): Sổ tay kỹ thuật (Engineering Notebook) ghi nhật ký 5 bước quy trình thiết kế kỹ thuật (Ask -> Imagine -> Plan -> Create -> Improve).
* `DANH_SACH_MUA_SAM_LINH_KIEN_THUC_TE.docx` (50 KB): Bảng kê chi phí 19 hạng mục (389.000 VNĐ sa bàn & gói backup 430.000 VNĐ).
* `MA_TRAN_BO_CUC_POSTER_80cmx180cm.docx` (43 KB): Bản thiết kế nội dung và ma trận phân khu poster triển lãm khổ đứng 80cm x 180cm.

### 3. `1.Data/3. Phan mem & Ma nguon Hybrid/` & `src/` (Mã Nguồn Sẵn Sàng Vận Hành)
* `traffic_light_hybrid_firmware.ino` / `src/traffic_light_arduino.ino`: Firmware C++ v2.3 Final cho Arduino Nano (Non-blocking FSM 6 trạng thái, Soft-ramp Servo 3°/20ms, chống giật nguồn khởi động `write(0)` trước `attach()`, ngắt ngoài D2 khử dội 300ms, Watchdog tự hành 1Hz theo QCVN 41:2019).
* `test_hardware_diagnostic.ino` / `src/test_hardware_diagnostic.ino`: Công cụ chẩn đoán phần cứng tự động qua Serial Console (Test LED, Còi Buzzer phím 3/'B', Servo Barie, Nút Failsafe).
* `du_an_sa_ban_pictoblox.sb3`: Dự án khối lệnh PictoBlox tích hợp Google Teachable Machine kèm bộ lọc chu kỳ debounce chống nhiễu khung hình.
* `src/ai_traffic_web_controller.html`: Bảng điều khiển Web giám sát thời gian thực kết nối Web Serial API.

### 4. `1.Data/4. Hinh anh & So do 3D/` & `assets/`
* `anh_3d_mo_hinh_stem_render_photoreal.png`: Ảnh render 3D phối cảnh sa bàn chân thực.
* `so_do_3d_ky_thuat.png` / `assets/so_do_3d_ky_thuat.svg`: Sơ đồ kỹ thuật lắp ráp và nối dây vi điều khiển.
* `so_do_3d_mo_hinh.html`: Mô hình 3D tương tác trực quan bằng Three.js.
* `so_do_khoi_lenh_pictoblox.png`: Sơ đồ thuật toán khối lệnh PictoBlox AI.
* `so_do_kien_truc_lai_hybrid.png`: Sơ đồ kiến trúc 2 tầng Hybrid Architecture.

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

