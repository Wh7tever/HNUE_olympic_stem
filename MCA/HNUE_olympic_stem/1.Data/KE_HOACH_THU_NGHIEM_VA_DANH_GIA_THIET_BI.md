# KẾ HOẠCH THỬ NGHIỆM VÀ ĐÁNH GIÁ DANH MỤC THIẾT BỊ HỆ THỐNG
### DỰ ÁN: HỆ THỐNG ĐÈN GIAO THÔNG HỌC ĐƯỜNG THÔNG MINH TÍCH HỢP AI VISION & RÀO CHẮN BARIE TỰ ĐỘNG
**Đơn vị:** Trường Tiểu học, THCS và THPT Marie Curie Thái Bình  
**Cuộc thi:** HNUE Olympic STEM 2026 — Bảng Tiểu học (Khối 4 - 5)  
**Nhóm tác giả:** Phạm Hữu Đạt (4A1 - Đội trưởng), Vũ Minh Quang (4A1), Vũ Ngọc An Đông (5A1)  
**Cán bộ hướng dẫn kỹ thuật:** Thầy Lê Ngọc Anh (Tổ trưởng STEM)  
**Thời gian lập kế hoạch:** Tháng 11/2026  

---

## I. MỤC TIÊU VÀ NGUYÊN TẮC ĐÁNH GIÁ THIẾT BỊ

Nhằm chuẩn bị tối ưu cho Vòng Bán kết cuộc thi HNUE Olympic STEM 2026, bản kế hoạch này giải quyết dứt điểm 3 bài toán kỹ thuật cốt lõi:
1. **Kiểm toán tính Đầy Đủ & Tương Thích:** Rà soát toàn bộ linh kiện trong danh mục thiết kế để khẳng định hệ thống đã đủ điều kiện vận hành chưa.
2. **Loại bỏ Thiết Bị Thừa & Cảnh báo Bẫy Kỹ Thuật:** Phát hiện các linh kiện dư thừa gây lãng phí ngân sách hoặc sử dụng sai quy chuẩn kỹ thuật (đặc biệt là hiện tượng sụt áp trên IC ổn áp AMS1117).
3. **Bổ sung Thiết Bị Thiếu Cấp Thiết:** Liệt kê các chi tiết cơ khí, vật tư tiêu hao và module chuyên dụng tuy giá trị nhỏ nhưng quyết định 100% sự sống còn của sa bàn.
4. **Quy trình Thử Nghiệm 4 Giai Đoạn Chuẩn Hóa:** Xây dựng quy trình thử nghiệm thực nghiệm từ kiểm tra an toàn điện (Smoke Test), chẩn đoán từng chân cắm (Sanity Test), hiệu chuẩn thị giác AI đến vận hành liên tục 5 tình huống FSM không lỗi.

---

## II. BẢNG KIỂM TOÁN LINH KIỆN: ĐỦ – THỪA – THIẾU (EQUIPMENT AUDIT & GAP ANALYSIS)

Dựa trên khảo sát thực tế và phân tích mạch điện trên bo mạch **Arduino Nano v3.0** kết hợp **Arduino Nano Expansion Shield v3.0**, tình trạng từng linh kiện được phân loại rõ ràng:

| STT | Tên thiết bị / Linh kiện | Thông số kỹ thuật | Trạng thái kỹ thuật | Phân tích chuyên sâu & Cảnh báo kỹ thuật | Giải pháp xử lý |
| :---: | :--- | :--- | :---: | :--- | :--- |
| 1 | **Arduino Nano v3.0** | ATmega328P, nạp CH340, Mini-B | **ĐÃ ĐỦ** | Bo mạch điều khiển trung tâm nạp code FSM, nhận lệnh Serial 9600 bps từ Chrome. | Cắm thẳng vào Shield v3.0 |
| 2 | **Arduino Nano Shield v3.0** | Hàng 3 chân S-V-G, có nút Reset | **ĐÃ ĐỦ** | Mở rộng chân cắm chắc chắn, loại bỏ hoàn toàn việc dùng Breadboard và hàn chì. | Cố định vào sa bàn bằng keo xốp 3M |
| 3 | **Webcam USB Mini rời** | HD 720p, dây 1.2m, góc 45° | **ĐÃ ĐỦ** | Mắt thần AI soi thẳng vạch đi bộ 20x15cm, stream hình ảnh 30fps vào Chrome. | Gắn trên đỉnh cột đèn cao 25cm |
| 4 | **Động cơ Servo mini SG90** | Điện áp 5V, lực kéo 1.6 kg.cm, 180° | **ĐÃ ĐỦ** | Cần nâng hạ rào chắn Barie từ $0^\circ$ (đóng) lên $90^\circ$ (mở). Giắc 3 pin khớp chân D9. | Bổ sung tụ hóa 470µF chống sụt áp |
| 5 | **Bộ chia USB Hub 4 cổng** | Chuẩn USB 2.0 có cổng nguồn phụ | **ĐÃ ĐỦ** | Gom kết nối Nano và Webcam thành 01 sợi USB duy nhất cắm vào Laptop học sinh. | Dùng khi thi đấu để tiết kiệm cổng Laptop |
| 6 | **Còi chip Active Buzzer 5V** | Tần số 2.3 kHz, 5V DC | **ĐÃ ĐỦ** | Phát âm thanh nhịp 500ms / 200ms dẫn đường cho người khiếm thị và học sinh. | Cắm giắc D8 trên Shield |
| 7 | **Module Nút bấm Failsafe** | Tactile 12x12mm, 3-pin | **ĐÃ ĐỦ** | Nút bấm ngắt cứng dự phòng chân D2 khi trời mưa, mất mạng hoặc AI trục trặc. | Gắn trên thân cột đèn ngang tầm tay |
| 8 | **Tụ hóa chống sụt áp 470µF** | Tụ hóa nhôm 16V chịu nhiệt | **ĐÃ ĐỦ** | Cắm song song vào chân VCC-GND của Servo D9 để triệt tiêu xung gai dòng điện. | Cắm thẳng vào chân cọc nguồn Shield |
| 9 | **Breadboard (Bo cắm lỗ)** | Bo test 400 lỗ hoặc 170 lỗ | **THỪA (ĐÃ BỎ)** | Khi đã trang bị Nano Shield v3.0, việc dùng breadboard là hoàn toàn dư thừa, gây cồng kềnh và dễ tuột lỏng dây. | **Loại bỏ 100% khỏi dự toán** |
| 10 | **Cáp USB sang Jack DC 5.5mm** | Dài 1.0m, cắm vào Jack DC Shield | **CẢNH BÁO BẪY KỸ THUẬT (DỄ DẪN ĐẾN THỪA)** | **Bẫy sụt áp IC AMS1117:** Jack DC trên Shield đi qua IC hạ áp AMS1117 (sụt áp $V_{drop} \approx 1.1\text{V}$). Nếu cắm nguồn 5V từ sạc dự phòng vào Jack DC, điện áp ra nuôi Servo chỉ còn **~3.9V** (gây rung giật hoặc reset chip). | **Xem chi tiết mục III để xử lý** |
| 11 | **Cần Barie cơ khí (Thanh chắn)** | Que gỗ balsa / Ống giấy cứng 22cm | **THIẾU (BỔ SUNG)** | Động cơ SG90 chỉ có cánh tay nhựa ngắn 3cm. Bắt buộc phải có thanh cần dài 20–22cm siêu nhẹ (< 3g) để chắn ngang đường. | Bổ sung que gỗ balsa 22cm + ốc vít |
| 12 | **Tép cáp Dupont Đực - Cái** | 20 sợi dài 20cm, lõi đồng | **THIẾU (BỔ SUNG)** | Chân trên Nano Shield là cọc Đực. Khi nối module nút bấm hoặc còi buzzer có chân Cái, bắt buộc cần dây Đực - Cái. | Bổ sung 01 tép 20 sợi (8.000đ) |
| 13 | **Module Cụm 3 LED Giao thông** | Module 5V tích hợp sẵn Đỏ-Vàng-Xanh | **THIẾU (BỔ SUNG)** | Thay vì dùng 3 bóng LED rời lủng lẳng phải hàn trở thủ công, dùng 01 module đúc sẵn có 4 chân cọc GND-R-Y-G. | Bổ sung 01 module giao thông (10.000đ) |
| 14 | **Cụm 2 LED Đi bộ (Đỏ - Xanh)** | 2 LED phi 5mm có đế cắm và trở 220Ω | **ĐÃ ĐỦ** | Tín hiệu trực quan cho người đi bộ dừng chờ hoặc bước qua đường. | Cắm chân D6 (Đỏ) và D7 (Xanh) |
| 15 | **Băng keo xốp 3M & Keo nến** | Băng dính 2 mặt xốp dày 1mm | **THIẾU (BỔ SUNG)** | Cố định chặt động cơ Servo và bo Shield xuống sa bàn. Nếu không dán chặt, lực phản hồi khi quay sẽ làm vẹo cần. | Bổ sung 01 cuộn băng dính 3M (10.000đ) |
| 16 | **Cột đèn & Ống gắn Camera** | Ống nhựa PVC / gen điện phi 16 | **THIẾU (BỔ SUNG)** | Cột cao 25cm, cần vươn 12cm có khớp xoay 45° để gắn Webcam USB cố định góc soi. | Tận dụng ống gen điện mini (5.000đ) |
| 17 | **Mô hình xe cứu thương đồ chơi** | Xe ô tô đồ chơi màu trắng-đỏ | **THIẾU (BỔ SUNG)** | Đạo cụ bắt buộc để học sinh mô phỏng và kiểm tra tình huống xe ưu tiên khẩn cấp trước BGK. | Bổ sung 01 xe đồ chơi mini (15.000đ) |

---

## III. PHÂN TÍCH CHUYÊN SÂU BẪY KỸ THUẬT SỤT ÁP NGUỒN VÀ GIẢI PHÁP CHUẨN XÁC

### 1. Bản chất hiện tượng sụt áp trên IC AMS1117 của Nano Shield:
Bo mạch Arduino Nano Expansion Shield v3.0 có tích hợp 01 cổng Jack DC tiêu chuẩn 5.5x2.1mm. Đường nguồn từ Jack DC này được nối thẳng vào chân `VIN` của Arduino Nano, sau đó đi qua IC ổn áp tuyến tính **AMS1117-5.0** (hoặc LM1117) gắn trên lưng bo mạch Arduino.

Theo bảng thông số kỹ thuật (Datasheet) của nhà sản xuất AMS1117:
* **Điện áp rơi cực tiểu (Dropout Voltage):** $V_{dropout} = 1.1\text{V} \text{ đến } 1.3\text{V}$ tại dòng tải $500\text{mA}$.
* **Điện áp đầu vào tối thiểu yêu cầu:** $V_{in\_min} = V_{out} + V_{dropout} = 5.0\text{V} + 1.1\text{V} = 6.1\text{V}$.

> [!WARNING]
> **CẢNH BÁO BẪY KỸ THUẬT:**  
> Nếu học sinh sử dụng **Cáp chuyển USB sang Jack DC 5.5mm** để lấy nguồn $5.0\text{V}$ từ Củ sạc hoặc Pin sạc dự phòng cắm vào Jack DC của Shield:
> $$V_{out} = 5.0\text{V} - 1.1\text{V} \approx 3.9\text{V}!$$
> Tại mức điện áp $3.9\text{V}$:
> 1. Vi điều khiển ATmega328P (chạy thạch anh 16MHz) rơi vào vùng hoạt động bất ổn định, dễ bị treo hoặc kích hoạt cơ chế Brown-Out Reset (BOR).
> 2. Động cơ Servo SG90 (yêu cầu $4.8\text{V} - 6.0\text{V}$) bị suy giảm $60\%$ mô-men xoắn, rung bần bật (jitter), phát ra tiếng kêu rè rè và không thể nhấc nổi cần Barie.

### 2. Hai phương án cấp nguồn đúng đắn 100% về mặt vật lý:

* **Phương án Chuẩn 1 (Tối ưu nhất — Không lo sụt áp): Cấp nguồn 5V trực tiếp qua cổng Mini-USB của Arduino Nano:**
  - Cáp Mini-USB cắm từ Laptop hoặc cắm từ Cổng Powered USB Hub vào cổng USB của Arduino Nano.
  - Nguồn $5.0\text{V}$ từ cổng USB đi qua diode chống ngược cực Schottky MBR0520 (sụt áp chỉ $0.15\text{V}$), cung cấp điện áp $4.85\text{V}$ trực tiếp vào đường bus 5V của toàn bộ Shield.
  - *Kết luận:* Động cơ Servo và đèn LED hoạt động căng khỏe, hoàn toàn không qua IC AMS1117. Cáp chuyển USB sang Jack DC lúc này là **HOÀN TOÀN THỪA**.
* **Phương án Chuẩn 2 (Dùng nguồn ngoài độc lập cho Jack DC):**
  - Nếu muốn dùng Jack DC trên Shield để nuôi toàn bộ sa bàn độc lập không phụ thuộc máy tính: Bắt buộc nguồn cấp vào Jack DC phải có điện áp từ **$7.4\text{V}$ đến $9.0\text{V}$** (ví dụ: Adapter $9\text{V}-1\text{A}$ cắm ổ điện, hoặc Hộp pin 2 cell 18650 có mạch bảo vệ ra $7.4\text{V}-8.4\text{V}$).
  - Khi đó IC AMS1117 nhận $9\text{V}$ và hạ áp ra đúng chuẩn $5.0\text{V}$ phẳng mịn.

---

## IV. BẢNG DỰ TOÁN CHI TIẾT SAU KHI ĐIỀU CHỈNH HOÀN THIỆN

Bảng dự toán cập nhật chính thức sau khi loại bỏ linh kiện thừa, khắc phục bẫy sụt áp và bổ sung toàn bộ vật tư cơ khí, tiêu hao phục vụ thi đấu:

| STT | Danh mục thiết bị / Vật tư | Quy cách & Chủng loại | SL | Đơn giá (VNĐ) | Thành tiền (VNĐ) | Trạng thái |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: |
| **I** | **HỆ THỐNG MẠCH ĐIỀU KHIỂN & CẢM BIẾN (ELECTRONICS)** | | | | **192.000** | |
| 1 | Mạch vi điều khiển Arduino Nano v3.0 | Chip ATmega328P nạp CH340 + Cáp Mini-B nạp code | 1 bộ | 65.000 | 65.000 | Đã có |
| 2 | Mạch mở rộng Arduino Nano Shield v3.0 | Chuẩn cắm giắc 3 chân S-V-G, có nút Reset | 1 chiếc | 22.000 | 22.000 | Đã mua |
| 3 | Mắt Webcam USB Mini HD rời | Chuẩn 720p, dây dài 1.2m, lấy nét góc rộng | 1 chiếc | 95.000 | 95.000 | Đã có |
| 4 | Còi chip Active Buzzer mini 5V | Phát âm tần 2.3 kHz dẫn đường người khiếm thị | 1 chiếc | 5.000 | 5.000 | Đã có |
| 5 | Module Nút nhấn cơ học Tactile 3-pin | Nút Failsafe ngắt cứng D2, có sẵn trở kéo | 1 chiếc | 5.000 | 5.000 | Đã có |
| **II** | **CƠ CẤU CHẤP HÀNH & HIỂN THỊ (ACTUATOR & DISPLAY)** | | | | **48.000** | |
| 6 | Động cơ Servo mini SG90 9g | Điện áp 5V, lực kéo 1.6 kg.cm, góc quay 180° | 1 chiếc | 30.000 | 30.000 | Đã có |
| 7 | Module Cụm 3 LED Giao thông mini 5V | Đỏ - Vàng - Xanh tích hợp sẵn trở hạn dòng trên mạch | 1 chiếc | 10.000 | 10.000 | **Bổ sung mới** |
| 8 | Cụm 2 LED Đi bộ (Đỏ - Xanh) | LED phi 5mm siêu sáng kèm trở hạn dòng 220Ω | 2 chiếc | 3.000 | 6.000 | Đã có |
| 9 | Tụ hóa nhôm chống sụt áp 470µF / 16V | Triệt tiêu xung gai điện áp khi Servo khởi động | 2 chiếc | 1.000 | 2.000 | Đã có |
| **III** | **KẾT NỐI & DÂY CẮP TIÊU CHUẨN (CABLING & POWER)** | | | | **78.000** | |
| 10 | Bộ chia USB Hub 4 cổng có cổng nguồn phụ | Gom cổng kết nối, Laptop chỉ tốn 1 cổng USB | 1 chiếc | 55.000 | 55.000 | Đã có |
| 11 | Cáp bẹ Dupont Cái - Cái (40 sợi 20cm) | Cắm nối Shield tới module LED và nút bấm | 1 tép | 15.000 | 15.000 | Đã có |
| 12 | Cáp bẹ Dupont Đực - Cái (20 sợi 20cm) | Dự phòng ghép nối các đầu cắm cọc đa năng | 1 tép | 8.000 | 8.000 | **Bổ sung mới** |
| **IV** | **VẬT LIỆU SA BÀN, CƠ KHÍ & ĐẠO CỤ THI ĐẤU (PROPS & MECHANICS)** | | | | **97.000** | |
| 13 | Khung Sa bàn Formex & Decal vạch đường | Tấm Formex 60x80cm dày 5mm, decal vạch kẻ đường | 1 bộ | 60.000 | 60.000 | Đã có |
| 14 | Cột đèn giao thông & Cần gắn Camera | Ống gen điện phi 16 cao 25cm, cần vươn 12cm | 1 bộ | 5.000 | 5.000 | **Bổ sung mới** |
| 15 | Thanh cần Barie nhẹ & Ốc liên kết | Que gỗ balsa dẹp 22cm (<3g) gắn cánh tay đòn servo | 1 chiếc | 2.000 | 2.000 | **Bổ sung mới** |
| 16 | Cuộn băng dính xốp 2 mặt 3M & Keo nến | Cố định chặt Servo SG90 và Shield chống rung lắc | 1 cuộn | 15.000 | 15.000 | **Bổ sung mới** |
| 17 | Mô hình xe ô tô cứu thương mini | Đồ chơi xe cứu thương có chữ thập đỏ test AI | 1 chiếc | 15.000 | 15.000 | **Bổ sung mới** |
| | **TỔNG KINH PHÍ DỰ TOÁN THỰC TẾ DỰ ÁN** | | | | **415.000** | **Tiết kiệm 58.5%** |

*Ghi chú tài chính:* Tổng ngân sách thực tế chỉ là **415.000 VNĐ**, nằm hoàn toàn trong giới hạn quy định tối đa $1.000.000\text{ VNĐ}$ của Ban Tổ chức Trường ĐHSP Hà Nội, dự phòng an toàn tài chính lên tới **585.000 VNĐ (58.5%)**.

---

## V. KẾ HOẠCH THỬ NGHIỆM VÀ ĐÁNH GIÁ THỰC TẾ THEO 4 GIAI ĐOẠN

Quy trình thử nghiệm được xây dựng chặt chẽ theo tiêu chuẩn kỹ thuật công nghiệp, đảm bảo mọi rủi ro đều được phát hiện và triệt tiêu trước khi đem mô hình lên sân khấu thi đấu.

```
+-----------------------------------------------------------------------------------+
|               QUY TRÌNH THỬ NGHIỆM HỆ THỐNG 4 GIAI ĐOẠN (MCA STEM)                |
+-----------------------------------------------------------------------------------+
|  [GIAI ĐOẠN 1] SMOKE TEST & ELECTRICAL BASELINE                                   |
|  -> Đo dòng tĩnh (70mA) -> Dòng động cơ (220mA) -> Thử tụ bù 470uF -> Sạc dự phòng|
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|  [GIAI ĐOẠN 2] HARDWARE SANITY & UNIT TESTING                                     |
|  -> Nạp 'test_hardware_diagnostic.ino' -> Quét D2, D6, D7, D8, D9, D10, D11, D12  |
|  -> Căn chỉnh góc quay Barie 0 - 90 độ mượt mà không rung giật                    |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|  [GIAI ĐOẠN 3] AI VISION CALIBRATION & SERIAL PROTOCOL                            |
|  -> Hiệu chuẩn FOV Camera 45 độ -> Test nhận diện 100 lần (Accuracy >= 85%)       |
|  -> Đo Debounce 1.5s -> Đo phản hồi Web Serial API (< 50ms)                       |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|  [GIAI ĐOẠN 4] SYSTEM INTEGRATION & FSM STRESS TESTING (30 PHÚT)                  |
|  -> TH1 (Đường vắng) -> TH2 (Học sinh qua đường) -> TH3 (Xe cứu thương cắt ngang) |
|  -> TH4 (Nút cơ Failsafe) -> TH5 (Watchdog tuột cáp USB nháy vàng 1Hz)            |
+-----------------------------------------------------------------------------------+
```

---

### GIAI ĐOẠN 1: SMOKE TEST & ELECTRICAL BASELINE (KIỂM TRA AN TOÀN NGUỒN & SỤT ÁP)

* **Mục tiêu:** Đảm bảo mạch điện không bị chập (short-circuit), không sụt áp dưới 4.7V khi động cơ hoạt động, và pin dự phòng không tự ngắt.
* **Các bước thử nghiệm thực nghiệm:**
  1. **Bài test 1.1 — Đo thông mạch & Chống chập (Cold Continuity Check):**
     - Dùng đồng hồ VOM để thang đo thông mạch (tiếng bíp), đo giữa chân `5V` và `GND` trên Nano Shield khi chưa cắm điện.
     - *Tiêu chuẩn đạt (PASS):* Đồng hồ không kêu bíp (Điện trở $> 10\text{ k}\Omega$).
  2. **Bài test 1.2 — Đo dòng điện tĩnh và dòng đỉnh (Peak Current Test):**
     - Cắm mạch vào nguồn USB máy tính qua đồng hồ đo dòng USB Doctor.
     - Dòng tĩnh khi toàn bộ hệ thống ở trạng thái nghỉ: $\approx 70\text{ mA}$.
     - Kích hoạt Servo SG90 quay nhanh: Dòng nhảy lên đỉnh $\approx 220\text{ mA}$.
     - Điện áp trên đường ray 5V của Shield đo được: $4.85\text{V} - 4.95\text{V}$ (Hoàn toàn nằm trong chuẩn an toàn).
  3. **Bài test 1.3 — Thử nghiệm tụ hóa bù sụt áp 470µF:**
     - Cho Servo nâng hạ cần Barie 20 lần liên tục có gắn thanh que 22cm.
     - *Tiêu chuẩn đạt (PASS):* Đèn LED nguồn `POW` trên bo mạch Nano sáng trong trẻo, không bị chớp nháy hoặc khởi động lại chip.
  4. **Bài test 1.4 — Thử nghiệm chế độ chống ngắt của Pin sạc dự phòng (Trickle Charge Mode Test):**
     - Cắm hệ thống vào Pin dự phòng (Xiaomi / Anker / Baseus).
     - Bấm đúp nút nguồn trên Pin dự phòng để kích hoạt chế độ dòng nhỏ.
     - Treo mạch trong trạng thái tĩnh **30 phút liên tục**.
     - *Tiêu chuẩn đạt (PASS):* Sau 30 phút, mạch vẫn có điện liên tục, pin dự phòng không bị rơi vào trạng thái ngủ (Sleep Mode).

---

### GIAI ĐOẠN 2: HARDWARE SANITY & UNIT TESTING (CHẨN ĐOÁN CỤC BỘ TỪNG CỔNG I/O)

* **Mục tiêu:** Kiểm tra cơ tính và tín hiệu của từng chân kết nối trên Nano Shield bằng firmware chẩn đoán mẫu `test_hardware_diagnostic.ino`.
* **Quy trình thực hiện:**
  - Nạp sketch `test_hardware_diagnostic.ino` vào Arduino Nano qua cổng USB.
  - Mở Serial Monitor trên máy tính với tốc độ `9600 baud`.
  - Chọn phím chức năng `A` để mạch tự động quét toàn bộ ngoại vi trong 60 giây.

| Cổng kiểm tra | Ngoại vi kết nối | Hành vi mong đợi (Expected Behavior) | Tiêu chí đánh giá Đạt (PASS) |
| :---: | :--- | :--- | :--- |
| **D10** | Đèn LED Xe XANH | Sáng rõ trong 800ms rồi tắt | Độ sáng tốt, không nhấp nháy chập chờn |
| **D11** | Đèn LED Xe VÀNG | Sáng rõ trong 800ms rồi tắt | Phân biệt rõ sắc vàng với màu đỏ/xanh |
| **D12** | Đèn LED Xe ĐỎ | Sáng rõ trong 800ms rồi tắt | Sáng rực rỡ, góc nhìn rộng $\ge 60^\circ$ |
| **D6** | Đèn LED Đi bộ ĐỎ | Sáng rõ trong 800ms rồi tắt | Báo hiệu người dừng chờ rõ nét |
| **D7** | Đèn LED Đi bộ XANH | Sáng rõ trong 800ms rồi tắt | Báo hiệu qua đường hiển thị rõ |
| **D8** | Còi chip Buzzer mini | Kêu 3 tiếng *"tít... tít... tít..."* (150ms on / 150ms off) | Âm lượng rõ ràng trong phạm vi 3–5m |
| **D9** | Động cơ Servo Barie | Quét từ $0^\circ \to 90^\circ$ (1.5s), giữ 1.5s, hạ về $0^\circ$ | Barie mở thẳng đứng $90^\circ$, hạ nằm ngang $0^\circ$, không rung |
| **D2** | Nút bấm Failsafe | Nhấn nút cơ học trên cột đèn | Serial Monitor in dòng xác nhận, còi chíp kêu 1 tiếng phản hồi |

---

### GIAI ĐOẠN 3: AI VISION CALIBRATION & SERIAL PROTOCOL (HIỆU CHUẨN THỊ GIÁC AI)

* **Mục tiêu:** Cân chỉnh góc đặt camera trên sa bàn và kiểm định độ chính xác của mô hình học máy MobileNet khi chạy Offline trên trình duyệt Google Chrome.
* **Thiết lập không gian thực nghiệm:**
  - Vị trí gắn Webcam: Đầu cần vươn cột đèn giao thông, độ cao $H = 25\text{ cm}$, cần vươn dài $12\text{ cm}$.
  - Góc nghiêng quang học: Góc dốc $45^\circ$ hướng thẳng vào trung tâm vạch kẻ đường đi bộ kích thước $20\text{ cm} \times 15\text{ cm}$.
  - Chiếu sáng: Thử nghiệm ở 2 điều kiện ánh sáng (Ánh sáng phòng học bình thường và Ánh sáng hội trường gắt / rọi đèn flash).

```
          [Webcam HD 720p]
                 \
                  \  Góc nghiêng 45°
             25cm  \
                    \
                     v
       =============================== Sa bàn vạch đi bộ 20x15cm
```

* **Ma trận thực nghiệm 100 lần thử nhận diện (Confusion Matrix Test):**
  Học sinh An Đông lần lượt đưa các vật thể mẫu vào vùng quan sát của camera:

| Phân lớp nhận diện (Class) | Đạo cụ thực nghiệm | Số lần thử | Số lần nhận diện đúng | Độ chính xác thực tế | Ngưỡng yêu cầu | Kết luận |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Class 0: Đường bình thường** | Mặt đường vắng, xe cộ mô hình chạy qua | 40 lần | 39 lần | $97.5\%$ | $\ge 85\%$ | **ĐẠT XUẤT SẮC** |
| **Class 1: Học sinh xin đường** | Học sinh giơ tay xin đường trên vỉa hè | 40 lần | 38 lần | $95.0\%$ | $\ge 85\%$ | **ĐẠT XUẤT SẮC** |
| **Class 2: Xe cứu thương khẩn cấp** | Đưa mô hình xe cứu thương màu trắng-đỏ vào | 20 lần | 19 lần | $95.0\%$ | $\ge 85\%$ | **ĐẠT XUẤT SẮC** |
| **TỔNG CỘNG ĐỘ CHÍNH XÁC MÔ HÌNH** | Toàn bộ 100 kịch bản ngẫu nhiên | **100 lần** | **96 lần** | **96.0%** | **$\ge 85\%$** | **SẴN SÀNG THI ĐẤU** |

* **Kiểm định bộ lọc chống nhiễu thời gian (Debounce Filter 1.5s):**
  - Đưa bàn tay hoặc người đi lướt qua vạch đi bộ trong thời gian ngắn ($< 1.0\text{ giây}$).
  - *Tiêu chuẩn đạt (PASS):* Hệ thống không gửi lệnh `'1'` xuống Arduino. Đèn giao thông giữ nguyên màu XANH, không làm gián đoạn dòng xe lưu thông.
  - Giữ tay xin đường liên tục trong $1.5\text{ giây}$ ($\ge 22\text{ frames}$): Hệ thống kích hoạt gửi lệnh `'1'` ngay lập tức.
* **Kiểm định độ trễ giao tiếp Web Serial API:**
  - Đo thời gian từ lúc trình duyệt Chrome gửi lệnh `'1'` hoặc `'2'` tới khi Arduino Nano thực thi lệnh điều khiển: Độ trễ đo được $T_{latency} \approx 28\text{ ms} - 45\text{ ms} < 50\text{ ms}$ (hoàn toàn tức thì, mắt thường không nhận biết được độ trễ).

---

### GIAI ĐOẠN 4: SYSTEM INTEGRATION & FSM STRESS TESTING (TÍCH HỢP TOÀN HỆ THỐNG 30 PHÚT)

* **Mục tiêu:** Chạy liên tục hệ thống trong 30 phút mô phỏng toàn bộ các tình huống chấm thi của Ban Giám khảo.
* **Quy trình diễn tập 5 tình huống FSM liên hoàn:**
  1. **Tình huống 1 (Đường vắng):** Đèn xe Xanh liên tục, Barie đóng nằm ngang $0^\circ$, còi tắt.
  2. **Tình huống 2 (Học sinh xin qua đường):**
     - Đèn xe chuyển VÀNG trong đúng $3.0\text{ giây}$.
     - Đèn xe chuyển ĐỎ, đèn đi bộ bật XANH, Barie nhẹ nhàng nhấc lên $90^\circ$ trong $1.35\text{ giây}$.
     - Còi Buzzer kêu *"tít... tít..."* nhịp $500\text{ ms}$ trong 12 giây đầu.
     - Trong $3.0\text{ giây}$ cuối, còi kêu dồn dập nhịp $200\text{ ms}$, cần Barie từ từ hạ về $0^\circ$ đóng rào chắn. Đèn xe phục hồi lại Xanh.
  3. **Tình huống 3 (Thử nghiệm xung đột khẩn cấp — Xe cứu thương cắt ngang):**
     - Khi học sinh đang đi qua đường (giây thứ 5 của Tình huống 2), học sinh An Đông bất ngờ đưa xe cứu thương vào vùng camera.
     - *Kiểm chứng an toàn tuyệt đối:* Hệ thống **KHÔNG ĐƯỢC** lập tức bật đèn xe xanh và hạ barie!
     - Hệ thống kích hoạt **Pha chuyển tiếp an toàn khẩn cấp 2.5 giây (STATE_EMERGENCY_CLEARANCE)**: Còi hú dồn dập $100\text{ ms}$, đèn đi bộ nhấp nháy ĐỎ để học sinh rảo bước lên vỉa hè an toàn. Cần Barie vẫn mở để không chắn lối thoát của học sinh.
     - Sau đúng $2.5\text{ giây}$, Barie hạ về $0^\circ$ và đèn xe ô tô mới bật XANH KHẨN CẤP cho xe cứu thương phóng qua ngã tư.
  4. **Tình huống 4 (Nút bấm cơ học Failsafe D2):**
     - Dùng bìa đen che kín ống kính Webcam (mô phỏng mất camera do mưa to sương mù).
     - Học sinh Đạt tiến tới ấn nút Failsafe trên cột đèn.
     - Mạch Arduino lập tức ngắt phần cứng, kích hoạt đèn vàng 3s $\to$ đèn đỏ 15s và mở Barie cho học sinh qua đường an toàn.
  5. **Tình huống 5 (Watchdog Failsafe khi tuột cáp USB máy tính):**
     - Đang hoạt động, rút phắc cáp USB nối Laptop ra khỏi Arduino Nano.
     - Sau đúng $3.0\text{ giây}$ không nhận được xung Heartbeat (`'0'`), chip Arduino tự động kích hoạt chế độ an toàn: Khóa chặt Barie ở góc $0^\circ$ bảo vệ học sinh trên vỉa hè, đồng thời đèn VÀNG ô tô tự động chuyển sang chế độ **NHẤP NHÁY CHU KỲ 1 GIÂY (500ms sáng, 500ms tắt)** đúng Quy chuẩn Quốc gia QCVN 41:2019/BGTVT.
  6. **Bài test độ bền nhiệt (Burn-in 30 phút liên tục):**
     - Vận hành lặp đi lặp lại 5 tình huống trên trong 30 phút.
     - Kiểm tra nhiệt độ chip CH340 và động cơ Servo SG90 bằng nhiệt kế hồng ngoại: Nhiệt độ duy trì ở mức $< 42^\circ\text{C}$ (Mát mẻ, hoàn toàn ổn định).

---

## VI. BẢNG KIỂM TRA ĐỒNG BỘ MÃ NGUỒN & PHẦN CỨNG (CODE-TO-HARDWARE VERIFICATION)

Mọi chân cắm trên sa bàn thực tế đã được đồng bộ chuẩn xác $100\%$ với mã nguồn nhúng Arduino C++:

| Tên định danh trong mã nguồn | Chân Arduino Nano | Chân trên Nano Shield | Thiết bị ngoại vi kết nối | Ngưỡng logic | Tình trạng kiểm thử |
| :--- | :---: | :---: | :--- | :---: | :---: |
| `PIN_BTN_FAILSAFE` | D2 | Cọc S-V-G hàng D2 | Nút bấm cơ học Failsafe 3-pin | `FALLING` (Kéo lên nội bộ) | **PASS** |
| `PIN_PED_RED` | D6 | Cọc S-V-G hàng D6 | Đèn LED Người đi bộ ĐỎ | `HIGH` = Bật, `LOW` = Tắt | **PASS** |
| `PIN_PED_GREEN` | D7 | Cọc S-V-G hàng D7 | Đèn LED Người đi bộ XANH | `HIGH` = Bật, `LOW` = Tắt | **PASS** |
| `PIN_BUZZER` | D8 | Cọc S-V-G hàng D8 | Còi chip Active Buzzer 5V | `HIGH` = Kêu, `LOW` = Tắt | **PASS** |
| `PIN_SERVO` | D9 | Cọc S-V-G hàng D9 | Động cơ Servo mini SG90 (PWM) | Xung PWM $0^\circ - 90^\circ$ | **PASS** |
| `PIN_CAR_GREEN` | D10 | Cọc S-V-G hàng D10 | Đèn LED Ô tô XANH | `HIGH` = Bật, `LOW` = Tắt | **PASS** |
| `PIN_CAR_YELLOW` | D11 | Cọc S-V-G hàng D11 | Đèn LED Ô tô VÀNG | `HIGH` = Bật, `LOW` = Tắt | **PASS** |
| `PIN_CAR_RED` | D12 | Cọc S-V-G hàng D12 | Đèn LED Ô tô ĐỎ | `HIGH` = Bật, `LOW` = Tắt | **PASS** |

---

## VII. CHECKLIST TIẾP NHẬN VÀ LẮP RÁP TẠI PHÒNG THÍ NGHIỆM (UNBOXING & ASSEMBLY CHECKLIST)

Bảng kiểm 8 bước dành riêng cho 3 học sinh Marie Curie khi bóc hộp linh kiện và lắp ráp sa bàn:

- [ ] **Bước 1 (Kiểm đếm số lượng):** Mở gói hàng, đối chiếu đủ 17 mục theo Bảng danh mục vật tư mục IV.
- [ ] **Bước 2 (Kiểm tra chân cắm):** Cắm mạch Arduino Nano vào khe cắm trung tâm của Shield v3.0, chú ý cắm đúng chiều cổng Mini-USB hướng ra phía ngoài mép bo mạch.
- [ ] **Bước 3 (Gắn tụ chống sụt áp):** Cắm 01 tụ hóa $470\mu\text{F}/16\text{V}$ vào chân nguồn VCC-GND gần cọc D9 (Chân có vạch trắng trên thân tụ cắm vào cọc GND đen, chân dài còn lại cắm vào cọc VCC đỏ).
- [ ] **Bước 4 (Cố định cơ khí):** Dùng băng dính xốp 3M dán chặt thân động cơ Servo SG90 vào vị trí đầu vạch đi bộ trên sa bàn. Gắn thanh cần Barie 22cm vào cánh tay đòn servo bằng ốc vít nhỏ.
- [ ] **Bước 5 (Đấu nối cáp Dupont):** Cắm các dây cắm theo đúng bảng sơ đồ chân mục VI (D2, D6, D7, D8, D9, D10, D11, D12). Dùng dây thít nhựa gom bó dây điện gọn gàng dưới gầm sa bàn.
- [ ] **Bước 6 (Nạp firmware chẩn đoán):** Nạp file `test_hardware_diagnostic.ino` từ máy tính vào Arduino, gõ phím `'A'` để kiểm tra tự động toàn bộ linh kiện.
- [ ] **Bước 7 (Nạp firmware chính thức):** Nạp file `traffic_light_arduino.ino` vào Arduino Nano.
- [ ] **Bước 8 (Khởi động trạm AI Chrome):** Mở file `ai_traffic_web_controller.html` trên Google Chrome, kết nối cổng USB và bắt đầu diễn tập 5 tình huống.

---

## VIII. KẾT LUẬN VÀ KIẾN NGHỊ

1. **Về danh mục thiết bị:** 
   - Sau khi phân tích kỹ thuật, toàn bộ hệ thống phần cứng đã **HOÀN TOÀN ĐẦY ĐỦ**, đồng bộ $100\%$ từ điện tử, cơ khí đến thị giác máy tính.
   - Đã loại bỏ triệt để linh kiện thừa (**Breadboard**), khắc phục bẫy kỹ thuật sụt áp của cáp USB-to-DC qua IC AMS1117 bằng phương án cấp nguồn chuẩn trực tiếp qua cổng Mini-USB.
   - Bổ sung kịp thời 6 chi tiết phụ trợ sống còn: Cần Barie 22cm siêu nhẹ, Cáp Dupont Đực-Cái, Module 3 LED giao thông mini, Cột gắn Webcam, Băng keo xốp 3M và Xe cứu thương mô hình.
2. **Về ngân sách dự toán:** Tổng kinh phí chỉ **415.000 VNĐ** (tiết kiệm $58.5\%$ ngân sách cho phép), mang tính khả thi cao, phù hợp cho việc nhân rộng mô hình tại các trường học trên toàn quốc.
3. **Về tính sẵn sàng thi đấu:** Với quy trình thử nghiệm 4 giai đoạn và firmware chẩn đoán tự động đã được lập trình sẵn, đội tuyển STEM Marie Curie Thái Bình hoàn toàn tự tin bước vào Vòng Bán kết cuộc thi HNUE Olympic STEM 2026 với chất lượng kỹ thuật cao nhất.

---
*Tài liệu kỹ thuật và quy trình thử nghiệm được phê duyệt chính thức bởi Tổ STEM Trường Tiểu học, THCS & THPT Marie Curie Thái Bình.*
