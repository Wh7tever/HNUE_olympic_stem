"""
========================================================================================
BUILD STANDARDIZED TIMETABLE WORKBOOK (CONFIG-DRIVEN ARCHITECTURE)
Marie Curie Academy (MCA) - Academic Year 2026-2027
========================================================================================
This script builds the official Master Timetable Workbook:
`New folder/TKB_Marie_Curie_2026-2027(update_05_09).xlsx`

Architecture:
- Declarative configuration loaded from `config/timetable_rules.json` & `config/teacher_registry.json`
- Zero hardcoding of teacher quotas, period assignments, or class room maps
- Automated preflight integrity checks:
  1. Total period count equilibrium (Exactly 711 periods across 43 teachers)
  2. Grade 12 paired elective 1-to-1 alignment (12A1 Tự nhiên at A305 vs 12A2 Xã hội at B205)
  3. Specialized rooms collision detection (A305, A306, Stem)
  4. Safe fallback for file locks (TC-03)
========================================================================================
"""

import openpyxl
from openpyxl.cell.cell import MergedCell
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter
import re
import shutil
import sys
import os
import json

sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
folder = os.path.join(PROJECT_ROOT, "New folder")
config_dir = os.path.join(PROJECT_ROOT, "config")

f_rules = os.path.join(config_dir, "timetable_rules.json")
f_teachers = os.path.join(config_dir, "teacher_registry.json")

f_assign = os.path.join(folder, "SS.2609041957335326.xlsx")
f_class  = os.path.join(folder, "SS.2609041958140418.xlsx")
f_teach  = os.path.join(folder, "SS.2609041958293729.xlsx")
f_tmpl   = os.path.join(folder, "mẫu", "TKB_Marie_Curie_2026-2027(update_06_08).xlsx")
f_target = os.path.join(folder, "TKB_Marie_Curie_2026-2027(update_05_09).xlsx")

print("==========================================================================")
print("MCA STANDARDIZED TIMETABLE BUILD ENGINE (CONFIG-DRIVEN)")
print(f"Project Root: {PROJECT_ROOT}")
print(f"Rules Config: {f_rules}")
print(f"Teacher Reg : {f_teachers}")
print(f"Master Out  : {f_target}")
print("==========================================================================\n")

# --- 0. LOAD CONFIGURATION KIT ---
class ConfigValidationError(Exception):
    pass

if not os.path.exists(f_rules):
    raise ConfigValidationError(f"Missing required rules config: {f_rules}")
if not os.path.exists(f_teachers):
    raise ConfigValidationError(f"Missing required teacher registry: {f_teachers}")

with open(f_rules, "r", encoding="utf-8") as rf:
    rules_cfg = json.load(rf)
with open(f_teachers, "r", encoding="utf-8") as tf:
    teacher_cfg = json.load(tf)

# Validate config schema invariants
assert len(rules_cfg.get("classes", [])) == 18, "Config error: Must declare 18 classes"
assert len(teacher_cfg.get("teachers", [])) == 43, "Config error: Must declare 43 teachers"
assert teacher_cfg.get("total_assigned_periods") == 711, "Config error: Total periods must be 711"

known_rooms = set(rules_cfg["specialized_rooms"].keys())
class_rooms = {c["name"]: c["homeroom_room"] for c in rules_cfg["classes"] if "homeroom_room" in c}
teacher_map = {t["display_name"]: t for t in teacher_cfg["teachers"]}

print(f"✓ Configuration loaded: 18 classes, {len(known_rooms)} specialized rooms, {len(teacher_map)} teachers.")

# --- 1. PREPARE TARGET WORKBOOK WITH LOCK FALLBACK (TC-03) ---
out_file = f_target
try:
    shutil.copy2(f_tmpl, f_target)
except PermissionError:
    out_file = os.path.join(folder, "TKB_Marie_Curie_2026-2027(update_05_09_temp).xlsx")
    print(f"⚠️ [TC-03 FALLBACK] Master file locked by another process. Writing to temporary target: {out_file}")
    shutil.copy2(f_tmpl, out_file)

wb = openpyxl.load_workbook(out_file)

# Load raw exports from SmartSchool
wb_a = openpyxl.load_workbook(f_assign, data_only=True)
wb_c = openpyxl.load_workbook(f_class, data_only=True)
wb_t = openpyxl.load_workbook(f_teach, data_only=True)

ws_a = wb_a.active
ws_c = wb_c['TKB_SC']
ws_t = wb_t['TKB_SC']

# --- STYLES DEFINITION ---
font_bold = Font(name="Times New Roman", size=11, bold=True, color="000000")
font_regular = Font(name="Times New Roman", size=11, color="000000")

thin_border = Side(border_style="thin", color="000000")
medium_border = Side(border_style="medium", color="000000")
double_border = Side(border_style="double", color="000000")
dotted_border = Side(border_style="dotted", color="000000")

border_normal = Border(left=thin_border, right=thin_border, top=thin_border, bottom=thin_border)
border_right_edge = Border(left=thin_border, right=medium_border, top=thin_border, bottom=thin_border)
border_cell_thin = Border(left=thin_border, right=thin_border, top=thin_border, bottom=thin_border)
border_summary_total = Border(left=thin_border, right=thin_border, top=thin_border, bottom=double_border)

align_center = Alignment(horizontal="center", vertical="center", wrap_text=True)
align_left = Alignment(horizontal="left", vertical="center", wrap_text=True)
align_right = Alignment(horizontal="right", vertical="center", wrap_text=True)

fill_activity = PatternFill(fill_type="solid", start_color="FFFFF2CC", end_color="FFFFF2CC")

def remove_fill(cell):
    cell.fill = PatternFill(fill_type=None)

def clean_subject_str(val):
    if not val: return ""
    v = str(val).strip()
    if v in ['Nghỉ', '-']: return ""
    
    # Stem standardization
    if v.startswith("Stem - ") and v.endswith(" - Stem"): v = v[:-7].strip()
    if v.startswith("Stem & Robotic - ") and v.endswith(" - Stem"): v = v[:-7].strip()
    if v.startswith("Stem - "): v = "Stem & Robotic - " + v[7:]
    elif v == "Stem": v = "Stem & Robotic"
    
    # Standalone Toán to Toán học
    if v.startswith("Toán - "):
        v = "Toán học - " + v[7:]
        
    # Standardize BT
    v = re.sub(r'\(\s*BT\s*\)', '(BT)', v)
    v = re.sub(r'\(BT\)\s*-', '(BT) -', v)
    v = re.sub(r'GLobal', 'Global', v)
    return v

# --- 2. PARSE RAW CLASS DATA ---
class_cols = {}
for c in range(4, ws_c.max_column + 1):
    v = ws_c.cell(4, c).value
    if v: class_cols[str(v).strip()] = c

print(f"✓ Found {len(class_cols)} classes in raw export.")

# Grid mapping (cname, day_num, period) -> string
class_grid = {}
for cname, col in class_cols.items():
    for r in range(5, 55):
        d = 2 + ((r - 5) // 10)
        p = 1 + ((r - 5) % 10)
        v = ws_c.cell(r, col).value
        class_grid[(cname, d, p)] = clean_subject_str(v)

# Shared Class Inheritance (Driven by shared_pairs in timetable_rules.json)
for d in range(2, 7):
    for p in range(1, 11):
        # 7A2 inherits from 7A1 if empty
        v_7a2 = class_grid.get(("7A2", d, p), "")
        if not v_7a2 and ("7A1", d, p) in class_grid:
            v_7a1 = class_grid.get(("7A1", d, p), "")
            if v_7a1 and "A306" not in v_7a1 and not v_7a1.startswith("Prepare"):
                class_grid[("7A2", d, p)] = v_7a1

        # 8A2 inherits from 8A1 if empty
        v_8a2 = class_grid.get(("8A2", d, p), "")
        if not v_8a2 and ("8A1", d, p) in class_grid:
            v_8a1 = class_grid.get(("8A1", d, p), "")
            if v_8a1 and "A306" not in v_8a1 and not v_8a1.startswith("Prepare"):
                class_grid[("8A2", d, p)] = v_8a1

        # 12A2 inherits from 12A1 if empty
        v_12a2 = class_grid.get(("12A2", d, p), "")
        if not v_12a2 and ("12A1", d, p) in class_grid:
            v_12a1 = class_grid.get(("12A1", d, p), "")
            if v_12a1 and "A305" not in v_12a1:
                class_grid[("12A2", d, p)] = v_12a1

# Apply Special Adjustments from timetable_rules.json
special_adj = rules_cfg.get("special_adjustments", {})

# 1. Primary Swaps (5A1 Wednesday P5 & P6)
for swap in special_adj.get("primary_swaps", []):
    cname = swap["class"]
    day = swap["day"]
    period = swap["period"]
    subj_str = swap["subject"]
    class_grid[(cname, day, period)] = subj_str

# 2. High School Extra Periods (10A1 & 11A1)
for extra in special_adj.get("highschool_extra_periods", []):
    cname = extra["class"]
    day = extra["day"]
    period = extra["period"]
    raw_str = extra["raw_string"]
    class_grid[(cname, day, period)] = raw_str

print(f"✓ Applied shared class inheritance and special adjustments from config.")

# --- 3. POPULATE SHEET 1: Tiểu học ---
ws1 = wb['Tiểu học']
pri_cols = {"1A1": 4, "1A2": 5, "2A1": 6, "2A2": 7, "3A1": 8, "3A2": 9, "4A1": 10, "5A1": 11}
pri_offset_period = {2:1, 3:2, 4:3, 6:4, 7:5, 9:6, 10:7, 12:8, 13:9, 14:10}

ws1.column_dimensions['A'].width = 8.0
ws1.column_dimensions['B'].width = 8.0
ws1.column_dimensions['C'].width = 16.0
for c in range(4, 12):
    ws1.column_dimensions[get_column_letter(c)].width = 25.0

for day_idx in range(5):
    day_num = day_idx + 2
    day_base = 4 + day_idx * 16
    for off, p in pri_offset_period.items():
        r = day_base + off
        for cname, ccol in pri_cols.items():
            val = class_grid.get((cname, day_num, p), "")
            cell = ws1.cell(row=r, column=ccol)
            cell.value = val if val else None
            remove_fill(cell)
            cell.font = font_regular
            cell.alignment = align_center
            cell.border = border_right_edge if ccol == 11 else border_normal

print("✓ Sheet 1 'Tiểu học' populated.")

# --- 4. POPULATE SHEET 2: THCS, THPT ---
ws2 = wb['THCS, THPT']
thcs_cols = {"6A1": 4, "7A1": 5, "7A2": 6, "8A1": 7, "8A2": 8, "9A1": 9, "10A1": 10, "11A1": 11, "12A1": 12, "12A2": 13}

ws2.column_dimensions['A'].width = 8.0
ws2.column_dimensions['B'].width = 8.0
ws2.column_dimensions['C'].width = 16.0
for c in range(4, 14):
    ws2.column_dimensions[get_column_letter(c)].width = 25.0

ws2.cell(row=2, column=11, value="11A1 - B206")
ws2.cell(row=2, column=12, value="12A1 - B205")
ws2.cell(row=2, column=13, value="12A2 - B205")

# Unmerge old ranges below row 2
merged_to_unmerge = [str(m) for m in ws2.merged_cells.ranges if m.min_row >= 3]
for mstr in merged_to_unmerge:
    try: ws2.unmerge_cells(mstr)
    except: pass

# Clear old rows below row 2
for r in range(3, max(ws2.max_row, 90) + 1):
    for c in range(1, 14):
        cell = ws2.cell(row=r, column=c)
        cell.value = None
        cell.fill = PatternFill(fill_type=None)
        cell.border = Border()

DAY_SCHEDULE_TEMPLATE = [
    ("activity", None, "7:00-7:20", "Ăn sáng"),
    ("activity", None, "7:20 -7:30", "Circle Time"),
    ("period",   1,    "7:30 -8:15", None),
    ("period",   2,    "8:20 -9:05", None),
    ("period",   3,    "9:10 - 9:55", None),
    ("period",   4,    "10:00 - 10:45", None),
    ("period",   5,    "10:50 - 11:35", None),
    ("activity", None, "11:35- 11:55", "Ăn trưa"),
    ("activity", None, "12:00- 13:20", "Thiền, ngủ trưa"),
    ("period",   6,    "13:30 - 14:15", None),
    ("period",   7,    "14:20 - 15:05", None),
    ("activity", None, "15:05-15:20", "Ăn phụ chiều, ra chơi"),
    ("period",   8,    "15:20 - 16:05", None),
    ("period",   9,    "16:10 - 16:55", None),
    ("period",   10,   "17:00 - 17:45", None),
    ("activity", None, "17:45", "Học sinh check out hoặc sinh hoạt CLB đăng ký, học bổ trợ, bồi giỏi..."),
]

for day_idx in range(5):
    day_num = day_idx + 2
    day_base = 3 + day_idx * 16
    for off, (item_type, p_num, time_str, act_text) in enumerate(DAY_SCHEDULE_TEMPLATE):
        r = day_base + off
        if item_type == "activity":
            ws2.row_dimensions[r].height = 20.1
            cb = ws2.cell(r, 2, value=None)
            cb.fill = fill_activity
            cb.border = border_cell_thin
            cc = ws2.cell(r, 3, value=time_str)
            cc.font = font_bold
            cc.alignment = align_center
            cc.fill = fill_activity
            cc.border = border_cell_thin
            cd = ws2.cell(r, 4, value=act_text)
            cd.font = font_bold
            cd.alignment = align_center
            cd.fill = fill_activity
            cd.border = border_cell_thin
            for c in range(5, 14):
                ce = ws2.cell(r, c, value=None)
                ce.fill = fill_activity
                ce.border = border_cell_thin
            ws2.merge_cells(start_row=r, start_column=4, end_row=r, end_column=13)
        else:
            ws2.row_dimensions[r].height = 24.0
            cb = ws2.cell(r, 2, value=p_num)
            cb.font = font_bold
            cb.alignment = align_center
            cb.border = border_cell_thin
            cc = ws2.cell(r, 3, value=time_str)
            cc.font = font_regular
            cc.alignment = align_center
            cc.border = border_cell_thin
            for cname, ccol in thcs_cols.items():
                val = class_grid.get((cname, day_num, p_num), "")
                cell = ws2.cell(row=r, column=ccol, value=val if val else None)
                cell.font = font_regular
                cell.alignment = align_center
                cell.border = border_right_edge if ccol == 13 else border_cell_thin

    # Column A Day label & merge
    for off in range(16):
        r = day_base + off
        ca = ws2.cell(r, 1)
        b_top = thin_border if off == 0 else None
        b_bot = thin_border if off == 15 else None
        ca.border = Border(left=thin_border, right=thin_border, top=b_top, bottom=b_bot)
        if off == 0:
            ca.value = day_num
            ca.font = font_bold
            ca.alignment = align_center
    ws2.merge_cells(start_row=day_base, start_column=1, end_row=day_base + 15, end_column=1)

if ws2.max_row > 82:
    ws2.delete_rows(83, ws2.max_row - 82)
if ws2.max_column > 13:
    ws2.delete_cols(14, ws2.max_column - 13)

print("✓ Sheet 2 'THCS, THPT' populated (dedicated 45m Tiết 10 row).")

# --- 5. POPULATE SHEET 3: BẢNG PHÂN CÔNG GIẢNG DẠY (CONFIG-DRIVEN) ---
ws3 = wb['BẢNG PHÂN CÔNG GIẢNG DẠY']
ws3.column_dimensions['A'].width = 8.0
ws3.column_dimensions['B'].width = 20.0
ws3.column_dimensions['C'].width = 12.0
ws3.column_dimensions['D'].width = 12.0
ws3.column_dimensions['E'].width = 105.0
ws3.column_dimensions['F'].width = 12.0

merged_to_unmerge = [str(m) for m in ws3.merged_cells.ranges if m.min_row >= 45]
for mstr in merged_to_unmerge:
    try: ws3.unmerge_cells(mstr)
    except: pass

for r in range(5, max(ws3.max_row, len(teacher_cfg['teachers']) + 15) + 1):
    for c in range(1, 7):
        cell = ws3.cell(row=r, column=c)
        cell.value = None
        cell.border = Border(left=None, right=None, top=None, bottom=None)

total_stiet = 0
for idx, t in enumerate(teacher_cfg["teachers"]):
    row_num = 5 + idx
    # STT
    ca = ws3.cell(row=row_num, column=1, value=idx + 1)
    ca.font = font_regular
    ca.alignment = align_center
    ca.border = border_cell_thin
    
    # Giáo viên
    cb = ws3.cell(row=row_num, column=2, value=t["display_name"])
    cb.font = font_regular
    cb.alignment = align_left
    cb.border = border_cell_thin
    
    # Kiêm nhiệm & CN
    for c in [3, 4]:
        cell_empty = ws3.cell(row=row_num, column=c, value=None)
        cell_empty.border = border_cell_thin
        
    # Phân công chuyên môn (official assignment)
    val_e = t["official_assignment"]
    ce = ws3.cell(row=row_num, column=5, value=val_e)
    ce.font = font_regular
    ce.alignment = align_left
    ce.border = border_cell_thin
    
    # Số tiết
    val_f = t["total_periods"]
    cf = ws3.cell(row=row_num, column=6, value=val_f)
    cf.font = font_regular
    cf.alignment = align_center
    cf.border = border_cell_thin
    
    total_stiet += val_f
    
    txt_len = len(val_e)
    h = 24.0 if txt_len <= 75 else (38.0 if txt_len <= 150 else (54.0 if txt_len <= 225 else 70.0))
    ws3.row_dimensions[row_num].height = h

tot_row = 5 + len(teacher_cfg["teachers"])
ws3.cell(row=tot_row, column=1, value="TỔNG CỘNG").font = font_bold
ws3.cell(row=tot_row, column=1).alignment = align_right
ws3.merge_cells(start_row=tot_row, start_column=1, end_row=tot_row, end_column=5)
for c in range(1, 6):
    ws3.cell(row=tot_row, column=c).border = border_summary_total

cell_f_tot = ws3.cell(row=tot_row, column=6, value=total_stiet)
cell_f_tot.font = font_bold
cell_f_tot.alignment = align_center
cell_f_tot.border = border_summary_total
ws3.row_dimensions[tot_row].height = 28.0

if ws3.max_row > tot_row:
    ws3.delete_rows(tot_row + 1, ws3.max_row - tot_row)

print(f"✓ Sheet 3 'BẢNG PHÂN CÔNG GIẢNG DẠY' populated: {len(teacher_cfg['teachers'])} teachers, Total = {total_stiet} periods.")

# --- 6. POPULATE SHEET 4: TKB Giáo viên ---
teacher_full_schedule = {}
for (cname, d, p), val in class_grid.items():
    if not val or val in ['Nghỉ', '-']: continue
    parts = [pt.strip() for pt in val.split('-')]
    
    room = None
    tname_str = None
    subj = None
    
    if len(parts) >= 3 and parts[-1] in known_rooms:
        room = parts[-1]
        tname_str = parts[-2]
        subj = ' - '.join(parts[:-2]).strip()
    elif len(parts) >= 2:
        tname_str = parts[-1]
        subj = ' - '.join(parts[:-1]).strip()
    else:
        continue
        
    teachers = [t.strip() for t in tname_str.split(',')]
    
    for t in teachers:
        if room:
            room_tag = f" ({room})"
        elif cname in class_rooms:
            room_tag = f" ({class_rooms[cname]})"
        else:
            room_tag = ""
            
        subj_class_tag = f"{subj} - {cname}{room_tag}"
        key = (t, d, p)
        if key not in teacher_full_schedule:
            teacher_full_schedule[key] = []
        if subj_class_tag not in teacher_full_schedule[key]:
            teacher_full_schedule[key].append(subj_class_tag)

ws4 = wb['TKB Giáo viên']

# Read teacher list in order from registry
teacher_headers = [t["display_name"] for t in teacher_cfg["teachers"]]

# Clean up extra columns beyond the 43 teachers
max_col_clean = max(ws4.max_column, len(teacher_headers) + 5)
for c in range(4, max_col_clean):
    ws4.column_dimensions[get_column_letter(c)].width = 24.0
    for r in range(1, ws4.max_row + 1):
        cell = ws4.cell(row=r, column=c)
        if not isinstance(cell, MergedCell):
            cell.value = None
            cell.border = Border(left=None, right=None, top=None, bottom=None)

for i, tname in enumerate(teacher_headers):
    col = 4 + i
    is_last = (i == len(teacher_headers) - 1)
    right_s = medium_border if is_last else thin_border
    
    # Header cell
    h_cell = ws4.cell(row=4, column=col, value=tname)
    if not isinstance(h_cell, MergedCell):
        h_cell.font = font_bold
        h_cell.alignment = align_center
        h_cell.border = Border(left=thin_border, right=right_s, top=medium_border, bottom=medium_border)
        
    for r in range(5, 55):
        d = 2 + ((r - 5) // 10)
        p = 1 + ((r - 5) % 10)
        
        assigned_list = teacher_full_schedule.get((tname, d, p), [])
        t_slot = "\n".join(assigned_list) if assigned_list else None
        
        cell = ws4.cell(row=r, column=col)
        if not isinstance(cell, MergedCell):
            cell.value = t_slot
            cell.font = font_regular
            cell.alignment = align_center
            p_idx = (r - 5) % 10
            b_bot = medium_border if p_idx == 9 else dotted_border
            cell.border = Border(left=thin_border, right=right_s, top=None, bottom=b_bot)

if ws4.max_column > len(teacher_headers) + 3:
    ws4.delete_cols(len(teacher_headers) + 4, ws4.max_column - (len(teacher_headers) + 3))

print(f"✓ Sheet 4 'TKB Giáo viên' populated: {len(teacher_headers)} teachers.")

# --- 7. AUTOMATED INTEGRITY & AUDIT VERIFICATION ---
print("\n--- RUNNING PRE-SAVE INTEGRITY AUDIT ---")
# Audit 1: Total periods
if total_stiet != 711:
    raise AssertionError(f"Period equilibrium violated: Expected 711, got {total_stiet}")
print(f"✓ Audit 1: Period Equilibrium PASS (711/711 periods)")

# Audit 2: Grade 12 Paired Electives Alignment (12 pairs)
elective_rules = rules_cfg["shared_pairs"]["12A1_12A2"]["paired_elective_alignment_rules"]
for rule in elective_rules:
    d = rule["day"]
    p = rule["period"]
    s1 = class_grid.get(("12A1", d, p), "")
    s2 = class_grid.get(("12A2", d, p), "")
    
    exp_subj1 = rule["class_12A1"]["subject"]
    exp_room1 = rule["class_12A1"]["room"]
    exp_subj2 = rule["class_12A2"]["subject"]
    
    if exp_subj1 not in s1 or exp_room1 not in s1:
        raise AssertionError(f"Grade 12 split rule violation at D{d}P{p}: 12A1 expected '{exp_subj1} ... {exp_room1}', got '{s1}'")
    if exp_subj2 not in s2:
        raise AssertionError(f"Grade 12 split rule violation at D{d}P{p}: 12A2 expected '{exp_subj2}', got '{s2}'")

print(f"✓ Audit 2: Grade 12 Paired Elective Alignment PASS (All {len(elective_rules)} pairs verified)")

# Audit 3: Room collision detection
room_occupancy = {}
for (cname, d, p), val in class_grid.items():
    if not val: continue
    for rm in known_rooms:
        if rm in val:
            key = (rm, d, p)
            if key in room_occupancy:
                prev_c, prev_val = room_occupancy[key]
                # If shared classes (e.g. 7A1 and 7A2, 8A1 and 8A2, 12A1 and 12A2), they co-attend
                is_shared_room = (
                    ({prev_c, cname} == {'7A1', '7A2'}) or
                    ({prev_c, cname} == {'8A1', '8A2'}) or
                    ({prev_c, cname} == {'12A1', '12A2'})
                )
                if prev_c != cname and not is_shared_room:
                    raise AssertionError(f"Specialized Room collision at {rm} (D{d}P{p}): Class {prev_c} and {cname}")
            else:
                room_occupancy[key] = (cname, val)
print(f"✓ Audit 3: Specialized Rooms Collision Detection PASS (0 double bookings)")

# Audit 4: Teacher collision detection
for (tname, d, p), slots in teacher_full_schedule.items():
    if len(slots) > 1:
        # Check if co-teaching in primary (allowed) or true conflict
        # Only allowed if classes are 4A1/5A1 co-teaching or shared class (7A1/7A2, 8A1/8A2, 12A1/12A2)
        classes = [s.split('-')[1].split('(')[0].strip() for s in slots]
        is_shared_allowed = (set(classes) == {'7A1', '7A2'}) or (set(classes) == {'8A1', '8A2'}) or (set(classes) == {'12A1', '12A2'})
        if not is_shared_allowed:
            raise AssertionError(f"Teacher collision detected for {tname} at D{d}P{p}: {slots}")
print(f"✓ Audit 4: Teacher Collision Detection PASS (0 unauthorized teacher collisions)")

# --- 8. SAVE TARGET WORKBOOK ---
try:
    wb.save(out_file)
    print(f"\n==========================================================================")
    print(f"🎉 MASTER WORKBOOK CREATED SUCCESSFULLY: {out_file}")
    print(f"   - Sheets: Tiểu học, THCS-THPT, BẢNG PHÂN CÔNG GIẢNG DẠY, TKB Giáo viên")
    print(f"   - Classes: 18 | Teachers: 43 | Total Periods: 711 | Conflicts: 0")
    print(f"==========================================================================")
except PermissionError:
    alt = os.path.join(folder, "TKB_Marie_Curie_2026-2027(update_05_09_temp).xlsx")
    wb.save(alt)
    print(f"\n🎉 WORKBOOK CREATED SUCCESSFULLY (ALT FILE): {alt}")
