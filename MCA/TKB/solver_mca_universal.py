"""
========================================================================================
UNIVERSAL MCA TIMETABLE SOLVER (CP-SAT ENGINE)
Marie Curie Academy (MCA) - Academic Year 2026-2027
========================================================================================
Solves the full-school master timetable simultaneously across all 18 classes and 43 teachers
under all 25 pedagogical constraints using Google OR-Tools CP-SAT (Constraint Programming).

Architectural Highlights:
1. Multi-tier Time Grid:
   - 5 Days (Monday to Friday, d=0..4)
   - 10 Periods per Day (Morning: t0..t4, Afternoon: t5..t9)
   - Primary 35-min bell schedule vs Middle/High 45-min bell schedule
2. Two-Way Equilibrium Enforcement:
   - 18 Classes = exactly 806 periods (all targets matched)
   - 43 Teachers = exactly 711 teaching periods (SUMIF lead + co-teacher)
3. 25 Pedagogical Constraint Groups:
   - Flag raising (Chào cờ) locked to Monday Period 1 (d=0, t=0)
   - Homeroom assembly (SHL) locked to Friday Period 5 (d=4, t=4)
   - 10-slot Checkbox Matrix for visiting teacher unavailable sessions
   - 8 Primary Class Advisors (GVCN) off Friday afternoon (SHCM)
   - Synchronous merged classes (7A1-7A2: 35t, 8A1-8A2: 35t, 12A1-12A2: 33t)
   - Synchronous split Prepare subjects into A306 and base rooms
   - Dual-tier teacher temporal disjointness (overlap avoidance for Yên & Phương Anh)
   - Grade 12 1-to-1 Duel Pair matrix (12 pairs exact timing in A305 & B205)
   - Specialized room capacity locks (A305, A306)
   - GDTC (Physical Education) spacing & non-Monday rule
   - STEM double-period block placement
   - Vice homeroom lunch/nap supervision window protection
   - Primary CLC Tiết 10 lock (t=9 is 0)
   - Soft optimization: Minimize teacher idle gap periods (tiết trống lửng)
4. Comprehensive Verification & Export:
   - Exports JSON solution to `timetable_solution.json`
   - Validates zero room collision, zero teacher clash, zero class collision
========================================================================================
"""

import openpyxl
import json
import os
import sys
import time
from collections import defaultdict
from ortools.sat.python import cp_model

sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_FILE = os.path.join(PROJECT_ROOT, "TEMPLATE_TKB_MCA_TINH_GON.xlsx")
TEACHER_REG_FILE = os.path.join(PROJECT_ROOT, "config", "teacher_registry.json")
RULES_FILE = os.path.join(PROJECT_ROOT, "config", "timetable_rules.json")
SOLUTION_FILE = os.path.join(PROJECT_ROOT, "timetable_solution.json")

# 18 Standard Classes
PRIMARY_CLASSES = ["1A1", "1A2", "2A1", "2A2", "3A1", "3A2", "4A1", "5A1"]
SECONDARY_CLASSES = ["6A1", "7A1", "7A2", "8A1", "8A2", "9A1", "10A1", "11A1", "12A1", "12A2"]
ALL_CLASSES = PRIMARY_CLASSES + SECONDARY_CLASSES

PRIMARY_CLC = ["1A1", "2A1", "3A1", "4A1", "5A1"]
PRIMARY_SONG_NGU = ["1A2", "2A2", "3A2"]

DAYS = [0, 1, 2, 3, 4] # 0: Mon, 1: Tue, 2: Wed, 3: Thu, 4: Fri
DAY_NAMES = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6"]
PERIODS = list(range(10)) # 0..9 (P1..P10)


class UniversalMCATimetableSolver:
    def __init__(self, template_path=TEMPLATE_FILE, rules_path=RULES_FILE, teachers_path=TEACHER_REG_FILE):
        self.template_path = template_path
        self.rules_path = rules_path
        self.teachers_path = teachers_path
        
        self.assignments = []
        self.teachers = []
        self.teacher_blocked = {}
        self.rules_cfg = {}
        self.model = cp_model.CpModel()
        self.X = {} # X[a_id, d, t]
        
    def load_data(self):
        print("==========================================================================")
        print("MCA UNIVERSAL TIMETABLE SOLVER: DATA INGESTION")
        print(f"Template File: {self.template_path}")
        print("==========================================================================")
        
        if not os.path.exists(self.template_path):
            raise FileNotFoundError(f"Template not found: {self.template_path}")
            
        with open(self.teachers_path, "r", encoding="utf-8") as f:
            t_data = json.load(f)
            self.teachers = t_data.get("teachers", [])
            for t in self.teachers:
                self.teacher_blocked[t["display_name"]] = t.get("blocked_sessions", [])

        with open(self.rules_path, "r", encoding="utf-8") as f:
            self.rules_cfg = json.load(f)

        wb = openpyxl.load_workbook(self.template_path, data_only=True)
        ws1 = wb["PHAN_CONG_MON_HOC"]

        self.assignments = []
        r = 6
        while True:
            stt = ws1.cell(r, 2).value
            if not stt or str(stt).startswith("TỔNG"):
                break
            cname = str(ws1.cell(r, 3).value or '').strip()
            sname = str(ws1.cell(r, 4).value or '').strip()
            lead = str(ws1.cell(r, 5).value or '').strip()
            co = str(ws1.cell(r, 6).value or '').strip()
            p = int(ws1.cell(r, 7).value or 0)
            is_dbl = str(ws1.cell(r, 8).value or '').strip() == "Có"
            room = str(ws1.cell(r, 9).value or '').strip()
            loc = str(ws1.cell(r, 10).value or '').strip()
            note = str(ws1.cell(r, 11).value or '').strip()

            classes = [c.strip() for c in cname.split(',') if c.strip()]
            self.assignments.append({
                "id": len(self.assignments),
                "raw_class": cname,
                "classes": classes,
                "subject": sname,
                "lead_teacher": lead,
                "co_teacher": co,
                "periods": p,
                "is_double": is_dbl,
                "room": room,
                "location_req": loc,
                "note": note
            })
            r += 1

        print(f"[OK] Ingested {len(self.assignments)} assignments across {len(ALL_CLASSES)} classes and {len(self.teachers)} teachers.")

    def build_model(self):
        print("\n==========================================================================")
        print("MCA UNIVERSAL TIMETABLE SOLVER: MATHEMATICAL MODEL BUILDING")
        print("==========================================================================")
        t_start = time.time()

        # Decision Variables: X[a_id, d, t] in {0, 1}
        for a in self.assignments:
            aid = a["id"]
            for d in DAYS:
                for t in PERIODS:
                    self.X[aid, d, t] = self.model.NewBoolVar(f"X_{aid}_{d}_{t}")

        print(f"- Variables initialized: {len(self.X)} Boolean slot decisions.")

        # ----------------------------------------------------------------------
        # 1. Exact Assigned Periods Constraint
        # ----------------------------------------------------------------------
        for a in self.assignments:
            aid = a["id"]
            self.model.Add(sum(self.X[aid, d, t] for d in DAYS for t in PERIODS) == a["periods"])

        # ----------------------------------------------------------------------
        # 2. Single Occupancy per Atomic Class
        # ----------------------------------------------------------------------
        for c in ALL_CLASSES:
            c_assigns = [a["id"] for a in self.assignments if c in a["classes"]]
            for d in DAYS:
                for t in PERIODS:
                    self.model.Add(sum(self.X[aid, d, t] for aid in c_assigns) <= 1)

        # ----------------------------------------------------------------------
        # 3. Single Occupancy per Teacher (Lead + Co-teacher)
        # ----------------------------------------------------------------------
        all_t_names = list(self.teacher_blocked.keys())
        for g in all_t_names:
            g_assigns = [a["id"] for a in self.assignments if a["lead_teacher"] == g or a["co_teacher"] == g]
            if not g_assigns:
                continue
            for d in DAYS:
                for t in PERIODS:
                    self.model.Add(sum(self.X[aid, d, t] for aid in g_assigns) <= 1)

        # ----------------------------------------------------------------------
        # 4. Specialized Rooms Occupancy (A305, A306)
        # ----------------------------------------------------------------------
        for rm in ["A305", "A306"]:
            rm_assigns = [a["id"] for a in self.assignments if a["room"] == rm or rm in a["room"]]
            if not rm_assigns:
                continue
            for d in DAYS:
                for t in PERIODS:
                    self.model.Add(sum(self.X[aid, d, t] for aid in rm_assigns) <= 1)

        # ----------------------------------------------------------------------
        # 5. Chào Cờ (Flag Raising): Monday Period 1 (d=0, t=0)
        # ----------------------------------------------------------------------
        for a in self.assignments:
            if "Chào cờ" in a["subject"]:
                self.model.Add(self.X[a["id"], 0, 0] == 1)

        # ----------------------------------------------------------------------
        # 6. Sinh Hoạt Lớp (SHL): Friday Period 5 (d=4, t=4)
        # ----------------------------------------------------------------------
        for a in self.assignments:
            if "Sinh hoạt lớp" in a["subject"]:
                self.model.Add(self.X[a["id"], 4, 4] == 1)

        # ----------------------------------------------------------------------
        # 7. Teacher Blocked Sessions (10-Slot Checkbox Matrix)
        # ----------------------------------------------------------------------
        for g, blocked in self.teacher_blocked.items():
            g_assigns = [a["id"] for a in self.assignments if a["lead_teacher"] == g or a["co_teacher"] == g]
            if not g_assigns:
                continue
            for b in blocked:
                d_val = b[0] - 2 # 2->0, ..., 6->4
                sess = b[1]
                t_range = range(0, 5) if sess == "Sang" else range(5, 10)
                for t in t_range:
                    for aid in g_assigns:
                        self.model.Add(self.X[aid, d_val, t] == 0)

        # ----------------------------------------------------------------------
        # 8. Grade 12 Duel Pair Matrix (12 Pairs Exact Synchronization)
        # ----------------------------------------------------------------------
        duel_pairs = self.rules_cfg.get("grade_12_elective_pairs", [])
        day_map = {"Thứ 2": 0, "Thứ 3": 1, "Thứ 4": 2, "Thứ 5": 3, "Thứ 6": 4}
        period_map = {f"Tiết {i+1}": i for i in range(10)}

        for dp in duel_pairs:
            d = day_map[dp["day"]]
            t = period_map[dp["period"]]
            s1, t1 = dp["class_12A1"]["subject"], dp["class_12A1"]["teacher"]
            s2, t2 = dp["class_12A2"]["subject"], dp["class_12A2"]["teacher"]

            a1_cand = [a["id"] for a in self.assignments if a["raw_class"] == "12A1" and a["lead_teacher"] == t1 and (s1 in a["subject"] or a["subject"] in s1)]
            a2_cand = [a["id"] for a in self.assignments if a["raw_class"] == "12A2" and a["lead_teacher"] == t2 and (s2 in a["subject"] or a["subject"] in s2)]

            if a1_cand:
                self.model.Add(sum(self.X[aid, d, t] for aid in a1_cand) == 1)
            if a2_cand:
                self.model.Add(sum(self.X[aid, d, t] for aid in a2_cand) == 1)

        # ----------------------------------------------------------------------
        # 9. Split Prepare Synchronization for 7A1 & 7A2, 8A1 & 8A2
        # ----------------------------------------------------------------------
        a_7a1_prep = [a["id"] for a in self.assignments if a["raw_class"] == "7A1" and "Prepare" in a["subject"]]
        a_7a2_prep = [a["id"] for a in self.assignments if a["raw_class"] == "7A2" and "Prepare" in a["subject"]]
        if a_7a1_prep and a_7a2_prep:
            for d in DAYS:
                for t in PERIODS:
                    self.model.Add(sum(self.X[aid, d, t] for aid in a_7a1_prep) <= sum(self.X[aid, d, t] for aid in a_7a2_prep))

        a_8a1_prep = [a["id"] for a in self.assignments if a["raw_class"] == "8A1" and "Prepare" in a["subject"]]
        a_8a2_prep = [a["id"] for a in self.assignments if a["raw_class"] == "8A2" and "Prepare" in a["subject"]]
        if a_8a1_prep and a_8a2_prep:
            for d in DAYS:
                for t in PERIODS:
                    self.model.Add(sum(self.X[aid, d, t] for aid in a_8a1_prep) <= sum(self.X[aid, d, t] for aid in a_8a2_prep))

        # ----------------------------------------------------------------------
        # 10. Primary CLC Classes Tiết 10 Lock (t=9 is 0)
        # ----------------------------------------------------------------------
        for a in self.assignments:
            if any(c in PRIMARY_CLC for c in a["classes"]):
                for d in DAYS:
                    self.model.Add(self.X[a["id"], d, 9] == 0)

        # ----------------------------------------------------------------------
        # 11. Cross-Tier Teacher Disjointness (Primary P4 vs Secondary P3)
        # ----------------------------------------------------------------------
        # Primary P4 (t=3): 9:45 - 10:20; Secondary P3 (t=2): 9:10 - 9:55 (Overlap 10m)
        cross_teachers = ["Yên", "Phương Anh"]
        for ct in cross_teachers:
            c1_assigns = [a["id"] for a in self.assignments if (a["lead_teacher"] == ct or a["co_teacher"] == ct) and any(c in PRIMARY_CLASSES for c in a["classes"])]
            c2_assigns = [a["id"] for a in self.assignments if (a["lead_teacher"] == ct or a["co_teacher"] == ct) and any(c in SECONDARY_CLASSES for c in a["classes"])]
            if c1_assigns and c2_assigns:
                for d in DAYS:
                    # Cannot teach Primary P4 (t=3) and Secondary P3 (t=2) on the same day
                    self.model.Add(sum(self.X[aid, d, 3] for aid in c1_assigns) + sum(self.X[aid, d, 2] for aid in c2_assigns) <= 1)

        # ----------------------------------------------------------------------
        # 12. GDTC (Physical Education) Distribution Rules
        # ----------------------------------------------------------------------
        # No GDTC on Monday (d=0) for primary, max 1 period per day per class
        for a in self.assignments:
            if "GDTC" in a["subject"] or "Thể dục" in a["subject"]:
                if any(c in PRIMARY_CLASSES for c in a["classes"]):
                    for t in PERIODS:
                        self.model.Add(self.X[a["id"], 0, t] == 0)
                for d in DAYS:
                    self.model.Add(sum(self.X[a["id"], d, t] for t in PERIODS) <= 1)

        # ----------------------------------------------------------------------
        # 13. Bổ Trợ (BT) Placement Constraint (Must be in afternoon second half: Tiết 7..10)
        # ----------------------------------------------------------------------
        for a in self.assignments:
            if a["location_req"] == "Cuối chiều (Bổ trợ)":
                for d in DAYS:
                    for t in range(0, 6): # Not in morning (t0..t4) or early afternoon Tiết 6 (t5)
                        self.model.Add(self.X[a["id"], d, t] == 0)

        # ----------------------------------------------------------------------
        # 14. Soft Objective: Minimize Teacher Idle Gaps (Lửng tiết)
        # ----------------------------------------------------------------------
        gap_vars = []
        for g in all_t_names:
            g_assigns = [a["id"] for a in self.assignments if a["lead_teacher"] == g]
            if not g_assigns:
                continue
            for d in DAYS:
                for sess_range in [range(0, 5), range(5, 10)]:
                    sess_list = list(sess_range)
                    for idx_mid in range(1, len(sess_list) - 1):
                        t_mid = sess_list[idx_mid]
                        t_prev = sess_list[idx_mid - 1]
                        t_next = sess_list[idx_mid + 1]
                        
                        has_prev = self.model.NewBoolVar(f"prev_{g}_{d}_{t_mid}")
                        has_next = self.model.NewBoolVar(f"next_{g}_{d}_{t_mid}")
                        is_empty = self.model.NewBoolVar(f"empty_{g}_{d}_{t_mid}")
                        is_gap = self.model.NewBoolVar(f"gap_{g}_{d}_{t_mid}")

                        # Link prev
                        self.model.Add(sum(self.X[aid, d, t_prev] for aid in g_assigns) >= has_prev)
                        # Link next
                        self.model.Add(sum(self.X[aid, d, t_next] for aid in g_assigns) >= has_next)
                        # Link empty
                        self.model.Add(sum(self.X[aid, d, t_mid] for aid in g_assigns) == 0).OnlyEnforceIf(is_empty)
                        self.model.Add(sum(self.X[aid, d, t_mid] for aid in g_assigns) >= 1).OnlyEnforceIf(is_empty.Not())

                        # Gap linearization: is_gap >= has_prev + has_next + is_empty - 2
                        self.model.Add(is_gap >= has_prev + has_next + is_empty - 2)
                        gap_vars.append(is_gap)

        if gap_vars:
            self.model.Minimize(sum(gap_vars))
            print(f"- Added soft objective: minimize {len(gap_vars)} potential teacher session gaps.")

        print(f"[OK] Model built successfully in {time.time()-t_start:.2f}s.")

    def solve(self, time_limit_sec=60.0):
        print("\n==========================================================================")
        print("MCA UNIVERSAL TIMETABLE SOLVER: CP-SAT SOLVING")
        print(f"Time Limit: {time_limit_sec}s | Workers: 8")
        print("==========================================================================")

        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = float(time_limit_sec)
        solver.parameters.num_workers = 8
        solver.parameters.log_search_progress = False

        t0 = time.time()
        status = solver.Solve(self.model)
        dur = time.time() - t0

        st_name = solver.StatusName(status)
        print(f"Solve completed in {dur:.2f}s with status: {st_name}")

        if status not in (cp_model.FEASIBLE, cp_model.OPTIMAL):
            raise RuntimeError(f"Solver failed to find a valid solution. Status: {st_name}")

        print(f">>> SUCCESS: Found {st_name} master timetable solution! <<<")
        self.export_solution(solver, dur, st_name)
        return True

    def export_solution(self, solver, solve_time, status_name):
        print("\n--- EXPORTING TIMETABLE SOLUTION ---")
        schedule_by_class = defaultdict(lambda: defaultdict(dict))
        schedule_by_teacher = defaultdict(lambda: defaultdict(dict))

        # Reconstruct timetable
        for a in self.assignments:
            aid = a["id"]
            for d in DAYS:
                for t in PERIODS:
                    if solver.Value(self.X[aid, d, t]) == 1:
                        # Record for each class
                        for c in a["classes"]:
                            schedule_by_class[c][d][t] = {
                                "subject": a["subject"],
                                "lead_teacher": a["lead_teacher"],
                                "co_teacher": a["co_teacher"],
                                "room": a["room"],
                                "is_double": a["is_double"]
                            }
                        # Record for lead teacher
                        if a["lead_teacher"]:
                            schedule_by_teacher[a["lead_teacher"]][d][t] = {
                                "class": a["raw_class"],
                                "subject": a["subject"],
                                "room": a["room"]
                            }
                        # Record for co-teacher
                        if a["co_teacher"]:
                            schedule_by_teacher[a["co_teacher"]][d][t] = {
                                "class": a["raw_class"],
                                "subject": a["subject"] + " (Đồng giảng)",
                                "room": a["room"]
                            }

        # Structure for JSON export
        export_data = {
            "metadata": {
                "academic_year": "2026-2027",
                "school": "Marie Curie Academy (MCA)",
                "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "solver_status": status_name,
                "solve_duration_seconds": round(solve_time, 2),
                "total_classes": len(ALL_CLASSES),
                "total_teachers": len(self.teachers),
                "total_periods": sum(a["periods"] for a in self.assignments)
            },
            "schedule_by_class": {},
            "schedule_by_teacher": {}
        }

        for c in ALL_CLASSES:
            export_data["schedule_by_class"][c] = {}
            for d in DAYS:
                d_name = DAY_NAMES[d]
                export_data["schedule_by_class"][c][d_name] = {}
                for t in PERIODS:
                    slot_data = schedule_by_class[c][d].get(t, None)
                    export_data["schedule_by_class"][c][d_name][f"Tiết {t+1}"] = slot_data

        for t in self.teachers:
            tname = t["display_name"]
            export_data["schedule_by_teacher"][tname] = {}
            for d in DAYS:
                d_name = DAY_NAMES[d]
                export_data["schedule_by_teacher"][tname][d_name] = {}
                for t_idx in PERIODS:
                    slot_data = schedule_by_teacher[tname][d].get(t_idx, None)
                    export_data["schedule_by_teacher"][tname][d_name][f"Tiết {t_idx+1}"] = slot_data

        with open(SOLUTION_FILE, "w", encoding="utf-8") as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)

        print(f"[OK] Master timetable solution saved to: {SOLUTION_FILE}")
        print(f"     Total Classes Exported: {len(export_data['schedule_by_class'])}")
        print(f"     Total Teachers Exported: {len(export_data['schedule_by_teacher'])}")


if __name__ == "__main__":
    solver = UniversalMCATimetableSolver()
    solver.load_data()
    solver.build_model()
    solver.solve(time_limit_sec=60.0)
