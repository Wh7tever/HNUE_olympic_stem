# BẢN THUYẾT MINH CÁC TÌNH HUỐNG HOẠT ĐỘNG VÀ QUY TRÌNH VẬN HÀNH
### DỰ ÁN: HỆ THỐNG ĐÈN GIAO THÔNG HỌC ĐƯỜNG THÔNG MINH TÍCH HỢP AI VISION
**Đơn vị:** Trường Tiểu học, THCS và THPT Marie Curie  
**Cuộc thi:** HNUE Olympic STEM 2026 — Bảng Tiểu học (Khối 4 - 5)  
**Tác giả:** Phạm Hữu Đạt (4A1), Vũ Minh Quang (4A1), Vũ Ngọc An Đông (5A1)  
**Cán bộ hướng dẫn:** Thầy Lê Ngọc Anh (Tổ trưởng chuyên môn STEM)

---

## I. NGUYÊN LÝ ĐIỀU KHIỂN THEO MÁY TRẠNG THÁI HỮU HẠN (FINITE STATE MACHINE)

Hệ thống Đèn giao thông học đường thông minh Marie Curie được thiết kế theo nguyên lý Máy trạng thái hữu hạn (FSM). Toàn bộ hành vi của cột đèn, góc quét camera AI, động cơ servo rào chắn Barie và còi chip cảnh báo được kiểm soát chặt chẽ qua 5 tình huống logic khép kín:

```
+----------------------------------------------------------------------------------------------------+
|                                SƠ ĐỒ CHUYỂN TRẠNG THÁI HỆ THỐNG (FSM)                              |
+----------------------------------------------------------------------------------------------------+
                                                  │
                                                  ▼
                       ┌─────────────────────────────────────────────────────┐
                       │   TÌNH HUỐNG 1: CHẾ ĐỘ ĐƯỜNG VẮNG (BÌNH THƯỜNG)     │
                       │   • Đèn xe: XANH liên tục (xe chạy thông suốt)      │
                       │   • Đèn đi bộ: ĐỎ | Barie: ĐÓNG (0 độ)              │
                       └──────────────────────────┬──────────────────────────┘
                                                  │
                                                  │ (Camera AI phát hiện học sinh giơ tay)
                                                  ▼
                       ┌─────────────────────────────────────────────────────┐
                       │   BỘ LỌC THỜI GIAN AI DEBOUNCE (1.5 Giây)           │
                       │   • AI nhận diện liên tục >= 22 frames              │
                       │   • Độ tin cậy Confidence >= 85%                    │
                       └──────────────┬───────────────────────────────┬──────┘
                                      │ (Đạt chuẩn)                   │ (Dưới 1.5s: Bỏ qua)
                                      ▼                               └──> Quay lại TH 1
                       ┌─────────────────────────────────────────────────────┐
                       │   TÌNH HUỐNG 2A: CẢNH BÁO GIẢM TỐC (3 Giây)         │
                       │   • Đèn xe: VÀNG | Đèn đi bộ: ĐỎ                    │
                       │   • Barie: Vẫn ĐÓNG | Xe từ xa chủ động hãm phanh   │
                       └──────────────────────────┬──────────────────────────┘
                                                  │ (Hết 3s đèn vàng)
                                                  ▼
                       ┌─────────────────────────────────────────────────────┐
                       │   TÌNH HUỐNG 2B: CHO HỌC SINH QUA ĐƯỜNG (15 Giây)    │
                       │   • Đèn xe: ĐỎ (dừng xe) | Đèn đi bộ: XANH          │
                       │   • Barie: TỰ ĐỘNG NÂNG LÊN 90 ĐỘ (Servo SG90)      │
                       │   • Còi Buzzer: Kêu "tít... tít..." dẫn đường       │
                       └──────────────────────────┬──────────────────────────┘
                                                  │ (Hết 15s đếm ngược)
                                                  ▼
                       ┌─────────────────────────────────────────────────────┐
                       │   PHỤC HỒI: Barie hạ về 0 độ -> Đèn xe chuyển XANH  │
                       └─────────────────────────────────────────────────────┘
                                                  ▲
                                                  │
          ┌───────────────────────────────────────┴───────────────────────────────────────┐
          │                                                                               │
          ▼                                                                               ▼
┌──────────────────────────────────────┐                                ┌──────────────────────────────────────┐
│  TÌNH HUỐNG 3: XE CỨU THƯƠNG ĐẾN     │                                │  TÌNH HUỐNG 4: NÚT BẤM DỰ PHÒNG      │
│  • NGẮT LẬP TỨC MỌI CHU KỲ KHÁC      │                                │  • Camera gặp sự cố / Ánh sáng xấu   │
│  • Barie: Hạ xuống 0 độ chặn người   │                                │  • Học sinh ấn nút cơ học Failsafe   │
│  • Đèn xe: BẬT XANH CẤP TỐC cho xe   │                                │  • Tự động kích hoạt chu kỳ an toàn  │
└──────────────────────────────────────┘                                └──────────────────────────────────────┘
                                                  ▲
                                                  │
                       ┌─────────────────────────────────────────────────────┐
                       │  TÌNH HUỐNG 5: MẤT KẾT NỐI MÁY TÍNH (> 3 GIÂY)      │
                       │  • Tự động kích hoạt cơ chế bảo vệ Watchdog         │
                       │  • Barie: ĐÓNG CHẶT 0 độ bảo vệ học sinh trên vỉa hè│
                       │  • Đèn xe: NHẤP NHÁY VÀNG (1s/lần) cảnh báo giảm tốc│
                       └─────────────────────────────────────────────────────┘
```

---

## II. BẢNG ĐỐI CHIẾU TRẠNG THÁI THIẾT BỊ TRONG 5 TÌNH HUỐNG

| Tình huống | Mắt Webcam AI nhận diện | Đèn Ô tô (Xe chạy) | Đèn Người Đi Bộ | Rào Chắn Barie (Servo) | Còi Buzzer Cảnh Báo |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **TH 1: Bình thường (Đường vắng)** | `0_Normal_Road` ($\ge 90\%$) | **XANH** (Chạy) | **ĐỎ** (Dừng) | **ĐÓNG ($0^\circ$)** | Tắt hoàn toàn |
| **TH 2: Học sinh xin qua đường** | `1_Student_Waiting` ($\ge 1.5\text{s}$) | **VÀNG ($3\text{s}$) $\to$ ĐỎ ($15\text{s}$)** | **XANH ($15\text{s}$)** | **MỞ LÊN ($90^\circ$)** | Kêu nhịp ngắt quãng *"tít... tít..."* |
| **TH 3: Xe cứu thương đến** | `2_Ambulance_Emergency` | **XANH KHẨN CẤP** | **ĐỎ** (Chặn) | **ĐÓNG ($0^\circ$)** | Kêu dài cảnh báo nguy hiểm |
| **TH 4: Bấm nút Failsafe dự phòng** | Bỏ qua AI (Mất nhận diện) | **VÀNG ($3\text{s}$) $\to$ ĐỎ ($15\text{s}$)** | **XANH ($15\text{s}$)** | **MỞ LÊN ($90^\circ$)** | Kêu nhịp ngắt quãng |
| **TH 5: Mất điện máy tính / Đứt cáp** | Mất tín hiệu USB ($> 3\text{s}$) | **VÀNG NHẤP NHÁY (1s/lần)** | **ĐỎ** | **ĐÓNG CHẶN ($0^\circ$)** | Tắt |

---

## III. PHÂN TÍCH CHUYÊN SÂU 5 TÌNH HUỐNG VẬN HÀNH THỰC TẾ

### 1. TÌNH HUỐNG 1: CHẾ ĐỘ ĐƯỜNG VẮNG (BÌNH THƯỜNG - IDLE STATE)
* **Bối cảnh thực tế:** Ngoài giờ tan học hoặc các thời điểm không có học sinh qua lại cổng trường, lòng đường thông thoáng.
* **Hoạt động của hệ thống:**
  - Mắt Webcam USB mini gắn trên đầu cần vươn của cột đèn (chếch góc 45 độ) liên tục ghi nhận hình ảnh lòng đường.
  - Mô hình AI nhận diện trạng thái `0_Normal_Road` với độ chính xác trên 98%.
  - Đèn tín hiệu ô tô duy trì màu **XANH liên tục** để các phương tiện lưu thông với vận tốc thiết kế, không bị dừng chờ máy móc.
  - Đèn đi bộ màu **ĐỎ**, cần Barie an toàn nằm ngang chốt chặn tại góc $0^\circ$, còi Buzzer tắt.
* **Giá trị khoa học & môi trường:** Giải quyết triệt để vấn nạn của đèn tín hiệu truyền thống (vẫn bật đỏ dù đường không có một bóng người). Giảm thiểu $35\%$ thời gian xe dừng chờ nổ máy tại chỗ, cắt giảm lượng lớn khí thải độc hại (CO, $CO_2$) ngay trước cổng trường học.

---

### 2. TÌNH HUỐNG 2: HỌC SINH QUA ĐƯỜNG ĐƯỢC AI NHẬN DIỆN (PEDESTRIAN AI MODE)
* **Bối cảnh thực tế:** Vào giờ tan trường, một học sinh (hoặc nhóm học sinh) đi đến mép vỉa hè, đứng trước vạch kẻ đường và thực hiện cử chỉ giơ tay vẫy xin đường.
* **Tiến trình 4 pha phối hợp tự động giữa AI và Arduino:**
  - **Pha 1 — Lọc nhiễu xác nhận ($1.5\text{ giây}$):** Camera phát hiện cử chỉ học sinh. Bộ lọc thời gian (Debounce Filter) lập tức kiểm tra: Mô hình AI phải nhận diện trạng thái `1_Student_Waiting` liên tục trong $1.5\text{ giây}$ (tương đương 22 khung hình liên tiếp) với độ tin cậy $Confidence \ge 85\%$. Nếu một người lớn chỉ vô tình đi lướt ngang qua mép đường dưới 1.5 giây rồi đi tiếp, hệ thống sẽ bỏ qua, không đổi đèn xe $\to$ *Bảo đảm dòng xe không bị gián đoạn sai lệch*.
  - **Pha 2 — Cảnh báo giảm tốc an toàn ($3\text{ giây}$):** Sau khi xác nhận đúng học sinh, máy tính gửi mã lệnh `'1'` qua cổng USB. Mạch Arduino chuyển đèn xe từ Xanh sang **VÀNG** trong đúng $3\text{ giây}$. Thời gian này giúp các tài xế từ xa kịp quan sát, hãm phanh từ từ và dừng lại trước vạch dừng, tránh hiện tượng phanh gấp nguy hiểm. Cần Barie lúc này vẫn đóng chặt để giữ học sinh an toàn trên vỉa hè.
  - **Pha 3 — Mở lối ưu tiên qua đường ($15\text{ giây}$):**
    - Đèn ô tô chuyển sang **ĐỎ** (xe dừng hẳn).
    - Đèn người đi bộ chuyển sang **XANH**.
    - Động cơ Servo SG90 quay từ từ từ $0^\circ \to 90^\circ$ (trong $1.35\text{ giây}$, quét $15\text{ms}$/độ) nhẹ nhàng nâng cần Barie lên mở lối cho học sinh bước qua.
    - Còi chip Buzzer phát âm thanh nhịp nhàng *"tít... tít... tít..."* ($0.5\text{s}$/nhịp) để hướng dẫn thính giác cho các em học sinh lớp nhỏ hoặc người khiếm thị.
    - Thời gian đếm ngược được cài đặt chính xác đúng **$15\text{ giây}$** (tính toán khoa học theo công thức Toán học: $t = s/v = 8\text{m} / 0.8\text{m/s} = 10\text{s}$ đi bộ cộng thêm $5\text{s}$ đệm an toàn).
  - **Pha 4 — Đóng rào chắn & Phục hồi:** Ở 3 giây cuối cùng, tiếng còi chíp kêu dồn dập cảnh báo sắp hết giờ. Sau đó, cần Barie từ từ hạ xuống góc $0^\circ$ chắn đường trước khi đèn xe chuyển lại màu Xanh.

---

### 3. TÌNH HUỐNG 3: XE CỨU THƯƠNG / XE CỨU HỎA KHẨN CẤP ĐẾN (EMERGENCY PREEMPTION VỚI PHA CHUYỂN TIẾP AN TOÀN)
* **Bối cảnh thực tế:** Trong khi học sinh đang chuẩn bị qua đường (hoặc đang bước dở qua đường), một chiếc xe cứu thương (hoặc xe chữa cháy) hú còi tiến nhanh về phía ngã tư.
* **Cơ chế ngắt ưu tiên bảo toàn sinh mạng (Emergency Preemption with Safe Clearance Interval):**
  - Mắt camera AI lập tức nhận dạng được hình dáng đặc trưng của xe cứu thương (`2_Ambulance_Emergency`) với độ tin cậy $Confidence \ge 85\%$.
  - **Trường hợp 1 (Đường đang ở TH1 - Đường vắng):** Cần Barie giữ nguyên $0^\circ$, đèn ô tô duy trì XANH LIÊN TỤC để xe cứu thương phóng qua ngã tư với thời gian chờ bằng 0.
  - **Trường hợp 2 (Hệ thống đang ở TH2 - Học sinh đang qua đường):** Để triệt tiêu rủi ro cần Barie hạ đập trúng người hoặc xe phóng qua khi học sinh còn ở giữa lòng đường, hệ thống kích hoạt **Pha chuyển tiếp an toàn khẩn cấp (Emergency Clearance Interval 2 – 3 giây)**:
    + Còi chip Buzzer lập tức phát âm thanh báo động dồn dập, đồng thời đèn đi bộ nhấp nháy **ĐỎ** liên tục cảnh báo các em học sinh đang ở dưới lòng đường nhanh chóng rảo bước lên vỉa hè an toàn.
    + Trong 2–3 giây này, cần Barie ở mép vỉa hè vẫn giữ mở để không chặn lối thoát lên vỉa hè của học sinh, đèn ô tô vẫn giữ ĐỎ chặn dòng xe.
    + Ngay sau khi hết 2–3 giây chuyển tiếp an toàn (học sinh đã lên vỉa hè an toàn), cần Barie mới từ từ hạ xuống chốt góc $0^\circ$, đèn đi bộ chuyển ĐỎ, và đèn ô tô bật **XANH KHẨN CẤP** để xe cứu thương lưu thông an toàn tuyệt đối.

* **Hoạt động của sa bàn & Thuyết minh trình diễn:**
  - Bạn Vũ Ngọc An Đông cầm mô hình xe cứu thương đồ chơi đẩy nhanh vào làn đường.
  - Bạn Đông thuyết minh tự tin: *"Đột nhiên có xe cứu thương tới... Camera AI lập tức nhận diện xe ưu tiên. Để đảm bảo an toàn tuyệt đối, hệ thống kích hoạt còi báo động khẩn cấp 3 giây cho các bạn học sinh dưới đường nhanh chóng bước lên vỉa hè, sau đó Barie mới nhẹ nhàng đóng sập chốt 0 độ và đèn xe bật xanh khẩn cấp cho xe cứu thương phóng qua ngã tư an toàn tuyệt đối ạ!"*

### 4. TÌNH HUỐNG 4: SỰ CỐ MẤT NHẬN DIỆN AI $\to$ NÚT BẤM CƠ HỌC FAILSAFE
* **Bối cảnh thực tế:** Vào ngày thời tiết mưa lớn, sương mù dày đặc làm mờ ống kính camera, hoặc ánh đèn rọi sân khấu tại hội trường thi đấu chiếu thẳng vào mắt webcam khiến AI không đạt ngưỡng tin cậy $85\%$.
* **Quy trình kích hoạt dự phòng cơ học:**
  - Học sinh nhận thấy sau 3 giây đứng giơ tay mà đèn chưa chuyển $\to$ Em chủ động đưa tay nhấn vào **Nút bấm cơ học màu đỏ (Failsafe Button)** gắn tại độ cao $1\text{m}$ trên thân cột đèn.
  - Nút bấm được nối trực tiếp vào chân ngắt phần cứng D2 của vi điều khiển Arduino Nano.
  - Mạch Arduino lập tức bỏ qua tín hiệu từ máy tính, tự động kích hoạt chu kỳ an toàn: Đèn xe chuyển vàng $3\text{s} \to$ Đèn xe đỏ + Barie mở $15\text{s} \to$ Barie đóng.
* **Ý nghĩa kỹ thuật:** Khẳng định năng lực tư duy dự phòng sự cố (Fail-Safe) chuẩn kỹ sư của đội tuyển Marie Curie, chứng minh với Ban Giám khảo rằng hệ thống không bao giờ bỏ rơi học sinh dù công nghệ có gặp sự cố.

---

### 5. TÌNH HUỐNG 5: MẤT NGUỒN MÁY TÍNH / ĐỨT CÁP USB (WATCHDOG SAFE STATE)
* **Bối cảnh thực tế:** Máy tính laptop điều hành trạm AI bị hết pin đột ngột, bị treo phần mềm hoặc tuột cáp kết nối USB.
* **Cơ chế an toàn tự động của Vi điều khiển (Hardware Watchdog):**
  - Giữa máy tính và Arduino luôn có một xung nhịp định kỳ (Heartbeat) gửi mỗi 1 giây để xác nhận hệ thống còn hoạt động.
  - Nếu quá $3\text{ giây}$ Arduino không nhận được xung nhịp từ máy tính:
    - Vi điều khiển tự xác định trung tâm AI đã mất kết nối.
    - **Cần Barie lập tức hạ xuống $0^\circ$** (khóa chặt lối đi bộ để giữ học sinh an toàn trên vỉa hè).
    - **Đèn ô tô chuyển sang chế độ NHẤP NHÁY VÀNG (1 giây/nhịp)** theo đúng Quy chuẩn kỹ thuật quốc gia về báo hiệu đường bộ (QCVN 41:2019/BGTVT), cảnh báo tất cả các phương tiện giảm tốc độ tối đa và chú ý quan sát khi đi qua khu vực trường học.

---

## IV. KỊCH BẢN BIỂU DIỄN THỰC CHIẾN 4 BƯỚC TẠI GIAN HÀNG THI ĐẤU

Khi Ban Giám khảo Hội đồng Sư phạm HNUE bước đến gian hàng thi đấu, 3 em học sinh Đạt, Quang, Đông sẽ phối hợp nhịp nhàng biểu diễn thực tế trên sa bàn theo 4 bước trực quan:

1. **Bước 1 — Trình diễn TH1 (Đường vắng):**
   - Bạn Phạm Hữu Đạt chỉ tay vào sa bàn: *"Kính thưa Ban Giám khảo, khi đường vắng, camera AI nhận diện `Normal Road`, đèn xe luôn xanh để phương tiện chạy thông suốt, không gây ùn tắc và không xả khói bụi ạ."*
2. **Bước 2 — Trình diễn TH2 (Học sinh qua đường & Barie an toàn):**
   - Bạn Đạt bước đến đứng trước sa bàn và giơ tay xin đường.
   - Bạn Vũ Minh Quang chỉ vào màn hình và sa bàn: *"Khi bạn Đạt giơ tay, camera AI nhận diện đúng 96% liên tục trong 1.5 giây. Đèn xe lập tức chuyển vàng 3 giây cảnh báo, sau đó đèn xe chuyển đỏ, cần Barie tự động nâng lên 90 độ mượt mà và còi chíp kêu tít tít hướng dẫn bạn Đạt qua đường an toàn trong đúng 15 giây ạ!"*
3. **Bước 3 — Trình diễn TH3 (Ưu tiên xe cứu thương):**
   - Bạn Vũ Ngọc An Đông cầm chiếc xe cứu thương đồ chơi đẩy vào làn đường.
   - Bạn Đông thuyết minh: *"Đột nhiên có xe cứu thương tới... Camera AI lập tức nhận diện xe cứu thương, ngay lập tức cần Barie đóng sập xuống bảo vệ người đi bộ, đèn xe chuyển xanh khẩn cấp cho xe cứu thương phóng qua không phải chờ đợi một giây nào ạ!"*
4. **Bước 4 — Trình diễn TH4 (Nút bấm dự phòng Failsafe):**
   - Bạn Quang dùng tay che mắt camera lại: *"Thưa Thầy Cô, nếu camera bị mờ hoặc hội trường mất mạng, con chỉ cần ấn nút đỏ này trên cột đèn. Hệ thống chạy mạch ngắt độc lập, mở Barie cho con qua đường an toàn 100% mà không phụ thuộc vào máy tính ạ!"*

---

## V. XÁC NHẬN CỦA ĐỘI TUYỂN VÀ GIÁO VIÊN HƯỚNG DẪN

Hồ sơ thuyết minh này là tài liệu kỹ thuật chính thức làm căn cứ để đội tuyển Marie Curie xây dựng Sổ tay kỹ thuật (Engineering Notebook), lập trình mã nguồn điều khiển vi điều khiển và luyện tập phần thuyết trình bảo vệ trước Hội đồng Giám khảo Cuộc thi HNUE Olympic STEM 2026.

*(Ký tên xác nhận của Đại diện học sinh, Cán bộ kỹ thuật và Trưởng đoàn)*
