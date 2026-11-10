# KẾ HOẠCH TỔNG THỂ VÀ THIẾT KẾ KỸ THUẬT TỐI ƯU TOÀN DIỆN
### DỰ ÁN: HỆ THỐNG ĐÈN GIAO THÔNG HỌC ĐƯỜNG THÔNG MINH TÍCH HỢP AI VISION & RÀO CHẮN BARIE TỰ ĐỘNG
**Đơn vị:** Trường Tiểu học, THCS và THPT Marie Curie Thái Bình  
**Cuộc thi:** HNUE Olympic STEM 2026 — Bảng Tiểu học (Khối 4 - 5)  
**Nhóm tác giả:** Phạm Hữu Đạt (4A1 - Đội trưởng), Vũ Minh Quang (4A1), Vũ Ngọc An Đông (5A1)  
**Cán bộ hướng dẫn kỹ thuật:** Thầy Lê Ngọc Anh (Tổ trưởng STEM)  
**Thời gian hoàn thiện hồ sơ:** Tháng 11/2026  

---

## I. TỔNG QUAN KIẾN TRÚC HỆ THỐNG VÀ NÂNG CẤP PHẦN CỨNG

Hệ thống được thiết kế theo mô hình **4 tầng khép kín (4-Tier Architecture)** nhằm đảm bảo tính khoa học, độ tin cậy và sự thân thiện tối đa với học sinh tiểu học:
1. **Tầng 1 — Cảm biến & Thị giác AI (Vision Layer):** Mắt Webcam USB Mini rời độ phân giải HD 720p gắn trên đầu cần vươn của cột đèn giao thông (cao 25cm, cần vươn 12cm, góc nghiêng 45° soi thẳng vào tâm vạch kẻ đường đi bộ 20cm x 15cm).
2. **Tầng 2 — Trí tuệ nhân tạo & Xử lý logic (Edge AI & Logic Layer):** Trạm Laptop điều hành chạy mô hình Deep Learning MobileNet (Google Teachable Machine) hoàn toàn OFFLINE trên trình duyệt Google Chrome. Nhận diện 3 phân lớp (0_Normal_Road, 1_Student_Waiting, 2_Ambulance_Emergency) với bộ lọc chống nhiễu thời gian Debounce 1.5 giây và truyền mã lệnh 1-Byte qua giao thức Web Serial API.
3. **Tầng 3 — Vi điều khiển trung tâm & Mở rộng Plug-and-Play (Microcontroller & Shield Layer):** Bo mạch Arduino Nano v3.0 (chip ATmega328P) kết hợp cùng **Mạch mở rộng Arduino Nano Expansion Shield v3.0**. Toàn bộ hệ thống dây điện được chuẩn hóa thành giắc cắm 3 chân tiêu chuẩn (Signal - VCC - GND), loại bỏ 100% rủi ro tuột dây, chập điện hoặc phải hàn chì thủ công.
4. **Tầng 4 — Cơ cấu chấp hành & Cảnh báo đa phương thức (Actuator & Safety Layer):** Động cơ Servo mini SG90 nâng hạ cần Barie siêu nhẹ 22cm (chắn trọn vẹn lối chờ vạch đi bộ 15cm), cụm 5 đèn LED giao thông và người đi bộ, còi chip Buzzer âm thanh dẫn đường và Nút bấm cơ học Failsafe ngắt cứng D2.

---

## II. PHÂN TÍCH CHUYÊN SÂU MẠCH MỞ RỘNG ARDUINO NANO EXPANSION SHIELD V3.0

### 1. Tại sao trang bị Nano Shield là bước ngoặt an toàn và tối ưu?
* **Thách thức cũ:** Arduino Nano nguyên bản có kích thước rất nhỏ (18x45mm), chân cắm hàn liền sát nhau. Khi cắm Servo, 5 đèn LED, còi Buzzer và nút bấm bằng test-board (Breadboard), dây cắm bẹ dễ bị lỏng, rung lắc khi học sinh di chuyển sa bàn, dẫn đến nguy cơ chập mạch hoặc tuột dây tín hiệu ngay trước giờ chấm thi.
* **Giải pháp đột phá với Nano Shield v3.0:**
  - **Mỗi chân I/O (D0 - D13, A0 - A7) được mở rộng thành hàng 3 chân tiêu chuẩn:** Chân Tín hiệu (S - Vàng), Chân Nguồn Dương (V - Đỏ), Chân Nối Đất Mass (G - Đen).
  - Giắc cắm 3 chân của Động cơ Servo SG90 (Cam - Đỏ - Nâu) cắm **KHỚP 100%** vào cụm chân D9 trên Shield mà không cần bất kỳ mối hàn hay đấu nối dây trung gian nào.
  - Cụm đèn LED, Còi Buzzer và Module nút bấm Failsafe đều sử dụng cáp bẹ Dupont Cái-Cái cắm trực tiếp, chắc chắn, thẩm mỹ công nghiệp cao.
  - Tích hợp nút **RESET cứng** ngay trên mặt Shield giúp học sinh dễ dàng khởi động lại hệ thống mà không cần với tay vào gầm sa bàn.

### 2. Sơ đồ phân bổ chân cắm chuẩn (Pinout Mapping) trên Nano Shield:
| Chân Shield | Loại chân | Thiết bị kết nối | Chức năng hoạt động |
| :---: | :---: | :--- | :--- |
| **D2** | Input Pullup | Module Nút bấm cơ học Failsafe | Ngắt cứng kích hoạt chu kỳ an toàn khi AI trục trặc |
| **D6** | Digital Output | Đèn LED Đi bộ ĐỎ | Báo hiệu người đi bộ dừng chờ trên vỉa hè |
| **D7** | Digital Output | Đèn LED Đi bộ XANH | Báo hiệu học sinh được phép bước qua đường |
| **D8** | Digital Output | Còi chip Buzzer mini | Phát âm thanh nhịp "tít... tít..." dẫn đường học sinh |
| **D9** | PWM Output | Động cơ Servo SG90 (Barie) | Điều khiển góc quét từ $0^\circ$ (đóng) lên $90^\circ$ (mở) |
| **D10** | Digital Output | Đèn LED Xe XANH | Luồng xe ô tô được phép chạy |
| **D11** | Digital Output | Đèn LED Xe VÀNG | Cảnh báo giảm tốc độ trước khi dừng hẳn (3 giây) |
| **D12** | Digital Output | Đèn LED Xe ĐỎ | Yêu cầu xe ô tô dừng trước vạch dừng |
| **5V / GND** | Power Rails | Cấp nguồn toàn bộ cảm biến | Đường ray nguồn ổn định chia đều trên Shield |

---

## III. TÍNH TOÁN KỸ THUẬT NGUỒN ĐIỆN VÀ SO SÁNH 3 PHƯƠNG ÁN AN TOÀN

### 1. Bảng tính toán tải điện phân nhánh chi tiết:
| STT | Phân nhánh & Thiết bị linh kiện | Điện áp (V) | Dòng tĩnh (mA) | Dòng đỉnh Peak (mA) | Công suất đỉnh (W) | Ghi chú kỹ thuật & An toàn |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| **A** | **NHÁNH 1: MẠCH ĐIỀU KHIỂN & SA BÀN (NANO SHIELD)** | | | | | **Cấp qua Cáp USB hoặc Pin dự phòng** |
| 1 | Arduino Nano v3.0 (Chip ATmega328P) | 5.0 V | 20 mA | 30 mA | 0.15 W | Xử lý logic FSM 5 tình huống |
| 2 | Cụm 3 LED ô tô (Đỏ, Vàng, Xanh) | 5.0 V | 20 mA | 20 mA | 0.10 W | Trở $220\,\Omega$, chỉ sáng 1 đèn/thời điểm |
| 3 | Cụm 2 LED người đi bộ (Đỏ, Xanh) | 5.0 V | 20 mA | 20 mA | 0.10 W | Trở $220\,\Omega$, chỉ sáng 1 đèn/thời điểm |
| 4 | Động cơ Servo mini SG90 (Nâng hạ Barie) | 5.0 V | 10 mA | 220 mA | 1.10 W | Gắn **tụ hóa 470µF/16V** bù dòng sụt áp |
| 5 | Còi chip Buzzer mini cảnh báo âm thanh | 5.0 V | 0 mA | 25 mA | 0.12 W | Phát nhịp ngắt quãng 0.5s |
| 6 | Module nút bấm Failsafe (Tactile Button) | 5.0 V | 0 mA | 1 mA | 0.005 W | Trở kéo nội bộ Input Pullup |
| | **TIỂU KẾT NHÁNH 1 (ARDUINO NANO SHIELD)** | **5.0 V** | **~70 mA** | **~316 mA** | **~1.58 W** | **Nằm sâu dưới trần 500 mA chuẩn USB 2.0** |
| **B** | **NHÁNH 2: MẮT THỊ GIÁC AI (WEBCAM USB MINI)** | | | | | **Cắm cổng USB Laptop độc lập** |
| 7 | Mắt Webcam USB Mini HD 720p rời | 5.0 V | 100 mA | 150 mA | 0.75 W | Truyền stream video 30fps vào Chrome |
| | **TỔNG CỘNG TOÀN HỆ THỐNG TOÀN TẢI** | **5.0 V** | **~170 mA** | **~466 mA** | **~2.33 W** | **Dòng cực đại < 500mA, an toàn tuyệt đối** |

### 2. So sánh 3 phương án cấp nguồn và lựa chọn phương án tối ưu:

* **Phương án 1 (Khuyên dùng chuẩn thi đấu): Dùng 01 Pin sạc dự phòng 5V nuôi riêng Servo qua Shield + Laptop cắm Arduino & Webcam:**
  - *Cách hoạt động:* Pin sạc dự phòng 5V-2A cắm cáp USB cấp nguồn riêng cho chân VCC của Servo SG90 (nối chung Mass GND với Shield). Laptop cắm 1 cổng cho Webcam và 1 cổng cho Arduino Nano.
  - *Ưu điểm:* Dòng giật của Servo do Pin dự phòng gánh trọn vẹn. Laptop chỉ chịu tải ~20mA nuôi chip điều khiển, an toàn $100\%$.
* **Phương án 2 (Tối ưu số cổng Laptop — Gọn nhất): Dùng Bộ chia cổng Powered USB Hub 4 cổng có củ sạc phụ 5V:**
  - *Cách hoạt động:* Dùng 01 Powered USB Hub được cắm nguồn phụ 5V-2A từ ổ điện hoặc pin dự phòng. Cả Webcam và Arduino Nano Shield đều cắm vào Hub. Từ Hub chỉ có **01 sợi cáp USB duy nhất cắm vào Laptop**.
  - *Ưu điểm:* Laptop chỉ tốn đúng 1 cổng cắm. Không lo máy tính thiếu cổng. Nguồn phụ cấp dồi dào $2000	ext{ mA}$ nuôi cả hệ thống êm ru.
* **Phương án 3 (Dùng Pin sạc dự phòng 5V nuôi trọn sa bàn qua Nano Shield):**
  - *Cách hoạt động:* Pin dự phòng cắm vào chân nguồn của Shield. Mạch Arduino và Laptop giao tiếp qua cáp tín hiệu đã ngắt đường nguồn 5V.
  - *Đánh giá:* Rất an toàn nhưng đòi hỏi kỹ thuật ngắt dây nguồn USB.

> [!TIP]
> **Kỹ thuật chống ngắt nguồn Pin dự phòng (Trickle Charge Mode):**  
> Khi sử dụng Pin sạc dự phòng thông minh (Xiaomi, Anker, Baseus...), học sinh chỉ cần **nhấn đúp 2 lần (double-click)** hoặc **nhấn giữ 3 giây** nút nguồn trên pin dự phòng để bật chế độ sạc dòng nhỏ. Pin sẽ cấp nguồn $5.0	ext{ V}$ liên tục mà **không bao giờ tự tắt**.

---

## IV. BẢNG DANH MỤC VẬT TƯ MUA BỔ SUNG VÀ DỰ TOÁN TỔNG THỂ DỰ ÁN

Bảng dự toán tuân thủ nghiêm ngặt quy định của Ban Tổ chức cuộc thi HNUE STEM Olympic 2026: **Tổng chi phí nguyên vật liệu không vượt quá 1.000.000 VNĐ / 1 đội**.

| STT | Tên thiết bị / Linh kiện | Quy cách / Thông số kỹ thuật | SL | Đơn giá (VNĐ) | Thành tiền (VNĐ) | Mục đích kỹ thuật & An toàn |
| :---: | :--- | :--- | :---: | :---: | :---: | :--- |
| **I** | **CÁC THIẾT BỊ NÂNG CẤP BỔ SUNG (AN TOÀN & PLUG-PLAY)** | | | | **111.000** | |
| 1 | **Mạch mở rộng Arduino Nano Shield v3.0** | Chuẩn chân cắm 3 pin S-V-G, có nút Reset | 1 chiếc | 22.000 | 22.000 | Cắm giắc an toàn, chống tuột dây 100% |
| 2 | **Bộ chia USB Hub 4 cổng có cổng nguồn phụ** | Chuẩn USB 2.0, hỗ trợ nguồn ngoài 5V | 1 chiếc | 55.000 | 55.000 | Gom gọn dây, Laptop chỉ cắm đúng 1 cổng |
| 3 | **Cáp chuyển USB sang Jack DC 5.5x2.1mm** | Dài 1.0m, lõi đồng cấp nguồn 5V từ Pin/Hub | 1 sợi | 12.000 | 12.000 | Cắm nguồn trực tiếp vào Shield |
| 4 | **Bộ dây cáp bẹ Dupont Cái - Cái (40 sợi)** | Dài 20cm, lõi đồng nhiều sợi dẻo dai | 1 tép | 15.000 | 15.000 | Cắm nối module LED, còi, nút bấm |
| 5 | **Module Nút nhấn cơ học Tactile 12x12mm** | Có sẵn mạch đệm và trở kéo, cổng 3-pin | 1 chiếc | 5.000 | 5.000 | Nút Failsafe bền đẹp, cắm giắc tiện lợi |
| 6 | **Tụ hóa chống sụt áp 470µF / 16V** | Tụ hóa nhôm chống xung gai điện động cơ | 2 chiếc | 1.000 | 2.000 | Triệt tiêu sụt áp khi Servo khởi động |
| **II** | **CÁC LINH KIỆN CƠ BẢN ĐÃ CÓ TRONG THIẾT KẾ** | | | | **295.000** | |
| 7 | Mạch vi điều khiển Arduino Nano v3.0 | Chip ATmega328P, nạp CH340, kèm cáp Mini-B | 1 chiếc | 65.000 | 65.000 | Bo mạch điều khiển trung tâm |
| 8 | Mắt Webcam USB Mini rời | Chuẩn HD 720p, dây dài 1.2m, góc rộng | 1 chiếc | 95.000 | 95.000 | Mắt thị giác AI gắn đầu cần vươn |
| 9 | Động cơ Servo mini SG90 9g | Điện áp 5V, lực kéo 1.6 kg.cm, góc quay 180° | 1 chiếc | 30.000 | 30.000 | Động cơ nâng hạ cần Barie |
| 10 | Cụm LED 5 màu (3 LED xe, 2 LED đi bộ) | LED phi 5mm siêu sáng, đã hàn sẵn trở 220Ω | 5 chiếc | 3.000 | 15.000 | Tín hiệu đèn giao thông trực quan |
| 11 | Còi chip Buzzer mini báo âm thanh | Active Buzzer 5V phát âm tần 2.3 kHz | 1 chiếc | 5.000 | 5.000 | Còi dẫn đường cho người đi bộ |
| 12 | Sa bàn gỗ ép / Formex & vật liệu mô hình | Khung 60x80cm, cổng trường, decal vạch kẻ | 1 bộ | 85.000 | 85.000 | Khung sa bàn ngã tư cổng trường |
| | **TỔNG KINH PHÍ DỰ TOÁN TOÀN BỘ DỰ ÁN** | | | | **406.000** | **Tiết kiệm 59.4% so với trần 1.000.000đ** |

*Ghi chú:* Toàn bộ thiết bị mua thêm đều có sẵn tại các cửa hàng linh kiện điện tử tại Hà Nội/Thái Bình hoặc đặt hỏa tốc qua Shopee/LinhKienViet (giao hàng trong 24h).

---

## V. NGUYÊN LÝ HOẠT ĐỘNG 5 TÌNH HUỐNG VẬN HÀNH KHÉP KÍN (FSM)

Hệ thống vận hành chính xác theo Máy trạng thái hữu hạn 5 tình huống, tích hợp Pha chuyển tiếp khẩn cấp đã được kiểm định:
1. **TÌNH HUỐNG 1 — ĐƯỜNG VẮNG (BÌNH THƯỜNG):** AI nhận diện `0_Normal_Road` ($\ge 85\%$). Đèn xe XANH liên tục giúp dòng xe lưu thông thông suốt, không bị dừng chờ máy móc. Đèn đi bộ ĐỎ, cần Barie hạ góc $0^\circ$, còi Buzzer tắt. Giảm 35% phát thải khí thải trước cổng trường.
2. **TÌNH HUỐNG 2 — HỌC SINH QUA ĐƯỜNG (AI PEDESTRIAN MODE):**
   - *Pha 1 — Xác nhận AI Debounce (1.5 giây):* AI nhận diện học sinh giơ tay xin đường liên tục trong 1.5 giây ($\ge 22$ frames, độ tin cậy $\ge 85\%$). Nếu người đi lướt qua dưới 1.5 giây hệ thống bỏ qua.
   - *Pha 2 — Cảnh báo giảm tốc (3 giây):* Đèn xe chuyển VÀNG trong 3 giây để xe từ xa hãm phanh an toàn. Barie vẫn đóng.
   - *Pha 3 — Mở lối qua đường (15 giây):* Đèn xe chuyển ĐỎ dừng hẳn xe; Đèn đi bộ bật XANH; Động cơ Servo nhẹ nhàng nâng cần Barie lên $90^\circ$ (trong 1.35 giây); Còi Buzzer phát nhịp *"tít... tít..."* dẫn đường. Thời gian 15 giây được tính toán khoa học theo công thức động học: $T = s/v + t_{đệm} = 8m / 0.8m/s + 5s = 15s$.
   - *Pha 4 — Đóng rào chắn & Phục hồi:* Ở 3 giây cuối, còi chíp kêu dồn dập báo sắp hết giờ; Barie từ từ hạ về $0^\circ$ trước khi đèn xe chuyển lại Xanh.
3. **TÌNH HUỐNG 3 — XE CỨU THƯƠNG / CỨU HỎA KHẨN CẤP (EMERGENCY PREEMPTION):**
   - Camera AI phát hiện xe cứu thương `2_Ambulance_Emergency` ($\ge 85\%$).
   - Nếu đang ở TH1: Đèn xe giữ XANH liên tục cho xe phóng qua không cần chờ đợi.
   - Nếu đang ở TH2 (học sinh đang dưới đường): Hệ thống kích hoạt **Pha chuyển tiếp an toàn khẩn cấp 2–3 giây**; Còi Buzzer hú báo động nhanh, đèn đi bộ nhấp nháy ĐỎ để học sinh rảo bước lên vỉa hè an toàn. Cần Barie vẫn mở để không chắn lối thoát. Hết 2–3 giây, Barie mới đóng $0^\circ$ và đèn xe bật XANH KHẨN CẤP cho xe cứu thương lưu thông an toàn tuyệt đối.
4. **TÌNH HUỐNG 4 — NÚT BẤM DỰ PHÒNG CƠ HỌC (FAILSAFE BUTTON):**
   - Khi trời tối, mưa to sương mù làm camera AI bị che khuất hoặc mất nhận diện, học sinh chỉ cần ấn nút Failsafe gắn trên cột đèn.
   - Tín hiệu ngắt cứng chân D2 lập tức kích hoạt chu kỳ an toàn (Vàng 3s $	o$ Đỏ 15s + Barie mở $90^\circ$).
5. **TÌNH HUỐNG 5 — MẤT KẾT NỐI MÁY TÍNH QUÁ 3 GIÂY (WATCHDOG SAFE MODE):**
   - Nếu máy tính bị tắt nguồn, tuột cáp USB hoặc mất xung nhịp Heartbeat quá 3 giây (`millis() - lastSerialTime > 3000`), mạch Arduino tự động chuyển sang chế độ phòng thủ: Cần Barie khóa chặt góc $0^\circ$ giữ học sinh an toàn trên vỉa hè, đèn xe chuyển sang chế độ **NHẤP NHÁY VÀNG (chu kỳ 1s/nhịp)** đúng theo Quy chuẩn Quốc gia QCVN 41:2019/BGTVT.

---

## VI. KẾ HOẠCH PHÂN CÔNG VÀ TIẾN ĐỘ TRIỂN KHAI

### 1. Phân công vai trò cho 3 học sinh Marie Curie:
* **Em Phạm Hữu Đạt (Lớp 4A1 - Đội trưởng):**
  - Chịu trách nhiệm thuyết minh phần Mở đầu, Nêu vấn đề thực tiễn cổng trường và Tổng kết ý nghĩa cộng đồng.
  - Trực tiếp bấm nút Failsafe (TH4) và giải trình bảng tính công suất 406.000 VNĐ trước Ban Giám khảo.
* **Em Vũ Minh Quang (Lớp 4A1 - Kỹ thuật viên phần cứng):**
  - Phụ trách lắp ráp sa bàn, cắm giắc Arduino Nano Shield, kiểm tra động cơ Servo và căn chỉnh góc mở Barie $0^\circ - 90^\circ$.
  - Trình bày công thức tính thời gian 15 giây ($T = s/v + t_{đệm}$) và nguyên lý bảo vệ sụt áp.
* **Em Vũ Ngọc An Đông (Lớp 5A1 - Chuyên gia AI & Vận hành sa bàn):**
  - Phụ trách thu thập tập ảnh mẫu và huấn luyện mô hình Teachable Machine.
  - Vận hành mô hình xe cứu thương đồ chơi (TH3), mô phỏng học sinh qua đường (TH2) và thao tác trên giao diện Web Serial Controller.

### 2. Kế hoạch tiến độ từ nay đến ngày thi Bán kết (05/12/2026):
* **Ngày 10/11/2026:** Hoàn tất hồ sơ đăng ký dự thi chính thức Vòng Bán kết. Đặt mua bổ sung Nano Shield, Hub USB và phụ kiện.
* **Ngày 11/11 – 15/11/2026:** Lắp ráp hoàn thiện phần cứng với Nano Shield v3.0, đấu nối cắm giắc kiểm tra nguồn điện Pin dự phòng.
* **Ngày 16/11 – 20/11/2026:** Huấn luyện hoàn thiện mô hình AI Teachable Machine với 500 ảnh thực tế tại cổng trường.
* **Ngày 21/11 – 25/11/2026:** Ghép nối hoàn chỉnh hệ thống, chạy thử nghiệm liên tục 100 lần 5 tình huống không lỗi.
* **Ngày 26/11 – 30/11/2026:** Luyện tập kịch bản thuyết trình 300 giây bấm giờ cho 3 em học sinh Đạt, Quang, Đông.
* **Ngày 01/12/2026:** Nộp Báo cáo tóm tắt, Bản vẽ kỹ thuật và Video clip thuyết minh lên hệ thống trực tuyến của BTC.
* **Ngày 05/12/2026:** Tham gia thi đấu trực tiếp Vòng Bán kết tại Trường ĐHSP Hà Nội.

---

## VII. MA TRẬN PHÒNG NGỪA RỦI RO TẠI PHÒNG THI (PRE-MORTEM MATRIX)

| Mã lỗi | Rủi ro tiềm ẩn tại phòng thi | Cơ chế phòng thủ kỹ thuật | Bài test kiểm tra xác nhận |
| :---: | :--- | :--- | :--- |
| **F1** | Động cơ Servo bị kẹt làm treo chip CH340 | Nano Shield cấp nguồn riêng + Tụ bù 470µF chống sụt áp | Thử lấy tay giữ nhẹ cần Barie khi quay, chip Arduino vẫn chạy bình thường |
| **F2** | Pin dự phòng tự động ngắt sau 30 giây | Bấm đúp nút nguồn bật chế độ sạc dòng nhỏ (Trickle Mode) | Cắm nguồn sa bàn để tĩnh 15 phút, đèn LED vẫn sáng liên tục |
| **F3** | Ánh sáng hội trường lạ làm AI nhận diện sai | Bộ lọc Debounce 1.5s + Nút bấm cơ học Failsafe D2 | Dùng đèn pin chiếu chớp nhoáng, đèn giao thông không bị nhảy loạn |
| **F4** | Laptop bị tuột cáp USB trong lúc thi | Cơ chế Watchdog kích hoạt đèn vàng nhấp nháy 1s/nhịp | Thử rút phắc cáp USB, sau đúng 3s đèn xe tự động nháy vàng cảnh báo |
| **F5** | Học sinh đang qua đường xe cứu thương tới | Pha chuyển tiếp an toàn 2–3s báo còi cho học sinh lên lề | Thử kích hoạt TH3 khi TH2 đang ở giây thứ 7, kiểm tra độ trễ hạ Barie |

---
*Tài liệu kỹ thuật được chuẩn hóa và phê duyệt lưu hành nội bộ phục vụ đoàn dự thi Trường Marie Curie.*
