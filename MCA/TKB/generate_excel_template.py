"""
========================================================================================
GENERATE STANDARDIZED EXCEL TEMPLATE WORKBOOK FOR MCA TIMETABLE INPUT
Marie Curie Academy (MCA) - Academic Year 2026-2027
========================================================================================
Generates: `TEMPLATE_NHAP_LIEU_TKB_MCA.xlsx` with 7 production-grade sheets:
1. HUONG_DAN_SU_DUNG
2. BANG_QUY_TAC_RANG_BUOC (Codifying all 25 user rules)
3. KHAI_BAO_GIAO_VIEN (43 teachers + visiting teachers + formulas)
4. KHAI_BAO_LOP_HOC (18 classes + 8 GVCN + 8 Phó CN)
5. PHAN_CONG_GIANG_DAY (Matrix assignment with extra GVCN subjects)
6. TACH_GHEP_LOP (Split/merge pairs + Grade 12 12-pair elective matrix)
7. LUOI_THOI_KHOA_BIEU_MAU (Master timetable grid with Period 10 row)
========================================================================================
"""

import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
out_file = os.path.join(PROJECT_ROOT, "TEMPLATE_NHAP_LIEU_TKB_MCA.xlsx")

print("==========================================================================")
print("BUILDING STANDARDIZED EXCEL INPUT TEMPLATE FOR MCA TIMETABLE")
print(f"Target: {out_file}")
print("==========================================================================\n")

wb = openpyxl.Workbook()
# Remove default sheet
wb.remove(wb.active)

# --- STYLES ---
font_title = Font(name="Times New Roman", size=15, bold=True, color="1B365D")
font_subtitle = Font(name="Times New Roman", size=11, italic=True, color="555555")
font_section = Font(name="Times New Roman", size=12, bold=True, color="1B365D")
font_header = Font(name="Times New Roman", size=11, bold=True, color="FFFFFF")
font_bold = Font(name="Times New Roman", size=11, bold=True, color="000000")
font_regular = Font(name="Times New Roman", size=11, color="000000")
font_note = Font(name="Times New Roman", size=10, italic=True, color="333333")

fill_header = PatternFill(fill_type="solid", start_color="1B365D", end_color="1B365D") # Marie Curie Navy
fill_subheader = PatternFill(fill_type="solid", start_color="2C4D75", end_color="2C4D75")
fill_input = PatternFill(fill_type="solid", start_color="FFF2CC", end_color="FFF2CC") # Light yellow for user input
fill_calc = PatternFill(fill_type="solid", start_color="D9E1F2", end_color="D9E1F2") # Soft blue for formulas
fill_locked = PatternFill(fill_type="solid", start_color="F2F2F2", end_color="F2F2F2") # Gray
fill_highlight = PatternFill(fill_type="solid", start_color="FCE4D6", end_color="FCE4D6") # Soft orange

thin_side = Side(border_style="thin", color="D9D9D9")
dark_side = Side(border_style="thin", color="000000")
med_side = Side(border_style="medium", color="1B365D")
double_side = Side(border_style="double", color="000000")

border_cell = Border(left=thin_side, right=thin_side, top=thin_side, bottom=thin_side)
border_header = Border(left=thin_side, right=thin_side, top=med_side, bottom=med_side)
border_total = Border(left=thin_side, right=thin_side, top=dark_side, bottom=double_side)

align_center = Alignment(horizontal="center", vertical="center", wrap_text=True)
align_left = Alignment(horizontal="left", vertical="center", wrap_text=True)
align_right = Alignment(horizontal="right", vertical="center", wrap_text=True)

# Load existing JSON config if available to pre-fill realistic data
rules_path = os.path.join(PROJECT_ROOT, "config", "timetable_rules.json")
teachers_path = os.path.join(PROJECT_ROOT, "config", "teacher_registry.json")

with open(rules_path, "r", encoding="utf-8") as f:
    rules_data = json.load(f)
with open(teachers_path, "r", encoding="utf-8") as f:
    teachers_data = json.load(f)

# ==============================================================================
# SHEET 1: HUONG_DAN_SU_DUNG
# ==============================================================================
ws1 = wb.create_sheet(title="HUONG_DAN_SU_DUNG")
ws1.views.sheetView[0].showGridLines = True

ws1.cell(2, 2, value="BỘ TEMPLATE NHẬP LIỆU & ĐIỀU CHỈNH THỜI KHÓA BIỂU MARIE CURIE ACADEMY").font = font_title
ws1.cell(3, 2, value="Áp dụng từ năm học 2026 - 2027 | Quy chuẩn chuẩn hóa dữ liệu 100% tự động").font = font_subtitle

instructions = [
    ("1. MỤC ĐÍCH SỬ DỤNG", [
        "File Excel này là khuôn mẫu chuẩn hóa (Standard Template) duy nhất để Ban Giám Hiệu, Tổ trưởng chuyên môn và Cán bộ phụ trách TKB nhập liệu.",
        "Mọi thông tin về giáo viên, phân công môn học, quy tắc tách ghép lớp và ràng buộc cá nhân được điền trực tiếp vào đây.",
        "Sau khi hoàn thành, hệ thống tự động đọc dữ liệu từ file này để kiểm toán xung đột và xuất Master Workbook trong 2 giây."
    ]),
    ("2. CẤU TRÚC 7 SHEETS NGHIỆP VỤ", [
        "Sheet 1 - HUONG_DAN_SU_DUNG: Tài liệu hướng dẫn thao tác và quy ước mã màu chuẩn.",
        "Sheet 2 - BANG_QUY_TAC_RANG_BUOC: Bách khoa 25 quy tắc sư phạm MCA (Khung giờ, SHCM, Stem, Thể dục, GVNN, 12 cặp đối ứng Lớp 12...).",
        "Sheet 3 - KHAI_BAO_GIAO_VIEN: Danh bạ 43 giáo viên cơ hữu và giáo viên thỉnh giảng kèm định mức tiết và lịch đăng ký nghỉ.",
        "Sheet 4 - KHAI_BAO_LOP_HOC: Khai báo 18 lớp học, phòng cơ sở, 8 Giáo viên Chủ nhiệm và 8 Giáo viên Phó Chủ nhiệm Tiểu học.",
        "Sheet 5 - PHAN_CONG_GIANG_DAY: Bảng ma trận phân công môn học chi tiết cho từng lớp, có mục điền thêm môn khác của GVCN.",
        "Sheet 6 - TACH_GHEP_LOP: Bảng cấu hình ghép lớp (7A1-7A2, 8A1-8A2, 12A1-12A2) và ma trận đối ứng 12 cặp phân ban Lớp 12.",
        "Sheet 7 - LUOI_THOI_KHOA_BIEU_MAU: Khung lưới thời khóa biểu mẫu phân tách rõ sáng/chiều và dòng Tiết 10 độc lập."
    ]),
    ("3. QUY ƯỚC MÃ MÀU CHUẨN", [
        "Màu Xanh Đậm (#1B365D): Tiêu đề cột và nhãn hệ thống (Cố định, không chỉnh sửa).",
        "Màu Vàng Nhạt (#FFF2CC): Ô NGƯỜI DÙNG ĐIỀN THÔNG TIN (Bạn có thể gõ, sửa, thay đổi tự do).",
        "Màu Xanh Nhạt (#D9E1F2): Ô CÔNG THỨC TỰ ĐỘNG TÍNH TOÁN (Tự động cập nhật tổng số tiết, không nên sửa đè).",
        "Màu Xám Nhạt (#F2F2F2): Ô khóa cố định hoặc thông tin tham chiếu không được đổi."
    ]),
    ("4. QUY TRÌNH THỰC HIỆN 3 BƯỚC", [
        "Bước 1: Mở Sheet KHAI_BAO_GIAO_VIEN và KHAI_BAO_LOP_HOC để cập nhật danh bạ nhân sự và chủ nhiệm.",
        "Bước 2: Mở Sheet PHAN_CONG_GIANG_DAY và TACH_GHEP_LOP để điều chỉnh môn học, số tiết, và kiểm tra 12 cặp đối ứng của Lớp 12.",
        "Bước 3: Chạy lệnh `python loader_template.py` trong terminal để tự động kiểm toán toàn vẹn và tạo lại Master Timetable."
    ])
]

curr_r = 5
for section_title, bullets in instructions:
    ws1.cell(curr_r, 2, value=section_title).font = font_section
    curr_r += 1
    for b in bullets:
        c = ws1.cell(curr_r, 2, value=f"•  {b}")
        c.font = font_regular
        curr_r += 1
    curr_r += 1

ws1.column_dimensions['A'].width = 4.0
ws1.column_dimensions['B'].width = 120.0

# ==============================================================================
# SHEET 2: BANG_QUY_TAC_RANG_BUOC (25 User Constraints Codified)
# ==============================================================================
ws2 = wb.create_sheet(title="BANG_QUY_TAC_RANG_BUOC")
ws2.views.sheetView[0].showGridLines = True

ws2.cell(2, 2, value="BẢNG TỔNG HỢP 25 QUY TẮC RÀNG BUỘC SƯ PHẠM THỜI KHÓA BIỂU MCA").font = font_title
ws2.cell(3, 2, value="Hệ thống quy chuẩn vận hành chính thức năm học 2026-2027").font = font_subtitle

headers_r2 = ["Mã QT", "Nhóm nghiệp vụ", "Quy tắc ràng buộc sư phạm", "Phạm vi áp dụng", "Mức độ ưu tiên", "Quy định chi tiết"]
for col_idx, h in enumerate(headers_r2, start=2):
    cell = ws2.cell(5, col_idx, value=h)
    cell.font = font_header
    cell.fill = fill_header
    cell.alignment = align_center
    cell.border = border_header
ws2.row_dimensions[5].height = 26.0

rules_list = [
    ("QT-01", "Khung giờ & Nghi lễ", "Chào cờ đầu tuần", "Toàn trường (18 lớp)", "Bắt buộc 100%", "Tiết 1 sáng Thứ 2 (7:30 - 8:15). BGH & đoàn thể không dạy chuyên môn."),
    ("QT-02", "Khung giờ & Nghi lễ", "Sinh hoạt lớp & HĐTN", "Cấp 1, Cấp 2, Cấp 3", "Bắt buộc 100%", "Tiết 5 sáng Thứ 6 (SHL Tiểu học và HĐTN Trung học)."),
    ("QT-03", "Giáo viên Chủ nhiệm", "Lịch dạy liền khối GVCN C1", "8 GVCN Tiểu học", "Bắt buộc 100%", "Các tiết trong buổi của GVCN phải xếp liền nhau; môn giống nhau xếp cạnh nhau. Nghỉ chiều Thứ 6 (SHCM) + 1 buổi khác bất kỳ trừ sáng Thứ 2."),
    ("QT-04", "Giáo viên Nước ngoài", "Gom tiết tập trung GVNN", "6 GVNN", "Bắt buộc 100%", "Mỗi buổi xếp ít nhất 2 tiết trở lên (đẹp nhất 3-4 tiết/buổi). Cô Catie KHÔNG DẠY BUỔI CHIỀU, chỉ dạy buổi sáng."),
    ("QT-05", "Tiết Bổ trợ", "Vị trí tiết Bổ trợ trong ngày", "Toàn trường", "Bắt buộc 100%", "Các tiết bổ trợ bắt buộc phải xếp là tiết cuối cùng của buổi chiều."),
    ("QT-06", "Thể dục (GDTC)", "Cách ngày mặc đồng phục", "Toàn trường", "Bắt buộc 100%", "Xếp cách ngày: Cặp Thứ 3+5 HOẶC Thứ 4+6. KHÔNG xếp Tiết 4, 5, 6; HẠN CHẾ Tiết 7. Chỉ xếp Tiết 1, 2, 3 sáng hoặc 8, 9 chiều."),
    ("QT-07", "Stem & Robotic", "Tiết kép Stem Tiểu học", "Khối 1 - Khối 5", "Bắt buộc 100%", "Bắt buộc xếp 2 tiết liền nhau. Chỉ có 3 cặp tiết hợp lệ: {Tiết 2, 3}, {Tiết 6, 7}, {Tiết 8, 9} (tránh cắt ngang giờ ra chơi)."),
    ("QT-08", "Phân bổ sư phạm", "Rải đều tiết trong tuần", "Toàn bộ các môn", "Bắt buộc", "Các tiết môn học rải đều từ Thứ 2 đến Thứ 6, không dồn hết vào đầu tuần hoặc cuối tuần."),
    ("QT-09", "Lệch giờ C1 vs C2/3", "Kiểm tra múi giờ thực tế", "Cô Yên (Tin), Cô P.Anh (Stem)", "Sinh tử", "Cấp 1 học 35m, Cấp 2/3 học 45m. Tiết 3 C2/3 (9:10-9:55) trùng 10 phút với Tiết 4 C1 (9:45-10:20). Cấm xếp trùng."),
    ("QT-10", "Bổ trợ Tiểu học", "Khung giờ Bổ trợ Cấp 1", "Khối 1 - Khối 5", "Bắt buộc", "Xếp 2 tiết cuối chiều (Tiết 8, 9 hoặc Tiết 9, 10) như dữ liệu Master 05/09."),
    ("QT-11", "Quản lý lớp GVCN", "Định mức sáng của GVCN C1", "8 GVCN Tiểu học", "Bắt buộc", "Đảm bảo mỗi cô chủ nhiệm phải có ít nhất 1 buổi sáng dạy từ 3 tiết trở lên trong tuần để quản lý nền nếp lớp."),
    ("QT-12", "Nhân sự GVCN", "Danh sách GVCN Cấp 1", "Khối 1 - Khối 5", "Chuẩn hóa", "1A1: Liễu, 1A2: Hạnh, 2A1: Tiểu Hà, 2A2: Khánh Linh, 3A1: Chín, 3A2: Chiến, 4A1: Hải, 5A1: Hiền."),
    ("QT-13", "HĐTN Trung học", "3 tiết HĐTN Cấp 2, Cấp 3", "Khối 6 - Khối 12", "Bắt buộc", "Tiết 1 sáng T2 + Tiết 5 sáng T6 + Tiết cuối cùng buổi chiều (để sau này có thể đổi thành tiết bổ trợ)."),
    ("QT-14", "Giờ ăn học sinh", "Stem C2 & Phó Chủ nhiệm C1", "Cô P.Anh, Ngọc, Thu, Liên", "Bắt buộc", "Không xếp Stem C2 vào cuối sáng (Tiết 5) và cuối chiều (Tiết 7) vì các cô Phó CN phải chăm sóc học sinh C1 ăn trưa và ăn chiều."),
    ("QT-15", "Nhân sự Phó CN", "Danh sách Phó CN Cấp 1", "Khối 1 - Khối 5", "Chuẩn hóa", "1A1: P.Anh, 1A2: Chi, 2A1: Ngọc, 2A2: Trống, 3A1: Lê, 3A2: Lam, 4A1: Thu, 5A1: Liên."),
    ("QT-16", "GV Thỉnh giảng", "Lịch nghỉ Cô Quyến (Toán)", "Cô Quyến", "Khóa cứng", "Cô Quyến NGHỈ TOÀN BỘ NGÀY THỨ 4, không xếp bất kỳ tiết nào vào Thứ 4."),
    ("QT-17", "Khối 7 & 8 Tách/Ghép", "CLC vs Song ngữ Khối 7, 8", "7A1, 7A2, 8A1, 8A2", "Bắt buộc 100%", "Global Success học chung. Prepare tách lớp (CLC 4 tiết tại A306, Song ngữ 9 tiết). 5 tiết Prepare còn lại của Song ngữ xếp ở cuối các buổi chiều."),
    ("QT-18", "Thời lượng GVNN", "Tối ưu buổi dạy GVNN", "6 GVNN", "Tối ưu", "Bố trí 1 buổi có ít nhất 2 tiết, đẹp nhất là 3 đến 4 tiết để thuận tiện công đi lại."),
    ("QT-19", "Cặp tiết 90 phút", "Toán & Ngữ văn C2, C3", "Khối 6 - Khối 12", "Bắt buộc", "Phải xếp 2 tiết cạnh nhau thành 1 cặp tiết 90 phút trong tuần để đảm bảo thời gian kiểm tra định kỳ."),
    ("QT-20", "Tiếng Anh & Môn khác", "Dàn đều tiết Tiếng Anh", "Khối 6 - Khối 12", "Sư phạm", "Có thể xếp tiết đôi hoặc đơn nhưng phải dàn đều các ngày trong tuần."),
    ("QT-21", "Họp Tổ Chuyên Môn", "Tiết trống chung họp tổ", "Tổ Tự nhiên, Xã hội, TA", "Bắt buộc", "Dư ra 1 tiết mà toàn bộ thành viên trong tổ đều nghỉ để họp tổ chuyên môn (theo danh sách D:\\SMAS...)."),
    ("QT-22", "Bổ trợ Lớp 12", "100% Bổ trợ 12 xếp cuối ngày", "Lớp 12A1 & 12A2", "Bắt buộc", "Gom toàn bộ các tiết Bổ trợ của Lớp 12 (Hóa BT, Sử BT, Prepare BT, Lí BT, KTPL BT, Sinh BT) về Tiết 8, 9 và 10 cuối chiều."),
    ("QT-23", "GV Thỉnh giảng", "Lịch cứng 4 GV thỉnh giảng", "Quyến, Thủy, Thiết, Yến LS", "Khóa cứng", "Thủy (KTPL): Sáng T4 + Cả ngày T5. Thiết (Địa): Sáng T2 + Cả ngày T5. Yến (Sử): Tiết 5 (T2-T5), Tiết 4 (T3), Tiết cuối chiều T5, T6."),
    ("QT-24", "Phân ban Lớp 12", "Ma trận 12 cặp đối ngẫu 1-1", "12A1 (A305) & 12A2 (B205)", "Sinh tử", "12 tiết phân ban của 12A1 tại A305 bắt buộc đối ứng chính xác từng tiết với 12 tiết của 12A2 tại B205."),
    ("QT-25", "Cân bằng Toán học", "Phương trình cân bằng 711 tiết", "Toàn trường", "Toán học 100%", "Tổng tiết lớp (806) - Tiết ghép (103) + Đồng giảng (8) = ĐÚNG 711 TIẾT GIÁO VIÊN.")
]

for row_idx, r_data in enumerate(rules_list, start=6):
    ws2.row_dimensions[row_idx].height = 24.0
    for c_idx, val in enumerate(r_data, start=2):
        c = ws2.cell(row_idx, c_idx, value=val)
        c.font = font_bold if c_idx in [2, 6] else font_regular
        c.alignment = align_center if c_idx in [2, 5] else align_left
        c.border = border_cell
        if c_idx == 6 and "Sinh tử" in r_data[4]:
            c.fill = fill_highlight

ws2.column_dimensions['A'].width = 4.0
ws2.column_dimensions['B'].width = 12.0
ws2.column_dimensions['C'].width = 24.0
ws2.column_dimensions['D'].width = 30.0
ws2.column_dimensions['E'].width = 24.0
ws2.column_dimensions['F'].width = 18.0
ws2.column_dimensions['G'].width = 75.0

# ==============================================================================
# SHEET 3: KHAI_BAO_GIAO_VIEN
# ==============================================================================
ws3 = wb.create_sheet(title="KHAI_BAO_GIAO_VIEN")
ws3.views.sheetView[0].showGridLines = True

ws3.cell(2, 2, value="DANH BẠ KHAI BÁO 43 GIÁO VIÊN & ĐỊNH MỨC GIẢNG DẠY MCA").font = font_title
ws3.cell(3, 2, value="Cột màu vàng: Người dùng có thể chỉnh sửa | Cột màu xanh: Tự động tính toán").font = font_subtitle

headers_r3 = ["STT", "Mã GV", "Tên hiển thị", "Danh xưng", "Tổ bộ môn", "Chủ nhiệm lớp", "Định mức gốc", "Tiết bổ trợ / bồi giỏi", "TỔNG SỐ TIẾT", "Lịch đăng ký nghỉ / Ràng buộc cá nhân", "Phân công chính thức Sheet 3"]
for col_idx, h in enumerate(headers_r3, start=2):
    cell = ws3.cell(5, col_idx, value=h)
    cell.font = font_header
    cell.fill = fill_header
    cell.alignment = align_center
    cell.border = border_header
ws3.row_dimensions[5].height = 26.0

teachers = teachers_data.get("teachers", [])
for idx, t in enumerate(teachers, start=1):
    r = 5 + idx
    ws3.row_dimensions[r].height = 22.0
    
    # STT, Code, Display Name, Honorific, Dept, Homeroom
    ws3.cell(r, 2, value=idx).alignment = align_center
    ws3.cell(r, 3, value=t.get("code", f"GV{idx:02d}")).alignment = align_center
    ws3.cell(r, 4, value=t["display_name"]).alignment = align_left
    ws3.cell(r, 5, value=t.get("honorific", "")).alignment = align_left
    ws3.cell(r, 6, value=t.get("department", "")).alignment = align_left
    ws3.cell(r, 7, value=t.get("homeroom", "") if t.get("homeroom") else "").alignment = align_center
    
    # Base, Extra (Editable - Yellow)
    c_base = ws3.cell(r, 8, value=t.get("base_periods", 0))
    c_base.alignment = align_center
    c_base.fill = fill_input
    
    c_adj = ws3.cell(r, 9, value=t.get("adjustments", 0))
    c_adj.alignment = align_center
    c_adj.fill = fill_input
    
    # Total = Formula (Blue)
    c_tot = ws3.cell(r, 10, value=f"=H{r}+I{r}")
    c_tot.alignment = align_center
    c_tot.fill = fill_calc
    c_tot.font = font_bold
    
    # Constraints
    c_list = list(t.get("constraints", []))
    if t["display_name"] == "Quyến":
        if not any("thứ 4" in c.lower() for c in c_list):
            c_list.append("Khóa lịch: Nghỉ trọn vẹn cả ngày Thứ 4")
    elif t["display_name"] == "Catie":
        if not any("sáng" in c.lower() for c in c_list):
            c_list.append("Chỉ dạy buổi sáng, không dạy buổi chiều; gom 3-4 tiết/buổi")
    elif t["display_name"] == "Duy":
        if not any("thứ 2" in c.lower() for c in c_list):
            c_list.append("Nghỉ sáng Thứ 2")
    elif t["display_name"] == "Thuỷ":
        if not any("thứ 4" in c.lower() for c in c_list):
            c_list.append("Lịch thỉnh giảng: Chỉ dạy sáng Thứ 4 và cả ngày Thứ 5")
    elif t["display_name"] == "Thiết":
        if not any("thứ 2" in c.lower() for c in c_list):
            c_list.append("Lịch thỉnh giảng: Chỉ dạy sáng Thứ 2 và cả ngày Thứ 5")
    elif t["display_name"] == "Yến LS":
        if not any("chỉ định" in c.lower() for c in c_list):
            c_list.append("Lịch thỉnh giảng: Tiết 9-10 T2, Tiết 9 T3, Tiết 4 T4, Tiết 5 T5, Tiết 4-5-8 T6")

    constraints_str = "; ".join(c_list)
    ws3.cell(r, 11, value=constraints_str).alignment = align_left
    
    # Official text
    ws3.cell(r, 12, value=t.get("official_assignment", "")).alignment = align_left
    
    for c_idx in range(2, 13):
        ws3.cell(r, c_idx).border = border_cell
        if c_idx not in [8, 9, 10]:
            ws3.cell(r, c_idx).font = font_regular

# Total Row
tot_r3 = 6 + len(teachers)
ws3.row_dimensions[tot_r3].height = 28.0
c_lbl = ws3.cell(tot_r3, 2, value="TỔNG CỘNG TIẾT TOÀN TRƯỜNG")
c_lbl.font = font_bold
c_lbl.alignment = align_right
ws3.merge_cells(start_row=tot_r3, start_column=2, end_row=tot_r3, end_column=9)
for c in range(2, 10):
    ws3.cell(tot_r3, c).border = border_total

c_grand = ws3.cell(tot_r3, 10, value=f"=SUM(J6:J{tot_r3-1})")
c_grand.font = font_bold
c_grand.alignment = align_center
c_grand.fill = fill_calc
c_grand.border = border_total

ws3.cell(tot_r3, 11, value="MỤC TIÊU CÂN BẰNG: ĐÚNG 711 TIẾT").font = font_bold
ws3.cell(tot_r3, 11).alignment = align_left
ws3.cell(tot_r3, 11).border = border_total
ws3.cell(tot_r3, 12, value=None).border = border_total

ws3.column_dimensions['A'].width = 4.0
ws3.column_dimensions['B'].width = 8.0
ws3.column_dimensions['C'].width = 14.0
ws3.column_dimensions['D'].width = 16.0
ws3.column_dimensions['E'].width = 20.0
ws3.column_dimensions['F'].width = 22.0
ws3.column_dimensions['G'].width = 16.0
ws3.column_dimensions['H'].width = 14.0
ws3.column_dimensions['I'].width = 18.0
ws3.column_dimensions['J'].width = 16.0
ws3.column_dimensions['K'].width = 45.0
ws3.column_dimensions['L'].width = 90.0

# ==============================================================================
# SHEET 4: KHAI_BAO_LOP_HOC
# ==============================================================================
ws4 = wb.create_sheet(title="KHAI_BAO_LOP_HOC")
ws4.views.sheetView[0].showGridLines = True

ws4.cell(2, 2, value="DANH SÁCH 18 LỚP HỌC & ĐỘI NGŨ CHỦ NHIỆM / PHÓ CHỦ NHIỆM MCA").font = font_title
ws4.cell(3, 2, value="Khai báo cấp học, hệ chương trình, phòng học cơ sở và định mức tiết").font = font_subtitle

headers_r4 = ["STT", "Tên Lớp", "Cấp học", "Khối", "Hệ chương trình", "Phòng học cơ sở", "GV Chủ Nhiệm", "GV Phó Chủ Nhiệm", "Định mức tiết/tuần", "Tiết sáng tối đa", "Tiết chiều tối đa"]
for col_idx, h in enumerate(headers_r4, start=2):
    cell = ws4.cell(5, col_idx, value=h)
    cell.font = font_header
    cell.fill = fill_header
    cell.alignment = align_center
    cell.border = border_header
ws4.row_dimensions[5].height = 26.0

classes_info = [
    (1, "1A1", "Tiểu học", 1, "Chất lượng cao (CLC)", "B301", "Cô Liễu", "Cô Phương Anh", 45, 5, 4),
    (2, "1A2", "Tiểu học", 1, "Song ngữ Quốc tế", "B302", "Cô Hạnh", "Cô Chi", 50, 5, 5),
    (3, "2A1", "Tiểu học", 2, "Chất lượng cao (CLC)", "B303", "Cô Tiểu Hà", "Cô Ngọc", 45, 5, 4),
    (4, "2A2", "Tiểu học", 2, "Song ngữ Quốc tế", "B304", "Cô Khánh Linh", "(Không có)", 50, 5, 5),
    (5, "3A1", "Tiểu học", 3, "Chất lượng cao (CLC)", "B305", "Cô Chín", "Cô Lê", 45, 5, 4),
    (6, "3A2", "Tiểu học", 3, "Song ngữ Quốc tế", "B306", "Thầy Chiến", "Cô Lam", 50, 5, 5),
    (7, "4A1", "Tiểu học", 4, "Chất lượng cao (CLC)", "B307", "Cô Hải", "Cô Thu", 45, 5, 4),
    (8, "5A1", "Tiểu học", 5, "Chất lượng cao (CLC)", "B308", "Cô Hiền", "Cô Liên", 45, 5, 4),
    (9, "6A1", "THCS", 6, "THCS Chuẩn", "B201", "Cô Nguyệt", "(Không có)", 39, 5, 4),
    (10, "7A1", "THCS", 7, "THCS Chất lượng cao", "B202", "Cô Yên", "(Không có)", 39, 5, 4),
    (11, "7A2", "THCS", 7, "THCS Song ngữ (+5 tiết TA)", "B202", "Cô Yên", "(Không có)", 44, 5, 5),
    (12, "8A1", "THCS", 8, "THCS Chất lượng cao", "B203", "Thầy Huy", "(Không có)", 39, 5, 4),
    (13, "8A2", "THCS", 8, "THCS Song ngữ (+5 tiết TA)", "B203", "Thầy Huy", "(Không có)", 44, 5, 5),
    (14, "9A1", "THCS", 9, "THCS Chuẩn", "B204", "Cô Hương", "(Không có)", 44, 5, 5),
    (15, "10A1", "THPT", 10, "THPT Chuẩn (+Bồi giỏi)", "B205", "Thầy Huy", "(Không có)", 47, 5, 5),
    (16, "11A1", "THPT", 11, "THPT Chuẩn (+Bổ trợ)", "B206", "Cô Giang", "(Không có)", 45, 5, 4),
    (17, "12A1", "THPT", 12, "THPT Phân ban Tự Nhiên", "B205", "Cô Thuý", "(Không có)", 45, 5, 5),
    (18, "12A2", "THPT", 12, "THPT Phân ban Xã Hội", "B205", "Cô Thuý", "(Không có)", 45, 5, 5),
]

for idx, c_data in enumerate(classes_info, start=1):
    r = 5 + idx
    ws4.row_dimensions[r].height = 22.0
    for col_idx, val in enumerate(c_data, start=2):
        cell = ws4.cell(r, col_idx, value=val)
        cell.border = border_cell
        cell.font = font_bold if col_idx == 3 else font_regular
        cell.alignment = align_center if col_idx in [2, 4, 5, 7, 10, 11, 12] else align_left
        if col_idx in [7, 8, 9, 10]:
            cell.fill = fill_input # Editable columns

# Total Class slots row
tot_r4 = 6 + len(classes_info)
ws4.row_dimensions[tot_r4].height = 26.0
c_l = ws4.cell(tot_r4, 2, value="TỔNG SỐ TIẾT LỚP HỌC (TRƯỚC KHI TRỪ GHÉP)")
c_l.font = font_bold
c_l.alignment = align_right
ws4.merge_cells(start_row=tot_r4, start_column=2, end_row=tot_r4, end_column=9)
for c in range(2, 10):
    ws4.cell(tot_r4, c).border = border_total

c_tot_slots = ws4.cell(tot_r4, 10, value=f"=SUM(J6:J{tot_r4-1})")
c_tot_slots.font = font_bold
c_tot_slots.alignment = align_center
c_tot_slots.fill = fill_calc
c_tot_slots.border = border_total

ws4.cell(tot_r4, 11, value=None).border = border_total
ws4.cell(tot_r4, 12, value=None).border = border_total

ws4.column_dimensions['A'].width = 4.0
ws4.column_dimensions['B'].width = 8.0
ws4.column_dimensions['C'].width = 14.0
ws4.column_dimensions['D'].width = 14.0
ws4.column_dimensions['E'].width = 10.0
ws4.column_dimensions['F'].width = 25.0
ws4.column_dimensions['G'].width = 18.0
ws4.column_dimensions['H'].width = 20.0
ws4.column_dimensions['I'].width = 20.0
ws4.column_dimensions['J'].width = 18.0
ws4.column_dimensions['K'].width = 16.0
ws4.column_dimensions['L'].width = 16.0

# ==============================================================================
# SHEET 5: PHAN_CONG_GIANG_DAY (Matrix with Extra GVCN Subjects)
# ==============================================================================
ws5 = wb.create_sheet(title="PHAN_CONG_GIANG_DAY")
ws5.views.sheetView[0].showGridLines = True

ws5.cell(2, 2, value="MA TRẬN PHÂN CÔNG GIẢNG DẠY CHI TIẾT THEO LỚP & MÔN HỌC").font = font_title
ws5.cell(3, 2, value="Cung cấp mục mở rộng để điền thêm các môn khác của GVCN ngoài Toán & Tiếng Việt").font = font_subtitle

headers_r5 = [
    "STT", "Lớp", "Tên Môn Học", "Phân loại môn", "GV Giảng Dạy Chính", 
    "GV Trợ Giảng / Đồng Giảng", "Số tiết/tuần", "Tiết kép bắt buộc", 
    "Phòng chuyên môn", "Môn kiêm nhiệm khác của GVCN", "Ghi chú sư phạm"
]

for col_idx, h in enumerate(headers_r5, start=2):
    cell = ws5.cell(5, col_idx, value=h)
    cell.font = font_header
    cell.fill = fill_header
    cell.alignment = align_center
    cell.border = border_header
ws5.row_dimensions[5].height = 26.0

sample_assignments = [
    (1, "1A1", "Toán học", "Chính khóa", "Liễu", "", 4, "Có", "", "", "Xếp liền 2 tiết nếu có"),
    (2, "1A1", "Tiếng Việt", "Chính khóa", "Liễu", "", 10, "Có", "", "", "Tối đa 3 tiết/buổi sáng"),
    (3, "1A1", "Tự nhiên - Xã hội", "Chính khóa", "Liễu", "", 2, "Không", "", "", "Môn do GVCN phụ trách"),
    (4, "1A1", "Hoạt động trải nghiệm", "Chính khóa", "Liễu", "", 2, "Không", "", "", "Gồm 1 tiết SHL T5 Thứ 6"),
    (5, "1A1", "Chào cờ", "Nghi lễ", "Liễu", "", 1, "Không", "", "", "Tiết 1 sáng Thứ 2"),
    (6, "1A1", "Bổ trợ Toán", "Bổ trợ", "Liễu", "", 2, "Có", "", "", "Xếp cuối chiều"),
    (7, "1A1", "Bổ trợ Tiếng Việt", "Bổ trợ", "Liễu", "", 2, "Có", "", "", "Xếp cuối chiều"),
    (8, "1A1", "Đạo đức", "Chính khóa", "Chi", "", 1, "Không", "", "Kỹ năng sống", "Cô Chi dạy kiêm nhiệm"),
    (9, "1A1", "Stem & Robotic", "Thực hành", "Phương Anh", "", 2, "Có (Tiết kép)", "Stem", "", "Cặp tiết 2-3, 6-7 hoặc 8-9"),
    (10, "1A1", "Mỹ thuật", "Năng khiếu", "Lê", "", 1, "Không", "", "", ""),
    (11, "1A1", "Âm nhạc", "Năng khiếu", "Nghĩa", "", 1, "Không", "", "", ""),
    (12, "1A1", "Tin học", "Thực hành", "Yên", "", 1, "Không", "A306", "", "Chú ý múi giờ 35m vs 45m"),
    (13, "1A1", "Giáo dục thể chất", "Thể chất", "Thu", "", 2, "Không", "", "", "Xếp Thứ 4 và Thứ 6, tránh trưa"),
    (14, "1A1", "Bright Ideas", "Ngoại ngữ", "Cybele", "", 3, "Có", "", "", "GVNN gom 3 tiết"),
    (15, "1A1", "Global Success", "Ngoại ngữ", "Vũ Hà", "", 4, "Có", "", "", ""),
    (16, "1A1", "Bổ trợ Tiếng Anh", "Bổ trợ", "Vũ Hà", "", 2, "Không", "", "", "Xếp cuối chiều"),
    # Co-teaching primary samples
    (17, "4A1", "Bổ trợ Toán (Đồng giảng)", "Bổ trợ", "Hải", "Chi", 2, "Có", "", "", "Cô Hải chính + Cô Chi trợ giảng"),
    (18, "4A1", "Bổ trợ T.Việt (Đồng giảng)", "Bổ trợ", "Hải", "Chi", 2, "Có", "", "", "Cô Hải chính + Cô Chi trợ giảng"),
    (19, "5A1", "Bổ trợ Toán (Đồng giảng)", "Bổ trợ", "Hiền", "Chi", 2, "Có", "", "", "Cô Hiền chính + Cô Chi trợ giảng"),
    (20, "5A1", "Bổ trợ T.Việt (Đồng giảng)", "Bổ trợ", "Hiền", "Chi", 2, "Có", "", "", "Cô Hiền chính + Cô Chi trợ giảng"),
    # Secondary split samples
    (21, "7A1", "Global Success", "Ngoại ngữ", "Hoà", "", 3, "Không", "B202", "", "Học ghép chung với 7A2"),
    (22, "7A1", "Prepare (Tách CLC)", "Ngoại ngữ", "Hoà, Catie", "", 4, "Có", "A306", "", "Tách phòng A306 (Catie chỉ dạy sáng)"),
    (23, "7A2", "Prepare (Tách Song ngữ)", "Ngoại ngữ", "Mela", "", 9, "Có", "B202", "", "4 tiết song song + 5 tiết cuối chiều"),
    (24, "10A1", "Toán học", "Chính khóa", "Quyến", "", 4, "Có (90 phút)", "", "", "Nghỉ Thứ 4, cặp 90 phút"),
    (25, "10A1", "Ngữ văn", "Chính khóa", "Du", "", 4, "Có (90 phút)", "", "", "Cặp 90 phút"),
    (26, "10A1", "Bồi giỏi Toán", "Bồi giỏi", "Quyến", "", 1, "Không", "", "", "Tiết 10 độc lập (Thứ 2)"),
    (27, "10A1", "Bồi giỏi Văn", "Bồi giỏi", "Du", "", 1, "Không", "", "", "Tiết 9 chiều (Thứ 2)"),
    # Grade 12 split samples
    (28, "12A1", "Hóa học (Tự nhiên)", "Phân ban", "Nguyệt", "", 4, "Có", "A305", "", "Đối ứng Địa lí 12A2 tại B205"),
    (29, "12A2", "Địa lí (Xã hội)", "Phân ban", "Thiết", "", 3, "Có", "B205", "", "Cô Thiết dạy sáng T2 & ngày T5"),
    (30, "12A1", "Global Success TC", "Tăng cường", "Nhung", "", 2, "Có", "A305", "", "Tiết 9-10 Thứ 2, đối ứng Sử TC"),
    (31, "12A2", "Lịch sử TC", "Tăng cường", "Yến LS", "", 2, "Có", "B205", "", "Cô Yến dạy Tiết 9-10 Thứ 2"),
]

for idx, a_data in enumerate(sample_assignments, start=1):
    r = 5 + idx
    ws5.row_dimensions[r].height = 22.0
    for col_idx, val in enumerate(a_data, start=2):
        cell = ws5.cell(r, col_idx, value=val)
        cell.border = border_cell
        cell.font = font_bold if col_idx in [3, 4] else font_regular
        cell.alignment = align_center if col_idx in [2, 3, 5, 8, 9, 10] else align_left
        if col_idx in [4, 6, 7, 8, 9, 10, 11]:
            cell.fill = fill_input # Highly editable

ws5.column_dimensions['A'].width = 4.0
ws5.column_dimensions['B'].width = 8.0
ws5.column_dimensions['C'].width = 12.0
ws5.column_dimensions['D'].width = 24.0
ws5.column_dimensions['E'].width = 18.0
ws5.column_dimensions['F'].width = 20.0
ws5.column_dimensions['G'].width = 24.0
ws5.column_dimensions['H'].width = 14.0
ws5.column_dimensions['I'].width = 18.0
ws5.column_dimensions['J'].width = 18.0
ws5.column_dimensions['K'].width = 26.0
ws5.column_dimensions['L'].width = 35.0

# ==============================================================================
# SHEET 6: TACH_GHEP_LOP
# ==============================================================================
ws6 = wb.create_sheet(title="TACH_GHEP_LOP")
ws6.views.sheetView[0].showGridLines = True

ws6.cell(2, 2, value="QUY TẮC GHÉP LỚP & MA TRẬN 12 CẶP ĐỐI NGẪU PHÂN BAN LỚP 12").font = font_title
ws6.cell(3, 2, value="Kiểm soát di chuyển phòng học cơ sở và phòng chuyên môn A305, A306").font = font_subtitle

# Part A: Merge Pairs
ws6.cell(5, 2, value="PHẦN A: DANH MỤC CÁC CẶP GHÉP LỚP VĂN HÓA CƠ BẢN").font = font_section
headers_pA = ["STT", "Cặp ghép", "Phòng học cơ sở", "Số tiết ghép chung", "Danh mục môn ghép chung", "Quy định tách môn"]
for c_idx, h in enumerate(headers_pA, start=2):
    cell = ws6.cell(6, c_idx, value=h)
    cell.font = font_header
    cell.fill = fill_header
    cell.alignment = align_center
    cell.border = border_header
ws6.row_dimensions[6].height = 24.0

pA_data = [
    (1, "7A1 & 7A2", "Phòng B202", 35, "Toán, Ngữ văn, KHTN, Lịch sử - Địa lí, GDCD, Tin học, GDTC, Âm nhạc, Global Success", "Tách duy nhất môn Prepare: 7A1 sang A306 (Hoà, Catie), 7A2 tại B202 (Mela)."),
    (2, "8A1 & 8A2", "Phòng B203", 35, "Toán, Ngữ văn, KHTN, Lịch sử - Địa lí, GDCD, Tin học, GDTC, Âm nhạc, Global Success", "Tách duy nhất môn Prepare: 8A1 sang A306 (Cybele, Hoà), 8A2 tại B203 (Saloni, Hoà)."),
    (3, "12A1 & 12A2", "Phòng B205", 33, "Toán học (Duy), Ngữ văn (Thuý), GDTC & GDQPAN (Liên), TNHN (Thuý), Chào cờ, SHL", "Tách toàn bộ các môn phân ban tự chọn và bổ trợ (12 cặp đối ứng đối ngẫu 1-1)."),
]

for idx, r_data in enumerate(pA_data, start=1):
    r = 6 + idx
    ws6.row_dimensions[r].height = 24.0
    for c_idx, val in enumerate(r_data, start=2):
        cell = ws6.cell(r, c_idx, value=val)
        cell.border = border_cell
        cell.font = font_regular
        cell.alignment = align_center if c_idx in [2, 3, 4, 5] else align_left

# Part B: Grade 12 Elective 1-to-1 Matrix
ws6.cell(12, 2, value="PHẦN B: MA TRẬN 12 CẶP MÔN HỌC ĐỐI NGẪU 1-1 PHÂN BAN KHỐI 12").font = font_section
headers_pB = [
    "Cặp", "Thứ", "Tiết", "12A1: Tên Môn Tự Nhiên", "12A1: Giáo Viên", "12A1: Phòng Học",
    "12A2: Tên Môn Xã Hội", "12A2: Giáo Viên", "12A2: Phòng Học", "Tính chất tiết học", "Trạng thái đối ứng"
]
for c_idx, h in enumerate(headers_pB, start=2):
    cell = ws6.cell(13, c_idx, value=h)
    cell.font = font_header
    cell.fill = fill_subheader
    cell.alignment = align_center
    cell.border = border_header
ws6.row_dimensions[13].height = 24.0

pB_data = [
    (1, "Thứ 2", "Tiết 3", "Hóa học", "Nguyệt", "Phòng A305", "Địa lí", "Thiết", "Phòng B205", "Chính khóa", "✓ Khớp 1-1"),
    (2, "Thứ 2", "Tiết 4", "Hóa học", "Nguyệt", "Phòng A305", "Địa lí", "Thiết", "Phòng B205", "Chính khóa", "✓ Khớp 1-1"),
    (3, "Thứ 2", "Tiết 9", "Global Success TC", "Nhung", "Phòng A305", "Lịch sử TC", "Yến LS", "Phòng B205", "Tăng cường", "✓ Khớp 1-1"),
    (4, "Thứ 2", "Tiết 10", "Global Success TC", "Nhung", "Phòng A305", "Lịch sử TC", "Yến LS", "Phòng B205", "Tiết 10 độc lập", "✓ Khớp 1-1"),
    (5, "Thứ 3", "Tiết 3", "Sinh học", "Giang", "Phòng A305", "Văn CĐ", "Thuý", "Phòng B205", "Chuyên đề", "✓ Khớp 1-1"),
    (6, "Thứ 3", "Tiết 9", "Vật lí BT", "Huy", "Phòng A305", "Lịch sử BT", "Yến LS", "Phòng B205", "Bổ trợ cuối ngày", "✓ Khớp 1-1"),
    (7, "Thứ 4", "Tiết 1", "Sinh học", "Giang", "Phòng A305", "GD KT - PL", "Thuỷ", "Phòng B205", "Chính khóa", "✓ Khớp 1-1"),
    (8, "Thứ 4", "Tiết 2", "Hóa học", "Nguyệt", "Phòng A305", "GD KT - PL", "Thuỷ", "Phòng B205", "Chính khóa", "✓ Khớp 1-1"),
    (9, "Thứ 5", "Tiết 7", "Hoá học BT", "Nguyệt", "Phòng A305", "GD KT-PL BT", "Thuỷ", "Phòng B205", "Bổ trợ buổi chiều", "✓ Khớp 1-1"),
    (10, "Thứ 5", "Tiết 8", "Hoá học BT", "Nguyệt", "Phòng A305", "GD KT-PL BT", "Thuỷ", "Phòng B205", "Bổ trợ buổi chiều", "✓ Khớp 1-1"),
    (11, "Thứ 5", "Tiết 9", "Prepare BT", "Charly", "Phòng A305", "Địa lí BT", "Thiết", "Phòng B205", "Bổ trợ cuối ngày", "✓ Khớp 1-1"),
    (12, "Thứ 6", "Tiết 9", "Prepare BT", "Charly", "Phòng A305", "Sinh học BT", "Giang", "Phòng B205", "Bổ trợ cuối ngày", "✓ Khớp 1-1"),
]

for idx, r_data in enumerate(pB_data, start=1):
    r = 13 + idx
    ws6.row_dimensions[r].height = 22.0
    for c_idx, val in enumerate(r_data, start=2):
        cell = ws6.cell(r, c_idx, value=val)
        cell.border = border_cell
        cell.font = font_bold if c_idx in [2, 12] else font_regular
        cell.alignment = align_center if c_idx in [2, 3, 4, 7, 10, 12] else align_left
        if c_idx in [5, 6, 8, 9]:
            cell.fill = fill_input # Editable elective mapping

ws6.column_dimensions['A'].width = 4.0
ws6.column_dimensions['B'].width = 8.0
ws6.column_dimensions['C'].width = 12.0
ws6.column_dimensions['D'].width = 12.0
ws6.column_dimensions['E'].width = 24.0
ws6.column_dimensions['F'].width = 16.0
ws6.column_dimensions['G'].width = 16.0
ws6.column_dimensions['H'].width = 24.0
ws6.column_dimensions['I'].width = 16.0
ws6.column_dimensions['J'].width = 16.0
ws6.column_dimensions['K'].width = 20.0
ws6.column_dimensions['L'].width = 16.0

# ==============================================================================
# SHEET 7: LUOI_THOI_KHOA_BIEU_MAU
# ==============================================================================
ws7 = wb.create_sheet(title="LUOI_THOI_KHOA_BIEU_MAU")
ws7.views.sheetView[0].showGridLines = True

ws7.cell(2, 2, value="KHUNG LƯỚI THỜI KHÓA BIỂU MẪU CHUẨN MCA (CÓ DÒNG TIẾT 10 ĐỘC LẬP)").font = font_title
ws7.cell(3, 2, value="Lưới chuẩn hóa phân định Cấp 1 (35 phút) vs Cấp 2/3 (45 phút)").font = font_subtitle

headers_grid = ["Thứ", "Buổi", "Tiết", "Thời gian Cấp 1 (35m)", "Thời gian Cấp 2/3 (45m)", "Hoạt động cố định", "1A1", "1A2", "6A1", "7A1", "7A2", "10A1", "11A1", "12A1", "12A2"]
for c_idx, h in enumerate(headers_grid, start=2):
    cell = ws7.cell(5, c_idx, value=h)
    cell.font = font_header
    cell.fill = fill_header
    cell.alignment = align_center
    cell.border = border_header
ws7.row_dimensions[5].height = 26.0

day_grid_template = [
    ("Sáng", 1, "7:40 - 8:15", "7:30 - 8:15", "Chào cờ (Thứ 2) / Học"),
    ("Sáng", 2, "8:20 - 8:55", "8:20 - 9:05", "Học"),
    ("Sáng", 3, "9:05 - 9:40", "9:10 - 9:55", "Học (Sau ra chơi C1)"),
    ("Sáng", 4, "9:45 - 10:20", "10:00 - 10:45", "Học"),
    ("Sáng", 5, "10:25 - 11:00", "10:50 - 11:35", "Học / SHL (Thứ 6)"),
    ("Trưa", "Trưa", "11:00 - 13:30", "11:35 - 13:20", "ĂN TRƯA, THIỀN, NGỦ TRƯA"),
    ("Chiều", 6, "13:30 - 14:05", "13:30 - 14:15", "Học chiều"),
    ("Chiều", 7, "14:10 - 14:45", "14:20 - 15:05", "Học chiều"),
    ("Chiều", "Ăn phụ", "14:45 - 15:05", "15:05 - 15:20", "ĂN PHỤ CHIỀU, RA CHƠI"),
    ("Chiều", 8, "15:05 - 15:40", "15:20 - 16:05", "Học chiều / Bổ trợ"),
    ("Chiều", 9, "15:45 - 16:20", "16:10 - 16:55", "Học chiều / Bổ trợ"),
    ("Chiều", 10, "16:25 - 17:00", "17:00 - 17:45", "TIẾT 10 ĐỘC LẬP (Bồi giỏi / Tăng cường)"),
    ("Muộn", "Check out", "17:00+", "17:45+", "Check out / Sinh hoạt CLB")
]

row_counter = 6
for day_num in range(2, 7):
    day_start_row = row_counter
    for b_lbl, p_num, t_c1, t_c2, act in day_grid_template:
        ws7.row_dimensions[row_counter].height = 20.0 if isinstance(p_num, str) else 22.0
        
        ws7.cell(row_counter, 2, value=f"Thứ {day_num}").alignment = align_center
        ws7.cell(row_counter, 3, value=b_lbl).alignment = align_center
        
        cp = ws7.cell(row_counter, 4, value=p_num)
        cp.alignment = align_center
        cp.font = font_bold if isinstance(p_num, int) else font_note
        
        ws7.cell(row_counter, 5, value=t_c1).alignment = align_center
        ws7.cell(row_counter, 6, value=t_c2).alignment = align_center
        
        c_act = ws7.cell(row_counter, 7, value=act)
        c_act.alignment = align_left
        c_act.font = font_note if isinstance(p_num, str) else font_regular
        
        is_break = isinstance(p_num, str)
        for col_idx in range(8, 17):
            cell = ws7.cell(row_counter, col_idx, value=None)
            cell.border = border_cell
            cell.alignment = align_center
            if is_break:
                cell.fill = fill_locked
            else:
                cell.fill = fill_input # Editable slots
                
        for c_idx in range(2, 8):
            ws7.cell(row_counter, c_idx).border = border_cell
            if is_break:
                ws7.cell(row_counter, c_idx).fill = fill_locked
                
        row_counter += 1
        
    # Merge Day label column
    ws7.merge_cells(start_row=day_start_row, start_column=2, end_row=row_counter - 1, end_column=2)

ws7.column_dimensions['A'].width = 4.0
ws7.column_dimensions['B'].width = 12.0
ws7.column_dimensions['C'].width = 10.0
ws7.column_dimensions['D'].width = 10.0
ws7.column_dimensions['E'].width = 22.0
ws7.column_dimensions['F'].width = 22.0
ws7.column_dimensions['G'].width = 30.0
for c in range(8, 17):
    ws7.column_dimensions[get_column_letter(c)].width = 20.0

# Save Workbook
wb.save(out_file)
print(f"\n==========================================================================")
print(f"🎉 EXCEL TEMPLATE GENERATED SUCCESSFULLY: {out_file}")
print(f"   - Sheets ({len(wb.sheetnames)}): {wb.sheetnames}")
print(f"   - File size: {os.path.getsize(out_file)} bytes")
print(f"==========================================================================")
