# -*- coding: utf-8 -*-
"""
HỒ SƠ TỔNG HỢP TOÀN DIỆN VÀ KẾ HOẠCH TRIỂN KHAI DỰ ÁN STEM OLYMPIC 2026
Dự án: Hệ thống Đèn Giao Thông Học Đường Thông Minh Tích Hợp AI Vision & Rào Chắn Barie Tự Động
Đơn vị: Trường Tiểu học, THCS và THPT Marie Curie Thái Bình
Cuộc thi: HNUE Olympic STEM 2026 — Bảng Tiểu học
Chuẩn thể thức: Nghị định 30/2020/NĐ-CP
Định dạng: CHỮ MÀU ĐEN 100%, KHÔNG ĐỔ MÀU NỀN CÁC Ô BẢNG TÍNH (CHUẨN IN ẤN HÀNH CHÍNH)
"""

import os
import sys
import docx
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

sys.stdout.reconfigure(encoding='utf-8')

# Màu chữ thuần đen chuẩn văn bản hành chính
COLOR_BLACK = RGBColor(0, 0, 0)

def set_cell_margins(cell, top=100, bottom=100, left=130, right=130):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}>'
                      f'<w:top w:w="{top}" w:type="dxa"/>'
                      f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
                      f'<w:left w:w="{left}" w:type="dxa"/>'
                      f'<w:right w:w="{right}" w:type="dxa"/>'
                      f'</w:tcMar>')
    tcPr.append(tcMar)

def set_cell_no_shading(cell):
    """Đảm bảo ô hoàn toàn không đổ màu nền (nền trắng trong suốt)"""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="auto"/>')
    tcPr.append(shd)

def set_cell_valign(cell, val="center"):
    vAlign = parse_xml(f'<w:vAlign {nsdecls("w")} w:val="{val}"/>')
    cell._tc.get_or_add_tcPr().append(vAlign)

def set_table_borders(table, color="000000", sz="4"):
    """Đường viền đơn mảnh màu đen chuẩn văn bản hành chính"""
    tblPr = table._tbl.tblPr
    tblBorders = parse_xml(f'<w:tblBorders {nsdecls("w")}>'
                           f'<w:top w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
                           f'<w:left w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
                           f'<w:bottom w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
                           f'<w:right w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
                           f'<w:insideH w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
                           f'<w:insideV w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
                           f'</w:tblBorders>')
    tblPr.append(tblBorders)

def set_table_no_borders(table):
    tblPr = table._tbl.tblPr
    tblBorders = parse_xml(f'<w:tblBorders {nsdecls("w")}>'
                           f'<w:top w:val="none"/>'
                           f'<w:left w:val="none"/>'
                           f'<w:bottom w:val="none"/>'
                           f'<w:right w:val="none"/>'
                           f'<w:insideH w:val="none"/>'
                           f'<w:insideV w:val="none"/>'
                           f'</w:tblBorders>')
    tblPr.append(tblBorders)

def set_row_cant_split(row):
    trPr = row._tr.get_or_add_trPr()
    trPr.append(OxmlElement('w:cantSplit'))

def set_row_tbl_header(row):
    trPr = row._tr.get_or_add_trPr()
    trPr.append(OxmlElement('w:tblHeader'))

def add_page_number_to_header(header):
    p = header.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    run = p.add_run()
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12)
    run.font.color.rgb = COLOR_BLACK
    fld1 = parse_xml(r'<w:fldChar %s w:fldCharType="begin"/>' % nsdecls('w'))
    instr = parse_xml(r'<w:instrText %s xml:space="preserve"> PAGE </w:instrText>' % nsdecls('w'))
    fld2 = parse_xml(r'<w:fldChar %s w:fldCharType="separate"/>' % nsdecls('w'))
    fld3 = parse_xml(r'<w:fldChar %s w:fldCharType="end"/>' % nsdecls('w'))
    run._r.append(fld1)
    run._r.append(instr)
    run._r.append(fld2)
    run._r.append(fld3)

def add_callout_box(doc, title, text):
    """Khung ghi chú không đổ màu, chỉ có đường viền viền trái đậm màu đen"""
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    cell.width = Cm(16.0)
    set_cell_margins(cell, top=100, bottom=100, left=150, right=150)
    set_cell_no_shading(cell)
    
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = parse_xml(f'<w:tcBorders {nsdecls("w")}>'
                          f'<w:top w:val="none"/>'
                          f'<w:left w:val="single" w:sz="18" w:space="0" w:color="000000"/>'
                          f'<w:bottom w:val="none"/>'
                          f'<w:right w:val="none"/>'
                          f'</w:tcBorders>')
    tcPr.append(tcBorders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.15
    run_t = p.add_run(f"📌 {title}\n")
    run_t.font.name = 'Times New Roman'
    run_t.font.size = Pt(12.5)
    run_t.font.bold = True
    run_t.font.color.rgb = COLOR_BLACK
    
    run_b = p.add_run(text)
    run_b.font.name = 'Times New Roman'
    run_b.font.size = Pt(11.5)
    run_b.font.color.rgb = COLOR_BLACK
    
    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_before = Pt(0)
    p_after.paragraph_format.space_after = Pt(4)

def add_heading_1(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(5)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(14)
    run.font.bold = True
    run.font.color.rgb = COLOR_BLACK
    return p

def add_heading_2(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(13)
    run.font.bold = True
    run.font.color.rgb = COLOR_BLACK
    return p

def add_heading_3(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12.5)
    run.font.bold = True
    run.font.color.rgb = COLOR_BLACK
    return p

def add_body_p(doc, text, bold_prefix=None, space_after=5, italic=False):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.15
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.font.name = 'Times New Roman'
        r_pre.font.size = Pt(12.5)
        r_pre.font.bold = True
        r_pre.font.color.rgb = COLOR_BLACK
        
    run = p.add_run(text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12.5)
    run.font.italic = italic
    run.font.color.rgb = COLOR_BLACK
    return p

def build_master_unified_document():
    doc = docx.Document()
    
    # 1. Khổ giấy & Căn lề chuẩn Nghị định 30/2020/NĐ-CP
    section = doc.sections[0]
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
    section.top_margin = Cm(2.0)
    section.bottom_margin = Cm(2.0)
    section.left_margin = Cm(3.0)
    section.right_margin = Cm(2.0)
    section.header_distance = Cm(1.2)
    section.footer_distance = Cm(1.2)
    section.different_first_page_header_footer = True
    add_page_number_to_header(section.header)
    
    # Thiết lập Normal style mặc định thuần đen
    style = doc.styles['Normal']
    style.font.name = 'Times New Roman'
    style.font.size = Pt(12.5)
    style.font.color.rgb = COLOR_BLACK
    style.paragraph_format.line_spacing = 1.15
    
    # ==========================================
    # TIÊU NGỮ VÀ TIÊU ĐỀ CHÍNH THỨC
    # ==========================================
    tbl_header = doc.add_table(rows=1, cols=2)
    tbl_header.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_no_borders(tbl_header)
    
    cell_l = tbl_header.cell(0, 0)
    cell_l.width = Cm(7.5)
    set_cell_no_shading(cell_l)
    p_l = cell_l.paragraphs[0]
    p_l.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_l.paragraph_format.space_before = Pt(0)
    p_l.paragraph_format.space_after = Pt(2)
    p_l.paragraph_format.line_spacing = 1.05
    r = p_l.add_run("TRƯỜNG LIÊN CẤP MARIE CURIE\n")
    r.font.name = 'Times New Roman'; r.font.size = Pt(11); r.font.bold = True; r.font.color.rgb = COLOR_BLACK
    r = p_l.add_run("TỔ STEM & CÔNG NGHỆ SỐ\n")
    r.font.name = 'Times New Roman'; r.font.size = Pt(11); r.font.bold = True; r.font.color.rgb = COLOR_BLACK
    r = p_l.add_run("Số: 10/HSTD-STEM-MCA")
    r.font.name = 'Times New Roman'; r.font.size = Pt(10); r.font.italic = True; r.font.color.rgb = COLOR_BLACK
    
    cell_r = tbl_header.cell(0, 1)
    cell_r.width = Cm(8.5)
    set_cell_no_shading(cell_r)
    p_r = cell_r.paragraphs[0]
    p_r.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_r.paragraph_format.space_before = Pt(0)
    p_r.paragraph_format.space_after = Pt(2)
    p_r.paragraph_format.line_spacing = 1.05
    r = p_r.add_run("CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM\n")
    r.font.name = 'Times New Roman'; r.font.size = Pt(11); r.font.bold = True; r.font.color.rgb = COLOR_BLACK
    r = p_r.add_run("Độc lập – Tự do – Hạnh phúc\n")
    r.font.name = 'Times New Roman'; r.font.size = Pt(11.5); r.font.bold = True; r.font.underline = True; r.font.color.rgb = COLOR_BLACK
    r = p_r.add_run("Thái Bình, ngày 10 tháng 11 năm 2026")
    r.font.name = 'Times New Roman'; r.font.size = Pt(10); r.font.italic = True; r.font.color.rgb = COLOR_BLACK
    
    p_div = doc.add_paragraph()
    p_div.paragraph_format.space_before = Pt(14)
    p_div.paragraph_format.space_after = Pt(3)
    p_div.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_title = p_div.add_run("HỒ SƠ TỔNG HỢP TOÀN DIỆN VÀ KẾ HOẠCH TRIỂN KHAI DỰ ÁN\n")
    r_title.font.name = 'Times New Roman'; r_title.font.size = Pt(15); r_title.font.bold = True; r_title.font.color.rgb = COLOR_BLACK
    r_sub = p_div.add_run("HỆ THỐNG ĐÈN GIAO THÔNG HỌC ĐƯỜNG THÔNG MINH TÍCH HỢP AI VISION & RÀO CHẮN BARIE TỰ ĐỘNG\n")
    r_sub.font.name = 'Times New Roman'; r_sub.font.size = Pt(12.5); r_sub.font.bold = True; r_sub.font.color.rgb = COLOR_BLACK
    r_event = p_div.add_run("(Tài liệu hợp nhất: Kế hoạch Tổng thể, Thiết kế Kỹ thuật, Dự toán BOM, Quy trình Thử nghiệm 4 Giai đoạn & Kịch bản Thi đấu)\nCuộc thi: HNUE Olympic STEM 2026 — Bảng Tiểu học (Khối 4 - 5)")
    r_event.font.name = 'Times New Roman'; r_event.font.size = Pt(11); r_event.font.italic = True; r_event.font.color.rgb = COLOR_BLACK
    
    # Thông tin nhóm
    p_info = doc.add_paragraph()
    p_info.paragraph_format.space_before = Pt(6)
    p_info.paragraph_format.space_after = Pt(10)
    p_info.paragraph_format.line_spacing = 1.15
    p_info.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p_info.add_run("Nhóm tác giả: "); r.font.bold = True; r.font.color.rgb = COLOR_BLACK
    r = p_info.add_run("Phạm Hữu Đạt (4A1 - Đội trưởng), Vũ Minh Quang (4A1), Vũ Ngọc An Đông (5A1)\n"); r.font.color.rgb = COLOR_BLACK
    r = p_info.add_run("Cán bộ hướng dẫn kỹ thuật: "); r.font.bold = True; r.font.color.rgb = COLOR_BLACK
    r = p_info.add_run("Thầy Lê Ngọc Anh (Tổ trưởng STEM) | Trường Tiểu học Marie Curie Thái Bình"); r.font.color.rgb = COLOR_BLACK
    
    # ==========================================
    # PHẦN I: TỔNG QUAN DỰ ÁN VÀ BỐI CẢNH
    # ==========================================
    add_heading_1(doc, "PHẦN I: TỔNG QUAN DỰ ÁN, BỐI CẢNH THỰC TIỄN VÀ MỤC TIÊU")
    
    add_heading_2(doc, "1.1. Bối cảnh thực tiễn tại cổng trường học giờ tan tầm")
    add_body_p(doc, "Vào các khung giờ cao điểm (7h00 - 7h30 sáng và 16h30 - 17h15 chiều), khu vực cổng trường học thường xuyên xảy ra tình trạng xung đột giao thông gay gắt giữa dòng xe ô tô, xe máy đưa đón và các em học sinh tự đi bộ qua đường. Học sinh tiểu học (lớp 1 đến lớp 5) có tầm vóc nhỏ bé, tầm nhìn bị che khuất, chưa có đầy đủ kỹ năng quan sát phán đoán tốc độ xe cơ giới. Mặt khác, đèn giao thông truyền thống hoạt động theo chu kỳ cố định máy móc, bắt dòng xe dừng chờ ngay cả khi không có người qua đường, gây dồn ứ cục bộ và tăng lượng khí phát thải độc hại ngay trước khuôn viên trường.")
    
    add_heading_2(doc, "1.2. Mục tiêu tối thượng (North Star Metric)")
    add_body_p(doc, "Dự án hướng tới giải quyết trọn vẹn 3 mục tiêu khoa học thực tiễn:")
    add_body_p(doc, "Bảo vệ an toàn tuyệt đối cho học sinh qua đường bằng cơ chế kép: Thị giác máy tính AI nhận diện cử chỉ xin đường kết hợp Rào chắn Barie vật lý ngăn học sinh tràn xuống lòng đường khi chưa có tín hiệu an toàn.", bold_prefix="1. An toàn học đường 100%: ")
    add_body_p(doc, "Đèn xe giữ Xanh liên tục khi đường vắng. Hệ thống chỉ kích hoạt chu kỳ dừng xe khi AI xác nhận có học sinh đứng chờ hợp lệ hoặc có xe ưu tiên khẩn cấp, cắt giảm 35% thời gian nổ máy chờ đợi vô lý của các phương tiện.", bold_prefix="2. Chống ùn tắc & Giảm phát thải: ")
    add_body_p(doc, "Mô hình được thiết kế vừa sức lứa tuổi tiểu học; 3 em học sinh làm chủ hoàn toàn từ thu thập tập ảnh mẫu, lắp ráp cắm giắc, hiểu rõ công thức động học đến tự tin vận hành sa bàn trước Ban Giám khảo.", bold_prefix="3. Tính giáo dục & Chân thực (Authenticity): ")

    add_heading_2(doc, "1.3. Phân công vai trò 3 học sinh Marie Curie")
    add_body_p(doc, "Thuyết minh phần Mở đầu, Nêu vấn đề cổng trường, Vận hành Nút bấm cơ học Failsafe (D2), Giải trình bảng dự toán 415.000 VNĐ và Tổng kết thông điệp xã hội.", bold_prefix="• Em Phạm Hữu Đạt (Lớp 4A1 - Đội trưởng): ")
    add_body_p(doc, "Phụ trách phần cứng, lắp ráp sa bàn, cắm giắc Arduino Nano Shield v3.0, căn chỉnh góc Barie 0° - 90°, trình bày công thức Toán học động học 15s và nguyên lý bảo vệ nguồn sụt áp.", bold_prefix="• Em Vũ Minh Quang (Lớp 4A1 - Kỹ thuật viên phần cứng): ")
    add_body_p(doc, "Phụ trách thu thập tập ảnh và huấn luyện mô hình AI Google Teachable Machine, điều hành trạm Chrome Web Serial, vận hành mô hình xe cứu thương (TH3) và kịch bản người qua đường (TH2).", bold_prefix="• Em Vũ Ngọc An Đông (Lớp 5A1 - Chuyên gia AI & Sa bàn): ")

    # ==========================================
    # PHẦN II: THIẾT KẾ KIẾN TRÚC VÀ PHẦN CỨNG
    # ==========================================
    add_heading_1(doc, "PHẦN II: THIẾT KẾ KIẾN TRÚC HỆ THỐNG 4 TẦNG & MẠCH SHIELD ĐỘT PHÁ")
    
    add_heading_2(doc, "2.1. Mô hình kiến trúc 4 tầng khép kín (4-Tier Architecture)")
    add_body_p(doc, "Hệ thống vận hành theo chu trình phản hồi kín 4 tầng công nghệ:")
    add_body_p(doc, "Mắt Webcam USB Mini rời HD 720p gắn trên đầu cần vươn cột đèn giao thông (cao 25cm, tay vươn 12cm, góc dốc 45° rọi thẳng vùng vạch kẻ đường 20x15cm).", bold_prefix="• Tầng 1 — Thị giác cảm biến (Vision Layer): ")
    add_body_p(doc, "Laptop điều hành chạy mô hình Deep Learning MobileNet (Google Teachable Machine) OFFLINE trên trình duyệt Google Chrome. Nhận diện 3 phân lớp với bộ lọc chống nhiễu Debounce 1.5s và truyền mã lệnh 1-Byte ('0', '1', '2') qua Web Serial API tốc độ 9600 bps.", bold_prefix="• Tầng 2 — Trí tuệ nhân tạo (Edge AI Layer): ")
    add_body_p(doc, "Bo mạch Arduino Nano v3.0 (chip ATmega328P) kết hợp Mạch mở rộng Arduino Nano Expansion Shield v3.0 xử lý toàn bộ máy trạng thái FSM 5 tình huống.", bold_prefix="• Tầng 3 — Điều khiển trung tâm (Microcontroller & Shield Layer): ")
    add_body_p(doc, "Động cơ Servo SG90 nâng hạ cần Barie siêu nhẹ 22cm, Cụm Module 3 LED ô tô, 2 LED người đi bộ, Còi chip Buzzer âm thanh dẫn đường và Nút bấm cơ học Failsafe D2.", bold_prefix="• Tầng 4 — Cơ cấu chấp hành & Cảnh báo (Actuator Layer): ")

    add_heading_2(doc, "2.2. Đột phá an toàn từ Mạch mở rộng Arduino Nano Expansion Shield v3.0")
    add_body_p(doc, "Trong các mô hình STEM truyền thống, việc dùng Breadboard (bo test cắm lỗ) khiến hệ thống chằng chịt hàng chục sợi dây cắm lỏng lẻo. Khi học sinh bưng bê sa bàn lên sân khấu thi đấu, chỉ cần 1 chân cắm bị tuột hoặc rung lắc sẽ làm tê liệt toàn bộ hệ thống ngay trước giờ chấm thi.")
    add_body_p(doc, "Việc nâng cấp bo mạch Nano Shield v3.0 mang lại 4 ưu thế vượt trội:")
    add_body_p(doc, "Mỗi chân I/O (D0 - D13, A0 - A7) được phân tách thành 3 cọc tiêu chuẩn: Tín hiệu (S - Vàng), Nguồn dương (V - Đỏ), Nối đất (G - Đen).", bold_prefix="1. Chuẩn hóa cắm giắc 3 chân S-V-G: ")
    add_body_p(doc, "Giắc cắm 3 pin của Động cơ Servo SG90 cắm khớp 100% vào hàng cọc D9 trên Shield, loại bỏ hoàn toàn việc hàn chì độc hại.", bold_prefix="2. Khớp trực tiếp giắc Servo SG90: ")
    add_body_p(doc, "Tích hợp sẵn nút bấm Reset cứng ngay trên mặt Shield giúp học sinh khởi động lại hệ thống dễ dàng mà không cần thò tay vào gầm sa bàn.", bold_prefix="3. Nút Reset cứng tiện lợi: ")
    add_body_p(doc, "Bảo vệ các chân chip ATmega328P khỏi cong vênh, chịu lực cơ học tốt khi di chuyển đường dài từ Thái Bình lên Hà Nội.", bold_prefix="4. Chống gãy chân chip: ")

    add_heading_2(doc, "2.3. Sơ đồ phân bổ chân cắm chuẩn (Pinout Mapping)")
    
    tbl_pin = doc.add_table(rows=1, cols=4)
    tbl_pin.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_pin)
    set_row_tbl_header(tbl_pin.rows[0])
    set_row_cant_split(tbl_pin.rows[0])
    
    p_hdrs = ["Chân Shield", "Loại chân", "Thiết bị ngoại vi kết nối", "Chức năng hoạt động chi tiết"]
    p_widths = [Cm(2.2), Cm(2.8), Cm(4.5), Cm(6.5)]
    for i, h in enumerate(p_hdrs):
        c = tbl_pin.rows[0].cells[i]
        c.width = p_widths[i]
        set_cell_margins(c, top=100, bottom=100, left=80, right=80)
        set_cell_no_shading(c)
        set_cell_valign(c, "center")
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.font.name = 'Times New Roman'; r.font.size = Pt(11); r.font.bold = True; r.font.color.rgb = COLOR_BLACK
        
    pin_data = [
        ("D2", "Input Pullup", "Module Nút bấm cơ học Failsafe 3-pin", "Ngắt phần cứng INT0 kích hoạt chu kỳ an toàn khi camera mất kết nối."),
        ("D6", "Digital Output", "Đèn LED Người đi bộ ĐỎ", "Báo hiệu người đi bộ dừng chờ an toàn trên vỉa hè."),
        ("D7", "Digital Output", "Đèn LED Người đi bộ XANH", "Báo hiệu học sinh được phép bước qua đường trong 15 giây."),
        ("D8", "Digital Output", "Còi chip Active Buzzer mini 5V", "Phát âm thanh nhịp 500ms (12s đầu) và dồn dập 200ms (3s cuối) dẫn đường."),
        ("D9", "PWM Output", "Động cơ Servo mini SG90 (Barie)", "Nâng hạ cần Barie: 0° (đóng ngang) đến 90° (dựng đứng mở lối)."),
        ("D10", "Digital Output", "Đèn LED Xe XANH", "Dòng xe ô tô được phép lưu thông thông suốt qua cổng trường."),
        ("D11", "Digital Output", "Đèn LED Xe VÀNG", "Cảnh báo giảm tốc độ trong 3 giây trước khi dừng hẳn."),
        ("D12", "Digital Output", "Đèn LED Xe ĐỎ", "Yêu cầu phương tiện dừng bánh trước vạch dừng nhường đường học sinh."),
        ("5V / GND", "Power Rails", "Toàn bộ cảm biến và cơ cấu chấp hành", "Đường ray nguồn ổn định 5V chia đều trên bo mạch Shield.")
    ]
    for r_idx, row_data in enumerate(pin_data):
        row = tbl_pin.add_row()
        set_row_cant_split(row)
        for c_idx, val in enumerate(row_data):
            c = row.cells[c_idx]
            c.width = p_widths[c_idx]
            set_cell_margins(c, top=80, bottom=80, left=80, right=80)
            set_cell_no_shading(c)
            set_cell_valign(c, "center")
            p = c.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx in [0, 1] else WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(val)
            r.font.name = 'Times New Roman'; r.font.size = Pt(10.5); r.font.color.rgb = COLOR_BLACK
            if c_idx == 0:
                r.font.bold = True

    # ==========================================
    # PHẦN III: TÍNH TOÁN KHOA HỌC STEM & ĐIỆN NĂNG
    # ==========================================
    add_heading_1(doc, "PHẦN III: TÍNH TOÁN KHOA HỌC, ĐỘNG HỌC & ĐIỆN NĂNG HỆ THỐNG")
    
    add_heading_2(doc, "3.1. Bản vẽ sa bàn tỷ lệ xích 1:20 (Toán học & Mô hình hóa)")
    add_body_p(doc, "Mô hình sa bàn được thiết kế theo đúng tỷ lệ thực tế 1:20 (1cm trên sa bàn tương ứng 20cm ngoài thực tế):")
    add_body_p(doc, "Kích thước sa bàn ngã tư: 60cm x 80cm (đặt vừa vặn trên bàn thi đấu 60cm x 120cm của BTC, dành 40cm còn lại để trạm Laptop điều hành).", bold_prefix="• ")
    add_body_p(doc, "Lòng đường xe chạy: 40cm sa bàn tương ứng 8 mét thực tế (chuẩn đường 2 làn xe trước cổng trường tiểu học).", bold_prefix="• ")
    add_body_p(doc, "Vỉa hè người đi bộ: Mỗi bên 10cm tương ứng 2 mét vỉa hè thực tế.", bold_prefix="• ")
    add_body_p(doc, "Cột đèn giao thông: Cao 25cm (tương ứng 5m thực tế); cần vươn ngang 12cm (tương ứng 2.4m thực tế).", bold_prefix="• ")
    add_body_p(doc, "Quy cách và hướng lắp đặt Rào chắn Barie học sinh: Động cơ Servo SG90 được gắn cố định tại mép vỉa hè trường học, ngay trước đầu vạch sang đường ngựa vằn. Cần Barie balsa dài 22cm dán sọc đỏ - trắng: Khi Đóng (0°), cần hạ nằm ngang song song mép vỉa hè tạo thành rào chắn vật lý ngăn học sinh tràn từ vỉa hè xuống lòng đường; lòng đường xe chạy hoàn toàn thông suốt không bị vướng. Khi Mở (90°), servo nâng cần dựng đứng lên trời để mở lối cho học sinh bước qua vạch sang đường an toàn trong 15 giây.", bold_prefix="• ")

    add_heading_2(doc, "3.2. Công thức tính thời gian chu kỳ đèn đi bộ 15 giây")
    add_body_p(doc, "Dựa trên các nghiên cứu về thể chất học sinh tiểu học Việt Nam lứa tuổi 9 - 10 tuổi (Lớp 4 - 5):")
    add_body_p(doc, "Chiều rộng lòng đường cổng trường: W = 8 mét.", bold_prefix="• ")
    add_body_p(doc, "Vận tốc đi bộ trung bình của học sinh: v_tb ≈ 0.8 m/giây.", bold_prefix="• ")
    add_body_p(doc, "Thời gian di chuyển lý thuyết: t_walk = W / v_tb = 8m / 0.8m/s = 10 giây.", bold_prefix="• ")
    add_body_p(doc, "Hệ số an toàn đệm (t_buffer): Dành cho học sinh lớp 1 đi chậm hoặc mang cặp nặng: t_buffer = 5 giây.", bold_prefix="• ")
    
    add_callout_box(doc, "CÔNG THỨC ĐỘNG HỌC TỔNG THỜI GIAN ĐÈN XANH NGƯỜI ĐI BỘ",
                    "T_ped_green = t_walk + t_buffer = (W / v_tb) + t_buffer = (8m / 0.8m/s) + 5s = 15 GIÂY.\n"
                    "Thời gian 15 giây vừa đủ cho nhóm 4-6 học sinh qua đường an toàn, vừa không làm dòng xe cộ bị dồn ứ quá lâu gây ùn tắc giao thông cục bộ.")

    add_heading_2(doc, "3.3. Tính toán bộ lọc xác nhận AI Debounce 1.5 giây")
    add_body_p(doc, "Để triệt tiêu lỗi nhận diện ảo do người đi ngang qua ngẫu nhiên hoặc ánh sáng thay đổi:")
    add_body_p(doc, "Tốc độ xử lý khung hình camera: FPS = 15 khung hình/giây.", bold_prefix="• ")
    add_body_p(doc, "Ngưỡng xác suất tối thiểu: Confidence Threshold ≥ 85%.", bold_prefix="• ")
    add_body_p(doc, "Thời gian xác nhận bắt buộc: t_confirm = 1.5 giây (tương đương AI phải nhận diện đúng liên tục trong ít nhất 22 frames liên tiếp). Nếu người đi lướt qua dưới 1.5s rồi biến mất, hệ thống bỏ qua, giữ đèn xe Xanh.", bold_prefix="• ")

    add_heading_2(doc, "3.4. Bảng tính toán công suất điện & Cân bằng tải phân nhánh")
    
    tbl_pwr = doc.add_table(rows=1, cols=6)
    tbl_pwr.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_pwr)
    set_row_tbl_header(tbl_pwr.rows[0])
    set_row_cant_split(tbl_pwr.rows[0])
    
    pw_hdrs = ["STT", "Phân nhánh & Thiết bị linh kiện", "Điện áp (V)", "Dòng tĩnh (mA)", "Dòng đỉnh (mA)", "Công suất đỉnh (W)"]
    pw_widths = [Cm(1.0), Cm(6.5), Cm(2.0), Cm(2.2), Cm(2.2), Cm(2.1)]
    for i, h in enumerate(pw_hdrs):
        c = tbl_pwr.rows[0].cells[i]
        c.width = pw_widths[i]
        set_cell_margins(c, top=100, bottom=100, left=60, right=60)
        set_cell_no_shading(c)
        set_cell_valign(c, "center")
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.font.name = 'Times New Roman'; r.font.size = Pt(10.5); r.font.bold = True; r.font.color.rgb = COLOR_BLACK
        
    pwr_data = [
        ("A", "NHÁNH 1: MẠCH ĐIỀU KHIỂN & SA BÀN (NANO SHIELD)", "5.0 V", "~70 mA", "~316 mA", "~1.58 W", True),
        ("1", "Mạch Arduino Nano v3.0 (chip ATmega328P)", "5.0 V", "20 mA", "30 mA", "0.15 W", False),
        ("2", "Cụm 3 LED ô tô (Đỏ, Vàng, Xanh có trở 220Ω)", "5.0 V", "20 mA", "20 mA", "0.10 W", False),
        ("3", "Cụm 2 LED người đi bộ (Đỏ, Xanh có trở 220Ω)", "5.0 V", "20 mA", "20 mA", "0.10 W", False),
        ("4", "Động cơ Servo mini SG90 (có tụ bù 470µF)", "5.0 V", "10 mA", "220 mA", "1.10 W", False),
        ("5", "Còi chip Buzzer mini 5V cảnh báo âm thanh", "5.0 V", "0 mA", "25 mA", "0.12 W", False),
        ("6", "Module Nút bấm cơ học Failsafe D2", "5.0 V", "0 mA", "1 mA", "0.005 W", False),
        ("B", "NHÁNH 2: MẮT THỊ GIÁC AI (WEBCAM USB MINI HD)", "5.0 V", "100 mA", "150 mA", "0.75 W", True),
        ("7", "Webcam USB Mini HD 720p cắm cổng máy tính/Hub", "5.0 V", "100 mA", "150 mA", "0.75 W", False),
        ("TỔNG", "TỔNG CỘNG TOÀN BỘ HỆ THỐNG TOÀN TẢI", "5.0 V", "~170 mA", "~466 mA", "~2.33 W", True)
    ]
    for r_idx, row_item in enumerate(pwr_data):
        row = tbl_pwr.add_row()
        set_row_cant_split(row)
        is_grp = row_item[6]
        for c_idx in range(6):
            c = row.cells[c_idx]
            c.width = pw_widths[c_idx]
            set_cell_margins(c, top=80, bottom=80, left=60, right=60)
            set_cell_no_shading(c)
            set_cell_valign(c, "center")
            p = c.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx in [0, 2] else (WD_ALIGN_PARAGRAPH.RIGHT if c_idx >= 3 else WD_ALIGN_PARAGRAPH.LEFT)
            r = p.add_run(row_item[c_idx])
            r.font.name = 'Times New Roman'; r.font.size = Pt(10.5); r.font.color.rgb = COLOR_BLACK
            if is_grp:
                r.font.bold = True

    add_body_p(doc, "Tổng dòng đỉnh toàn hệ thống chỉ đạt 466 mA, nằm hoàn toàn dưới ngưỡng giới hạn 500 mA của chuẩn USB 2.0 trên máy tính xách tay, đảm bảo an toàn tuyệt đối chống quá dòng.", italic=True)

    add_heading_2(doc, "3.5. Giải phẫu bẫy kỹ thuật sụt áp IC AMS1117 và 2 phương án cấp nguồn chuẩn")
    add_callout_box(doc, "CẢNH BÁO BẪY SỤT ÁP IC AMS1117 KHI DÙNG CÁP USB-TO-DC 5V",
                    "Jack DC 5.5x2.1mm trên bo Shield v3.0 được nối trực tiếp vào chân VIN của Arduino Nano, qua IC hạ áp tuyến tính AMS1117-5.0.\n"
                    "Theo Datasheet của AMS1117, điện áp rơi cực tiểu (Dropout Voltage) là Vdrop ≈ 1.1V đến 1.3V.\n"
                    "Nếu lấy nguồn 5.0V từ sạc dự phòng cắm vào Jack DC, điện áp đầu ra cấp cho Shield và Servo chỉ còn:\n"
                    "       V_out = V_in - V_drop = 5.0V - 1.1V ≈ 3.9V!\n"
                    "Tại mức 3.9V: Động cơ Servo SG90 (vốn yêu cầu 4.8V - 6.0V) sẽ bị suy giảm 60% lực kéo, rung bần bật, không nâng nổi cần Barie hoặc vi điều khiển ATmega328P bị reset liên tục!")
                    
    add_body_p(doc, "Cáp Mini-USB cắm trực tiếp từ Laptop hoặc cổng Powered USB Hub vào cổng USB của Arduino Nano. Nguồn 5.0V đi qua diode Schottky MBR0520 (sụt áp chỉ 0.15V), cung cấp mức 4.85V phẳng mịn cho toàn bộ hàng chân 5V của Shield. Động cơ Servo hoạt động mạnh mẽ, không qua IC AMS1117. Lúc này Cáp USB-to-DC 5.5mm hoàn toàn không cần dùng (THỪA).", bold_prefix="• Phương án Chuẩn 1 (Tối ưu nhất — Khuyên dùng): ")
    add_body_p(doc, "Nếu muốn cấp nguồn riêng cho Jack DC trên Shield để sa bàn chạy độc lập không phụ thuộc máy tính: Bắt buộc nguồn cấp vào Jack DC phải là Adapter 9V-1A hoặc Hộp pin 2 cell 18650 (7.4V - 8.4V). Khi đó IC AMS1117 hạ áp từ 9V ra đúng chuẩn 5.0V ổn định.", bold_prefix="• Phương án Chuẩn 2 (Khi dùng nguồn ngoài cho Jack DC): ")

    add_body_p(doc, "Khi sử dụng Pin sạc dự phòng thông minh (Xiaomi, Anker, Baseus...), học sinh chỉ cần bấm đúp 2 lần (double-click) hoặc nhấn giữ 3 giây nút nguồn trên pin dự phòng để bật chế độ Trickle Charge Mode (sạc dòng nhỏ). Pin sẽ cấp nguồn 5.0V liên tục mà không bao giờ tự động tắt nguồn khi hệ thống ở trạng thái dòng nghỉ thấp.", bold_prefix="• Kỹ thuật chống ngắt Pin sạc dự phòng: ")

    # ==========================================
    # PHẦN IV: BẢNG DỰ TOÁN KINH PHÍ & KIỂM TOÁN
    # ==========================================
    add_heading_1(doc, "PHẦN IV: BẢNG DỰ TOÁN KINH PHÍ & KIỂM TOÁN LINH KIỆN")
    add_body_p(doc, "Bảng dự toán tuân thủ nghiêm ngặt quy chế của Ban Tổ chức: Tổng chi phí nguyên vật liệu không vượt quá 1.000.000 VNĐ / 1 đội thi.")
    
    tbl_bom = doc.add_table(rows=1, cols=6)
    tbl_bom.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_bom)
    set_row_tbl_header(tbl_bom.rows[0])
    set_row_cant_split(tbl_bom.rows[0])
    
    b_hdrs = ["STT", "Danh mục thiết bị / Vật tư", "Quy cách kỹ thuật", "SL", "Đơn giá (đ)", "Thành tiền (đ)"]
    b_widths = [Cm(1.0), Cm(5.2), Cm(4.3), Cm(1.2), Cm(2.2), Cm(2.3)]
    for i, h in enumerate(b_hdrs):
        c = tbl_bom.rows[0].cells[i]
        c.width = b_widths[i]
        set_cell_margins(c, top=100, bottom=100, left=80, right=80)
        set_cell_no_shading(c)
        set_cell_valign(c, "center")
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.font.name = 'Times New Roman'; r.font.size = Pt(11); r.font.bold = True; r.font.color.rgb = COLOR_BLACK
        
    bom_items = [
        ("I", "HỆ THỐNG MẠCH ĐIỀU KHIỂN & CẢM BIẾN", "", "", "", "192.000", True),
        ("1", "Mạch vi điều khiển Arduino Nano v3.0", "ATmega328P nạp CH340 + Cáp Mini-B", "1 bộ", "65.000", "65.000", False),
        ("2", "Mạch mở rộng Arduino Nano Shield v3.0", "Chuẩn 3-pin S-V-G, tích hợp nút Reset", "1 chiếc", "22.000", "22.000", False),
        ("3", "Mắt Webcam USB Mini HD rời", "HD 720p, dây dài 1.2m, góc rộng", "1 chiếc", "95.000", "95.000", False),
        ("4", "Còi chip Active Buzzer mini 5V", "Phát âm tần 2.3 kHz dẫn đường", "1 chiếc", "5.000", "5.000", False),
        ("5", "Module Nút nhấn cơ học Tactile 3-pin", "Nút Failsafe ngắt cứng D2 có sẵn trở", "1 chiếc", "5.000", "5.000", False),
        ("II", "CƠ CẤU CHẤP HÀNH & HIỂN THỊ", "", "", "", "48.000", True),
        ("6", "Động cơ Servo mini SG90 9g", "Điện áp 5V, lực kéo 1.6kg.cm, 180°", "1 chiếc", "30.000", "30.000", False),
        ("7", "Module Cụm 3 LED Giao thông 5V", "Đỏ-Vàng-Xanh đúc sẵn có trở hạn dòng", "1 chiếc", "10.000", "10.000", False),
        ("8", "Cụm 2 LED Đi bộ (Đỏ - Xanh)", "LED phi 5mm siêu sáng kèm trở 220Ω", "2 chiếc", "3.000", "6.000", False),
        ("9", "Tụ hóa nhôm chống sụt áp 470µF/16V", "Triệt tiêu xung gai điện áp motor", "2 chiếc", "1.000", "2.000", False),
        ("III", "KẾT NỐI & DÂY CẮP TIÊU CHUẨN", "", "", "", "78.000", True),
        ("10", "Bộ chia USB Hub 4 cổng có nguồn phụ", "USB 2.0 gom gọn dây cắm Laptop", "1 chiếc", "55.000", "55.000", False),
        ("11", "Cáp bẹ Dupont Cái - Cái (40 sợi 20cm)", "Cắm nối module Shield tới đèn, còi", "1 tép", "15.000", "15.000", False),
        ("12", "Cáp bẹ Dupont Đực - Cái (20 sợi 20cm)", "Dự phòng ghép nối linh hoạt các cổng", "1 tép", "8.000", "8.000", False),
        ("IV", "VẬT LIỆU SA BÀN, CƠ KHÍ & ĐẠO CỤ", "", "", "", "97.000", True),
        ("13", "Khung Sa bàn Formex & Decal vạch kẻ", "Tấm Formex 60x80cm, decal kẻ vạch", "1 bộ", "60.000", "60.000", False),
        ("14", "Cột đèn giao thông & Cần gắn Camera", "Ống gen điện phi 16 cao 25cm, cần 12cm", "1 bộ", "5.000", "5.000", False),
        ("15", "Thanh cần Barie nhẹ 22cm & Ốc vít", "Que gỗ balsa (<3g) gắn cánh tay servo", "1 chiếc", "2.000", "2.000", False),
        ("16", "Băng dính xốp 3M & Keo nến", "Cố định chắc Servo và Shield xuống sa bàn", "1 cuộn", "15.000", "15.000", False),
        ("17", "Mô hình xe ô tô cứu thương mini", "Xe đồ chơi trắng-đỏ làm mẫu test AI", "1 chiếc", "15.000", "15.000", False),
        ("TỔNG", "TỔNG KINH PHÍ THỰC TẾ DỰ ÁN", "", "", "", "415.000", True)
    ]
    for r_idx, item in enumerate(bom_items):
        row = tbl_bom.add_row()
        set_row_cant_split(row)
        is_grp = item[6]
        for c_idx in range(6):
            c = row.cells[c_idx]
            c.width = b_widths[c_idx]
            set_cell_margins(c, top=80, bottom=80, left=60, right=60)
            set_cell_no_shading(c)
            set_cell_valign(c, "center")
            p = c.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            val = item[c_idx]
            if is_grp:
                if c_idx == 1: val = item[1]
                elif c_idx == 5: val = item[5]
                elif c_idx > 1 and c_idx < 5: val = ""
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx in [0, 3] else (WD_ALIGN_PARAGRAPH.RIGHT if c_idx in [4, 5] else WD_ALIGN_PARAGRAPH.LEFT)
            r = p.add_run(val)
            r.font.name = 'Times New Roman'; r.font.size = Pt(11 if is_grp else 10.5); r.font.color.rgb = COLOR_BLACK
            if is_grp:
                r.font.bold = True

    add_body_p(doc, "Tổng chi phí 415.000 VNĐ giúp tiết kiệm 58.5% (dư địa an toàn 585.000 VNĐ). Đã loại bỏ hoàn toàn Breadboard thừa và cáp USB-to-DC sụt áp, bổ sung kịp thời cần Barie balsa, dây Đực-Cái, module LED giao thông, cột đèn và xe cứu thương đồ chơi.", italic=True)

    # ==========================================
    # PHẦN V: QUY TRÌNH THỰC HIỆN THEO 6 GIAI ĐOẠN (PHASES)
    # ==========================================
    add_heading_1(doc, "PHẦN V: QUY TRÌNH THỰC HIỆN DỰ ÁN THEO 6 GIAI ĐOẠN (PHASES)")
    add_body_p(doc, "Toàn bộ lộ trình triển khai từ nay đến ngày thi Bán kết (05/12/2026) được chia thành 6 giai đoạn rõ ràng, có phân công người phụ trách và sản phẩm đầu ra cụ thể:")

    add_heading_2(doc, "PHASE 1: Mua sắm, Kiểm đếm và Lắp ráp Cơ điện (10/11 – 13/11/2026)")
    add_body_p(doc, "Thầy Lê Ngọc Anh (cố vấn kỹ thuật), Em Vũ Minh Quang (chính), Em Phạm Hữu Đạt.", bold_prefix="• Người phụ trách: ")
    add_body_p(doc, "Đặt mua hỏa tốc 17 hạng mục theo Bảng BOM; cắm bo Arduino Nano vào trung tâm Shield v3.0; gắn tụ bù 470µF vào chân nguồn VCC-GND gần D9; dán cố định Servo SG90 bằng băng dính xốp 3M xuống sa bàn; bắt vít cần Barie gỗ balsa 22cm vào cánh tay đòn servo horn; dựng cột đèn ống gen phi 16 cao 25cm luồn dây LED.", bold_prefix="• Công việc chi tiết: ")
    add_body_p(doc, "Sa bàn cơ khí hoàn thiện, hệ thống mạch điện cắm giắc chắc chắn, không bị lỏng dây khi rung lắc.", bold_prefix="• Sản phẩm đầu ra: ")

    add_heading_2(doc, "PHASE 2: Chẩn đoán & Thử nghiệm Phần cứng Tự động (14/11 – 17/11/2026)")
    add_body_p(doc, "Em Vũ Minh Quang (chính), Em Phạm Hữu Đạt.", bold_prefix="• Người phụ trách: ")
    add_body_p(doc, "Nạp sketch chẩn đoán 'test_hardware_diagnostic.ino' vào Arduino Nano qua cổng USB; mở Serial Monitor 9600 bps, bấm phím 'A' để hệ thống tự động quét tuần tự: D10-D11-D12 (LED xe), D6-D7 (LED đi bộ), D8 (Còi kêu 3 nhịp), D9 (Servo quét 0° - 90° - 0°), D2 (Nút bấm Failsafe); đo dòng tĩnh 70mA và dòng đỉnh 220mA; thử nghiệm chế độ chống ngắt Trickle Mode của pin dự phòng trong 30 phút liên tục.", bold_prefix="• Công việc chi tiết: ")
    add_body_p(doc, "Biên bản chẩn đoán phần cứng PASS 100%, góc quay Barie 90° vuông vức, không sụt áp.", bold_prefix="• Sản phẩm đầu ra: ")

    add_heading_2(doc, "PHASE 3: Huấn luyện Mắt AI & Hiệu chuẩn Truyền thông (18/11 – 21/11/2026)")
    add_body_p(doc, "Em Vũ Ngọc An Đông (chuyên gia AI), Thầy Lê Ngọc Anh.", bold_prefix="• Người phụ trách: ")
    add_body_p(doc, "Thu thập 500 ảnh thực tế tại cổng trường Marie Curie (gồm đường vắng, học sinh giơ tay xin đường góc nhìn từ trên cao xuống 45°, và ảnh mô hình xe cứu thương); huấn luyện mô hình MobileNet trên Google Teachable Machine; xuất mô hình dạng TensorFlow.js nạp vào 'ai_traffic_web_controller.html' chạy hoàn toàn OFFLINE trên Google Chrome; chạy bài test thực nghiệm 100 lần ngẫu nhiên (Confusion Matrix) đạt độ chính xác ≥ 85%; đo độ trễ Web Serial API < 50ms.", bold_prefix="• Công việc chi tiết: ")
    add_body_p(doc, "Trạm điều khiển AI trên Chrome nhận diện siêu nhạy, bộ lọc Debounce 1.5s triệt tiêu 100% nhận diện ảo.", bold_prefix="• Sản phẩm đầu ra: ")

    add_heading_2(doc, "PHASE 4: Tích hợp Toàn diện 5 Tình huống FSM & Diễn tập Khẩn cấp (22/11 – 26/11/2026)")
    add_body_p(doc, "Cả 3 học sinh (Đạt, Quang, Đông) dưới sự giám sát của Thầy Lê Ngọc Anh.", bold_prefix="• Người phụ trách: ")
    add_body_p(doc, "Nạp firmware chính thức 'traffic_light_arduino.ino' vào Arduino Nano; kết nối cổng USB với trạm Chrome; diễn tập liên hoàn 5 tình huống: TH1 (Đường vắng), TH2 (Học sinh qua đường 15s), TH3 (Xe cứu thương cắt ngang khi học sinh đang qua đường — kiểm chứng Pha giải tỏa an toàn 2.5s), TH4 (Nút cơ học Failsafe D2), TH5 (Watchdog Safe Mode rút cáp USB nháy vàng 1Hz); chạy thử nghiệm độ bền liên tục trong 30 phút không nghỉ.", bold_prefix="• Công việc chi tiết: ")
    add_body_p(doc, "Hệ thống vận hành trơn tru không lỗi logic, nhiệt độ chip và động cơ < 42°C.", bold_prefix="• Sản phẩm đầu ra: ")

    add_heading_2(doc, "PHASE 5: Luyện tập Kịch bản Thuyết trình & Phản biện Bấm giờ (27/11 – 30/11/2026)")
    add_body_p(doc, "Em Phạm Hữu Đạt (chính), Em Vũ Minh Quang, Em Vũ Ngọc An Đông.", bold_prefix="• Người phụ trách: ")
    add_body_p(doc, "Luyện tập kịch bản bấm giờ chuẩn 300 giây (5 phút), phân vai rõ ràng: Đạt (60s mở đầu + 60s kết luận), Quang (90s kỹ thuật phần cứng & công thức), Đông (90s AI và sa bàn); luyện tập trả lời ngân hàng 10 câu hỏi phản biện của Ban Giám khảo; quay video clip thực tế sa bàn 3 phút chất lượng cao.", bold_prefix="• Công việc chi tiết: ")
    add_body_p(doc, "Học sinh tự tin làm chủ kiến thức, thuyết trình lưu loát đúng thời lượng, dung sai không quá ±10 giây.", bold_prefix="• Sản phẩm đầu ra: ")

    add_heading_2(doc, "PHASE 6: Hoàn tất Hồ sơ & Tham gia Thi đấu Bán kết (01/12 – 05/12/2026)")
    add_body_p(doc, "Thầy Lê Ngọc Anh, Đội tuyển STEM MCA, Ban Giám Hiệu nhà trường.", bold_prefix="• Người phụ trách: ")
    add_body_p(doc, "Nộp Báo cáo tóm tắt dự án, Bản vẽ kỹ thuật và Video clip lên cổng thông tin trực tuyến của BTC trước 17h00 ngày 01/12/2026; đóng gói sa bàn trong thùng chống sốc; tham gia thi đấu trực tiếp Vòng Bán kết tại Trường ĐH Sư phạm Hà Nội vào ngày 05/12/2026.", bold_prefix="• Công việc chi tiết: ")
    add_body_p(doc, "Hoàn thành xuất sắc bài thi và bảo vệ trước Hội đồng Giám khảo, hướng tới Giải Nhất cuộc thi.", bold_prefix="• Sản phẩm đầu ra: ")

    # ==========================================
    # PHẦN VI: THUYẾT MINH CHI TIẾT 5 TÌNH HUỐNG FSM
    # ==========================================
    add_heading_1(doc, "PHẦN VI: THUYẾT MINH CHI TIẾT 5 TÌNH HUỐNG VẬN HÀNH (FSM)")
    add_body_p(doc, "Hệ thống vận hành chính xác theo Máy trạng thái hữu hạn 5 tình huống, tích hợp Pha chuyển tiếp an toàn khẩn cấp:")

    add_heading_2(doc, "Tình huống 1: Đường vắng — Dòng xe lưu thông thông suốt (Normal Road)")
    add_body_p(doc, "Camera AI liên tục quét mặt đường vạch kẻ, phân lớp '0_Normal_Road' đạt xác suất ≥ 85%. Đèn xe Xanh sáng liên tục, đèn người đi bộ Đỏ, cần Barie hạ góc 0° nằm ngang chắn học sinh trên vỉa hè, còi Buzzer tắt. Dòng phương tiện di chuyển thông suốt không bị gián đoạn, giảm 35% lượng khí thải nổ máy chờ đèn đỏ trước cổng trường.")

    add_heading_2(doc, "Tình huống 2: Học sinh qua đường (AI Pedestrian Crossing)")
    add_body_p(doc, "Khi học sinh đứng trên vỉa hè giơ tay xin qua đường:", bold_prefix="• ")
    add_body_p(doc, "Học sinh phải giơ tay liên tục trong 1.5 giây (≥ 22 frames liên tiếp) với độ tin cậy ≥ 85%. Nếu người đi lướt qua dưới 1.5s, hệ thống bỏ qua.", bold_prefix="  - Pha 1 (Xác nhận Debounce 1.5s): ")
    add_body_p(doc, "Đèn xe chuyển VÀNG trong đúng 3.0 giây để phương tiện từ xa hãm phanh an toàn. Barie vẫn đóng.", bold_prefix="  - Pha 2 (Cảnh báo giảm tốc 3s): ")
    add_body_p(doc, "Đèn xe chuyển ĐỎ dừng hẳn xe; Đèn đi bộ bật XANH; Động cơ Servo nhẹ nhàng nâng cần Barie lên 90° (trong 1.35s); Còi chip kêu nhịp 'tít... tít...' 500ms dẫn đường người khiếm thị. Thời gian 15s được tính toán khoa học theo công thức động học.", bold_prefix="  - Pha 3 (Mở lối an toàn 15s): ")
    add_body_p(doc, "Trong 3 giây cuối cùng, còi chip kêu dồn dập nhịp 200ms báo sắp hết giờ; cần Barie từ từ hạ về 0° chắn ngang vỉa hè; sau đó đèn xe mới chuyển lại Xanh.", bold_prefix="  - Pha 4 (Đóng Barie & Phục hồi): ")

    add_heading_2(doc, "Tình huống 3: Xe cứu thương ưu tiên khẩn cấp (Emergency Preemption)")
    add_body_p(doc, "Camera AI phát hiện xe cứu thương '2_Ambulance_Emergency' (độ tin cậy ≥ 85%):", bold_prefix="• ")
    add_body_p(doc, "Đèn xe lập tức giữ XANH liên tục, còi hú dài cảnh báo, xe cứu thương phóng qua ngã tư thông suốt.", bold_prefix="  - Nếu đang ở TH1 (Đường vắng): ")
    add_body_p(doc, "Hệ thống KHÔNG ĐƯỢC lập tức hạ Barie và bật đèn xe xanh ngay (tránh xe đâm vào học sinh). Hệ thống lập tức kích hoạt Pha chuyển tiếp an toàn khẩn cấp 2.5 giây: Còi hú dồn dập 100ms, đèn đi bộ nhấp nháy ĐỎ báo học sinh rảo bước lên vỉa hè. Cần Barie vẫn MỞ để học sinh có lối thoát. Sau đúng 2.5s, Barie mới hạ về 0° và đèn xe ô tô mới bật XANH KHẨN CẤP cho xe cứu thương lưu thông tuyệt đối an toàn.", bold_prefix="  - Nếu đang ở TH2 (Học sinh đang đi giữa đường): ")

    add_heading_2(doc, "Tình huống 4: Nút bấm dự phòng cơ học (Failsafe Override)")
    add_body_p(doc, "Khi trời mưa to sương mù làm mờ camera hoặc mất nhận diện AI, học sinh chỉ cần ấn Nút bấm cơ học gắn trên thân cột đèn. Tín hiệu ngắt cứng INT0 trên chân D2 lập tức kích hoạt chu kỳ an toàn: Đèn xe chuyển Vàng 3s -> Đèn xe Đỏ 15s + Người Xanh + Barie nhấc 90° cho học sinh sang đường an toàn.")

    add_heading_2(doc, "Tình huống 5: Watchdog Safe Mode khi mất kết nối máy tính")
    add_body_p(doc, "Nếu máy tính bị hết pin, tuột cáp USB hoặc mất nhịp sống còn Heartbeat quá 3.0 giây, mạch Arduino tự động chuyển sang chế độ phòng thủ: Cần Barie khóa chặt góc 0° bảo vệ học sinh trên vỉa hè, đồng thời đèn VÀNG ô tô tự động chuyển sang chế độ NHẤP NHÁY 1Hz (500ms sáng, 500ms tắt) đúng theo Quy chuẩn Quốc gia QCVN 41:2019/BGTVT cảnh báo các phương tiện giảm tốc độ khi đi qua trường học.")

    # ==========================================
    # PHẦN VII: KỊCH BẢN THUYẾT TRÌNH & PHẢN BIỆN
    # ==========================================
    add_heading_1(doc, "PHẦN VII: KỊCH BẢN THUYẾT TRÌNH 5 PHÚT & NGÂN HÀNG 10 CÂU HỎI PHẢN BIỆN")
    
    add_heading_2(doc, "7.1. Kịch bản thuyết trình bấm giờ đúng 300 giây (5 phút)")
    add_body_p(doc, "\"Kính chào Ban Giám khảo! Chúng con là đội tuyển STEM Marie Curie Thái Bình. Hàng ngày tan trường, chúng con chứng kiến bạn bè rất sợ hãi khi tự qua đường giữa dòng xe đông đúc. Đèn tín hiệu cũ thì máy móc bắt xe dừng vô lý gây tắc đường. Vì vậy, chúng con sáng chế: 'Hệ thống Đèn Giao Thông Học Đường Thông Minh Tích Hợp AI Vision & Rào Chắn Barie Tự Động' để giải quyết triệt để vấn đề này ạ!\"", bold_prefix="• Em Phạm Hữu Đạt (0:00 - 1:00 — Mở đầu & Nêu vấn đề): ")
    add_body_p(doc, "\"Thưa Thầy Cô, hệ thống của chúng con gồm 4 tầng công nghệ. Nhờ nâng cấp bo mạch Arduino Nano Shield v3.0, toàn bộ dây nối được chuẩn hóa cắm giắc 3-pin S-V-G, loại bỏ 100% rủi ro tuột dây. Chúng con dùng công thức Toán học: T = s/v + t_đệm = 8m/0.8m/s + 5s = 15 giây để tính chu kỳ đèn đi bộ. Toàn bộ sa bàn chỉ tiêu thụ 466mA điện áp 5V, an toàn tuyệt đối chống giật và tiết kiệm ngân sách chỉ 415.000 VNĐ ạ!\"", bold_prefix="• Em Vũ Minh Quang (1:00 - 2:30 — Giải pháp kỹ thuật & Toán học): ")
    add_body_p(doc, "\"Thưa Ban Giám khảo, đây là Mắt thần AI Webcam HD 720p. Con đã huấn luyện mô hình MobileNet trên Google Teachable Machine chạy hoàn toàn Offline trên trình duyệt Chrome. Bây giờ con xin mô phỏng: Khi con giơ tay xin đường 1.5 giây, AI xác nhận và ra lệnh cho Barie mở 90°. Đặc biệt, khi bạn Đạt đang qua đường mà xe cứu thương tới, hệ thống có Pha giải tỏa khẩn cấp 2.5s để bạn kịp lên lề an toàn trước khi xe cứu thương phóng qua ngã tư ạ!\"", bold_prefix="• Em Vũ Ngọc An Đông (2:30 - 4:00 — Biểu diễn trực tiếp Sa bàn & AI): ")
    add_body_p(doc, "\"Dự án của chúng con không chỉ là sản phẩm công nghệ mà còn là thông điệp về một môi trường học đường an toàn, thông minh và thân thiện. Nếu camera bị trục trặc, chúng con luôn có Nút bấm Failsafe ngắt cứng dự phòng. Chúng con xin trân trọng cảm ơn Ban Giám khảo và kính mời Thầy Cô đặt câu hỏi cho đội con ạ!\"", bold_prefix="• Em Phạm Hữu Đạt (4:00 - 5:00 — Tổng kết & Kêu gọi bảo vệ): ")

    add_heading_2(doc, "7.2. Ngân hàng 10 câu hỏi phản biện của Ban Giám khảo & Câu trả lời mẫu")
    
    qa_list = [
        ("Câu 1 (Công nghệ AI)",
         "Tại sao các con dùng Teachable Machine mà không dùng cảm biến siêu âm gắn ở vạch kẻ đường, vừa rẻ vừa không lo ánh sáng?",
         "Em Phạm Hữu Đạt (4A1)",
         "Thưa Ban Giám khảo, cảm biến siêu âm không phân biệt được đâu là học sinh xin đường, đâu là người đi bộ ngẫu nhiên, một chú chó chạy qua hay chiếc lá rơi. Teachable Machine giúp chúng con nhận diện đúng CỬ CHỈ GIƠ TAY xin đường của học sinh và phân biệt được HÌNH DÁNG XE CỨU THƯƠNG để ưu tiên. Đó là sự khác biệt giữa cảm biến thông thường và Trí tuệ nhân tạo ạ!"),
        ("Câu 2 (An toàn dự phòng)",
         "Nếu camera AI bị hỏng hoặc mất mạng Internet thì hệ thống có làm tê liệt ngã tư không?",
         "Em Vũ Minh Quang (4A1)",
         "Thưa Thầy Cô, hệ thống của chúng con có cơ chế An toàn kép (Fail-Safe): Thứ nhất, mô hình AI chạy OFFLINE 100% trên Chrome không cần mạng. Thứ hai, trên cột đèn có Nút bấm cơ học Failsafe D2, học sinh bấm nút là đèn chuyển đỏ an toàn ngay. Thứ ba, nếu mất cáp USB quá 3s, mạch chuyển sang đèn vàng nhấp nháy 1Hz theo chuẩn QCVN 41:2019/BGTVT ạ!"),
        ("Câu 3 (Toán học ứng dụng)",
         "Tại sao lại cài đặt đèn xanh cho người đi bộ là 15 giây mà không phải là 30 giây hay 1 phút?",
         "Em Vũ Ngọc An Đông (5A1)",
         "Thưa Thầy Cô, chúng con tính toán theo công thức Toán học: T = s/v + t_đệm. Chiều rộng cổng trường là 8m, vận tốc học sinh tiểu học là 0.8m/s, thời gian đi là 10 giây. Chúng con cộng thêm 5 giây đệm an toàn cho các em nhỏ lớp 1, tổng cộng đúng 15 giây. Nếu để 30s hay 1 phút thì dòng xe bị dồn ứ gây tắc đường và xả nhiều khí thải độc hại ạ!"),
        ("Câu 4 (Xung đột an toàn)",
         "Nếu học sinh đang đi giữa đường mà xe cứu thương lao tới, các con giải quyết thế nào để không đâm vào học sinh?",
         "Em Vũ Ngọc An Đông (5A1)",
         "Thưa Ban Giám khảo, hệ thống của chúng con có Pha chuyển tiếp an toàn khẩn cấp 2.5 giây (STATE_EMERGENCY_CLEARANCE). Khi phát hiện xe cứu thương, còi hú dồn dập 100ms giục học sinh rảo bước lên vỉa hè, cần Barie vẫn MỞ để học sinh thoát thân. Sau đúng 2.5 giây học sinh đã lên lề an toàn thì Barie mới đóng và đèn xe mới bật XANH KHẨN CẤP cho xe cứu thương đi qua ạ!"),
        ("Câu 5 (Sụt áp nguồn)",
         "Động cơ Servo SG90 khi quay hay bị giật dòng làm sụt áp vi điều khiển, các con chống sụt áp thế nào?",
         "Em Vũ Minh Quang (4A1)",
         "Thưa Thầy Cô, chúng con đã gắn 02 tụ hóa nhôm 470µF/16V song song vào chân nguồn VCC-GND của Servo trên Shield để bù dòng tức thời. Đồng thời chúng con cắm cáp Mini-USB trực tiếp nuôi Arduino để điện áp đạt 4.88V phẳng mịn, không cắm nguồn 5V qua Jack DC vì IC AMS1117 sẽ sụt áp xuống 3.9V làm yếu motor ạ!"),
        ("Câu 6 (Chi phí hạn mức)",
         "Ban tổ chức quy định kinh phí tối đa 1.000.000 VNĐ, sản phẩm của các con tốn bao nhiêu tiền?",
         "Em Phạm Hữu Đạt (4A1)",
         "Dạ thưa Ban Giám khảo, tổng chi phí thực tế của chúng con chỉ có 415.000 VNĐ (tiết kiệm tới 58.5% ngân sách). Máy tính là thiết bị lập trình ngoại vi sẵn có. Toàn bộ linh kiện trên sa bàn từ Arduino, Shield, Servo, Webcam, đèn LED đến khung formex đều có hóa đơn chi tiết trong Sổ tay kỹ thuật ạ!"),
        ("Câu 7 (Môi trường & Xã hội)",
         "Dự án của các con đóng góp gì cho thông điệp 'Những nhà kiến tạo tương lai' và bảo vệ môi trường?",
         "Em Vũ Minh Quang (4A1)",
         "Thưa Thầy Cô, sa bàn được làm từ vật liệu formex tái chế và que gỗ balsa. Đèn thông minh giúp xe ô tô không phải dừng chờ đèn đỏ khi không có người qua đường, cắt giảm đáng kể lượng khói bụi CO2 và tiếng ồn ngay trước cổng trường học ạ!"),
        ("Câu 8 (Phân biệt người lớn làm hộ)",
         "Đoạn code Arduino và mô hình AI này ai làm cho các con? Các con có tự làm được không?",
         "Em Vũ Minh Quang & Em Vũ Ngọc An Đông",
         "Dạ, Thầy Lê Ngọc Anh hướng dẫn chúng con nguyên lý máy trạng thái FSM và cách huấn luyện AI. Bạn Đông tự tay chụp 500 bức ảnh mẫu, bạn Quang tự cắm giắc trên Shield và nạp code chẩn đoán, bạn Đạt bấm nút Failsafe. Trong Sổ tay kỹ thuật có đầy đủ ảnh các bước chúng con tự tay làm từ ngày đầu tiên ạ!"),
        ("Câu 9 (Nhận diện vật lạ)",
         "Nếu thầy cầm bức ảnh xe cứu thương giơ nghiêng hoặc xe cứu thương đồ chơi khác màu thì AI có nhận ra không?",
         "Em Vũ Ngọc An Đông (5A1)",
         "Thưa Thầy, khi huấn luyện Teachable Machine, con đã chụp ảnh mẫu xe cứu thương ở nhiều góc nghiêng, khoảng cách xa gần và điều kiện ánh sáng khác nhau. Tuy nhiên, nếu xe lạ không nhận diện được thì trên cột đèn luôn có Nút bấm Failsafe để học sinh chủ động bấm xin đường an toàn 100% ạ!"),
        ("Câu 10 (Triển khai thực tế)",
         "Nếu nhà trường muốn lắp hệ thống này ở cổng trường thật thì cần thay đổi những gì?",
         "Em Phạm Hữu Đạt (4A1)",
         "Thưa Ban Giám khảo, để lắp cổng trường thật, chúng con chỉ cần thay Webcam mini bằng Camera IP ngoài trời chống nước chuẩn IP67, thay Servo 9g bằng Động cơ giảm tốc Barie công nghiệp 220V qua rơ-le (Relay), và thay bóng LED 5mm bằng Cụm đèn giao thông LED D200 tiêu chuẩn. Toàn bộ logic FSM và mô hình AI vẫn giữ nguyên 100% ạ!")
    ]

    for item_qa in qa_list:
        p_q = doc.add_paragraph()
        p_q.paragraph_format.space_before = Pt(6)
        p_q.paragraph_format.space_after = Pt(2)
        p_q.paragraph_format.line_spacing = 1.15
        r = p_q.add_run(f"❓ {item_qa[0]}: \"{item_qa[1]}\"")
        r.font.name = 'Times New Roman'; r.font.size = Pt(12); r.font.bold = True; r.font.color.rgb = COLOR_BLACK
        
        p_a = doc.add_paragraph()
        p_a.paragraph_format.space_before = Pt(0)
        p_a.paragraph_format.space_after = Pt(6)
        p_a.paragraph_format.line_spacing = 1.15
        r_spk = p_a.add_run(f"👉 Trả lời ({item_qa[2]}): ")
        r_spk.font.name = 'Times New Roman'; r_spk.font.size = Pt(12); r_spk.font.bold = True; r_spk.font.color.rgb = COLOR_BLACK
        r_ans = p_a.add_run(f"\"{item_qa[3]}\"")
        r_ans.font.name = 'Times New Roman'; r_ans.font.size = Pt(11.5); r_ans.font.italic = True; r_ans.font.color.rgb = COLOR_BLACK

    # ==========================================
    # PHẦN VIII: MA TRẬN PHÒNG NGỪA RỦI RO & CHỮ KÝ
    # ==========================================
    add_heading_1(doc, "PHẦN VIII: MA TRẬN PHÒNG NGỪA RỦI RO PHÒNG THI & PHÊ DUYỆT")
    
    add_heading_2(doc, "8.1. Ma trận 6 điểm chết Pre-Mortem Failure Matrix")
    
    tbl_pm = doc.add_table(rows=1, cols=4)
    tbl_pm.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_pm)
    set_row_tbl_header(tbl_pm.rows[0])
    set_row_cant_split(tbl_pm.rows[0])
    
    pm_hdrs = ["Mã lỗi", "Rủi ro tiềm ẩn tại phòng thi", "Cơ chế phòng thủ kỹ thuật", "Bài test kiểm tra xác nhận"]
    pm_widths = [Cm(1.2), Cm(4.8), Cm(5.2), Cm(4.8)]
    for i, h in enumerate(pm_hdrs):
        c = tbl_pm.rows[0].cells[i]
        c.width = pm_widths[i]
        set_cell_margins(c, top=100, bottom=100, left=80, right=80)
        set_cell_no_shading(c)
        set_cell_valign(c, "center")
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.font.name = 'Times New Roman'; r.font.size = Pt(11); r.font.bold = True; r.font.color.rgb = COLOR_BLACK
        
    pm_data = [
        ("F1", "Servo quay giật tải gây sụt áp làm treo chip CH340.", "Gắn 02 tụ bù 470µF/16V song song nguồn + cắm thẳng Mini-USB.", "Lấy tay giữ nhẹ cần barie khi quay, chip Arduino vẫn chạy bình thường."),
        ("F2", "Pin dự phòng tự ngắt sau 30 giây do dòng nghỉ thấp.", "Bấm đúp nút nguồn kích hoạt Trickle Charge Mode (dòng nhỏ).", "Cắm sa bàn để tĩnh 30 phút, mạch vẫn có điện liên tục."),
        ("F3", "Ánh sáng hội trường lạ làm AI nhận diện chập chờn.", "Bộ lọc Debounce 1.5s + Nút bấm cơ học Failsafe D2 dự phòng.", "Chiếu đèn pin chớp nháy vào camera, đèn giao thông không bị nhảy loạn."),
        ("F4", "Laptop bị tuột cáp USB trong lúc đang thi đấu.", "Watchdog Safe Mode tự động chuyển đèn vàng nháy 1Hz, đóng barie.", "Rút phắc cáp USB, sau đúng 3s đèn xe tự động nháy vàng cảnh báo."),
        ("F5", "Học sinh đang qua đường xe cứu thương bất ngờ tới.", "Pha chuyển tiếp an toàn 2.5s (STATE_EMERGENCY_CLEARANCE) hú còi.", "Thử kích hoạt TH3 khi TH2 đang ở giây thứ 5, Barie vẫn mở chờ học sinh lên lề."),
        ("F6", "Giám khảo nghi ngờ người lớn làm hộ sản phẩm.", "Sổ tay kỹ thuật có ảnh học sinh tự tay làm + 3 em trả lời phản biện.", "Hỏi trực tiếp học sinh về các bước thực hiện và xử lý lỗi kỹ thuật.")
    ]
    for r_idx, r_item in enumerate(pm_data):
        row = tbl_pm.add_row()
        set_row_cant_split(row)
        for c_idx, val in enumerate(r_item):
            c = row.cells[c_idx]
            c.width = pm_widths[c_idx]
            set_cell_margins(c, top=80, bottom=80, left=80, right=80)
            set_cell_no_shading(c)
            set_cell_valign(c, "center")
            p = c.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx == 0 else WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(val)
            r.font.name = 'Times New Roman'; r.font.size = Pt(10.5); r.font.color.rgb = COLOR_BLACK
            if c_idx == 0:
                r.font.bold = True

    add_heading_2(doc, "8.2. Kết luận và Ký duyệt")
    add_body_p(doc, "Hồ sơ tổng hợp toàn diện đã tích hợp trọn vẹn toàn bộ các nghiên cứu, tính toán khoa học, dự toán kinh phí, quy trình 6 giai đoạn và kịch bản bảo vệ trước Hội đồng Giám khảo cuộc thi HNUE Olympic STEM 2026. Đội tuyển STEM Trường Liên cấp Marie Curie Thái Bình sẵn sàng 100% tham gia tranh tài với tinh thần sáng tạo, tự tin và quyết tâm giành thành tích cao nhất.")

    p_sign_note = doc.add_paragraph()
    p_sign_note.paragraph_format.space_before = Pt(14)
    p_sign_note.paragraph_format.space_after = Pt(6)
    
    tbl_sign = doc.add_table(rows=2, cols=3)
    tbl_sign.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_no_borders(tbl_sign)
    
    sign_widths = [Cm(5.0), Cm(5.5), Cm(5.5)]
    sign_titles = [
        ("BAN GIÁM HIỆU\nPHÊ DUYỆT", "(Ký, đóng dấu)"),
        ("CÁN BỘ HƯỚNG DẪN\nKỸ THUẬT", "Thầy Lê Ngọc Anh"),
        ("ĐỘI TRƯỞNG\nĐỘI TUYỂN STEM", "Em Phạm Hữu Đạt (4A1)")
    ]
    for i, (t_top, t_bot) in enumerate(sign_titles):
        c_top = tbl_sign.cell(0, i)
        c_top.width = sign_widths[i]
        set_cell_no_shading(c_top)
        p = c_top.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(t_top)
        r.font.name = 'Times New Roman'; r.font.size = Pt(11); r.font.bold = True; r.font.color.rgb = COLOR_BLACK
        
        c_bot = tbl_sign.cell(1, i)
        c_bot.width = sign_widths[i]
        set_cell_no_shading(c_bot)
        p_b = c_bot.paragraphs[0]
        p_b.paragraph_format.space_before = Pt(45)
        p_b.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_b = p_b.add_run(t_bot)
        r_b.font.name = 'Times New Roman'; r_b.font.size = Pt(11); r_b.font.italic = (i == 0); r_b.font.bold = (i > 0); r_b.font.color.rgb = COLOR_BLACK
        
    return doc

if __name__ == "__main__":
    doc = build_master_unified_document()
    
    out_dir_1 = r"C:\Users\ADMIN\.gemini\antigravity\worktrees\HNUE_olympic_stem\hnue_olympic_stem\MCA\HNUE_olympic_stem\1.Data"
    out_dir_2 = r"E:\Antigravity\MCA\HNUE_olympic_stem\1.Data"
    
    fname = "HO_SO_TOAN_DIEN_DU_AN_STEM_OLYMPIC_2026.docx"
    
    docx_path_1 = os.path.join(out_dir_1, fname)
    doc.save(docx_path_1)
    print(f"[OK] Saved Monochrome Master DOCX 1: {docx_path_1}")
    
    if os.path.exists(out_dir_2):
        docx_path_2 = os.path.join(out_dir_2, fname)
        doc.save(docx_path_2)
        print(f"[OK] Saved Monochrome Master DOCX 2: {docx_path_2}")
