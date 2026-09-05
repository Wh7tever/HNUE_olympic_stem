"""
========================================================================================
GENERATE STANDARDIZED COMPACT EXCEL TEMPLATE FOR MCA TIMETABLE INPUT
Marie Curie Academy (MCA) - Academic Year 2026-2027
========================================================================================
Generates: `TEMPLATE_TKB_MCA_TINH_GON.xlsx` with exactly 3 ultra-focused sheets:
1. PHAN_CONG_MON_HOC: Single Source of Truth for all class assignments (304 records, 711 periods)
2. GIAO_VIEN_LICH_BAN: 43 teachers + Unavailability locks + automated SUMIF formula
3. TACH_GHEP_VA_PHAN_BAN: 3 basic merge pairs, 12 Grade 12 duel pairs & system rule toggles
========================================================================================
"""

import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter
import json
import os
import re
import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
out_file = os.path.join(PROJECT_ROOT, "TEMPLATE_TKB_MCA_TINH_GON.xlsx")
master_file = os.path.join(PROJECT_ROOT, "New folder", "TKB_Marie_Curie_2026-2027(update_05_09).xlsx")
rules_path = os.path.join(PROJECT_ROOT, "config", "timetable_rules.json")
teachers_path = os.path.join(PROJECT_ROOT, "config", "teacher_registry.json")

print("==========================================================================")
print("BUILDING STANDARDIZED COMPACT EXCEL INPUT TEMPLATE FOR MCA TIMETABLE")
print(f"Target: {out_file}")
print("==========================================================================\n")

wb = openpyxl.Workbook()
wb.remove(wb.active) # Remove default sheet

# --- STYLES ---
font_title = Font(name="Times New Roman", size=14, bold=True, color="1B365D")
font_subtitle = Font(name="Times New Roman", size=10, italic=True, color="555555")
font_section = Font(name="Times New Roman", size=11, bold=True, color="1B365D")
font_header = Font(name="Times New Roman", size=10, bold=True, color="FFFFFF")
font_bold = Font(name="Times New Roman", size=10, bold=True, color="000000")
font_regular = Font(name="Times New Roman", size=10, color="000000")
font_note = Font(name="Times New Roman", size=9, italic=True, color="444444")

fill_header = PatternFill(fill_type="solid", start_color="1B365D", end_color="1B365D") # Navy
fill_subheader = PatternFill(fill_type="solid", start_color="2C4D75", end_color="2C4D75")
fill_input = PatternFill(fill_type="solid", start_color="FFF2CC", end_color="FFF2CC") # Editable Yellow
fill_calc = PatternFill(fill_type="solid", start_color="D9E1F2", end_color="D9E1F2") # Formula Blue
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

# ==============================================================================
# 0. EXTRACT ACTUAL DATA FROM MASTER TKB
# ==============================================================================
wb_master = openpyxl.load_workbook(master_file, data_only=True)
ws4_teach = wb_master['TKB Giáo viên']

# Parse all actual teaching assignments directly from teacher timetable
raw_assignments = []
for c in range(4, ws4_teach.max_column + 1):
    tname = ws4_teach.cell(4, c).value
    if not tname:
        continue
    tname = tname.strip()
    
    t_dict = defaultdict(int)
    for r in range(5, ws4_teach.max_row + 1):
        tiet = ws4_teach.cell(r, 3).value
        if tiet is None or not isinstance(tiet, (int, float)):
            continue
        val = ws4_teach.cell(r, c).value
        if val and isinstance(val, str):
            lines = [l.strip() for l in val.split('\n') if l.strip()]
            first_line = lines[0]
            parts = first_line.split('-')
            subj = parts[0].strip()
            classes = set()
            rooms = set()
            for l in lines:
                l_parts = l.split('-')
                l_rest = '-'.join(l_parts[1:]).strip()
                m_rm = re.search(r'\((.*?)\)', l_rest)
                if m_rm:
                    rooms.add(m_rm.group(1).strip())
                    l_rest = re.sub(r'\(.*?\)', '', l_rest).strip()
                classes.add(l_rest.strip())
            c_str = ', '.join(sorted(classes))
            r_str = ', '.join(sorted(rooms))
            t_dict[(subj, c_str, r_str)] += 1
            
    for (subj, c_str, r_str), count in t_dict.items():
        # Infer is_double
        is_double = "Có" if any(k in subj for k in ["Stem", "Toán", "Văn", "Tiếng Việt"]) else "Không"
        # Infer location requirement
        loc = "Không yêu cầu"
        if "(BT)" in subj or "Bổ trợ" in subj or "TC" in subj:
            loc = "Cuối chiều (Bổ trợ)"
        elif "Bồi giỏi" in subj or "Tiết 10" in subj:
            loc = "Tiết 10"
        elif "Chào cờ" in subj:
            loc = "Chào cờ (T1 sáng T2)"
        elif "Sinh hoạt lớp" in subj or "HĐTN" in subj:
            loc = "SHL (T5 sáng T6)"

        raw_assignments.append({
            "class_name": c_str,
            "subject_name": subj,
            "lead_teacher": tname,
            "co_teacher": "",
            "periods": count,
            "is_double": is_double,
            "room": r_str if r_str not in ["B201","B202","B203","B204","B205","B206","B301","B302","B303","B304","B305","B306","B307","B308"] else "",
            "location_req": loc,
            "note": ""
        })

# Sort assignments logically by class then subject
def sort_key(a):
    c = a["class_name"]
    # Natural sort order for classes
    order = ["1A1", "1A2", "2A1", "2A2", "3A1", "3A2", "4A1", "5A1", "6A1", "7A1", "7A2", "7A1, 7A2", "8A1", "8A2", "8A1, 8A2", "9A1", "10A1", "11A1", "12A1", "12A2", "12A1, 12A2"]
    c_idx = order.index(c) if c in order else 99
    return (c_idx, a["subject_name"], a["lead_teacher"])

raw_assignments.sort(key=sort_key)
print(f"Extracted {len(raw_assignments)} actual teaching assignments (Total periods: {sum(a['periods'] for a in raw_assignments)}).")

# ==============================================================================
# SHEET 1: PHAN_CONG_MON_HOC (Single Source of Truth)
# ==============================================================================
ws1 = wb.create_sheet(title="PHAN_CONG_MON_HOC")
ws1.views.sheetView[0].showGridLines = True

ws1.cell(2, 2, value="BẢNG PHÂN CÔNG GIẢNG DẠY THEO LỚP & MÔN HỌC (SOURCE OF TRUTH)").font = font_title
ws1.cell(3, 2, value="Các ô màu vàng là ô bạn nhập hoặc chỉnh sửa. Tổng tiết giáo viên tại Sheet 2 sẽ tự động cập nhật ngay lập tức.").font = font_subtitle

headers_s1 = [
    "STT", "Lớp", "Tên Môn Học", "Giáo Viên Chính", "Trợ Giảng / Đồng Giảng", 
    "Số tiết / tuần", "Xếp tiết kép?", "Phòng học riêng", "Yêu cầu vị trí", "Ghi chú"
]

ws1.row_dimensions[5].height = 24.0
for col_idx, h in enumerate(headers_s1, start=2):
    c = ws1.cell(5, col_idx, value=h)
    c.font = font_header
    c.fill = fill_header
    c.alignment = align_center
    c.border = border_header

for idx, a in enumerate(raw_assignments, start=1):
    r = 5 + idx
    ws1.row_dimensions[r].height = 20.0
    
    # Col B: STT
    ws1.cell(r, 2, value=idx).alignment = align_center
    
    # Col C: Lớp (Yellow)
    c_cls = ws1.cell(r, 3, value=a["class_name"])
    c_cls.alignment = align_center
    c_cls.fill = fill_input
    c_cls.font = font_bold
    
    # Col D: Tên Môn Học (Yellow)
    c_sub = ws1.cell(r, 4, value=a["subject_name"])
    c_sub.alignment = align_left
    c_sub.fill = fill_input
    
    # Col E: Giáo Viên Chính (Yellow)
    c_tea = ws1.cell(r, 5, value=a["lead_teacher"])
    c_tea.alignment = align_center
    c_tea.fill = fill_input
    c_tea.font = font_bold
    
    # Col F: Trợ Giảng / Đồng Giảng (Yellow)
    c_co = ws1.cell(r, 6, value=a["co_teacher"])
    c_co.alignment = align_center
    c_co.fill = fill_input
    
    # Col G: Số tiết / tuần (Yellow - Editable Number)
    c_per = ws1.cell(r, 7, value=a["periods"])
    c_per.alignment = align_center
    c_per.fill = fill_input
    c_per.font = font_bold
    
    # Col H: Xếp tiết kép? (Yellow)
    c_db = ws1.cell(r, 8, value=a["is_double"])
    c_db.alignment = align_center
    c_db.fill = fill_input
    
    # Col I: Phòng học riêng (Yellow)
    c_rm = ws1.cell(r, 9, value=a["room"])
    c_rm.alignment = align_center
    c_rm.fill = fill_input
    
    # Col J: Yêu cầu vị trí (Yellow)
    c_loc = ws1.cell(r, 10, value=a["location_req"])
    c_loc.alignment = align_left
    c_loc.fill = fill_input
    
    # Col K: Ghi chú (Yellow)
    c_nt = ws1.cell(r, 11, value=a["note"])
    c_nt.alignment = align_left
    c_nt.fill = fill_input
    
    for c_idx in range(2, 12):
        ws1.cell(r, c_idx).border = border_cell
        if c_idx not in [3, 5, 7]:
            ws1.cell(r, c_idx).font = font_regular

# Total row for Sheet 1
tot_r1 = 6 + len(raw_assignments)
ws1.row_dimensions[tot_r1].height = 26.0
c_lbl1 = ws1.cell(tot_r1, 2, value="TỔNG CỘNG SỐ TIẾT PHÂN CÔNG")
c_lbl1.font = font_bold
c_lbl1.alignment = align_right
ws1.merge_cells(start_row=tot_r1, start_column=2, end_row=tot_r1, end_column=6)
for c in range(2, 7):
    ws1.cell(tot_r1, c).border = border_total

c_grand1 = ws1.cell(tot_r1, 7, value=f"=SUM(G6:G{tot_r1-1})")
c_grand1.font = font_bold
c_grand1.alignment = align_center
c_grand1.fill = fill_calc
c_grand1.border = border_total

ws1.cell(tot_r1, 8, value="MỤC TIÊU: 711 TIẾT").font = font_bold
ws1.cell(tot_r1, 8).alignment = align_left
ws1.cell(tot_r1, 8).border = border_total
for c in range(9, 12):
    ws1.cell(tot_r1, c).border = border_total

ws1.column_dimensions['A'].width = 4.0
ws1.column_dimensions['B'].width = 6.0
ws1.column_dimensions['C'].width = 16.0
ws1.column_dimensions['D'].width = 24.0
ws1.column_dimensions['E'].width = 16.0
ws1.column_dimensions['F'].width = 18.0
ws1.column_dimensions['G'].width = 14.0
ws1.column_dimensions['H'].width = 14.0
ws1.column_dimensions['I'].width = 16.0
ws1.column_dimensions['J'].width = 22.0
ws1.column_dimensions['K'].width = 22.0

# ==============================================================================
# SHEET 2: GIAO_VIEN_LICH_BAN (Teachers & Unavailability with SUMIF)
# ==============================================================================
ws2 = wb.create_sheet(title="GIAO_VIEN_LICH_BAN")
ws2.views.sheetView[0].showGridLines = True

ws2.cell(2, 2, value="DANH SÁCH 43 GIÁO VIÊN & ĐĂNG KÝ LỊCH BẬN / KHÓA TIẾT CÁ NHÂN").font = font_title
ws2.cell(3, 2, value="Cột 'Tổng Tiết Phân Công' hoàn toàn tự động nhảy số theo công thức =SUMIF từ Sheet 1. Bạn không cần tự tính tay.").font = font_subtitle

headers_s2 = [
    "STT", "Tên Giáo Viên", "Tổ Chuyên Môn", "Chủ Nhiệm Lớp", "Phó Chủ Nhiệm", 
    "Lịch Đăng Ký Bận / Khóa Tiết Không Xếp Lịch", "Tổng Tiết Phân Công", "Ghi chú cá nhân"
]

ws2.row_dimensions[5].height = 24.0
for col_idx, h in enumerate(headers_s2, start=2):
    c = ws2.cell(5, col_idx, value=h)
    c.font = font_header
    c.fill = fill_header
    c.alignment = align_center
    c.border = border_header

# Load teacher metadata from teacher_registry.json
with open(teachers_path, "r", encoding="utf-8") as f:
    t_reg = json.load(f)
teachers_list = t_reg.get("teachers", [])

# Known PCN map
pcn_map = {
    "Phương Anh": "1A1", "Chi": "1A2", "Ngọc": "2A1", 
    "Lê": "3A1", "Lam": "3A2", "Thu": "4A1", "Liên": "5A1"
}

# Standardized concise unavailability notes
unavail_map = {
    "Quyến": "Khóa lịch: Nghỉ trọn vẹn cả ngày Thứ 4",
    "Duy": "Khóa lịch: Nghỉ sáng Thứ 2 (học chuyên môn / công tác)",
    "Catie": "Khóa lịch: Chỉ dạy các buổi sáng, tuyệt đối không dạy chiều",
    "Thuỷ": "Thỉnh giảng: Chỉ dạy sáng Thứ 4 và cả ngày Thứ 5",
    "Thiết": "Thỉnh giảng: Chỉ dạy sáng Thứ 2 và cả ngày Thứ 5",
    "Yến LS": "Thỉnh giảng: Tiết 9-10 T2, Tiết 9 T3, Tiết 4 T4, Tiết 5 T5, Tiết 4-5-8 T6",
    "Liễu": "Khóa chiều Thứ 6 sinh hoạt chuyên môn Tiểu học + Nghỉ 1 buổi tự chọn",
    "Hạnh": "Khóa chiều Thứ 6 sinh hoạt chuyên môn Tiểu học + Nghỉ 1 buổi tự chọn",
    "Tiểu Hà": "Khóa chiều Thứ 6 sinh hoạt chuyên môn Tiểu học + Nghỉ 1 buổi tự chọn",
    "Khánh Linh": "Khóa chiều Thứ 6 sinh hoạt chuyên môn Tiểu học + Nghỉ 1 buổi tự chọn",
    "Chín": "Khóa chiều Thứ 6 sinh hoạt chuyên môn Tiểu học + Nghỉ 1 buổi tự chọn",
    "Chiến": "Khóa chiều Thứ 6 sinh hoạt chuyên môn Tiểu học + Nghỉ 1 buổi tự chọn",
    "Hải": "Khóa chiều Thứ 6 sinh hoạt chuyên môn Tiểu học + Nghỉ 1 buổi tự chọn",
    "Hiền": "Khóa chiều Thứ 6 sinh hoạt chuyên môn Tiểu học + Nghỉ 1 buổi tự chọn",
    "Yên": "Giáo viên liên cấp: Tránh xếp Tiết 4 C1 (9:45-10:20) và Tiết 3 C2 (9:10-9:55)",
    "Phương Anh": "Giáo viên liên cấp: Tránh xếp Tiết 4 C1 (9:45-10:20) và Tiết 3 C2 (9:10-9:55)"
}

for idx, t in enumerate(teachers_list, start=1):
    r = 5 + idx
    ws2.row_dimensions[r].height = 20.0
    tname = t["display_name"]
    
    # Col B: STT
    ws2.cell(r, 2, value=idx).alignment = align_center
    
    # Col C: Tên Giáo Viên (Yellow)
    c_tn = ws2.cell(r, 3, value=tname)
    c_tn.alignment = align_left
    c_tn.fill = fill_input
    c_tn.font = font_bold
    
    # Col D: Tổ Chuyên Môn (Yellow)
    c_dp = ws2.cell(r, 4, value=t.get("department", ""))
    c_dp.alignment = align_left
    c_dp.fill = fill_input
    
    # Col E: Chủ Nhiệm Lớp (Yellow)
    c_hr = ws2.cell(r, 5, value=t.get("homeroom", "") or "")
    c_hr.alignment = align_center
    c_hr.fill = fill_input
    
    # Col F: Phó Chủ Nhiệm (Yellow)
    c_pcn = ws2.cell(r, 6, value=pcn_map.get(tname, ""))
    c_pcn.alignment = align_center
    c_pcn.fill = fill_input
    
    # Col G: Lịch Bận / Khóa Tiết (Yellow)
    unavail = unavail_map.get(tname, "; ".join(t.get("constraints", [])))
    c_un = ws2.cell(r, 7, value=unavail)
    c_un.alignment = align_left
    c_un.fill = fill_input
    
    # Col H: Tổng Tiết Phân Công (FORMULA: SUMIF lead + SUMIF co-teacher)
    # Target in Sheet 1: Col E = Lead Teacher, Col F = Co-Teacher, Col G = Periods
    formula_str = f"=SUMIF(PHAN_CONG_MON_HOC!E:E, C{r}, PHAN_CONG_MON_HOC!G:G) + SUMIF(PHAN_CONG_MON_HOC!F:F, C{r}, PHAN_CONG_MON_HOC!G:G)"
    c_tot = ws2.cell(r, 8, value=formula_str)
    c_tot.alignment = align_center
    c_tot.fill = fill_calc
    c_tot.font = font_bold
    
    # Col I: Ghi chú
    c_gc = ws2.cell(r, 9, value="")
    c_gc.alignment = align_left
    c_gc.fill = fill_input
    
    for c_idx in range(2, 10):
        ws2.cell(r, c_idx).border = border_cell
        if c_idx not in [3, 8]:
            ws2.cell(r, c_idx).font = font_regular

# Total Row for Teachers
tot_r2 = 6 + len(teachers_list)
ws2.row_dimensions[tot_r2].height = 26.0
c_lbl2 = ws2.cell(tot_r2, 2, value="TỔNG CỘNG TIẾT TOÀN BỘ 43 GIÁO VIÊN")
c_lbl2.font = font_bold
c_lbl2.alignment = align_right
ws2.merge_cells(start_row=tot_r2, start_column=2, end_row=tot_r2, end_column=7)
for c in range(2, 8):
    ws2.cell(tot_r2, c).border = border_total

c_grand2 = ws2.cell(tot_r2, 8, value=f"=SUM(H6:H{tot_r2-1})")
c_grand2.font = font_bold
c_grand2.alignment = align_center
c_grand2.fill = fill_calc
c_grand2.border = border_total

ws2.cell(tot_r2, 9, value="CÂN BẰNG ĐÚNG: 711 TIẾT").font = font_bold
ws2.cell(tot_r2, 9).alignment = align_left
ws2.cell(tot_r2, 9).border = border_total

ws2.column_dimensions['A'].width = 4.0
ws2.column_dimensions['B'].width = 6.0
ws2.column_dimensions['C'].width = 16.0
ws2.column_dimensions['D'].width = 18.0
ws2.column_dimensions['E'].width = 16.0
ws2.column_dimensions['F'].width = 16.0
ws2.column_dimensions['G'].width = 50.0
ws2.column_dimensions['H'].width = 20.0
ws2.column_dimensions['I'].width = 24.0

# ==============================================================================
# SHEET 3: TACH_GHEP_VA_PHAN_BAN (Merges, Grade 12 Duels & System Toggles)
# ==============================================================================
ws3 = wb.create_sheet(title="TACH_GHEP_VA_PHAN_BAN")
ws3.views.sheetView[0].showGridLines = True

ws3.cell(2, 2, value="QUY ĐỊNH TÁCH GHÉP LỚP, MA TRẬN 12 CẶP ĐỐI ỨNG LỚP 12 & CÔNG TẮC QUY TẮC SƯ PHẠM").font = font_title
ws3.cell(3, 2, value="Khai báo các cặp học chung, ma trận đối ứng phân ban Khối 12 và cấu hình nhanh các quy tắc toàn trường.").font = font_subtitle

# --- PART 1: MERGE PAIRS ---
ws3.cell(5, 2, value="PHẦN 1: DANH MỤC CÁC CẶP GHÉP LỚP VĂN HÓA CƠ SỞ (THCS & THPT)").font = font_section
headers_p1 = ["STT", "Cặp ghép", "Phòng cơ sở", "Số tiết ghép", "Môn học ghép chung", "Quy định tách môn"]
for c_idx, h in enumerate(headers_p1, start=2):
    c = ws3.cell(6, c_idx, value=h)
    c.font = font_header
    c.fill = fill_header
    c.alignment = align_center
    c.border = border_header
ws3.row_dimensions[6].height = 22.0

p1_data = [
    (1, "7A1 & 7A2", "Phòng B202", 35, "Toán, Văn, KHTN, Lịch sử - Địa lí, GDCD, Tin học, GDTC, Âm nhạc, Global Success", "Tách duy nhất môn Prepare: 7A1 sang A306 (Hoà, Catie), 7A2 tại B202 (Mela)."),
    (2, "8A1 & 8A2", "Phòng B203", 35, "Toán, Văn, KHTN, Lịch sử - Địa lí, GDCD, Tin học, GDTC, Âm nhạc, Global Success", "Tách duy nhất môn Prepare: 8A1 sang A306 (Cybele, Hoà), 8A2 tại B203 (Saloni, Hoà)."),
    (3, "12A1 & 12A2", "Phòng B205", 33, "Toán học (Duy), Ngữ văn (Thuý), GDTC & GDQPAN (Liên), TNHN (Thuý), Chào cờ, SHL", "Tách toàn bộ các môn phân ban tự chọn và bổ trợ (12 cặp đối ứng đối ngẫu 1-1)."),
]

for idx, r_data in enumerate(p1_data, start=1):
    r = 6 + idx
    ws3.row_dimensions[r].height = 22.0
    for c_idx, val in enumerate(r_data, start=2):
        cell = ws3.cell(r, c_idx, value=val)
        cell.border = border_cell
        cell.font = font_regular
        cell.alignment = align_center if c_idx in [2, 3, 4, 5] else align_left

# --- PART 2: GRADE 12 12-PAIR DUEL MATRIX ---
ws3.cell(11, 2, value="PHẦN 2: MA TRẬN 12 CẶP ĐỐI ỨNG 1-1 PHÂN BAN KHỐI 12 (TỰ NHIÊN A305 <==> XÃ HỘI B205)").font = font_section
headers_p2 = [
    "Cặp", "Thứ", "Tiết", "12A1: Môn Tự Nhiên", "12A1: Giáo Viên", "12A1: Phòng",
    "12A2: Môn Xã Hội", "12A2: Giáo Viên", "12A2: Phòng", "Tính chất", "Trạng thái đối ứng"
]
for c_idx, h in enumerate(headers_p2, start=2):
    c = ws3.cell(12, c_idx, value=h)
    c.font = font_header
    c.fill = fill_subheader
    c.alignment = align_center
    c.border = border_header
ws3.row_dimensions[12].height = 22.0

p2_data = [
    (1, "Thứ 2", "Tiết 3", "Hóa học", "Nguyệt", "Phòng A305", "Địa lí", "Thiết", "Phòng B205", "Chính khóa", "✓ Khớp 1-1"),
    (2, "Thứ 2", "Tiết 4", "Hóa học", "Nguyệt", "Phòng A305", "Địa lí", "Thiết", "Phòng B205", "Chính khóa", "✓ Khớp 1-1"),
    (3, "Thứ 2", "Tiết 9", "Global Success TC", "Nhung", "Phòng A305", "Lịch sử TC", "Yến LS", "Phòng B205", "Tăng cường", "✓ Khớp 1-1"),
    (4, "Thứ 2", "Tiết 10", "Global Success TC", "Nhung", "Phòng A305", "Lịch sử TC", "Yến LS", "Phòng B205", "Tiết 10 độc lập", "✓ Khớp 1-1"),
    (5, "Thứ 3", "Tiết 3", "Sinh học", "Giang", "Phòng A305", "Văn CĐ", "Thuý", "Phòng B205", "Chuyên đề", "✓ Khớp 1-1"),
    (6, "Thứ 3", "Tiết 9", "Vật lí BT", "Huy", "Phòng A305", "Lịch sử BT", "Yến LS", "Phòng B205", "Bổ trợ cuối ngày", "✓ Khớp 1-1"),
    (7, "Thứ 4", "Tiết 1", "Sinh học", "Giang", "Phòng A305", "GD KT - PL", "Thuỷ", "Phòng B205", "Chính khóa", "✓ Khớp 1-1"),
    (8, "Thứ 4", "Tiết 2", "Hóa học", "Nguyệt", "Phòng A305", "GD KT - PL", "Thuỷ", "Phòng B205", "Chính khóa", "✓ Khớp 1-1"),
    (9, "Thứ 5", "Tiết 7", "Hoá học BT", "Nguyệt", "Phòng A305", "GD KT-PL BT", "Thuỷ", "Phòng B205", "Bổ trợ chiều", "✓ Khớp 1-1"),
    (10, "Thứ 5", "Tiết 8", "Hoá học BT", "Nguyệt", "Phòng A305", "GD KT-PL BT", "Thuỷ", "Phòng B205", "Bổ trợ chiều", "✓ Khớp 1-1"),
    (11, "Thứ 5", "Tiết 9", "Prepare BT", "Charly", "Phòng A305", "Địa lí BT", "Thiết", "Phòng B205", "Bổ trợ cuối ngày", "✓ Khớp 1-1"),
    (12, "Thứ 6", "Tiết 9", "Prepare BT", "Charly", "Phòng A305", "Sinh học BT", "Giang", "Phòng B205", "Bổ trợ cuối ngày", "✓ Khớp 1-1"),
]

for idx, r_data in enumerate(p2_data, start=1):
    r = 12 + idx
    ws3.row_dimensions[r].height = 20.0
    for c_idx, val in enumerate(r_data, start=2):
        cell = ws3.cell(r, c_idx, value=val)
        cell.border = border_cell
        cell.font = font_bold if c_idx in [2, 12] else font_regular
        cell.alignment = align_center if c_idx in [2, 3, 4, 7, 10, 12] else align_left
        # Highlight editable subject & teacher columns in yellow
        if c_idx in [5, 6, 8, 9]:
            cell.fill = fill_input

# --- PART 3: SYSTEM RULE TOGGLES ---
ws3.cell(26, 2, value="PHẦN 3: BẢNG CÔNG TẮC BẬT/TẮT QUY TẮC SƯ PHẠM TOÀN TRƯỜNG").font = font_section
headers_p3 = ["STT", "Tên Quy Tắc Sư Phạm", "Khung Thời Gian Áp Dụng", "Trạng Thái", "Mô Tả & Hướng Dẫn Vận Hành"]
for c_idx, h in enumerate(headers_p3, start=2):
    c = ws3.cell(27, c_idx, value=h)
    c.font = font_header
    c.fill = fill_subheader
    c.alignment = align_center
    c.border = border_header
ws3.row_dimensions[27].height = 22.0

p3_data = [
    (1, "Chào cờ đồng bộ đầu tuần", "Thứ 2 - Tiết 1", "BẬT", "Toàn bộ 18 lớp học đồng loạt thực hiện nghi lễ Chào cờ tại Tiết 1 sáng Thứ 2."),
    (2, "Sinh hoạt lớp (C1) & HĐTN (C2, C3)", "Thứ 6 - Tiết 5", "BẬT", "Toàn trường tổng kết tuần học vào Tiết 5 sáng Thứ 6. GVCN trực tiếp quản lý lớp."),
    (3, "GVCN Cấp 1 nghỉ SHCM Tiểu học", "Chiều Thứ 6", "BẬT", "Toàn bộ 8 GVCN Tiểu học không được xếp tiết dạy vào chiều Thứ 6 để sinh hoạt chuyên môn."),
    (4, "Tiết Bổ trợ (BT) bắt buộc xếp cuối chiều", "Tiết 8, 9 hoặc 10", "BẬT", "Các tiết Bổ trợ kiến thức (BT) chỉ được xếp vào các tiết cuối cùng của buổi chiều, cấm xếp buổi sáng."),
    (5, "Giáo dục thể chất cách ngày", "Thứ 3+5 hoặc Thứ 4+6", "BẬT", "Xếp giãn cách tối thiểu 1 ngày giữa 2 tiết thể dục trong tuần. Tránh các tiết trưa nắng (P4, P5, P6)."),
    (6, "Stem & Robotic Cấp 1 xếp tiết kép", "Cặp {P2,P3}, {P6,P7} hoặc {P8,P9}", "BẬT", "Bắt buộc xếp liền 2 tiết thực hành liên tiếp. Cấm xếp tiết đơn lẻ."),
    (7, "Tiết 10 độc lập Cấp 2 & Cấp 3", "17:00 - 17:45 hàng ngày", "BẬT", "Dành cho các lớp có định mức lớn hoặc bồi dưỡng học sinh giỏi (10A1, 11A1, 12A1, 12A2)."),
]

for idx, r_data in enumerate(p3_data, start=1):
    r = 27 + idx
    ws3.row_dimensions[r].height = 20.0
    for c_idx, val in enumerate(r_data, start=2):
        cell = ws3.cell(r, c_idx, value=val)
        cell.border = border_cell
        cell.font = font_bold if c_idx == 5 else font_regular
        cell.alignment = align_center if c_idx in [2, 4, 5] else align_left
        if c_idx == 5:
            cell.fill = fill_input # Toggle BẬT / TẮT editable

ws3.column_dimensions['A'].width = 4.0
ws3.column_dimensions['B'].width = 6.0
ws3.column_dimensions['C'].width = 16.0
ws3.column_dimensions['D'].width = 16.0
ws3.column_dimensions['E'].width = 24.0
ws3.column_dimensions['F'].width = 18.0
ws3.column_dimensions['G'].width = 16.0
ws3.column_dimensions['H'].width = 24.0
ws3.column_dimensions['I'].width = 18.0
ws3.column_dimensions['J'].width = 16.0
ws3.column_dimensions['K'].width = 18.0
ws3.column_dimensions['L'].width = 18.0

wb.save(out_file)
print("\n==========================================================================")
print(f"🎉 COMPACT EXCEL TEMPLATE GENERATED SUCCESSFULLY: {out_file}")
print(f"   - Sheets (3): {wb.sheetnames}")
print(f"   - File size: {os.path.getsize(out_file)} bytes")
print("==========================================================================\n")
