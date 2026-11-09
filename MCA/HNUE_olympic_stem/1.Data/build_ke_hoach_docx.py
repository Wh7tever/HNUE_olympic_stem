# -*- coding: utf-8 -*-
"""
Tự động định dạng văn bản: Kế hoạch thi HNUE STEM OLYMPIC
Tuân thủ chuẩn Nghị định 30/2020/NĐ-CP và phong cách văn bản hành chính Marie Curie
Giữ nguyên 100% nội dung nguyên bản từ file gốc
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

def set_cell_margins(cell, top=100, bottom=100, left=140, right=140):
    """Thiết lập padding cho ô bảng tính (đơn vị dxa: 20 dxa = 1 pt)"""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}>'
                      f'<w:top w:w="{top}" w:type="dxa"/>'
                      f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
                      f'<w:left w:w="{left}" w:type="dxa"/>'
                      f'<w:right w:w="{right}" w:type="dxa"/>'
                      f'</w:tcMar>')
    tcPr.append(tcMar)

def set_cell_shading(cell, color_hex="F2F2F2"):
    """Đặt màu nền cho ô"""
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shd)

def set_cell_valign(cell, val="center"):
    """Căn lề dọc cho ô"""
    vAlign = parse_xml(f'<w:vAlign {nsdecls("w")} w:val="{val}"/>')
    cell._tc.get_or_add_tcPr().append(vAlign)

def set_table_borders(table, color="A0A0A0", sz="4"):
    """Thiết lập đường viền mỏng tinh tế cho bảng"""
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
    """Xóa bỏ toàn bộ đường viền bảng (dùng cho bảng tiêu đề và bảng chữ ký)"""
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
    """Ngăn hàng trong bảng bị cắt đôi qua 2 trang"""
    trPr = row._tr.get_or_add_trPr()
    trPr.append(OxmlElement('w:cantSplit'))

def set_row_tbl_header(row):
    """Đặt hàng làm tiêu đề lặp lại khi sang trang mới"""
    trPr = row._tr.get_or_add_trPr()
    trPr.append(OxmlElement('w:tblHeader'))

def set_col_widths(table, col_widths):
    """Cài đặt độ rộng cố định cho từng cột của bảng"""
    for row in table.rows:
        for idx, width in enumerate(col_widths):
            row.cells[idx].width = width

def add_page_number_to_header(header):
    """Thêm số trang tự động vào Header theo chuẩn NĐ 30/2020 (canh giữa lề trên)"""
    p = header.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    run = p.add_run()
    run.font.name = 'Times New Roman'
    run.font.size = Pt(13)
    run.font.color.rgb = RGBColor(0, 0, 0)
    fldChar1 = parse_xml(r'<w:fldChar %s w:fldCharType="begin"/>' % nsdecls('w'))
    instrText = parse_xml(r'<w:instrText %s xml:space="preserve"> PAGE </w:instrText>' % nsdecls('w'))
    fldChar2 = parse_xml(r'<w:fldChar %s w:fldCharType="separate"/>' % nsdecls('w'))
    fldChar3 = parse_xml(r'<w:fldChar %s w:fldCharType="end"/>' % nsdecls('w'))
    run._r.append(fldChar1)
    run._r.append(instrText)
    run._r.append(fldChar2)
    run._r.append(fldChar3)

def create_document():
    doc = docx.Document()
    
    # 1. Khổ giấy & Căn lề chuẩn NĐ 30/2020/NĐ-CP
    section = doc.sections[0]
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
    section.top_margin = Cm(2.0)
    section.bottom_margin = Cm(2.0)
    section.left_margin = Cm(3.0)
    section.right_margin = Cm(2.0)
    section.header_distance = Cm(1.2)
    section.footer_distance = Cm(1.2)
    
    # Đánh số trang từ trang 2 trở đi (không hiển thị số trang thứ nhất)
    section.different_first_page_header_footer = True
    add_page_number_to_header(section.header)
    
    # Thiết lập Normal style mặc định
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(13)
    font.color.rgb = RGBColor(0, 0, 0)
    style.paragraph_format.line_spacing = 1.15
    style.paragraph_format.space_before = Pt(2)
    style.paragraph_format.space_after = Pt(3)
    
    # ==========================================
    # BẢNG TIÊU ĐỀ ĐẦU TRANG (QUỐC HIỆU & CƠ QUAN)
    # Tổng độ rộng: 16.0 cm (Cột trái 6.5 cm, Cột phải 9.5 cm)
    # ==========================================
    t_header = doc.add_table(rows=1, cols=2)
    t_header.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_no_borders(t_header)
    set_col_widths(t_header, [Cm(6.5), Cm(9.5)])
    set_row_cant_split(t_header.rows[0])
    
    # Cột trái: Tên cơ quan ban hành
    c_left = t_header.rows[0].cells[0]
    set_cell_margins(c_left, top=0, bottom=0, left=0, right=20)
    p_cq1 = c_left.paragraphs[0]
    p_cq1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cq1.paragraph_format.space_before = Pt(0)
    p_cq1.paragraph_format.space_after = Pt(0)
    p_cq1.paragraph_format.line_spacing = 1.15
    r = p_cq1.add_run('TRƯỜNG TIỂU HỌC, THCS,')
    r.font.name = 'Times New Roman'
    r.font.size = Pt(11)
    r.font.bold = True
    
    p_cq2 = c_left.add_paragraph()
    p_cq2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cq2.paragraph_format.space_before = Pt(0)
    p_cq2.paragraph_format.space_after = Pt(2)
    p_cq2.paragraph_format.line_spacing = 1.15
    r = p_cq2.add_run('THPT MARIE CURIE THÁI BÌNH')
    r.font.name = 'Times New Roman'
    r.font.size = Pt(11)
    r.font.bold = True
    
    p_cq_line = c_left.add_paragraph()
    p_cq_line.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cq_line.paragraph_format.space_before = Pt(0)
    p_cq_line.paragraph_format.space_after = Pt(0)
    r = p_cq_line.add_run('————————')
    r.font.name = 'Times New Roman'
    r.font.size = Pt(8)
    r.font.bold = True
    
    # Cột phải: Quốc hiệu, Tiêu ngữ & Ngày tháng
    c_right = t_header.rows[0].cells[1]
    set_cell_margins(c_right, top=0, bottom=0, left=20, right=0)
    p_qh = c_right.paragraphs[0]
    p_qh.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_qh.paragraph_format.space_before = Pt(0)
    p_qh.paragraph_format.space_after = Pt(0)
    p_qh.paragraph_format.line_spacing = 1.15
    r = p_qh.add_run('CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM')
    r.font.name = 'Times New Roman'
    r.font.size = Pt(12)
    r.font.bold = True
    
    p_tn = c_right.add_paragraph()
    p_tn.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_tn.paragraph_format.space_before = Pt(0)
    p_tn.paragraph_format.space_after = Pt(2)
    p_tn.paragraph_format.line_spacing = 1.15
    r = p_tn.add_run('Độc lập – Tự do – Hạnh phúc')
    r.font.name = 'Times New Roman'
    r.font.size = Pt(13)
    r.font.bold = True
    
    p_tn_line = c_right.add_paragraph()
    p_tn_line.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_tn_line.paragraph_format.space_before = Pt(0)
    p_tn_line.paragraph_format.space_after = Pt(3)
    r = p_tn_line.add_run('————————————')
    r.font.name = 'Times New Roman'
    r.font.size = Pt(9)
    r.font.bold = True
    
    p_date = c_right.add_paragraph()
    p_date.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_date.paragraph_format.space_before = Pt(2)
    p_date.paragraph_format.space_after = Pt(0)
    p_date.paragraph_format.line_spacing = 1.15
    r = p_date.add_run('Hưng Yên, ngày 01 tháng 11 năm 2026')
    r.font.name = 'Times New Roman'
    r.font.size = Pt(13)
    r.font.italic = True
    
    # ==========================================
    # TÊN LOẠI VĂN BẢN VÀ TRÍCH YẾU NỘI DUNG
    # ==========================================
    p_title1 = doc.add_paragraph()
    p_title1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title1.paragraph_format.space_before = Pt(12)
    p_title1.paragraph_format.space_after = Pt(2)
    p_title1.paragraph_format.line_spacing = 1.15
    r = p_title1.add_run('KẾ HOẠCH CHI TIẾT')
    r.font.name = 'Times New Roman'
    r.font.size = Pt(14)
    r.font.bold = True
    
    p_title2 = doc.add_paragraph()
    p_title2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title2.paragraph_format.space_before = Pt(0)
    p_title2.paragraph_format.space_after = Pt(2)
    p_title2.paragraph_format.line_spacing = 1.15
    r = p_title2.add_run('Tổ chức tham gia thi HNUE STEM OLYMPIC')
    r.font.name = 'Times New Roman'
    r.font.size = Pt(13)
    r.font.bold = True
    
    p_title3 = doc.add_paragraph()
    p_title3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title3.paragraph_format.space_before = Pt(0)
    p_title3.paragraph_format.space_after = Pt(2)
    p_title3.paragraph_format.line_spacing = 1.15
    r = p_title3.add_run('Năm học 2026-2027')
    r.font.name = 'Times New Roman'
    r.font.size = Pt(13)
    r.font.bold = True
    
    p_title4 = doc.add_paragraph()
    p_title4.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title4.paragraph_format.space_before = Pt(0)
    p_title4.paragraph_format.space_after = Pt(10)
    p_title4.paragraph_format.line_spacing = 1.15
    r = p_title4.add_run('(Bảng Tiểu học)')
    r.font.name = 'Times New Roman'
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.italic = True
    
    # ==========================================
    # CĂN CỨ VÀ MỞ ĐẦU
    # ==========================================
    p_intro = doc.add_paragraph()
    p_intro.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_intro.paragraph_format.first_line_indent = Cm(1.0)
    p_intro.paragraph_format.space_before = Pt(4)
    p_intro.paragraph_format.space_after = Pt(6)
    p_intro.paragraph_format.line_spacing = 1.2
    r = p_intro.add_run('Căn cứ vào kế hoạch cuộc thi và tình hình thực tế, trường TH, THCS, THPT Marie Curie xây dựng kế hoạch tham gia vòng Bán kết và Chung kết cuộc thi HNUE STEM OLYMPIC (do Trường Đại học Sư phạm Hà Nội tổ chức) như sau:')
    r.font.name = 'Times New Roman'
    r.font.size = Pt(13)
    
    # ==========================================
    # PHẦN I. THỜI GIAN, ĐỊA ĐIỂM
    # ==========================================
    p_h1 = doc.add_paragraph()
    p_h1.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_h1.paragraph_format.space_before = Pt(8)
    p_h1.paragraph_format.space_after = Pt(3)
    p_h1.paragraph_format.line_spacing = 1.15
    p_h1.paragraph_format.keep_with_next = True
    r = p_h1.add_run('I. Thời gian, địa điểm')
    r.font.name = 'Times New Roman'
    r.font.size = Pt(13)
    r.font.bold = True
    
    p_h1_sub = doc.add_paragraph()
    p_h1_sub.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_h1_sub.paragraph_format.space_before = Pt(1)
    p_h1_sub.paragraph_format.space_after = Pt(4)
    p_h1_sub.paragraph_format.line_spacing = 1.15
    p_h1_sub.paragraph_format.keep_with_next = True
    r = p_h1_sub.add_run('- Thời gian thi dự kiến:')
    r.font.name = 'Times New Roman'
    r.font.size = Pt(13)
    r.font.italic = True
    
    # BẢNG 1: LỊCH TRÌNH
    t_sched = doc.add_table(rows=4, cols=4)
    t_sched.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_sched, color="808080", sz="4")
    col_w_sched = [Cm(1.2), Cm(3.8), Cm(3.2), Cm(7.8)]
    set_col_widths(t_sched, col_w_sched)
    
    # Header Bảng 1
    sched_headers = ['STT', 'Thời gian', 'Nội dung', 'Địa điểm']
    for idx, h in enumerate(sched_headers):
        cell = t_sched.rows[0].cells[idx]
        set_cell_margins(cell, top=100, bottom=100, left=120, right=120)
        set_cell_shading(cell, "F2F2F2")
        set_cell_valign(cell, "center")
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.15
        r = p.add_run(h)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(12)
        r.font.bold = True
    set_row_cant_split(t_sched.rows[0])
    set_row_tbl_header(t_sched.rows[0])
    
    # Dữ liệu Bảng 1
    sched_data = [
        ('1', '07:00 – 17:00\nngày 05/12/2026\n(Thứ Bảy)', 'Thi vòng\nBán kết', 'Nhà thi đấu và Hội trường 11/10\nTrường ĐHSP Hà Nội'),
        ('2', '07:00 – 11:30\nngày 06/12/2026\n(Chủ nhật)', 'Thi vòng Chung kết\n(nếu có)', 'Nhà thi đấu và Hội trường 11/10\nTrường ĐHSP Hà Nội'),
        ('3', '11:30 – 12:30\nngày 06/12/2026\n(Chủ nhật)', 'Trao giải', 'Hội trường 11/10\nTrường ĐHSP Hà Nội')
    ]
    
    for row_idx, data in enumerate(sched_data, start=1):
        row = t_sched.rows[row_idx]
        set_row_cant_split(row)
        for col_idx, text in enumerate(data):
            cell = row.cells[col_idx]
            set_cell_margins(cell, top=80, bottom=80, left=120, right=120)
            set_cell_valign(cell, "center")
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.15
            
            if col_idx in (0, 1, 2):
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                
            r = p.add_run(text)
            r.font.name = 'Times New Roman'
            r.font.size = Pt(12)
            if col_idx == 0:
                r.font.bold = True
    
    p_loc = doc.add_paragraph()
    p_loc.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_loc.paragraph_format.space_before = Pt(6)
    p_loc.paragraph_format.space_after = Pt(6)
    p_loc.paragraph_format.line_spacing = 1.15
    r = p_loc.add_run('- Địa điểm thi: ')
    r.font.name = 'Times New Roman'
    r.font.size = Pt(13)
    r.font.bold = True
    r2 = p_loc.add_run('Trường ĐHSP Hà Nội – số 136 Xuân Thủy, phường Cầu Giấy, Hà Nội')
    r2.font.name = 'Times New Roman'
    r2.font.size = Pt(13)
    
    # ==========================================
    # PHẦN II. ĐỐI TƯỢNG THAM GIA
    # ==========================================
    p_h2 = doc.add_paragraph()
    p_h2.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_h2.paragraph_format.space_before = Pt(8)
    p_h2.paragraph_format.space_after = Pt(3)
    p_h2.paragraph_format.line_spacing = 1.15
    p_h2.paragraph_format.keep_with_next = True
    r = p_h2.add_run('II. Đối tượng tham gia:')
    r.font.name = 'Times New Roman'
    r.font.size = Pt(13)
    r.font.bold = True
    
    # Cán bộ giáo viên
    p_cb = doc.add_paragraph()
    p_cb.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_cb.paragraph_format.space_before = Pt(2)
    p_cb.paragraph_format.space_after = Pt(2)
    p_cb.paragraph_format.line_spacing = 1.15
    p_cb.paragraph_format.keep_with_next = True
    r = p_cb.add_run('- Cán bộ, giáo viên:')
    r.font.name = 'Times New Roman'
    r.font.size = Pt(13)
    r.font.bold = True
    
    cb_list = [
        'Cô Ngọc, cô Phương Anh phụ trách đoàn',
        'Thầy Ngọc Anh hỗ trợ kỹ thuật'
    ]
    for item in cb_list:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.left_indent = Cm(0.8)
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.15
        r_bullet = p.add_run('● ')
        r_bullet.font.name = 'Times New Roman'
        r_bullet.font.size = Pt(10)
        r = p.add_run(item)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(13)
        
    # Học sinh
    p_hs = doc.add_paragraph()
    p_hs.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_hs.paragraph_format.space_before = Pt(3)
    p_hs.paragraph_format.space_after = Pt(2)
    p_hs.paragraph_format.line_spacing = 1.15
    p_hs.paragraph_format.keep_with_next = True
    r = p_hs.add_run('- Học sinh: đội thi bao gồm 3 học sinh')
    r.font.name = 'Times New Roman'
    r.font.size = Pt(13)
    r.font.bold = True
    
    hs_list = [
        'Phạm Hữu Đạt - Lớp 4A1',
        'Vũ Minh Quang - Lớp 4A1',
        'Vũ Ngọc An Đông - Lớp 5A1'
    ]
    for item in hs_list:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.left_indent = Cm(0.8)
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.15
        r_bullet = p.add_run('● ')
        r_bullet.font.name = 'Times New Roman'
        r_bullet.font.size = Pt(10)
        r = p.add_run(item)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(13)
        
    # ==========================================
    # PHẦN III. THÔNG TIN CHI TIẾT
    # ==========================================
    p_h3 = doc.add_paragraph()
    p_h3.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_h3.paragraph_format.space_before = Pt(8)
    p_h3.paragraph_format.space_after = Pt(3)
    p_h3.paragraph_format.line_spacing = 1.15
    p_h3.paragraph_format.keep_with_next = True
    r = p_h3.add_run('III. Thông tin chi tiết')
    r.font.name = 'Times New Roman'
    r.font.size = Pt(13)
    r.font.bold = True
    
    # 1. Nhiệm vụ của đội thi
    p_sec1 = doc.add_paragraph()
    p_sec1.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_sec1.paragraph_format.space_before = Pt(4)
    p_sec1.paragraph_format.space_after = Pt(2)
    p_sec1.paragraph_format.line_spacing = 1.15
    p_sec1.paragraph_format.keep_with_next = True
    r = p_sec1.add_run('1. Nhiệm vụ của đội thi')
    r.font.name = 'Times New Roman'
    r.font.size = Pt(13)
    r.font.bold = True
    
    p_pres = doc.add_paragraph()
    p_pres.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_pres.paragraph_format.first_line_indent = Cm(1.0)
    p_pres.paragraph_format.space_before = Pt(2)
    p_pres.paragraph_format.space_after = Pt(2)
    p_pres.paragraph_format.line_spacing = 1.15
    r = p_pres.add_run('Trong 5 phút thuyết trình, đội thi cần trình bày rõ:')
    r.font.name = 'Times New Roman'
    r.font.size = Pt(13)
    
    pres_bullets = [
        'Vấn đề các em giải quyết là gì?',
        'Ý tưởng STEM và công nghệ được dùng như thế nào?',
        'Bản thiết kế – mô hình – sản phẩm thực tế',
        'Điểm mới, điểm sáng tạo, điểm khác biệt',
        'Ý nghĩa của sản phẩm đối với cộng đồng, môi trường và cuộc sống tương lai'
    ]
    for b in pres_bullets:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.left_indent = Cm(0.8)
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.15
        r_bullet = p.add_run('● ')
        r_bullet.font.name = 'Times New Roman'
        r_bullet.font.size = Pt(10)
        r = p.add_run(b)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(13)
        
    p_qa = doc.add_paragraph()
    p_qa.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_qa.paragraph_format.first_line_indent = Cm(1.0)
    p_qa.paragraph_format.space_before = Pt(2)
    p_qa.paragraph_format.space_after = Pt(4)
    p_qa.paragraph_format.line_spacing = 1.15
    r = p_qa.add_run('Sau đó 5 phút phản biện, BGK sẽ hỏi và đội thi trả lời.')
    r.font.name = 'Times New Roman'
    r.font.size = Pt(13)
    
    # 2. Yêu cầu sản phẩm
    p_sec2 = doc.add_paragraph()
    p_sec2.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_sec2.paragraph_format.space_before = Pt(6)
    p_sec2.paragraph_format.space_after = Pt(3)
    p_sec2.paragraph_format.line_spacing = 1.15
    p_sec2.paragraph_format.keep_with_next = True
    r = p_sec2.add_run('2. Yêu cầu sản phẩm')
    r.font.name = 'Times New Roman'
    r.font.size = Pt(13)
    r.font.bold = True
    
    p_sp = doc.add_paragraph()
    p_sp.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_sp.paragraph_format.left_indent = Cm(0.8)
    p_sp.paragraph_format.space_before = Pt(2)
    p_sp.paragraph_format.space_after = Pt(2)
    p_sp.paragraph_format.line_spacing = 1.15
    r_bullet = p_sp.add_run('● ')
    r_bullet.font.name = 'Times New Roman'
    r_bullet.font.size = Pt(10)
    r = p_sp.add_run('Sản phẩm hoặc mô hình hoàn chỉnh')
    r.font.name = 'Times New Roman'
    r.font.size = Pt(13)
    r.font.bold = True
    
    p_nvl = doc.add_paragraph()
    p_nvl.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_nvl.paragraph_format.first_line_indent = Cm(1.0)
    p_nvl.paragraph_format.space_before = Pt(1)
    p_nvl.paragraph_format.space_after = Pt(2)
    p_nvl.paragraph_format.line_spacing = 1.15
    r = p_nvl.add_run('Nguyên vật liệu không vượt quá 1.000.000 VNĐ/1 đội.')
    r.font.name = 'Times New Roman'
    r.font.size = Pt(13)
    
    p_bgk = doc.add_paragraph()
    p_bgk.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_bgk.paragraph_format.first_line_indent = Cm(1.0)
    p_bgk.paragraph_format.space_before = Pt(1)
    p_bgk.paragraph_format.space_after = Pt(3)
    p_bgk.paragraph_format.line_spacing = 1.15
    r = p_bgk.add_run('BGK có thể yêu cầu đội giải trình bảng kê chi phí trong phần phản biện. Ưu tiên vật liệu tái chế, tiết kiệm năng lượng, thân thiện môi trường.')
    r.font.name = 'Times New Roman'
    r.font.size = Pt(13)
    
    doc_bullets = [
        'Sổ tay kỹ thuật',
        'Bản thiết kế/bản vẽ',
        'Poster theo kích thước quy định của BGK.'
    ]
    for b in doc_bullets:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.left_indent = Cm(0.8)
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.15
        r_bullet = p.add_run('● ')
        r_bullet.font.name = 'Times New Roman'
        r_bullet.font.size = Pt(10)
        r = p.add_run(b)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(13)
        
    p_booth = doc.add_paragraph()
    p_booth.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_booth.paragraph_format.first_line_indent = Cm(1.0)
    p_booth.paragraph_format.space_before = Pt(3)
    p_booth.paragraph_format.space_after = Pt(5)
    p_booth.paragraph_format.line_spacing = 1.15
    r_lead = p_booth.add_run('Không gian trưng bày của mỗi đội: ')
    r_lead.font.name = 'Times New Roman'
    r_lead.font.size = Pt(13)
    r_lead.font.bold = True
    r_body = p_booth.add_run('Mỗi đội được BTC bố trí một không gian trưng bày có kích thước 2m x 2m. Bên trong có sẵn 1 cái bàn 0,6m x 1,2 m; 3 ghế cho 3 thành viên và 1 khung treo poster')
    r_body.font.name = 'Times New Roman'
    r_body.font.size = Pt(13)
    
    # 3. Tiêu chí chấm điểm
    p_sec3 = doc.add_paragraph()
    p_sec3.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_sec3.paragraph_format.space_before = Pt(6)
    p_sec3.paragraph_format.space_after = Pt(3)
    p_sec3.paragraph_format.line_spacing = 1.15
    p_sec3.paragraph_format.keep_with_next = True
    r = p_sec3.add_run('3. Tiêu chí chấm điểm')
    r.font.name = 'Times New Roman'
    r.font.size = Pt(13)
    r.font.bold = True
    
    criteria = [
        ('Tính khoa học (20 điểm): ', 'Mức độ chính xác và hợp lí của việc vận dụng các kiến thức nền tảng được áp dụng trong việc thiết kế, lí giải, bản thiết kế và thử nghiệm, chế tạo sản phẩm.'),
        ('Tính sáng tạo (20 điểm): ', 'Sự mới mẻ, độc đáo trong ý tưởng, cách giải quyết vấn đề và cách ứng dụng công nghệ của sản phẩm.'),
        ('Tính ứng dụng, khả thi & thân thiện môi trường (20 điểm): ', 'Khả năng áp dụng của sản phẩm vào thực tế (tính khả thi về kĩ thuật, chi phí, an toàn) và tác động đối với cộng đồng, môi trường. Điểm trừ do vượt giới hạn chi phí (mục 2.5) được tính vào tiêu chí này, tối đa 3 điểm.'),
        ('Tính tích hợp liên môn STEM (20 điểm): ', 'Mức độ kết hợp hài hòa và hiệu quả kiến thức, kỹ năng, tiến trình tìm tòi khám phá, thiết kế kĩ thuật từ các lĩnh vực S (Khoa học), T (Công nghệ), E (Kĩ thuật) và M (Toán học), thể hiện qua sản phẩm và sổ tay kĩ thuật.'),
        ('Kĩ năng thuyết trình và phản biện (20 điểm): ', 'Khả năng trình bày trên bản mô tả, bản thiết kế, và trình bày trực tiếp, bảo vệ ý tưởng, trả lời câu hỏi về sản phẩm của nhóm; mỗi thành viên đều cần trả lời được câu hỏi.')
    ]
    
    for title, desc in criteria:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.left_indent = Cm(0.8)
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.15
        r_bullet = p.add_run('● ')
        r_bullet.font.name = 'Times New Roman'
        r_bullet.font.size = Pt(10)
        r_t = p.add_run(title)
        r_t.font.name = 'Times New Roman'
        r_t.font.size = Pt(13)
        r_t.font.bold = True
        r_d = p.add_run(desc)
        r_d.font.name = 'Times New Roman'
        r_d.font.size = Pt(13)
        
    # ==========================================
    # PHẦN IV. KINH PHÍ
    # ==========================================
    p_h4 = doc.add_paragraph()
    p_h4.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_h4.paragraph_format.space_before = Pt(8)
    p_h4.paragraph_format.space_after = Pt(4)
    p_h4.paragraph_format.line_spacing = 1.15
    p_h4.paragraph_format.keep_with_next = True
    r = p_h4.add_run('IV. Kinh phí: Gia đình học sinh tự túc và nhà trường hỗ trợ')
    r.font.name = 'Times New Roman'
    r.font.size = Pt(13)
    r.font.bold = True
    
    # BẢNG 2: KINH PHÍ
    t_budget = doc.add_table(rows=5, cols=3)
    t_budget.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_budget, color="808080", sz="4")
    col_w_budget = [Cm(5.0), Cm(3.2), Cm(7.8)]
    set_col_widths(t_budget, col_w_budget)
    
    # Header Bảng 2
    budget_headers = ['Hạng mục', 'Chi phí/người', 'Ghi chú']
    for idx, h in enumerate(budget_headers):
        cell = t_budget.rows[0].cells[idx]
        set_cell_margins(cell, top=100, bottom=100, left=120, right=120)
        set_cell_shading(cell, "F2F2F2")
        set_cell_valign(cell, "center")
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.15
        r = p.add_run(h)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(12)
        r.font.bold = True
    set_row_cant_split(t_budget.rows[0])
    set_row_tbl_header(t_budget.rows[0])
    
    # Dữ liệu Bảng 2
    budget_data = [
        ('Xe di chuyển (2 chiều)', '350.000 vnđ', '175.000 vnđ/1 chiều'),
        ('Các bữa ăn\n+ Ăn sáng\n+ Ăn trưa\n+ Bữa phụ chiều\n+ Hoa quả\n+ Nước uống', '200.000 vnđ', 'Gia đình chi trả các con ăn ngày Bán kết. Nhà trường hỗ trợ ăn ngày Chung kết.'),
        ('Lệ phí thi', '834.000 vnđ', '2.500.000 vnđ/1 đội'),
        ('Thiết bị, nguyên vật liệu phục vụ phần thi', '334.000 vnđ', 'Nhà trường hỗ trợ tối đa 1.000.000 vnđ/1 đội')
    ]
    
    for row_idx, data in enumerate(budget_data, start=1):
        row = t_budget.rows[row_idx]
        set_row_cant_split(row)
        for col_idx, text in enumerate(data):
            cell = row.cells[col_idx]
            set_cell_margins(cell, top=80, bottom=80, left=120, right=120)
            set_cell_valign(cell, "center")
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.15
            
            if col_idx == 0:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            elif col_idx == 1:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                
            r = p.add_run(text)
            r.font.name = 'Times New Roman'
            r.font.size = Pt(12)
            if col_idx == 0 and not '\n' in text:
                r.font.bold = True
            elif col_idx == 1:
                r.font.bold = True
                
    # Đoạn kết luận dưới Bảng 2
    p_tot = doc.add_paragraph()
    p_tot.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_tot.paragraph_format.space_before = Pt(6)
    p_tot.paragraph_format.space_after = Pt(2)
    p_tot.paragraph_format.line_spacing = 1.15
    r_lbl = p_tot.add_run('Tổng: ')
    r_lbl.font.name = 'Times New Roman'
    r_lbl.font.size = Pt(13)
    r_lbl.font.bold = True
    r_val = p_tot.add_run('1.384.000 vnđ/1 thí sinh, 550.000 vnđ/1 người nhà.')
    r_val.font.name = 'Times New Roman'
    r_val.font.size = Pt(13)
    
    p_sup = doc.add_paragraph()
    p_sup.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_sup.paragraph_format.space_before = Pt(2)
    p_sup.paragraph_format.space_after = Pt(4)
    p_sup.paragraph_format.line_spacing = 1.15
    r = p_sup.add_run('Nhà trường hỗ trợ nguyên vật liệu tối đa 1.000.000 vnđ/1 đội và tiền ăn trưa ngày Chung kết.')
    r.font.name = 'Times New Roman'
    r.font.size = Pt(13)
    
    p_concl = doc.add_paragraph()
    p_concl.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_concl.paragraph_format.first_line_indent = Cm(1.0)
    p_concl.paragraph_format.space_before = Pt(4)
    p_concl.paragraph_format.space_after = Pt(12)
    p_concl.paragraph_format.line_spacing = 1.2
    p_concl.paragraph_format.keep_with_next = True
    r = p_concl.add_run('Trên đây là kế hoạch tổ chức tham gia cuộc thi HNUE STEM OLYMPIC năm học 2025 – 2026 của trường tiểu học, THCS, THPT Marie Curie Thái Bình ./.')
    r.font.name = 'Times New Roman'
    r.font.size = Pt(13)
    
    # ==========================================
    # BẢNG NƠI NHẬN & CHỮ KÝ
    # ==========================================
    t_sign = doc.add_table(rows=1, cols=2)
    t_sign.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_no_borders(t_sign)
    set_col_widths(t_sign, [Cm(7.5), Cm(8.5)])
    set_row_cant_split(t_sign.rows[0])
    
    # Cột trái: Nơi nhận
    c_rec = t_sign.rows[0].cells[0]
    set_cell_margins(c_rec, top=0, bottom=0, left=0, right=50)
    p_nn = c_rec.paragraphs[0]
    p_nn.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_nn.paragraph_format.space_before = Pt(0)
    p_nn.paragraph_format.space_after = Pt(2)
    p_nn.paragraph_format.line_spacing = 1.1
    r = p_nn.add_run('Nơi nhận:')
    r.font.name = 'Times New Roman'
    r.font.size = Pt(12)
    r.font.bold = True
    r.font.italic = True
    
    rec_items = [
        '- BLĐ nhà trường;',
        '- Các tổ CM;',
        '- TPT Đội;',
        '- Lưu: VT.'
    ]
    for item in rec_items:
        p = c_rec.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(1)
        p.paragraph_format.line_spacing = 1.1
        r = p.add_run(item)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(11)
        
    # Cột phải: Chức vụ & Người ký
    c_sig = t_sign.rows[0].cells[1]
    set_cell_margins(c_sig, top=0, bottom=0, left=50, right=0)
    p_role = c_sig.paragraphs[0]
    p_role.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_role.paragraph_format.space_before = Pt(0)
    p_role.paragraph_format.space_after = Pt(45)  # Khoảng trống để ký tên
    p_role.paragraph_format.line_spacing = 1.15
    r = p_role.add_run('CHỦ TỊCH')
    r.font.name = 'Times New Roman'
    r.font.size = Pt(13)
    r.font.bold = True
    
    p_name = c_sig.add_paragraph()
    p_name.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_name.paragraph_format.space_before = Pt(0)
    p_name.paragraph_format.space_after = Pt(0)
    p_name.paragraph_format.line_spacing = 1.15
    r = p_name.add_run('Trần Thị Hồng')
    r.font.name = 'Times New Roman'
    r.font.size = Pt(13)
    r.font.bold = True

    return doc

if __name__ == '__main__':
    doc = create_document()
    out_dir = r'E:\Antigravity\MCA\HNUE_olympic_stem\1.Data'
    os.makedirs(out_dir, exist_ok=True)
    out_docx = os.path.join(out_dir, 'Ke_hoach_thi_HNUE_STEM_OLYMPIC_chuan_the_thuc.docx')
    doc.save(out_docx)
    print(f'Saved DOCX successfully: {out_docx}')
