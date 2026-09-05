"""
========================================================================================
GENERATE STANDARDIZED SMART COMPACT EXCEL TEMPLATE V2 FOR MCA TIMETABLE INPUT
Marie Curie Academy (MCA) - Academic Year 2026-2027
========================================================================================
Upgraded Smart Features (V2):
1. PHAN_CONG_MON_HOC:
   - 304 actual teaching assignments
   - Built-in 2-Way Monitoring Dashboard: 18 Classes target vs assigned periods
   - Data Validation dropdowns (Classes, Teachers, Double periods, Locations)
2. GIAO_VIEN_LICH_BAN:
   - 43 teachers
   - 10-slot Checkbox Matrix (T2_Sang -> T6_Chieu) with pre-filled 'X' for locks
   - Dynamic SUMIF formula for total periods
3. TACH_GHEP_VA_PHAN_BAN:
   - 3 basic merge pairs
   - 12 Grade 12 duel pairs
   - 7 system rule toggles
========================================================================================
"""

import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
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
print("BUILDING STANDARDIZED SMART COMPACT EXCEL TEMPLATE V2 FOR MCA TIMETABLE")
print(f"Target: {out_file}")
print("==========================================================================\n")

wb = openpyxl.Workbook()
wb.remove(wb.active) # Remove default sheet

# --- STYLES ---
font_title = Font(name="Times New Roman", size=13, bold=True, color="1B365D")
font_subtitle = Font(name="Times New Roman", size=10, italic=True, color="555555")
font_section = Font(name="Times New Roman", size=11, bold=True, color="1B365D")
font_header = Font(name="Times New Roman", size=10, bold=True, color="FFFFFF")
font_bold = Font(name="Times New Roman", size=10, bold=True, color="000000")
font_regular = Font(name="Times New Roman", size=10, color="000000")
font_status_pass = Font(name="Times New Roman", size=10, bold=True, color="006100")
font_status_fail = Font(name="Times New Roman", size=10, bold=True, color="9C0006")

fill_header = PatternFill(fill_type="solid", start_color="1B365D", end_color="1B365D") # Navy
fill_subheader = PatternFill(fill_type="solid", start_color="2C4D75", end_color="2C4D75")
fill_input = PatternFill(fill_type="solid", start_color="FFF2CC", end_color="FFF2CC") # Editable Yellow
fill_calc = PatternFill(fill_type="solid", start_color="D9E1F2", end_color="D9E1F2") # Formula Blue
fill_lock = PatternFill(fill_type="solid", start_color="FCE4D6", end_color="FCE4D6") # Soft Orange / Lock
fill_status_pass = PatternFill(fill_type="solid", start_color="C6EFCE", end_color="C6EFCE")
fill_status_fail = PatternFill(fill_type="solid", start_color="FFC7CE", end_color="FFC7CE")

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

# Load existing configurations
with open(rules_path, "r", encoding="utf-8") as f:
    rules_cfg = json.load(f)
with open(teachers_path, "r", encoding="utf-8") as f:
    teachers_cfg = json.load(f)

# ==============================================================================
# 0. EXTRACT ACTUAL DATA FROM MASTER TKB
# ==============================================================================
wb_master = openpyxl.load_workbook(master_file, data_only=True)
ws4_teach = wb_master['TKB Giáo viên']

CLASS_PATTERNS = ['1A1','1A2','2A1','2A2','3A1','3A2','4A1','5A1','6A1','7A1','7A2','8A1','8A2','9A1','10A1','11A1','12A1','12A2']

def parse_cell_content(cell_str):
    lines = [l.strip() for l in cell_str.split('\n') if l.strip()]
    if not lines: return None, None, None
    line0 = lines[0]
    rooms = []
    classes = set()
    first_subj = ''
    
    for l in lines:
        for rm in re.findall(r'\((.*?)\)', l):
            rooms.append(rm.strip())
        line_clean = re.sub(r'\(.*?\)', '', l).strip()
        first_idx = len(line_clean)
        found_in_line = []
        for c in CLASS_PATTERNS:
            m = re.search(rf'\b{c}\b', line_clean)
            if m:
                classes.add(c)
                found_in_line.append(c)
                if m.start() < first_idx:
                    first_idx = m.start()
        if not first_subj and found_in_line:
            first_subj = line_clean[:first_idx].rstrip(' -').strip()
            
    if not first_subj:
        first_subj = re.sub(r'\(.*?\)', '', line0).strip()
        
    c_str = ', '.join(sorted(classes))
    r_str = ', '.join(sorted(set(rooms)))
    return first_subj, c_str, r_str

raw_assignments = []
for c in range(4, ws4_teach.max_column + 1):
    tname = ws4_teach.cell(4, c).value
    if not tname: continue
    tname = tname.strip()
    
    t_dict = defaultdict(int)
    for r in range(5, ws4_teach.max_row + 1):
        tiet = ws4_teach.cell(r, 3).value
        if tiet is None or not isinstance(tiet, (int, float)): continue
        val = ws4_teach.cell(r, c).value
        if val and isinstance(val, str):
            subj, c_str, r_str = parse_cell_content(str(val))
            if not subj or not c_str: continue
            # If Chi is co-teaching Bo tro in 4A1 or 5A1, skip adding as lead
            if tname == 'Chi' and ('Bổ trợ' in subj or 'Bo tro' in subj):
                continue
            t_dict[(subj, c_str, r_str)] += 1
            
    for (subj, c_str, r_str), count in t_dict.items():
        is_double = "Có" if any(k in subj for k in ["Stem", "Toán", "Văn", "Tiếng Việt"]) else "Không"
        loc = "Không yêu cầu"
        if "(BT)" in subj or "Bổ trợ" in subj or " BT" in subj or bool(re.search(r'\bTC\b', subj)):
            loc = "Cuối chiều (Bổ trợ)"
        elif "Bồi giỏi" in subj or "Tiết 10" in subj:
            loc = "Tiết 10"
        elif "Chào cờ" in subj:
            loc = "Chào cờ (T1 sáng T2)"
        elif "Sinh hoạt lớp" in subj or "HĐTN" in subj:
            loc = "SHL (T5 sáng T6)"

        co_t = ""
        if tname == 'Hải' and ('Bổ trợ' in subj) and c_str == '4A1':
            co_t = 'Chi'
        elif tname == 'Hiền' and ('Bổ trợ' in subj) and c_str == '5A1':
            co_t = 'Chi'

        raw_assignments.append({
            "class_name": c_str,
            "subject_name": subj,
            "lead_teacher": tname,
            "co_teacher": co_t,
            "periods": count,
            "is_double": is_double,
            "room": r_str if r_str not in ["B201","B202","B203","B204","B205","B206","B301","B302","B303","B304","B305","B306","B307","B308"] else "",
            "location_req": loc,
            "note": ""
        })

def sort_key(a):
    c = a["class_name"]
    order = ["1A1", "1A2", "2A1", "2A2", "3A1", "3A2", "4A1", "5A1", "6A1", "7A1", "7A2", "7A1, 7A2", "8A1", "8A2", "8A1, 8A2", "9A1", "10A1", "11A1", "12A1", "12A2", "12A1, 12A2"]
    c_idx = order.index(c) if c in order else 99
    return (c_idx, a["subject_name"], a["lead_teacher"])

raw_assignments.sort(key=sort_key)

# ==============================================================================
# SHEET 1: PHAN_CONG_MON_HOC & BẢNG GIÁM SÁT 18 LỚP HỌC (2-WAY EQUILIBRIUM)
# ==============================================================================
ws1 = wb.create_sheet(title="PHAN_CONG_MON_HOC")
ws1.views.sheetView[0].showGridLines = True

ws1.cell(2, 2, value="BẢNG PHÂN CÔNG GIẢNG DẠY (SOURCE OF TRUTH) & BẢNG GIÁM SÁT ĐỊNH MỨC 18 LỚP").font = font_title
ws1.cell(3, 2, value="Khu vực bên trái là phân công chi tiết. Khu vực bên phải (cột M -> Q) là bảng kiểm soát cân bằng định mức từng lớp học.").font = font_subtitle

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
    
    ws1.cell(r, 2, value=idx).alignment = align_center
    c_cls = ws1.cell(r, 3, value=a["class_name"])
    c_cls.alignment = align_center
    c_cls.fill = fill_input
    c_cls.font = font_bold
    
    c_sub = ws1.cell(r, 4, value=a["subject_name"])
    c_sub.alignment = align_left
    c_sub.fill = fill_input
    
    c_tea = ws1.cell(r, 5, value=a["lead_teacher"])
    c_tea.alignment = align_center
    c_tea.fill = fill_input
    c_tea.font = font_bold
    
    c_co = ws1.cell(r, 6, value=a["co_teacher"])
    c_co.alignment = align_center
    c_co.fill = fill_input
    
    c_per = ws1.cell(r, 7, value=a["periods"])
    c_per.alignment = align_center
    c_per.fill = fill_input
    c_per.font = font_bold
    
    c_db = ws1.cell(r, 8, value=a["is_double"])
    c_db.alignment = align_center
    c_db.fill = fill_input
    
    c_rm = ws1.cell(r, 9, value=a["room"])
    c_rm.alignment = align_center
    c_rm.fill = fill_input
    
    c_loc = ws1.cell(r, 10, value=a["location_req"])
    c_loc.alignment = align_left
    c_loc.fill = fill_input
    
    c_nt = ws1.cell(r, 11, value=a["note"])
    c_nt.alignment = align_left
    c_nt.fill = fill_input
    
    for c_idx in range(2, 12):
        ws1.cell(r, c_idx).border = border_cell
        if c_idx not in [3, 5, 7]:
            ws1.cell(r, c_idx).font = font_regular

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

# --- BẢNG GIÁM SÁT ĐỊNH MỨC 18 LỚP HỌC (COLUMNS M TO Q) ---
headers_monitor = ["STT", "Tên Lớp", "Định Mức Chuẩn", "Đã Phân Công", "Trạng Thái Kiểm Toán"]
ws1.cell(4, 13, value="BẢNG GIÁM SÁT CÂN BẰNG ĐỊNH MỨC 18 LỚP HỌC").font = font_section
for col_idx, h in enumerate(headers_monitor, start=13):
    c = ws1.cell(5, col_idx, value=h)
    c.font = font_header
    c.fill = fill_subheader
    c.alignment = align_center
    c.border = border_header

classes_target = [
    (1, "1A1", 45, "Tiểu học"),
    (2, "1A2", 50, "Song ngữ"),
    (3, "2A1", 45, "Tiểu học"),
    (4, "2A2", 50, "Song ngữ"),
    (5, "3A1", 45, "Tiểu học"),
    (6, "3A2", 50, "Song ngữ"),
    (7, "4A1", 45, "Tiểu học"),
    (8, "5A1", 45, "Tiểu học"),
    (9, "6A1", 39, "THCS"),
    (10, "7A1", 39, "THCS"),
    (11, "7A2", 44, "Song ngữ"),
    (12, "8A1", 39, "THCS"),
    (13, "8A2", 44, "Song ngữ"),
    (14, "9A1", 44, "THCS"),
    (15, "10A1", 47, "THPT"),
    (16, "11A1", 45, "THPT"),
    (17, "12A1", 45, "THPT"),
    (18, "12A2", 45, "THPT"),
]

for idx, (stt, cname, target, tier) in enumerate(classes_target, start=1):
    r = 5 + idx
    ws1.row_dimensions[r].height = 20.0
    
    # Col M: STT
    ws1.cell(r, 13, value=stt).alignment = align_center
    ws1.cell(r, 13).font = font_regular
    ws1.cell(r, 13).border = border_cell
    
    # Col N: Tên Lớp
    ws1.cell(r, 14, value=cname).alignment = align_center
    ws1.cell(r, 14).font = font_bold
    ws1.cell(r, 14).border = border_cell
    
    # Col O: Định Mức Chuẩn
    ws1.cell(r, 15, value=target).alignment = align_center
    ws1.cell(r, 15).font = font_bold
    ws1.cell(r, 15).border = border_cell
    
    # Col P: Đã Phân Công (Công thức SUMIF)
    if cname in ["7A1", "7A2"]:
        form_assigned = f"=SUMIF(C:C, N{r}, G:G) + SUMIF(C:C, \"7A1, 7A2\", G:G)"
    elif cname in ["8A1", "8A2"]:
        form_assigned = f"=SUMIF(C:C, N{r}, G:G) + SUMIF(C:C, \"8A1, 8A2\", G:G)"
    elif cname in ["12A1", "12A2"]:
        form_assigned = f"=SUMIF(C:C, N{r}, G:G) + SUMIF(C:C, \"12A1, 12A2\", G:G)"
    else:
        form_assigned = f"=SUMIF(C:C, N{r}, G:G)"
        
    c_p = ws1.cell(r, 16, value=form_assigned)
    c_p.alignment = align_center
    c_p.fill = fill_calc
    c_p.font = font_bold
    c_p.border = border_cell
    
    # Col Q: Trạng Thái
    form_status = f"=IF(P{r}=O{r}, \"✓ ĐỦ\", IF(P{r}>O{r}, \"✗ THỪA \" & (P{r}-O{r}), \"✗ THIẾU \" & (O{r}-P{r})))"
    c_q = ws1.cell(r, 17, value=form_status)
    c_q.alignment = align_center
    c_q.font = font_bold
    c_q.border = border_cell

# Total Row for Monitor
r_mon_tot = 24
ws1.cell(r_mon_tot, 13, value="TỔNG TIẾT LỚP HỌC").alignment = align_right
ws1.cell(r_mon_tot, 13).font = font_bold
ws1.merge_cells(start_row=r_mon_tot, start_column=13, end_row=r_mon_tot, end_column=14)
for c in range(13, 15):
    ws1.cell(r_mon_tot, c).border = border_total

c_tot_target = ws1.cell(r_mon_tot, 15, value=f"=SUM(O6:O23)")
c_tot_target.alignment = align_center
c_tot_target.font = font_bold
c_tot_target.border = border_total

c_tot_actual = ws1.cell(r_mon_tot, 16, value=f"=SUM(P6:P23)")
c_tot_actual.alignment = align_center
c_tot_actual.font = font_bold
c_tot_actual.fill = fill_calc
c_tot_actual.border = border_total

c_tot_st = ws1.cell(r_mon_tot, 17, value=f"=IF(P{r_mon_tot}=O{r_mon_tot}, \"✓ CÂN BẰNG 806T\", \"✗ LỆCH\")")
c_tot_st.alignment = align_center
c_tot_st.font = font_bold
c_tot_st.border = border_total

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
ws1.column_dimensions['K'].width = 20.0
ws1.column_dimensions['L'].width = 4.0
ws1.column_dimensions['M'].width = 6.0
ws1.column_dimensions['N'].width = 12.0
ws1.column_dimensions['O'].width = 16.0
ws1.column_dimensions['P'].width = 16.0
ws1.column_dimensions['Q'].width = 20.0

# ==============================================================================
# SHEET 2: GIAO_VIEN_LICH_BAN (With 10-Slot Checkbox Matrix)
# ==============================================================================
ws2 = wb.create_sheet(title="GIAO_VIEN_LICH_BAN")
ws2.views.sheetView[0].showGridLines = True

ws2.cell(2, 2, value="DANH SÁCH 43 GIÁO VIÊN & MA TRẬN 10 BUỔI ĐĂNG KÝ LỊCH BẬN (CHECKBOX 'X')").font = font_title
ws2.cell(3, 2, value="Giáo viên bận buổi nào, bạn chỉ cần gõ chữ 'X' vào ô đó. Cột Tổng tiết phân công tự động tính bằng =SUMIF từ Sheet 1.").font = font_subtitle

headers_s2 = [
    "STT", "Tên Giáo Viên", "Tổ Chuyên Môn", "Chủ Nhiệm", "Phó Chủ Nhiệm",
    "T2_Sang", "T2_Chieu", "T3_Sang", "T3_Chieu", "T4_Sang", "T4_Chieu", "T5_Sang", "T5_Chieu", "T6_Sang", "T6_Chieu",
    "Tổng Tiết Phân Công", "Ghi chú cá nhân"
]

ws2.row_dimensions[5].height = 24.0
for col_idx, h in enumerate(headers_s2, start=2):
    c = ws2.cell(5, col_idx, value=h)
    c.font = font_header
    c.fill = fill_subheader if col_idx in range(7, 17) else fill_header
    c.alignment = align_center
    c.border = border_header

teachers_list = teachers_cfg.get("teachers", [])

# Mapping of blocked sessions (day 0..4, session 0..1) -> checkbox 'X'
# Sessions: 0=Sáng, 1=Chiều. Days: 0=T2, 1=T3, 2=T4, 3=T5, 4=T6
# Columns in Excel:
# Col 7: T2_Sang, Col 8: T2_Chieu, Col 9: T3_Sang, Col 10: T3_Chieu
# Col 11: T4_Sang, Col 12: T4_Chieu, Col 13: T5_Sang, Col 14: T5_Chieu
# Col 15: T6_Sang, Col 16: T6_Chieu

pcn_map = {
    "Phương Anh": "1A1", "Chi": "1A2", "Ngọc": "2A1", 
    "Lê": "3A1", "Lam": "3A2", "Thu": "4A1", "Liên": "5A1"
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
    
    # Col G to P (7 to 16): 10 Checkbox columns
    # Determine pre-filled locks
    blocked_cols = set()
    if tname == "Quyến":
        blocked_cols.update([11, 12]) # T4_Sang, T4_Chieu
    elif tname == "Duy":
        blocked_cols.add(7) # T2_Sang
    elif tname == "Catie":
        blocked_cols.update([8, 10, 12, 14, 16]) # Chiều cả tuần
    elif tname == "Thuỷ":
        # Only Wed am + all Thu -> Blocked: T2(S,C), T3(S,C), T4(C), T6(S,C)
        blocked_cols.update([7, 8, 9, 10, 12, 15, 16])
    elif tname == "Thiết":
        # Only Mon am + all Thu -> Blocked: T2(C), T3(S,C), T4(S,C), T6(S,C)
        blocked_cols.update([8, 9, 10, 11, 12, 15, 16])
    elif tname == "Yến LS":
        # Only Mon pm + Tue pm -> Blocked: T2(S), T3(S), T4(S,C), T5(S,C), T6(S,C)
        blocked_cols.update([7, 9, 11, 12, 13, 14, 15, 16])
    elif tname in ["Liễu", "Hạnh", "Tiểu Hà", "Khánh Linh", "Chín", "Chiến", "Hải", "Hiền"]:
        blocked_cols.add(16) # T6_Chieu (SHCM)

    for c_idx in range(7, 17):
        is_blocked = c_idx in blocked_cols
        val = "X" if is_blocked else ""
        c_chk = ws2.cell(r, c_idx, value=val)
        c_chk.alignment = align_center
        c_chk.font = font_bold if is_blocked else font_regular
        c_chk.fill = fill_lock if is_blocked else fill_input
    
    # Col Q (17): Tổng Tiết Phân Công (FORMULA: SUMIF lead + SUMIF co-teacher)
    formula_str = f"=SUMIF(PHAN_CONG_MON_HOC!E:E, C{r}, PHAN_CONG_MON_HOC!G:G) + SUMIF(PHAN_CONG_MON_HOC!F:F, C{r}, PHAN_CONG_MON_HOC!G:G)"
    c_tot = ws2.cell(r, 17, value=formula_str)
    c_tot.alignment = align_center
    c_tot.fill = fill_calc
    c_tot.font = font_bold
    
    # Col R (18): Ghi chú
    note_str = "; ".join(t.get("constraints", []))
    c_gc = ws2.cell(r, 18, value=note_str)
    c_gc.alignment = align_left
    c_gc.fill = fill_input
    
    for c_idx in range(2, 19):
        ws2.cell(r, c_idx).border = border_cell
        if c_idx not in [3, 17] and c_idx not in range(7, 17):
            ws2.cell(r, c_idx).font = font_regular

# Total Row for Teachers
tot_r2 = 6 + len(teachers_list)
ws2.row_dimensions[tot_r2].height = 26.0
c_lbl2 = ws2.cell(tot_r2, 2, value="TỔNG CỘNG TIẾT TOÀN BỘ 43 GIÁO VIÊN")
c_lbl2.font = font_bold
c_lbl2.alignment = align_right
ws2.merge_cells(start_row=tot_r2, start_column=2, end_row=tot_r2, end_column=16)
for c in range(2, 17):
    ws2.cell(tot_r2, c).border = border_total

c_grand2 = ws2.cell(tot_r2, 17, value=f"=SUM(Q6:Q{tot_r2-1})")
c_grand2.font = font_bold
c_grand2.alignment = align_center
c_grand2.fill = fill_calc
c_grand2.border = border_total

ws2.cell(tot_r2, 18, value="CÂN BẰNG ĐÚNG: 711 TIẾT").font = font_bold
ws2.cell(tot_r2, 18).alignment = align_left
ws2.cell(tot_r2, 18).border = border_total

ws2.column_dimensions['A'].width = 4.0
ws2.column_dimensions['B'].width = 6.0
ws2.column_dimensions['C'].width = 16.0
ws2.column_dimensions['D'].width = 16.0
ws2.column_dimensions['E'].width = 14.0
ws2.column_dimensions['F'].width = 16.0
ws2.column_dimensions['G'].width = 10.0
ws2.column_dimensions['H'].width = 10.0
ws2.column_dimensions['I'].width = 10.0
ws2.column_dimensions['J'].width = 10.0
ws2.column_dimensions['K'].width = 10.0
ws2.column_dimensions['L'].width = 10.0
ws2.column_dimensions['M'].width = 10.0
ws2.column_dimensions['N'].width = 10.0
ws2.column_dimensions['O'].width = 10.0
ws2.column_dimensions['P'].width = 10.0
ws2.column_dimensions['Q'].width = 20.0
ws2.column_dimensions['R'].width = 35.0

# ==============================================================================
# SHEET 3: TACH_GHEP_VA_PHAN_BAN (Merges, Grade 12 Duels & System Toggles)
# ==============================================================================
ws3 = wb.create_sheet(title="TACH_GHEP_VA_PHAN_BAN")
ws3.views.sheetView[0].showGridLines = True

ws3.cell(2, 2, value="QUY ĐỊNH TÁCH GHÉP LỚP, MA TRẬN 12 CẶP ĐỐI ỨNG LỚP 12 & CÔNG TẮC QUY TẮC SƯ PHẠM").font = font_title
ws3.cell(3, 2, value="Khai báo các cặp học chung, ma trận đối ứng phân ban Khối 12 và cấu hình nhanh các quy tắc toàn trường.").font = font_subtitle

# Part 1: Merge pairs
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

# Part 2: Grade 12 12-Pair Duel Matrix
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
        if c_idx in [5, 6, 8, 9]:
            cell.fill = fill_input

# Part 3: System rule toggles
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
            cell.fill = fill_input

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
print(f"🎉 SMART COMPACT EXCEL TEMPLATE V2 GENERATED: {out_file}")
print(f"   - Sheets (3): {wb.sheetnames}")
print(f"   - Checkbox Matrix (10 slots): Col G to P in GIAO_VIEN_LICH_BAN")
print(f"   - 2-Way Monitoring Dashboard: Col M to Q in PHAN_CONG_MON_HOC")
print(f"   - File size: {os.path.getsize(out_file)} bytes")
print("==========================================================================\n")
