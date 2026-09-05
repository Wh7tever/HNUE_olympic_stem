# ĐẶC TẢ KIẾN TRÚC TOÀN DIỆN THỜI KHÓA BIỂU MARIE CURIE ACADEMY (MCA)
## Niên khóa: 2026 - 2027 | Phiên bản chuẩn hóa Config-Driven

---

## 1. TỔNG QUAN KIẾN TRÚC HỆ THỐNG

Thời khóa biểu Marie Curie Academy (MCA) năm học 2026 - 2027 là một hệ thống lập lịch học đa cấp phức hợp, bao gồm 18 lớp học từ Tiểu học đến THPT, 43 giáo viên, vận hành trên hai thang thời lượng tiết học khác biệt (35 phút và 45 phút), tích hợp cơ chế ghép lớp, tách môn phân ban chuyên sâu, và đồng giảng song ngữ.

Hệ thống được thiết kế theo mô hình **Config-Driven Declarative Framework**:
- **Tầng Dữ liệu Cấu hình (Declarative Config Kit):** Toàn bộ danh mục 43 giáo viên, 18 lớp học, ma trận phòng học, khung thời gian phân cấp và quy tắc ghép/tách lớp được lưu trữ độc lập tại thư mục `config/` (`teacher_registry.json` và `timetable_rules.json`).
- **Tầng Xử lý & Xuất bản (Engine):** File `build_tkb_master.py` chịu trách nhiệm nạp cấu hình, thẩm định tính hợp lệ nhị phân (Validation Gate) và tái sinh Master Workbook `New folder/TKB_Marie_Curie_2026-2027(update_05_09).xlsx` gồm 4 sheet đồng bộ 100%.

```
                   +----------------------------------+
                   |     USER SCHEDULE CHANGE REQ     |
                   +----------------------------------+
                                     |
                                     v
       +-----------------------------+-----------------------------+
       |                                                           |
       v                                                           v
+-----------------------------+             +-----------------------------+
| config/teacher_registry.json|             |  config/timetable_rules.json|
| - 43 Giao vien & Danh xung  |             | - 18 Lop hoc & Phong co so  |
| - Dinh muc 711 tiet         |             | - 12 Cap doi ngau Khoi 12   |
| - Phan cong SmartSchool     |             | - Tach phong A305, A306     |
+-----------------------------+             +-----------------------------+
       |                                                           |
       +-----------------------------+-----------------------------+
                                     |
                                     v
                   +----------------------------------+
                   |       build_tkb_master.py        |
                   |  (Config Loader & Pre-Validator) |
                   +----------------------------------+
                                     |
                                     v
                   +----------------------------------+
                   |         MASTER WORKBOOK          |
                   | Sheet 1: Tieu hoc (35m)          |
                   | Sheet 2: THCS, THPT (45m)        |
                   | Sheet 3: BANG PHAN CONG (711)    |
                   | Sheet 4: TKB Giao vien (711)     |
                   +----------------------------------+
```

---

## 2. MA TRẬN KHUNG THỜI GIAN PHÂN CẤP (TIERED TIMEFRAMES)

Hệ thống MCA vận hành hai múi giờ tiết học độc lập cho hai khối học:

### 2.1. Cấp 1 (Tiểu học - 35 phút/tiết)
- **Buổi Sáng (5 tiết):**
  - `07:00 - 07:25`: Học sinh ăn sáng tại trường
  - `07:25 - 07:40`: Circle Time (Sinh hoạt đầu giờ)
  - `Tiết 1`: 07:40 - 08:15 (35 phút)
  - `Tiết 2`: 08:15 - 08:50 (35 phút)
  - `Tiết 3`: 08:50 - 09:25 (35 phút)
  - *Nghỉ giữa giờ - Uống nước, ăn hoa quả:* 09:25 - 09:45 (20 phút)
  - `Tiết 4`: 09:45 - 10:20 (35 phút)
  - `Tiết 5`: 10:20 - 10:55 (35 phút)
- **Khung Trưa:**
  - `10:55 - 13:30`: Ăn trưa, thiền, ngủ trưa và vệ sinh cá nhân
- **Buổi Chiều (5 tiết):**
  - `Tiết 6`: 13:35 - 14:10 (35 phút)
  - `Tiết 7`: 14:10 - 14:45 (35 phút)
  - *Nghỉ xế - Ăn chiều, uống sữa:* 14:45 - 15:15 (30 phút)
  - `Tiết 8`: 15:15 - 15:50 (35 phút)
  - `Tiết 9`: 15:50 - 16:20 (30-35 phút)
  - `Tiết 10`: 16:20 - 16:55 (35 phút)
- **Sau 17:00:** Hoạt động Câu lạc bộ ngoại khóa và đón trẻ.

### 2.2. Cấp 2 & Cấp 3 (THCS / THPT - 45 phút/tiết)
- **Buổi Sáng (5 tiết):**
  - `07:00 - 07:20`: Học sinh ăn sáng tại trường
  - `07:20 - 07:30`: Circle Time
  - `Tiết 1`: 07:30 - 08:15 (45 phút)
  - `Tiết 2`: 08:20 - 09:05 (45 phút)
  - `Tiết 3`: 09:10 - 09:55 (45 phút)
  - `Tiết 4`: 10:00 - 10:45 (45 phút)
  - `Tiết 5`: 10:50 - 11:35 (45 phút)
- **Khung Trưa:**
  - `11:35 - 13:20`: Ăn trưa và nghỉ trưa
- **Buổi Chiều (4 tiết chính khóa + 1 tiết bổ trợ độc lập):**
  - `Tiết 6`: 13:30 - 14:15 (45 phút)
  - `Tiết 7`: 14:20 - 15:05 (45 phút)
  - *Nghỉ giải lao phụ:* 15:05 - 15:20 (15 phút)
  - `Tiết 8`: 15:20 - 16:05 (45 phút)
  - `Tiết 9`: 16:10 - 16:55 (45 phút)
  - `Tiết 10 (Dòng bổ trợ độc lập)`: 17:00 - 17:45 (45 phút)
- **Sau 17:45:** Học sinh tan trường, sinh hoạt CLB và check out.

### 2.3. Bảng Kiểm Toán Giao Thoa Múi Giờ Tuyệt Đối (Minute-Level Clock Time)
Đối với các giáo viên dạy liên cấp (Cô Hồng, Cô Yên, Cô Phương Anh, Thầy Huy, Cô Giang, Cô Liên, Thầy Du, Thầy Nghĩa), toàn bộ lịch dạy được quy đổi ra số phút tuyệt đối tính từ 00:00. Kết quả kiểm toán tự động xác nhận **0 lỗi giao thoa múi giờ (0 overlap)** giữa tiết 35 phút của Tiểu học và 45 phút của THCS/THPT.

---

## 3. DANH BẠ VÀ PHÂN CÔNG CHUYÊN MÔN 43 GIÁO VIÊN

Dữ liệu được đối soát trực tiếp từ bảng phân công SmartSchool (`SS.2609041957335326.xlsx`) và xác thực hai chiều với Sheet 3 (BPCGD: 711 tiết) và Sheet 4 (TKB Giáo viên: 711 ô).

| STT | Mã GV | Danh xưng chuẩn | Tổ chuyên môn | Số tiết | Phân công chuyên môn chính thức & Lớp giảng dạy |
|:---:|---|---|---|:---:|---|
| 1 | **Liễu** | Cô Liễu *(GVCN 1A1)* | Tiểu học | 26 | Toán (1A1) + Tiếng Việt (1A1) + TN - XH (1A1) + HĐTN (1A1) + Bổ trợ Toán (1A1) + Bổ trợ T.Việt (1A1) |
| 2 | **Hạnh** | Cô Hạnh *(GVCN 1A2)* | Tiểu học | 26 | Toán (1A2) + Tiếng Việt (1A2) + Đạo đức (1A2) + TN - XH (1A2) + HĐTN (1A2) + Chào cờ (1A2) + Bổ trợ Toán (1A2) + Bổ trợ T.Việt (1A2) |
| 3 | **Tiểu Hà** | Cô Tiểu Hà *(GVCN 2A1)* | Tiểu học | 26 | Toán (2A1) + Tiếng Việt (2A1) + TN - XH (2A1) + HĐTN (2A1) + Bổ trợ Toán (2A1) + Bổ trợ T.Việt (2A1) |
| 4 | **Khánh Linh** | Cô Khánh Linh *(GVCN 2A2)* | Tiểu học | 23 | Toán (2A2) + Tiếng Việt (2A2) + Chào cờ (2A2) + Sinh hoạt lớp (2A2) + Bổ trợ Toán (2A2) + Bổ trợ T.Việt (2A2) |
| 5 | **Chín** | Cô Chín *(GVCN 3A1)* | Tiểu học | 26 | Toán (3A1) + Tiếng Việt (3A1) + TN - XH (3A1) + Chào cờ (3A1) + Sinh hoạt lớp (3A1) + Bổ trợ Toán (3A1) + Bổ trợ T.Việt (3A1) |
| 6 | **Chiến** | Thầy Chiến *(GVCN 3A2)* | Tiểu học | 26 | Toán (3A2) + Tiếng Việt (3A2) + Đạo đức (3A2) + TN - XH (3A2) + HĐTN (3A2) + Chào cờ (3A2) + Bổ trợ Toán (3A2) + Bổ trợ T.Việt (3A2) + Công nghệ (3A2) |
| 7 | **Hải** | Cô Hải *(GVCN 4A1)* | Tiểu học | 26 | Toán (4A1) + Tiếng Việt (4A1) + LS - ĐL (4A1) + Khoa học (4A1) + HĐTN (4A1) + Chào cờ (4A1) + Bổ trợ Toán (4A1) + Bổ trợ T.Việt (4A1) |
| 8 | **Hiền** | Cô Hiền *(GVCN 5A1)* | Tiểu học | 26 | Toán (5A1) + Tiếng Việt (5A1) + LS - ĐL (5A1) + Khoa học (5A1) + HĐTN (5A1) + Chào cờ (5A1) + Bổ trợ Toán (5A1) + Bổ trợ T.Việt (5A1) |
| 9 | **Chi** | Cô Chi | Tiểu học | 20 | Đạo đức (1A1, 2A1, 2A2, 3A1, 4A1, 5A1) + TN - XH (2A2) + HĐTN (2A2, 3A1) + Sinh hoạt lớp (1A2) + Bổ trợ Toán (4A1, 5A1) + Bổ trợ T.Việt (4A1, 5A1) + Công nghệ (3A1) |
| 10 | **Vũ Hà** | Cô Vũ Hà | Tiếng Anh Tiểu học | 16 | Maths (2A2) + Science (2A2) + Global English (2A2) + Bright Ideas (1A1, 2A1) + Global Success (1A1, 2A1) + Bổ trợ T.Anh (1A1, 2A1, 2A2) |
| 11 | **Hồng** | Cô Hồng | Tiếng Anh Liên cấp | 18 | Maths (1A2) + Science (1A2) + Global English (1A2) + Bright Ideas (5A1) + Global Success (5A1, 11A1) + Bổ trợ T.Anh (1A2, 5A1, 11A1) + Prepare (11A1) |
| 12 | **Nguyễn Linh** | Cô Nguyễn Linh | Tiếng Anh Tiểu học | 16 | Maths (3A2) + Science (3A2) + Global English (3A2) + Bright Ideas (3A1, 4A1) + Global Success (3A1, 4A1) + Bổ trợ T.Anh (3A1, 3A2, 4A1) |
| 13 | **Nghĩa** | Thầy Nghĩa | Nghệ thuật | 12 | Âm nhạc (1A1, 1A2, 2A1, 2A2, 3A1, 3A2, 4A1, 5A1, 6A1, 7A1, 8A1, 9A1) |
| 14 | **Lê** | Cô Lê | Nghệ thuật | 9 | Mỹ thuật (1A1, 1A2, 2A1, 2A2, 3A1, 3A2, 4A1, 5A1) + Sinh hoạt lớp (3A2) |
| 15 | **Yên** | Cô Yên *(GVCN 7A1/2)* | Tin học | 21 | Tin học (1A1, 1A2, 2A1, 2A2, 3A1, 3A2, 4A1, 5A1, 6A1, 7A1, 8A1, 9A1, 10A1, 11A1, 12A1/2) + HĐTN (7A1, 7A2) |
| 16 | **Thu** | Cô Thu | Thể chất | 17 | GDTC (1A1, 1A2, 2A1, 2A2, 3A1, 3A2, 4A1, 5A1) + Sinh hoạt lớp (4A1) |
| 17 | **Bình** | Thầy Bình | Nghệ thuật | 4 | Mỹ thuật (6A1, 7A1, 8A1, 9A1) |
| 18 | **Phương Anh** | Cô Phương Anh | Stem & Robotic | 12 | Stem & Robotic (1A1, 1A2, 5A1, 6A1, 7A1, 8A1, 9A1) + Chào cờ (1A1) + Sinh hoạt lớp (1A1) |
| 19 | **Ngọc** | Cô Ngọc | Stem & Robotic | 14 | Stem & Robotic (2A1, 2A2, 3A1, 3A2, 4A1) + Chào cờ (2A1) + Sinh hoạt lớp (2A1) + Công nghệ (4A1, 5A1) |
| 20 | **Liên** | Cô Liên | Thể chất & QPAN | 18 | GDTC (6A1, 7A1, 8A1, 9A1, 10A1, 11A1, 12A1/2) + GD QPAN (10A1, 11A1, 12A1/2) + Sinh hoạt lớp (5A1) |
| 21 | **Du** | Thầy Du | Ngữ văn & GDĐP | 17 | Ngữ văn chính khóa, BT Văn, Bồi giỏi Văn (10A1) + GDĐP (Toàn bộ Cấp 2 và Cấp 3: 6A1 đến 12A2) |
| 22 | **Quyến** | Cô Quyến | Toán học | 25 | Toán chính khóa, Bổ trợ Toán, Bồi giỏi Toán (6A1, 10A1, 11A1) |
| 23 | **Phương** | Cô Phương *(Tổ trưởng)* | Tiếng Anh | 7 | Global Success (10A1) + Prepare (10A1) + Bổ trợ TA / Bồi giỏi TA (10A1) |
| 24 | **Yến LS** | Cô Yến LS | Lịch sử | 8 | Lịch sử (10A1, 11A1, 12A1) + Lịch sử TC (12A2) + Lịch sử BT (12A2) |
| 25 | **Huy** | Thầy Huy *(GVCN 10A1)* | Vật lí | 19 | Vật lí (6A1, 7A1, 8A1, 9A1, 10A1, 11A1, 12A1/2) + Vật lí BT (12A1) + Công nghệ (8A1, 9A1) + TNHN (10A1) |
| 26 | **Thiết** | Cô Thiết | Địa lí | 11 | Địa lí (6A1, 7A1, 8A1, 9A1, 10A1, 12A2) + Địa lí BT (12A2) |
| 27 | **Thuỷ** | Cô Thuỷ | KT - PL | 6 | GD KT - PL (10A1, 12A2) + GD KT-PL BT (12A2) |
| 28 | **Thuý** | Cô Thuý *(Tổ trưởng, GVCN 12)* | Ngữ văn | 20 | Ngữ văn (11A1, 12A1, 12A2) + Văn CĐ (12A2) + Bổ trợ Văn (11A1) + TNHN (12A1, 12A2) |
| 29 | **Giang** | Cô Giang *(Tổ trưởng, GVCN 11)* | Sinh học | 14 | Sinh học (6A1, 7A1, 8A1, 9A1, 11A1, 12A1) + Sinh học BT (12A2) + Công nghệ (7A1) + TNHN (11A1) |
| 30 | **Nguyệt** | Cô Nguyệt *(GVCN 6A1)* | Hóa học | 17 | Hóa học (6A1, 7A1, 8A1, 9A1, 11A1, 12A1) + Hoá học BT (12A1) + Công nghệ (6A1) + HĐTN (6A1) |
| 31 | **Duy** | Thầy Duy *(BGH/Tổ trưởng)* | Toán học | 9 | Toán chính khóa (12A1, 12A2) |
| 32 | **Nhung** | Cô Nhung | Tiếng Anh | 11 | Global Success (9A1, 12A1, 12A2) + Prepare (9A1) + Global Success TC (12A1) |
| 33 | **Hương** | Cô Hương *(GVCN 9A1)* | Ngữ văn & GDCD | 17 | Ngữ văn (6A1, 9A1) + HĐTN (9A1) + GDCD (6A1, 9A1) |
| 34 | **Hoà** | Cô Hoà | Tiếng Anh | 19 | Global Success (6A1, 7A1, 7A2, 8A1, 8A2) + Prepare (6A1, 7A1, 7A2, 8A1, 8A2) |
| 35 | **Nga** | Cô Nga *(GVCN 8A1/2)* | Ngữ văn & GDCD | 17 | Ngữ văn (7A1, 8A1) + HĐTN (8A1, 8A2) + GDCD (7A1, 8A1) |
| 36 | **Huyền** | Cô Huyền | Toán học | 18 | Toán học (7A1, 7A2, 8A1, 8A2, 9A1) |
| 37 | **Nhung LS** | Cô Nhung LS | Lịch sử | 6 | Lịch sử (6A1, 7A1, 8A1, 9A1) |
| 38 | **Cybele** | GVNN Cô Cybele | Tiếng Anh | 13 | Bright Ideas (1A1) + Prepare (6A1, 8A1, 10A1) |
| 39 | **Catie** | GVNN Cô Catie | Tiếng Anh | 15 | Bright Ideas (3A1, 4A1, 5A1) + Prepare (7A1) |
| 40 | **Vincent** | GVNN Thầy Vincent | Toán & Khoa học TA | 18 | Maths (1A2, 2A2, 3A2) + Science (1A2, 2A2, 3A2) |
| 41 | **Mela** | GVNN Cô Mela | Tiếng Anh | 15 | Global English (2A2) + Bright Ideas (2A1) + Prepare (7A2) |
| 42 | **Charly** | GVNN Thầy Charly | Tiếng Anh | 12 | Prepare (9A1, 11A1) + Prepare BT (12A1) |
| 43 | **Saloni** | GVNN Cô Saloni | Tiếng Anh | 15 | Global English (1A2, 3A2) + Prepare (8A2) |
| | **TỔNG CỘNG** | | | **711** | **Khớp chính xác 100% Sheet 3 và Sheet 4** |

---

## 4. MA TRẬN 18 LỚP HỌC & ĐỊNH MỨC TIẾT

| STT | Lớp | Khối | Hệ đào tạo | Phòng học cơ sở | Số tiết/tuần | Đặc thù chương trình |
|:---:|:---:|:---:|:---:|:---:|:---:|---|
| 1 | 1A1 | Tiểu học | CLC | A101 | 45 | 5 tiết sáng + 4 tiết chiều P6-P9; Tiết 10 nghỉ/CLB |
| 2 | 1A2 | Tiểu học | Song ngữ | A102 | 50 | Kín 10 tiết/ngày x 5 ngày; Đồng giảng Vincent, Saloni |
| 3 | 2A1 | Tiểu học | CLC | A103 | 45 | 5 tiết sáng + 4 tiết chiều P6-P9; Tiết 10 nghỉ/CLB |
| 4 | 2A2 | Tiểu học | Song ngữ | A104 | 50 | Kín 10 tiết/ngày x 5 ngày; Đồng giảng Vincent, Mela |
| 5 | 3A1 | Tiểu học | CLC | A105 | 45 | 5 tiết sáng + 4 tiết chiều P6-P9; Tiết 10 nghỉ/CLB |
| 6 | 3A2 | Tiểu học | Song ngữ | A106 | 50 | Kín 10 tiết/ngày x 5 ngày; Đồng giảng Vincent, Saloni |
| 7 | 4A1 | Tiểu học | CLC | A205 | 45 | Bổ trợ Toán & TV cuối chiều có cô Chi trợ giảng |
| 8 | 5A1 | Tiểu học | CLC | A206 | 45 | Thứ 4 P5 Tin học - Yên, P6 Bright Ideas - Hồng |
| 9 | 6A1 | THCS | Chuẩn | B305 | 39 | Học chính khóa; Chiều kết thúc tại Tiết 8 hoặc 9 |
| 10 | 7A1 | THCS | Chuẩn | B304 | 39 | Ghép chung với 7A2; Tách môn Prepare tại A306 |
| 11 | 7A2 | THCS | Tăng cường | B304 | 44 | Học nhiều hơn 7A1 5 tiết Tiếng Anh (Prepare) buổi chiều |
| 12 | 8A1 | THCS | Chuẩn | B303 | 39 | Ghép chung với 8A2; Tách môn Prepare tại A306 |
| 13 | 8A2 | THCS | Tăng cường | B303 | 44 | Học nhiều hơn 8A1 5 tiết Tiếng Anh (Prepare) buổi chiều |
| 14 | 9A1 | THCS | Nâng cao | B302 | 44 | Khóa cuối cấp THCS; Học tăng cường Tiếng Anh |
| 15 | 10A1 | THPT | Nâng cao | B301 | 47 | Bổ sung 3 tiết BT/BG; Học Tiết 10 Thứ 2 và Thứ 3 (17:00-17:45) |
| 16 | 11A1 | THPT | Nâng cao | B206 | 45 | Bổ sung 3 tiết bổ trợ (Toán - Quyến, Văn - Thuý, TA - Hồng) |
| 17 | 12A1 | THPT | Phân ban TN | B205 | 45 | 33 tiết ghép chung tại B205 + 12 tiết Ban Tự nhiên tại A305 |
| 18 | 12A2 | THPT | Phân ban XH | B205 | 45 | 33 tiết ghép chung tại B205 + 12 tiết Ban Xã hội tại B205 |
| | **TỔNG LƯỢT TIẾT LỚP** | | | | **806** | |

---

## 5. CƠ CHẾ TÁCH / GHÉP LỚP CHUYÊN SÂU

### 5.1. Khối 12: Ma Trận Đối Ngẫu 1-1 Phân Ban Bắt Buộc (Paired Elective Invariant)
Lớp 12A1 và 12A2 cùng đặt tại phòng sinh hoạt chung **B205**.
- **Tiết ghép lớp (33 tiết):** Toán học (Thầy Duy - 9 tiết), Ngữ văn (Cô Thuý - 7 tiết), GDTC & GDQPAN (Cô Liên - 4 tiết), Tin học (Cô Yên - 2 tiết), GDĐP (Thầy Du - 2 tiết), Global Success (Cô Nhung - 5 tiết), Vật lí (Thầy Huy - 2 tiết), Lịch sử (Cô Yến LS - 2 tiết).
- **Tiết tách lớp phân ban (12 tiết):** 12A1 (Ban Tự nhiên) di chuyển sang phòng chuyên môn **A305**, 12A2 (Ban Xã hội) học tại phòng **B205**. Toàn bộ 12 cặp tiết phải khớp đúng 100%:

| Cặp | Thứ | Tiết | Khung giờ | 12A1 (Ban Tự nhiên - Phòng A305) | 12A2 (Ban Xã hội - Phòng B205) | Logic Nghiệp Vụ Đối Ứng |
|:---:|:---:|:---:|:---:|---|---|---|
| **1** | Thứ 2 | P3 | 09:10 - 09:55 | **Hóa học** - Cô Nguyệt | **Địa lí** - Cô Thiết | Tự nhiên (Hóa) đối ứng Xã hội (Địa) |
| **2** | Thứ 2 | P4 | 10:00 - 10:45 | **Hóa học** - Cô Nguyệt | **Địa lí** - Cô Thiết | Tự nhiên (Hóa) đối ứng Xã hội (Địa) |
| **3** | Thứ 2 | P9 | 16:10 - 16:55 | **Global Success TC** - Cô Nhung | **Lịch sử TC** - Cô Yến LS | Tiếng Anh TC đối ứng Lịch sử TC |
| **4** | Thứ 2 | P10 | 17:00 - 17:45 | **Global Success TC** - Cô Nhung | **Lịch sử TC** - Cô Yến LS | Tiếng Anh TC đối ứng Lịch sử TC |
| **5** | Thứ 3 | P3 | 09:10 - 09:55 | **Sinh học** - Cô Giang | **Văn Chuyên đề** - Cô Thuý | Tự nhiên (Sinh) đối ứng Xã hội (Văn CĐ) |
| **6** | Thứ 3 | P9 | 16:10 - 16:55 | **Vật lí BT** - Thầy Huy | **Lịch sử BT** - Cô Yến LS | Bổ trợ Lí đối ứng Bổ trợ Sử |
| **7** | Thứ 4 | P1 | 07:30 - 08:15 | **Sinh học** - Cô Giang | **GD KT - PL** - Cô Thuỷ | Tự nhiên (Sinh) đối ứng Xã hội (KT-PL) |
| **8** | Thứ 4 | P2 | 08:20 - 09:05 | **Hóa học** - Cô Nguyệt | **GD KT - PL** - Cô Thuỷ | Tự nhiên (Hóa) đối ứng Xã hội (KT-PL) |
| **9** | Thứ 5 | P7 | 14:20 - 15:05 | **Hoá học BT** - Cô Nguyệt | **GD KT-PL BT** - Cô Thuỷ | Bổ trợ Hóa đối ứng Bổ trợ KT-PL |
| **10** | Thứ 5 | P8 | 15:20 - 16:05 | **Hoá học BT** - Cô Nguyệt | **GD KT-PL BT** - Cô Thuỷ | Bổ trợ Hóa đối ứng Bổ trợ KT-PL |
| **11** | Thứ 5 | P9 | 16:10 - 16:55 | **Prepare BT** - GVNN Thầy Charly | **Địa lí BT** - Cô Thiết | Tiếng Anh BT đối ứng Bổ trợ Địa |
| **12** | Thứ 6 | P9 | 16:10 - 16:55 | **Prepare BT** - GVNN Thầy Charly | **Sinh học BT** - Cô Giang | Tiếng Anh BT đối ứng Bổ trợ Sinh |

### 5.2. Khối 7 & Khối 8: Tách Môn Prepare Sang Phòng Máy A306
- **Khối 7 (7A1 - 7A2):** Ghép 35 tiết tại phòng B304. Môn Tiếng Anh `Prepare` tách lớp:
  - 7A1 di chuyển sang phòng **A306** học với Cô Catie và Cô Hoà.
  - 7A2 học tại lớp chính với Cô Mela và Cô Hoà.
  - 7A2 học thêm 5 tiết Tiếng Anh buổi chiều (Thứ 3 P8-P9, Thứ 4 P9, Thứ 5 P9, Thứ 6 P9).
- **Khối 8 (8A1 - 8A2):** Ghép 35 tiết tại phòng B303. Môn Tiếng Anh `Prepare` tách lớp:
  - 8A1 di chuyển sang phòng **A306** học với Cô Cybele và Cô Hoà.
  - 8A2 học tại lớp chính với Cô Saloni và Cô Hoà.
  - 8A2 học thêm 5 tiết Tiếng Anh buổi chiều (Thứ 3 P9, Thứ 4 P9, Thứ 5 P8-P9, Thứ 6 P9).

### 5.3. Tiểu Học: Cơ Chế Đồng Giảng (Co-teaching) 8 Tiết
Hệ thống bố trí Cô Chi làm giáo viên trợ giảng đồng thời cùng GVCN tại hai lớp 4A1 và 5A1 vào khung giờ Bổ trợ cuối chiều:
1. **Thứ 2 Chiều P3 (Tiết 8):** Lớp 4A1 — Cô Hải & Cô Chi dạy Bổ trợ T.Việt
2. **Thứ 2 Chiều P4 (Tiết 9):** Lớp 4A1 — Cô Hải & Cô Chi dạy Bổ trợ T.Việt
3. **Thứ 3 Chiều P3 (Tiết 8):** Lớp 5A1 — Cô Hiền & Cô Chi dạy Bổ trợ T.Việt
4. **Thứ 3 Chiều P4 (Tiết 9):** Lớp 5A1 — Cô Hiền & Cô Chi dạy Bổ trợ T.Việt
5. **Thứ 4 Chiều P3 (Tiết 8):** Lớp 4A1 — Cô Hải & Cô Chi dạy Bổ trợ Toán
6. **Thứ 4 Chiều P4 (Tiết 9):** Lớp 4A1 — Cô Hải & Cô Chi dạy Bổ trợ Toán
7. **Thứ 5 Chiều P3 (Tiết 8):** Lớp 5A1 — Cô Hiền & Cô Chi dạy Bổ trợ Toán
8. **Thứ 5 Chiều P4 (Tiết 9):** Lớp 5A1 — Cô Hiền & Cô Chi dạy Bổ trợ Toán

---

## 6. CÁC QUY TẮC BẤT BIẾN (INVARIANTS & HARD CONSTRAINTS)

1. **Ràng buộc Họp Chuyên Môn Chiều Thứ 6 (SHCM GVCN Cấp 1):**
   Toàn bộ 8 giáo viên chủ nhiệm Tiểu học (Liễu, Hạnh, Tiểu Hà, Khánh Linh, Chín, Chiến, Hải, Hiền) BẮT BUỘC trống toàn bộ lịch dạy buổi chiều Thứ 6 (từ Tiết 6 đến Tiết 10) để tham gia sinh hoạt chuyên môn khối. Lịch chiều Thứ 6 của học sinh được giao cho các giáo viên chuyên biệt đảm nhiệm (Cô Lê, Thầy Nghĩa, Cô Phương Anh, Cô Ngọc, Cô Vũ Hà, Thầy Vincent, Cô Hồng).
2. **Ràng buộc Khóa Lịch Sáng Thứ 2 (BGH & Tổ Trưởng):**
   Thầy Duy (BGH), Cô Giang (Tổ trưởng Tự nhiên), Cô Phương (Tổ trưởng Ngoại ngữ), Cô Thuý (Tổ trưởng Xã hội) không xếp lịch giảng dạy vào sáng Thứ 2 để phục vụ họp giao ban trường.
3. **Bảo tồn Tiết Học Đã Điều Chỉnh:**
   - Lớp 5A1 Thứ 4: P5 Tin học (Cô Yên), P6 Bright Ideas (Cô Hồng).
   - Lớp 10A1: 47 tiết (gồm 2 tiết T10 Thứ 2 và Thứ 3: 17:00 - 17:45).
   - Lớp 11A1: 45 tiết.
   - Master Workbook duy nhất: `New folder/TKB_Marie_Curie_2026-2027(update_05_09).xlsx`.
