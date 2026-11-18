# CẨM NANG CHUYỂN GIAO & VẬN HÀNH TRÊN LAPTOP DỰ THI
## DỰ ÁN ĐÈN GIAO THÔNG HỌC ĐƯỜNG THÔNG MINH AI — MARIE CURIE ACADEMY (HNUE STEM 2026)

Tài liệu này hướng dẫn chi tiết cách thiết lập và tiếp tục làm việc với Antigravity trên Laptop dự thi mang lên Hà Nội.

---

## 1. Cách Lấy Toàn Bộ Dự Án Sang Laptop

Thầy/cô có thể chọn **1 trong 2 cách** sau:

### Cách A: Qua GitHub (Khuyên dùng — Tự động cập nhật)
1. Mở Terminal / PowerShell trên Laptop.
2. Chạy lệnh:
   ```bash
   git clone https://github.com/Wh7tever/HNUE_olympic_stem.git
   cd HNUE_olympic_stem
   ```
3. Mở thư mục này trong **Antigravity** trên Laptop. AI của Antigravity sẽ đọc ngay tệp `CONTEXT.md` và `AGENTS.md` để hiểu toàn bộ dự án mà không cần giải thích lại.

### Cách B: Qua Ổ Cứng Di Động / USB
1. Toàn bộ thư mục dự án đã được nén sẵn thành tệp:  
   `HNUE_OLYMPIC_STEM_2026_FULL_PACKAGE.zip` (hoặc copy cả thư mục từ ổ `E:\Antigravity\MCA\HNUE_olympic_stem`).
2. Giải nén vào thư mục làm việc trên Laptop (ví dụ `C:\HNUE_olympic_stem` hoặc `D:\HNUE_olympic_stem`).
3. Mở Antigravity trên Laptop và chọn thư mục vừa giải nén.

---

## 2. Kích Hoạt "Bộ Não" Antigravity Engine (AE) Trên Laptop

Thầy/cô **KHÔNG CẦN LO LẮNG** việc Laptop chưa có AE vì tôi đã thiết kế **2 tầng kích hoạt sẵn**:

### 🌟 Tầng 1: Tự Động Kích Hoạt Theo Dự Án (Không cần cài gì cả!)
- Trong thư mục gốc của dự án đã có sẵn tệp **`AGENTS.md`**.
- Tệp này đã được nhúng sẵn **12 Điều Răn của Hiến Pháp AE** và toàn bộ thông số phần cứng / quy tắc kỹ thuật nghiêm ngặt.
- Ngay khi thầy/cô mở thư mục dự án trên Antigravity của Laptop, AI trên Laptop sẽ **tự động đọc tệp này và ngay lập tức trở thành Antigravity Engine** chuẩn mực, không bao giờ phỏng đoán hay hallucinate!

### 🚀 Tầng 2: Cài Đặt Trọn Bộ 30+ Skills Của AE Lên Toàn Bộ Laptop (1-Click)
Nếu thầy/cô muốn Laptop có trọn vẹn toàn bộ hệ sinh thái AE (bao gồm 30+ skills như phản biện đối kháng, kiểm toán code, quản lý ngữ cảnh, TDD...):
1. Tìm tệp **`AE_FULL_SETUP_FOR_LAPTOP.zip`** (đã có trong ổ E hoặc trong thư mục dự án).
2. Giải nén tệp này ra.
3. Nhấp đúp chuột vào tệp: **`Cai-Dat-AE-Cho-Laptop.bat`**.
4. Script sẽ tự động cài Hiến pháp AE và toàn bộ Skills vào thư mục cấu hình `%USERPROFILE%\.gemini\config\` của Laptop trong 2 giây!
5. Khởi động lại Antigravity trên Laptop là xong 100%.

---

## 3. Các Phần Mềm Cần Cài Trên Laptop

1. **Driver CH340 / USB Serial:**  
   - Đa số Windows 10/11 tự nhận driver khi cắm Arduino Nano.  
   - Nếu trong `Device Manager` hiện dấu chấm than vàng tại cổng `USB-SERIAL CH340`, tải và cài driver CH340 (link chính hãng: `wch-ic.com`).
2. **Trình duyệt Google Chrome:**  
   - Dùng để chạy Trạm giám sát thị giác AI góc 45°: `src/ai_traffic_web_controller.html` (sử dụng công nghệ Web Serial API không cần cài đặt gì thêm).
3. **Phần mềm PictoBlox (Bản Windows):**  
   - Tải miễn phí tại trang chủ PictoBlox (`pictoblox.ai`). Dùng để mở tệp `du_an_sa_ban_pictoblox.sb3` cho học sinh thi biểu diễn kéo thả khối AI.

---

## 4. Cách Kết Nối Phần Cứng Trên Laptop

1. **Cắm cáp USB:** Cắm đầu cáp USB Mini vào Arduino Nano, đầu kia cắm vào cổng USB của Laptop.
2. **Kiểm tra cổng COM:**
   - Trên Laptop, chuột phải vào nút Start $\to$ chọn **Device Manager** $\to$ mục **Ports (COM & LPT)**.
   - Nhìn tên cổng (ví dụ: `COM3`, `COM4` hoặc `COM5`). Ghi nhớ số hiệu cổng này.
3. **Thông số nạp & giao tiếp đã chuẩn hóa:**
   - **Board:** Arduino Nano
   - **Processor:** ATmega328P (Old Bootloader)
   - **Baudrate nạp:** `57600 baud`
   - **Baudrate giao tiếp:** `9600 baud`

---

## 5. Kịch Bản Biểu Diễn 5 Tình Huống Trước Ban Giám Khảo

| Tình huống | Thao tác trên Laptop / Sa bàn | Phản ứng trên Sa bàn |
| :--- | :--- | :--- |
| **TH1: Đường vắng** | Gửi lệnh `0` hoặc giữ kết nối bình thường | Đèn xe **XANH**, Đi bộ **ĐỎ**, Barie đóng ngang **0°**. |
| **TH2: Học sinh qua đường** | Giơ hình học sinh trước Camera (hoặc gửi lệnh `2`) | Đèn xe chuyển **VÀNG 3s** $\to$ **ĐỎ**, Đi bộ **XANH**, Barie nâng đứng **90°**, Còi bíp 15s đếm ngược. Sau 15s tự động hạ Barie về **0°**. |
| **TH3: Xe cứu thương** | Giơ hình xe cấp cứu trước Camera (hoặc gửi lệnh `1`) | Còi hú liên tục, Barie đóng chắn đường, đèn xe bật **XANH** thông luồng cứu thương 8 giây. Tự động từ chối nút bấm vỉa hè để bảo vệ xe ưu tiên. |
| **TH4: Nút bấm cứu hộ Failsafe** | Chạm nhẹ đầu dây tím (D2) vào vỏ USB hoặc cọc GND | Kích hoạt ngắt cứng tức thì $<0.01$ms. Đèn xe lập tức chuyển Vàng 3s rồi mở Barie cho học sinh qua đường. Chứng minh hệ thống không phụ thuộc 100% vào AI khi camera gặp sự cố. |
| **TH5: Chế độ tự hành Watchdog** | Tắt phần mềm hoặc rút dây tín hiệu USB | Sau 5 giây mất kết nối, hệ thống tự động nhấp nháy **đèn VÀNG ô tô tần số 1Hz** theo đúng Quy chuẩn Quốc gia QCVN 41:2019 để cảnh báo người đi đường. |
