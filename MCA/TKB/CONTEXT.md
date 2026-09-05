# CONTEXT.md - TKB (Thời Khóa Biểu Khối Tiểu Học & THCS-THPT 2026-2027)

## Domain Language (Thuật ngữ Nhà trường)

| Term | Meaning | Source/Owner | Notes |
| --- | --- | --- | --- |
| **Hệ CLC** | Hệ Chất lượng cao (45 tiết/tuần) | File DOCX/XLSX | Lớp 1A1, 2A1, 3A1, 4A1, 5A1 |
| **Hệ Song ngữ** | Hệ Song ngữ (48 tiết/tuần) | File DOCX/XLSX | Lớp 1A2, 2A2, 3A2 |
| **BG+BT** | Bồi giỏi + Bổ trợ kiến thức | Bảng Phân công | 2 tiết Toán + 2 tiết Tiếng Việt cho Khối 1, 2, 3 |
| **SHCM** | Sinh hoạt chuyên môn GVCN | Quy định nhà trường | Toàn bộ GVCN trống lịch Chiều Thứ 6 |
| **Đồng dạy (Co-teaching)** | 2 GV (GV nước ngoài + Trợ giảng) dạy cùng lúc tại 1 lớp | Quy chế song ngữ | Cần khóa biến thời gian `Linked Interval Variables` |
| **Khóa Khung (Slot Lock)** | Các tiết BG+BT của 2 lớp cùng khối phải xếp trùng khung giờ | File DOCX | Ví dụ: BG Toán 1A1 trùng giờ BG Toán 1A2 |
| **Tiết Kép (Double Period)** | 2 tiết liền nhau của cùng 1 môn trong 1 buổi | Quy tắc tối ưu | Áp dụng cho các môn có dung lượng lớn (TA, TV, Toán) |
| **Nhóm GDTC** | Phân nhóm Thể dục học Thứ 3+5 (Nhóm 1) hoặc Thứ 4+6 (Nhóm 2) | File DOCX P[8] | Dùng để phân bố đều lịch của GV Thể dục cô Thu |
| **Khung 15h45-17h00** | 2 Tiết cuối buổi học (tiết 8, 9) dành cho BG+BT của Khối 4, 5 | File DOCX P[5] | Khóa khung giờ cuối chiều |
| **CLB 17h** | Tiết câu lạc bộ ngoại khóa sau giờ học chính thức | File DOCX P[10] | Xếp sau 17h, có thể thuộc tiết 10 (nếu đưa vào lưới) |
| **PA1 Sheet** | Sheet chứa ma trận phân công giảng dạy chuẩn (được làm sạch) | File XLSX mới | Bỏ qua dòng rác từ Row 244-3552 |

## Core Architecture & Modeling Concepts (CP-SAT)

| Concept | Description | Implementation Pattern |
| --- | --- | --- |
| **Boolean Assignment Variable** | `X[a_idx, d, t]` = 1 nếu phân công `a_idx` được giảng dạy vào ngày `d` tiết `t` | `model.NewBoolVar(f"X_{a_idx}_{d}_{t}")` |
| **Hard Constraint: Class Capacity** | Mỗi lớp học tối đa 1 tiết tại 1 thời điểm | `model.Add(sum(X[a_idx, d, t] for a_idx with class c) <= 1)` |
| **Hard Constraint: Period Count** | Tổng số tiết của phân công bằng định mức được giao | `model.Add(sum(X[a_idx, d, t] for d, t) == a["periods"])` |
| **Hard Constraint: Teacher Clash** | Mỗi giáo viên dạy tối đa 1 tiết tại 1 thời điểm (trừ các tiết ghép lớp) | Grouped by `(subject, division)` with `AddMaxEquality` |
| **Hard Constraint: Class Synchronization** | Ghép lớp cho các tiết học chung THCS/THPT | `model.Add(X[a1_idx, d, t] == X[a2_idx, d, t])` |
| **Soft Constraint: No Idle Gaps** | Hạn chế tiết trống lửng của giáo viên trong ngày | Minimize `sum(gap_var)` |
| **Soft Constraint: Adjacency** | Khuyến khích xếp liền nhau nếu môn học có >= 2 tiết/buổi | Maximize `sum(adj_pairs)` |

## Release Timetable & Advanced Constraints (Update 2026-07-16)

- **Official Release Path:** [release/TKB_Marie_Curie_Tieu_Hoc_2026_2027.xlsx](file:///E:/Antigravity/MCA/TKB/release/TKB_Marie_Curie_Tieu_Hoc_2026_2027.xlsx)
- **Advanced Constraints Integrated:**
  1. **GDTC (Thể dục):** Chỉ được xếp vào Tiết 1, 2, 3 Sáng (`t0, t1, t2`) hoặc Tiết 4, 5 Chiều (`t8, t9`). Phân nhóm GDTC: GROUP 1 = `1A2, 2A1, 3A1, 4A1` (Thứ 3/5), GROUP 2 = `1A1, 2A2, 3A2, 5A1` (Thứ 4/6).
  2. **Không học 3 tiết/buổi:** Khóa số tiết tối đa của một môn học đối với 1 lớp trong cùng 1 buổi là 2 (riêng Tiếng Việt tối đa 3 tiết buổi sáng).
  3. **Phân bổ đều BG+BT hàng ngày:** BG+BT Toán/TV Khối 1-5 được chia đều mỗi ngày 1 tiết cuối chiều tại Tiết 9 (`t8`) từ Thứ 2 đến Thứ 5.
  4. **Học ghép lớp Khối 1-3:** Các lớp cùng khối song hành (`A1` và `A2`) được ghép trùng ngày và giờ học BG+BT Toán/TV.
  5. **Xếp liền nhau (Adjacency):** Chuyển sang dạng tối ưu hóa (soft constraint) để tránh vỡ lịch đối với các lớp Song ngữ do trùng với các tiết khóa khung BG+BT.
  6. **Cấm học dồn 3 tiết liền:** Cấm tuyệt đối xếp 3 tiết của cùng một môn học liên tiếp nhau.
  7. **Tiết kép Stem:** Bắt buộc xếp liền nhau thành tiết kép cho toàn bộ các lớp có 2 tiết Stem (cả CLC và Song ngữ).
- **THCS/THPT Integration:**
  - Lớp học: `6A1`, `7A1`, `7A2`, `8A1`, `8A2`, `9A2`, `10A1`, `11A1`, `12A1`.
  - Khóa Tiết 10 cho toàn bộ các lớp ngoại trừ `12A1` (do định mức lớn 46 tiết/tuần).
  - Tự động đồng bộ hóa các môn học chung (ngoại trừ Tiếng Anh) giữa `7A1-7A2` và `8A1-8A2`.
  - Tự động xếp TNHN tại Sáng Thứ 2 Tiết 1 cho toàn bộ các lớp THCS/THPT.
- **Verification Commands:**
  - `python verify_release_tkb.py` (PASS with success summary).
  - `Invoke-ProjectOperatingGate.ps1 -ProjectRoot "E:\Antigravity\MCA\TKB" -Mode final` (PASS with Delivery score = 100).

## Master Timetable Release (Update 05/09/2026)

- **Target Output Path:** [New folder/TKB_Marie_Curie_2026-2027(update_05_09).xlsx](file:///E:/Antigravity/MCA/TKB/New%20folder/TKB_Marie_Curie_2026-2027(update_05_09).xlsx)
- **Source Data (SmartSchool exports):**
  1. `SS.2609041957335326.xlsx`: Bảng phân công giảng dạy (43 giáo viên, 700 tiết gốc + 11 tiết Bổ trợ/Bồi giỏi = 711 tiết).
  2. `SS.2609041958140418.xlsx`: Thời khóa biểu toàn trường theo lớp (18 lớp: 8 lớp Tiểu học 1A1-5A1, 10 lớp THCS/THPT 6A1-12A2).
  3. `SS.2609041958293729.xlsx`: Thời khóa biểu toàn trường theo giáo viên (43 giáo viên).
- **Template Reference:** [New folder/mẫu/TKB_Marie_Curie_2026-2027(update_06_08).xlsx](file:///E:/Antigravity/MCA/TKB/New%20folder/m%E1%BA%ABu/TKB_Marie_Curie_2026-2027(update_06_08).xlsx)
- **Standardization & Architecture Details:**
  1. **Sheet 1 `Tiểu học` (83 rows, 11 cols):** Lớp 1A1-5A1, giữ nguyên các khung hoạt động cố định (ăn sáng, Circle time, ăn trưa, ra chơi, sinh hoạt CLB), chuẩn hóa tên môn (`Toán học`, `Stem & Robotic`, `(BT)`). Cập nhật Thứ 4 lớp 5A1: P5 = Tin học - Yên, P6 = Bright Ideas - Hồng.
  2. **Sheet 2 `THCS, THPT` (82 rows, 13 cols):** Lớp 6A1-12A2, kế thừa lớp ghép (`7A1-7A2`, `8A1-8A2`, `12A1-12A2`) khi học chung phòng học và tách môn khi học phòng chuyên môn (`A305`, `A306`). Bổ sung dòng riêng cho Tiết 10 mỗi ngày (thời lượng 45 phút, 17:00 - 17:45). Cập nhật đầy đủ các tiết: 10A1 (47 tiết, gồm T10 Thứ 2 và Thứ 3), 11A1 (45 tiết), 12A1/12A2 (T10 Thứ 2). Khung 17:45 chuyển cho hoạt động check out / sinh hoạt CLB.
  3. **Sheet 3 `BẢNG PHÂN CÔNG GIẢNG DẠY` (48 rows, 6 cols):** 43 giáo viên, row 48 `TỔNG CỘNG` = 711 tiết. Cập nhật phân công chi tiết cho Hồng (18), Du (17), Quyến (25), Phương (7), Thuý (20).
  4. **Sheet 4 `TKB Giáo viên` (54 rows, 46 cols):** 43 cột giáo viên (Liễu -> Saloni), gắn nhãn phòng `(B205)` cho 12A1/12A2, `(B206)` cho 11A1, phòng chuyên môn `(A305)` và `(A306)` cho tiết thực hành, ghép lịch đa lớp khi dạy chung. Toàn bộ 43 giáo viên khớp 100% với Sheet 3 (0 sai lệch).
- **Generator Script:** `E:\Antigravity\MCA\TKB\build_tkb_master.py` (Hoàn toàn điều khiển bằng cấu hình - Config-driven engine).

## Declarative Framework & Configuration Kit (Update 2026-09-05)

- **Architecture Spec:** [TKB_ARCHITECTURE_SPEC.md](file:///E:/Antigravity/MCA/TKB/TKB_ARCHITECTURE_SPEC.md)
  - Phân tích cặn kẽ 100% nguyên lý xếp TKB:
    1. Ma trận khung giờ chênh lệch: Cấp 1 (35 phút/tiết, 5 sáng + 5 chiều) vs Cấp 2/3 (45 phút/tiết, 5 sáng + 4 chiều + Tiết 10 độc lập từ 17:00-17:45).
    2. Cơ chế Tách/Ghép lớp: Khối 7 và 8 tách môn `Prepare` sang phòng máy `A306`; Khối 12 tại `B205` ghép môn cơ bản và tách môn tự chọn Tự nhiên (`A305`) vs Xã hội (`B205`) theo nguyên lý đối ngẫu 1-1 (12 cặp đối ứng bắt buộc).
    3. Kiểm toán 43 giáo viên, 8 tiết đồng giảng Tiểu học, ràng buộc SHCM chiều Thứ 6 của 8 GVCN Tiểu học, khóa sáng Thứ 2 của Thầy Duy.
- **Declarative Configuration Kit:**
  1. [config/timetable_rules.json](file:///E:/Antigravity/MCA/TKB/config/timetable_rules.json): Định nghĩa khung giờ, 18 lớp học, phòng chuyên môn (`A305`, `A306`, `Stem`), các cặp ghép lớp kèm danh sách 12 cặp đối ứng tự chọn Lớp 12, và các điều chỉnh đặc thù (5A1 Thứ 4, 10A1, 11A1).
  2. [config/teacher_registry.json](file:///E:/Antigravity/MCA/TKB/config/teacher_registry.json): Danh bạ 43 giáo viên chuẩn hóa với tổ bộ môn, định mức gốc, số tiết bổ trợ, tổng 711 tiết và chuỗi phân công chính thức của Sheet 3.
- **Workflow bảo trì thời khóa biểu tương lai:**
  - Người dùng thay đổi thông tin giáo viên, phòng học, hoặc phân công: **Chỉ cần chỉnh sửa trực tiếp file JSON trong `config/`**.
  - Chạy `python -X utf8 E:\Antigravity\MCA\TKB\build_tkb_master.py` để tự động kiểm toán toàn vẹn và tạo lại Master Workbook ngay lập tức mà không cần can thiệp mã nguồn.

## Standard Excel Input Template & 25-Constraint Framework (Update 2026-09-05 - Current)

- **Pedagogical Constraint Encyclopaedia:** [TKB_MCA_CONSTRAINT_CATALOGUE.md](file:///E:/Antigravity/MCA/TKB/TKB_MCA_CONSTRAINT_CATALOGUE.md) (21.171 bytes)
  - 10 chương quy chuẩn mã hóa toàn diện 25 quy tắc sư phạm của trường Marie Curie:
    1. Chào cờ Tiết 1 sáng Thứ 2 (18 lớp).
    2. SHL C1 và HĐTN C2/C3 Tiết 5 sáng Thứ 6.
    3. GVCN C1 dạy liền khối, môn giống nhau cạnh nhau, nghỉ chiều T6 (SHCM) + 1 buổi tự chọn khác (trừ sáng T2); có mục điền môn khác.
    4. GVNN dồn >= 2 tiết/buổi (ưu tiên 3-4 tiết); Cô Catie chỉ dạy buổi sáng.
    5. Tiết Bổ trợ (BT) xếp cuối chiều.
    6. GDTC cách ngày (T3+T5 hoặc T4+T6), tránh trưa nắng, ưu tiên sáng sớm hoặc cuối chiều.
    7. Stem & Robotic C1 xếp 2 tiết kép (cặp 2-3, 6-7, 8-9).
    8. Phân bổ môn đều cả tuần.
    9. Quản lý lệch múi giờ C1 (35m) vs C2/3 (45m), chặn xung đột thời gian thực C1 P4 (9:45-10:20) vs C2/3 P3 (9:10-9:55) cho GV liên cấp (Yên, Phương Anh).
    10. Bổ trợ C1 giữ 2 tiết cuối chiều.
    11. GVCN C1 dạy >= 3 tiết/buổi sáng để quản lý lớp.
    12. Danh bạ 8 GVCN C1 (Liễu, Hạnh, Tiểu Hà, Khánh Linh, Chín, Chiến, Hải, Hiền).
    13. HĐTN C2/C3: P1 sáng T2, P5 sáng T6, 1 tiết cuối chiều linh hoạt.
    14. Stem C2 & Nhiệm vụ ăn bán trú C1: Tránh P5 sáng và P7 chiều cho Phó Chủ nhiệm C1 (ăn trưa 11:00, ăn chiều 14:45).
    15. Danh bạ 8 Phó Chủ nhiệm C1 (Phương Anh, Chi, Ngọc, Lê, Lam, Thu, Liên).
    16. Cô Quyến (Toán) nghỉ trọn vẹn Thứ 4.
    17. Khối 7 & 8: Global Success học chung; Prepare tách phòng A306 (CLC 4 tiết) và 5 tiết Song ngữ ở cuối chiều.
    18. GVNN dồn lịch tập trung.
    19. Toán & Văn THCS/THPT: Cặp 2 tiết kép (90 phút) để kiểm tra định kỳ.
    20. Tiếng Anh & các môn THCS phân bổ đều.
    21. Họp 3 Tổ chuyên môn (Tự nhiên, Xã hội, Tiếng Anh): Bố trí tiết trống chung.
    22. Bổ trợ Khối 12: Giữ đúng vị trí 12 cặp đối ứng theo master hiện tại.
    23. Khóa cứng lịch GV Thỉnh giảng: Quyến (nghỉ T4), Thủy (sáng T4 + T5), Thiết (sáng T2 + T5), Yến LS (các tiết chỉ định), Duy (nghỉ sáng T2).
    24 & 25. Các điểm làm rõ từ Nhà trường: Giờ họp tổ bất kỳ tiết nào trống; Ma trận Khối 12 giữ nguyên đối ứng 1-1; Nghỉ GVCN buổi bất kỳ; Môn khác GVCN lấy trực tiếp từ TKB.

- **Standard Excel Input Template Workbook:** [TEMPLATE_NHAP_LIEU_TKB_MCA.xlsx](file:///E:/Antigravity/MCA/TKB/TEMPLATE_NHAP_LIEU_TKB_MCA.xlsx) (30.865 bytes)
  - Sheet 1: `HUONG_DAN_SU_DUNG` (Quy trình 3 bước, mã màu chuẩn Marie Curie).
  - Sheet 2: `BANG_QUY_TAC_RANG_BUOC` (Bách khoa 25 quy tắc và ma trận 12 cặp lớp 12).
  - Sheet 3: `KHAI_BAO_GIAO_VIEN` (43 GV, công thức tính tổng tự động, mục ghi chú ràng buộc).
  - Sheet 4: `KHAI_BAO_LOP_HOC` (18 lớp học, phòng cơ sở, định mức tiết, GVCN và Phó CN).
  - Sheet 5: `PHAN_CONG_GIANG_DAY` (Ma trận môn học theo lớp, GV chính, trợ giảng, môn khác của GVCN).
  - Sheet 6: `TACH_GHEP_LOP` (Cấu hình ghép lớp văn hóa và ma trận 12 cặp đối ứng phân ban 12).
  - Sheet 7: `LUOI_THOI_KHOA_BIEU_MAU` (Khung lưới TKB mẫu kèm Tiết 10 độc lập).
  - Generator: `E:\Antigravity\MCA\TKB\generate_excel_template.py`.

- **Template Loader & Deep Audit Engine:** [loader_template.py](file:///E:/Antigravity/MCA/TKB/loader_template.py)
  - Tự động nạp dữ liệu từ `TEMPLATE_NHAP_LIEU_TKB_MCA.xlsx`.
  - Thực hiện 4 bài kiểm toán sâu (Toán học 711 tiết, Khóa lịch GV thỉnh giảng, Đối ngẫu 12 cặp Lớp 12, Lệch múi giờ C1/C2).
  - Tự động đồng bộ ngược lại vào `config/teacher_registry.json` và `config/timetable_rules.json`.
  - Đạt 100% PASS (0 Errors, 0 Warnings).


