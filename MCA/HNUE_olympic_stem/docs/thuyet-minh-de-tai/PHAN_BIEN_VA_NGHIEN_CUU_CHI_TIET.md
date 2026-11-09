# BẢN NGHIÊN CỨU CHI TIẾT & MA TRẬN PHẢN BIỆN DỰ ÁN STEM (HNUE OLYMPIC STEM 2026)

> **Dự án:** Smart School-Zone — Hệ thống Đèn Giao Thông Học Đường Thông Minh Tích Hợp Thị Giác AI & Cơ Chế Bảo Vệ Kép  
> **Đơn vị:** Trường Tiểu học, THCS, THPT Marie Curie  
> **Bảng thi đấu:** Bảng Tiểu học (Học sinh lớp 4 - 5)  
> **Mục tiêu:** Đạt giải cao nhất (Giải Nhất / Huy chương Vàng) tại Vòng Bán kết & Chung kết ĐH Sư phạm Hà Nội.

---

## PHẦN 1: BẢN GIẢI PHẪU DỰ ÁN QUA 5 LĂNG KÍNH (5 LENSES FRAMEWORK)

### 1. Mục tiêu tối thượng (North Star Metric)
Chế tạo thành công mô hình sa bàn giao thông cổng trường học thông minh, chứng minh được 3 giá trị cốt lõi trước Hội đồng Giám khảo HNUE trong đúng 5 phút:
1. **Cứu hộ an toàn:** Giảm 100% nguy cơ tai nạn cho học sinh tự qua đường bằng nhận diện AI + Rào chắn Barie vật lý.
2. **Chống ùn tắc:** Chu kỳ đèn thích ứng thông minh (chỉ chuyển đỏ khi thực sự có học sinh chờ hoặc có xe cứu thương, không bắt xe cộ chờ đèn đỏ vô lý).
3. **Tính chân thực của học sinh (Authenticity):** Cả 3 em học sinh Đạt, Quang, Đông đều làm chủ 100% kiến thức, tự tay vận hành, không mang bóng dáng "người lớn làm hộ".

### 2. Ranh giới hệ thống (System Boundaries)
- **Trong phạm vi (In-Scope):**
  - Sa bàn ngã tư ngõ trường học kích thước `60cm x 80cm` đặt vừa bàn thi đấu (`60cm x 120cm`).
  - Hệ thống 2 cột đèn LED (1 cột cho ô tô, 1 cột cho người đi bộ).
  - 1 rào chắn Barie an toàn điều khiển bằng động cơ Servo mini 9g.
  - Camera AI tích hợp mô hình Google Teachable Machine nhận diện 3 phân lớp ảnh (Trạng thái tĩnh, Học sinh vẫy tay xin đường, Mô hình xe cứu thương).
  - 1 nút bấm cơ học dự phòng (Failsafe Button) lắp tại cột đèn.
- **Ngoài phạm vi (Out-of-Scope):**
  - Không kết nối Internet đám mây khi thi đấu (mô hình AI phải xuất ra chạy Offline hoàn toàn trên trình duyệt cục bộ qua TensorFlow.js).
  - Không dùng các linh kiện công nghiệp đắt tiền vượt quá ngân sách 1.000.000 VNĐ.

---

## PHẦN 2: MA TRẬN ĐIỂM CHẾT 1:1 (PRE-MORTEM FAILURE MATRIX)

Bảng đối chiếu 6 điểm chết chí mạng có thể đánh trượt đội thi và giải pháp phòng vệ tương ứng:

| Mã | Điểm chết tiềm ẩn (Failure Mode - $F_k$) | Cơ chế phòng thủ kỹ thuật (Defense Strategy - $S_k$) | Lệnh kiểm thử nhị phân (Verification Test - $T_k$) |
| :---: | :--- | :--- | :--- |
| **F-01** | **Ánh sáng hội trường lạ làm AI nhận diện sai / chớp tắt liên tục.** | Thêm bộ lọc xác nhận thời gian (Confirmation Debounce): AI phải phát hiện liên tục $\ge 1.5$ giây với độ tin cậy $\ge 85\%$ mới kích hoạt chuyển đèn. | Kiểm tra bằng cách chiếu đèn pin hoặc đổi phông nền đột ngột; đèn không được phép chuyển trạng thái sai. |
| **F-02** | **Giám khảo nghi ngờ "Người lớn làm hộ", học sinh chỉ đọc vẹt.** | Mỗi em giữ 1 phần việc cụ thể; kèm **Sổ tay kỹ thuật (Engineering Notebook)** có ảnh các em tự tay chụp dataset, tự đo đạc, tự dán bìa carton. | Hỏi trực tiếp học sinh: *"Bước nào khó nhất các con đã từng làm sai và sửa thế nào?"* $\to$ Học sinh trả lời tự nhiên theo nhật ký. |
| **F-03** | **Cần Barie Servo bị kẹt răng, gãy hoặc rung bần bật khi demo.** | Dùng ống hút giấy siêu nhẹ làm cần barie; chèn lệnh làm mềm góc quay (Sweep delay $15\text{ms}$/độ) trong Arduino để cần nâng hạ êm ái. | Cho chạy chu kỳ đóng/mở liên tục 50 lần không kẹt, không nóng động cơ. |
| **F-04** | **Bị bắt bẻ vượt hạn mức kinh phí 1.000.000 VNĐ vì tính cả máy tính.** | Phân định rõ trong Thuyết minh: Laptop/máy tính bảng là công cụ điều khiển ngoại vi (thuộc cơ sở vật chất sẵn có). Toàn bộ vật liệu chế tạo sa bàn trị giá 215.000 VNĐ kèm hóa đơn mua linh kiện. | Trình Bảng kê chi tiết linh kiện có chữ ký phụ trách kỹ thuật. |
| **F-05** | **Tích hợp liên môn STEM bị đánh giá là gượng ép, thiếu Toán học.** | Xây dựng công thức tính chu kỳ đèn theo tỷ lệ xích sa bàn ($1:20$): $t = \frac{s}{v} + t_{đệm}$. Có biểu đồ đo lường thời gian xe chờ giảm $35\%$. | Học sinh chỉ được công thức và số liệu tính toán cụ thể trên poster. |
| **F-06** | **Cháy giáo án thuyết trình quá 5 phút hoặc 1 bạn nói lấn lướt bạn khác.** | Thiết lập kịch bản phân đoạn cứng: Bạn 1 ($60\text{s}$), Bạn 2 ($90\text{s}$), Bạn 3 ($90\text{s}$), Kết luận chung ($60\text{s}$). Dùng đồng hồ bấm giờ tập luyện. | Chạy thử nghiệm ít nhất 5 lần, dung sai thời gian không vượt quá $\pm 10$ giây. |

---

## PHẦN 3: BỘ 6 CÂU HỎI PHẢN BIỆN "HIỂM HÓC" CỦA BAN GIÁM KHẢO HNUE & CÂU TRẢ LỜI MẪU

### Câu hỏi 1 (Giám khảo Công nghệ / AI):
> *"Tại sao các con lại chọn Teachable Machine mà không dùng cảm biến khoảng cách siêu âm (Ultrasonic Sensor) gắn ở vạch kẻ đường, vừa rẻ vừa không sợ sai sót do ánh sáng?"*

* **Ý nghĩa câu hỏi:** Giám khảo kiểm tra xem các em có thực sự hiểu ưu thế của AI so với cảm biến thường không, hay chỉ "đú trend" công nghệ.
* **Câu trả lời xuất sắc (Phạm Hữu Đạt - 4A1):**
  > *"Thưa Ban Giám khảo, chúng con đã từng thử nghiệm cảm biến siêu âm trong giai đoạn 1 (có ghi trong Sổ tay kỹ thuật trang 4). Tuy nhiên, cảm biến siêu âm không phân biệt được đâu là học sinh xin qua đường, đâu là một chú chó chạy qua, một chiếc lá rơi hay người chỉ đứng ngắm cảnh. Teachable Machine giúp chúng con nhận diện đúng **hành vi giơ tay xin đường của học sinh** và phân biệt được **hình dáng xe cứu thương** để ưu tiên. Đó chính là sự khác biệt giữa cảm biến đơn thuần và Trí tuệ nhân tạo ạ!"*

---

### Câu hỏi 2 (Giám khảo Sư phạm / Xã hội):
> *"Nếu camera AI bị mất mạng Internet hoặc ống kính bị bụi bẩn che khuất thì hệ thống có làm tê liệt toàn bộ ngã tư không?"*

* **Ý nghĩa câu hỏi:** Đánh giá tính dự phòng an toàn (Fail-Safe) và tư duy kỹ thuật thực tế.
* **Câu trả lời xuất sắc (Vũ Minh Quang - 4A1):**
  > *"Dạ thưa Thầy/Cô, hệ thống của chúng con được thiết kế theo nguyên lý An toàn kép (Fail-Safe):*  
  > *1. Mô hình AI sau khi huấn luyện được tải thẳng về máy tính chạy Offline, hoàn toàn không cần Internet.*  
  > *2. Trên cột đèn luôn có một **Nút bấm cơ học dự phòng**. Nếu camera bị hỏng, học sinh chỉ cần bấm nút, hệ thống sẽ ngay lập tức chuyển đèn an toàn.*  
  > *3. Nếu mất hoàn toàn tín hiệu từ máy tính quá 3 giây, mạch điều khiển sẽ tự động chuyển về chế độ đèn vàng nhấp nháy cảnh báo giảm tốc độ ạ!"*

---

### Câu hỏi 3 (Giám khảo Toán học / Tính toán):
> *"Tại sao các con lại cài đặt đèn xanh cho người đi bộ là 15 giây mà không phải là 30 giây hay 1 phút cho học sinh đi cho thoải mái?"*

* **Ý nghĩa câu hỏi:** Kiểm tra kiến thức Toán học ứng dụng thực tế.
* **Câu trả lời xuất sắc (Vũ Ngọc An Đông - 5A1):**
  > *"Thưa Thầy/Cô, chúng con đã sử dụng công thức Toán học: $t = \frac{s}{v} + t_{an\_toàn}$.*  
  > *Chiều rộng cổng trường thực tế là $8\text{ mét}$. Tốc độ đi bộ trung bình của học sinh Tiểu học chúng con đo được là $0.8\text{ m/giây}$.*  
  > *Thời gian để đi hết đường là: $8 : 0.8 = 10\text{ giây}$. Chúng con cộng thêm $5\text{ giây}$ đệm an toàn cho các em nhỏ lớp 1 đi chậm hơn, tổng cộng đúng $15\text{ giây}$.*  
  > *Nếu để $30$ giây hay $1$ phút thì các phương tiện giao thông sẽ bị dồn ứ lại gây tắc đường nghiêm trọng hơn và thải ra nhiều khí CO2 hơn ạ!"*

---

### Câu hỏi 4 (Giám khảo Môi trường & Chi phí):
> *"Sản phẩm của các con đóng góp gì cho thông điệp 'Những nhà kiến tạo tương lai' và bảo vệ môi trường của cuộc thi năm nay?"*

* **Câu trả lời xuất sắc (Vũ Minh Quang - 4A1):**
  > *"Thưa Ban Giám khảo:*  
  > *Thứ nhất, toàn bộ sa bàn ngã tư, trụ đèn và biển báo được chúng con thu gom từ bìa carton cũ của thư viện trường và que kem gỗ, giúp giảm rác thải nhựa.*  
  > *Thứ hai, hệ thống đèn thông minh giúp phương tiện giao thông không phải dừng chờ đèn đỏ vô lý khi cổng trường không có học sinh qua lại. Theo tính toán của chúng con, việc giảm thời gian xe nổ máy chờ đợi giúp cắt giảm đáng kể lượng khí thải độc hại ngay trước cổng trường học ạ!"*

---

### Câu hỏi 5 (Giám khảo Kiểm tra độ hiểu biết sâu):
> *"Bản thiết kế này ai vẽ cho các con? Đoạn code điều khiển servo này hoạt động ra sao?"*

* **Câu trả lời xuất sắc (Phạm Hữu Đạt & Vũ Minh Quang):**
  > *"Dạ, bản phác thảo ý tưởng đầu tiên chúng con tự vẽ bằng tay trong Sổ tay kỹ thuật. Thầy Ngọc Anh hướng dẫn chúng con hiểu về góc quay từ 0 đến 90 độ của động cơ servo. Trong code Arduino, chúng con dùng hàm `servo.write(90)` để mở cần gạt và `servo.write(0)` để đóng cần gạt. Khi máy tính nhận diện đúng ảnh học sinh, nó sẽ gửi ký tự chữ 'H' (Học sinh) qua cổng USB cho Arduino nhận lệnh ạ!"*

---

### Câu hỏi 6 (Giám khảo Thách đố tình huống bất ngờ):
> *"Bây giờ nếu thầy cầm bức ảnh xe cứu thương giơ ngược hoặc bị nghiêng thì camera của các con có nhận ra được không?"*

* **Câu trả lời xuất sắc (Vũ Ngọc An Đông - 5A1):**
  > *"Thưa Thầy, khi huấn luyện trên Teachable Machine, chúng con đã lường trước điều này nên đã chụp mô hình xe ở nhiều góc độ: góc thẳng, góc nghiêng 45 độ, góc từ trên xuống và cả khi bật đèn flash. Con xin phép được mời Thầy giơ thử ảnh nghiêng ngay trước camera để hệ thống kiểm chứng thực tế ạ!"*

---

## PHẦN 4: THÔNG SỐ KỸ THUẬT SA BÀN & DANH MỤC THỬ NGHIỆM

```
+--------------------------------------------------------------+
|                     SA BÀN GIAO THÔNG (60cm x 80cm)          |
|                                                              |
|   [Cổng trường MCA]                   [Đường đi bộ vạch kẻ]   |
|         ||                                   ||              |
|         ||   +--------------------------+   ||  [Trụ Đèn]    |
|         ||   | Camera AI (Webcam góc rộng|   ||  [Barie Servo]|
|         ==== | hướng xuống vạch qua đường|  ====     ||      |
|              +--------------------------+           ||      |
|  ===========[ Làn xe ô tô / xe máy chạy ]=================== |
|                                                              |
|  [Module Arduino Nano giấu dưới gầm sa bàn bằng bìa carton]  |
+--------------------------------------------------------------+
```

1. **Chu kỳ vận hành tối ưu (State Machine):**
   - **State 0 (Idle):** Đèn xe Xanh, Đèn người Đỏ, Barie đóng ($0^\circ$).
   - **State 1 (Pending AI):** AI phát hiện Học sinh $\ge 1.5\text{s} \to$ Đèn xe chuyển Vàng ($3\text{s}$).
   - **State 2 (Crosswalk Active):** Đèn xe Đỏ, Đèn người Xanh, Barie mở ($90^\circ$), Loa Buzzer kêu tít tít nhịp $0.5\text{s}$ (Thời gian: $15\text{s}$).
   - **State 3 (Closing):** Barie đóng lại từ từ, Đèn người chuyển Đỏ, Đèn xe chuẩn bị Xanh.
   - **State Emergency (Ngắt ưu tiên):** Bất kỳ lúc nào AI thấy Xe cứu thương $\to$ Lập tức chuyển Đèn xe Xanh khẩn cấp, Barie đóng chặn người đi bộ để xe ưu tiên phóng qua an toàn.
