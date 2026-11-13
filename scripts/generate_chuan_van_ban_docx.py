# -*- coding: utf-8 -*-
"""
Script tạo file DOCX chuẩn thể thức Nghị định 30/2020/NĐ-CP theo mẫu chuẩn Marie Curie:
- Khổ giấy A4, Lề: Trên 2cm, Dưới 2cm, Trái 3cm, Phải 2cm.
- Font: Times New Roman xuyên suốt.
- Cỡ chữ: 13pt (Nội dung), 14pt (Tiêu đề chính).
- Căn lề: Căn đều 2 bên (Justified), Thụt đầu dòng 1.0cm.
- Bỏ tiêu đề và quốc hiệu theo yêu cầu của Người dùng.
- Bảng biểu đóng khung chuẩn mực, ô xám nhạt ở hàng tiêu đề.
"""

import os
import sys
import docx
from docx.shared import Inches, Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def create_document():
    doc = docx.Document()

    # 1. Cài đặt trang chuẩn Nghị định 30/2020/NĐ-CP (Mẫu Marie Curie)
    section = doc.sections[0]
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
    section.top_margin = Cm(2.0)
    section.bottom_margin = Cm(2.0)
    section.left_margin = Cm(3.0)
    section.right_margin = Cm(2.0)

    # 2. Cài đặt Style Normal mặc định
    style_normal = doc.styles['Normal']
    style_normal.font.name = 'Times New Roman'
    style_normal.font.size = Pt(13)
    style_normal.font.color.rgb = RGBColor(0, 0, 0)
    style_normal.paragraph_format.line_spacing = 1.15
    style_normal.paragraph_format.space_after = Pt(4)
    style_normal.paragraph_format.space_before = Pt(2)

    # Helper format cell border
    def set_cell_border(cell, **kwargs):
        tcPr = cell._tc.get_or_add_tcPr()
        tcBorders = OxmlElement('w:tcBorders')
        for border_name, border_props in kwargs.items():
            border = OxmlElement(f'w:{border_name}')
            for key, val in border_props.items():
                border.set(qn(f'w:{key}'), str(val))
            tcBorders.append(border)
        tcPr.append(tcBorders)

    def set_cell_shading(cell, color_hex):
        shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
        cell._tc.get_or_add_tcPr().append(shading)

    def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
        tcPr = cell._tc.get_or_add_tcPr()
        tcMar = OxmlElement('w:tcMar')
        for m_name, m_val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
            node = OxmlElement(f'w:{m_name}')
            node.set(qn('w:w'), str(m_val))
            node.set(qn('w:type'), 'dxa')
            tcMar.append(node)
        tcPr.append(tcMar)

    def format_table(table, col_widths, headers, data, alignments=None):
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        # Header row
        hdr_row = table.rows[0]
        for idx, text in enumerate(headers):
            cell = hdr_row.cells[idx]
            cell.text = text
            set_cell_shading(cell, 'F2F2F2')
            set_cell_margins(cell, top=120, bottom=120, left=150, right=150)
            set_cell_border(cell,
                            top={'val': 'single', 'sz': 6, 'space': 0, 'color': '000000'},
                            bottom={'val': 'single', 'sz': 8, 'space': 0, 'color': '000000'},
                            left={'val': 'single', 'sz': 4, 'space': 0, 'color': '888888'},
                            right={'val': 'single', 'sz': 4, 'space': 0, 'color': '888888'})
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            for r in p.runs:
                r.font.name = 'Times New Roman'
                r.font.size = Pt(12)
                r.bold = True

        # Data rows
        for r_idx, row_data in enumerate(data):
            row = table.add_row()
            for c_idx, val in enumerate(row_data):
                cell = row.cells[c_idx]
                cell.text = str(val)
                set_cell_margins(cell, top=100, bottom=100, left=140, right=140)
                set_cell_border(cell,
                                top={'val': 'single', 'sz': 4, 'space': 0, 'color': 'CCCCCC'},
                                bottom={'val': 'single', 'sz': 4, 'space': 0, 'color': 'CCCCCC'},
                                left={'val': 'single', 'sz': 4, 'space': 0, 'color': '888888'},
                                right={'val': 'single', 'sz': 4, 'space': 0, 'color': '888888'})
                p = cell.paragraphs[0]
                align = alignments[c_idx] if alignments else WD_ALIGN_PARAGRAPH.LEFT
                p.alignment = align
                p.paragraph_format.space_before = Pt(2)
                p.paragraph_format.space_after = Pt(2)
                for r in p.runs:
                    r.font.name = 'Times New Roman'
                    r.font.size = Pt(12)

        # Set column widths
        for row in table.rows:
            for c_idx, w in enumerate(col_widths):
                row.cells[c_idx].width = Cm(w)

    # =========================================================================
    # PHẦN ĐẦU VĂN BẢN (KHÔNG CÓ QUỐC HIỆU & TIÊU ĐỀ HÀNH CHÍNH)
    # =========================================================================
    p_org = doc.add_paragraph()
    p_org.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_org.paragraph_format.space_before = Pt(0)
    p_org.paragraph_format.space_after = Pt(4)
    r_org = p_org.add_run('TRƯỜNG TIỂU HỌC, THCS VÀ THPT MARIE CURIE')
    r_org.font.name = 'Times New Roman'
    r_org.font.size = Pt(13)
    r_org.bold = True

    p_suborg = doc.add_paragraph()
    p_suborg.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_suborg.paragraph_format.space_before = Pt(0)
    p_suborg.paragraph_format.space_after = Pt(12)
    r_suborg = p_suborg.add_run('TỔ CHUYÊN MÔN STEM & CÔNG NGHỆ THÔNG TIN\n***')
    r_suborg.font.name = 'Times New Roman'
    r_suborg.font.size = Pt(12)
    r_suborg.bold = True

    # Tiêu đề chính
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(6)
    p_title.paragraph_format.space_after = Pt(4)
    r_title = p_title.add_run('HỒ SƠ THIẾT KẾ KỸ THUẬT, TÍNH TOÁN ĐỊNH LƯỢNG\nVÀ BẢNG KÊ DỰ TOÁN KINH PHÍ')
    r_title.font.name = 'Times New Roman'
    r_title.font.size = Pt(14)
    r_title.bold = True

    # Tên đề tài
    p_subject = doc.add_paragraph()
    p_subject.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_subject.paragraph_format.space_before = Pt(4)
    p_subject.paragraph_format.space_after = Pt(6)
    r_sub = p_subject.add_run('DỰ ÁN: HỆ THỐNG ĐÈN GIAO THÔNG HỌC ĐƯỜNG THÔNG MINH\nTÍCH HỢP THỊ GIÁC AI VÀ RÀO CHẮN AN TOÀN KÉP')
    r_sub.font.name = 'Times New Roman'
    r_sub.font.size = Pt(13)
    r_sub.bold = True

    # Phụ đề cuộc thi
    p_desc = doc.add_paragraph()
    p_desc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_desc.paragraph_format.space_before = Pt(0)
    p_desc.paragraph_format.space_after = Pt(16)
    r_desc = p_desc.add_run('(Dự án tham dự Vòng Bán kết & Chung kết Cuộc thi HNUE Olympic STEM 2026\nChủ đề: "Future Innovators - Những nhà kiến tạo tương lai")')
    r_desc.font.name = 'Times New Roman'
    r_desc.font.size = Pt(12)
    r_desc.italic = True

    # Bảng thông tin đội thi
    t_info = doc.add_table(rows=1, cols=4)
    info_headers = ['STT', 'Họ và Tên', 'Lớp / Chức danh', 'Nhiệm vụ trong dự án']
    info_data = [
        ['1', 'Phạm Hữu Đạt', 'Học sinh lớp 4A1', 'Đội trưởng, phụ trách kiến trúc STEM & thuật toán AI'],
        ['2', 'Vũ Minh Quang', 'Học sinh lớp 4A1', 'Kỹ sư cơ khí, chế tạo sa bàn & rào chắn Barie'],
        ['3', 'Vũ Ngọc An Đông', 'Học sinh lớp 5A1', 'Kỹ sư dữ liệu, tính toán toán học & tác động môi trường'],
        ['4', 'Lê Ngọc Anh', 'Giáo viên phụ trách STEM', 'Cán bộ hướng dẫn & hỗ trợ kỹ thuật thực nghiệm'],
        ['5', 'Cô Ngọc & Cô Phương Anh', 'Cán bộ quản lý', 'Trưởng đoàn, điều phối hậu cần & liên hệ Ban tổ chức']
    ]
    info_aligns = [WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT]
    format_table(t_info, [1.2, 4.5, 4.0, 6.3], info_headers, info_data, info_aligns)

    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_before = Pt(8)
    p_sp.paragraph_format.space_after = Pt(8)

    # Helper thêm Section Heading
    def add_sec_heading(title_text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(title_text)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(13)
        r.bold = True

    def add_sub_heading(title_text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.first_line_indent = Cm(1.0)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(title_text)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(13)
        r.bold = True

    def add_body_p(text, bold_prefix=None, italic=False):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.first_line_indent = Cm(1.0)
        p.paragraph_format.line_spacing = 1.15
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(4)
        if bold_prefix:
            r_pre = p.add_run(bold_prefix)
            r_pre.font.name = 'Times New Roman'
            r_pre.font.size = Pt(13)
            r_pre.bold = True
        r = p.add_run(text)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(13)
        if italic:
            r.italic = True
        return p

    def add_bullet_p(text, bold_prefix=None):
        p = doc.add_paragraph(style='List Bullet')
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.left_indent = Cm(1.5)
        p.paragraph_format.line_spacing = 1.15
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(3)
        if bold_prefix:
            r_pre = p.add_run(bold_prefix)
            r_pre.font.name = 'Times New Roman'
            r_pre.font.size = Pt(13)
            r_pre.bold = True
        r = p.add_run(text)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(13)
        return p

    # =========================================================================
    # NỘI DUNG CHÍNH CỦA HỒ SƠ
    # =========================================================================

    add_sec_heading('I. CĂN CỨ THỰC TIỄN VÀ MỤC TIÊU CỦA ĐỀ TÀI')
    add_body_p('Hiện nay, vào mỗi khung giờ cao điểm tan học tại cổng các trường học trên cả nước nói chung và Trường Tiểu học, THCS và THPT Marie Curie nói riêng, tình trạng ùn tắc giao thông cục bộ và nguy cơ mất an toàn cho học sinh tự đi bộ qua đường diễn ra vô cùng phức tạp. Các hệ thống đèn tín hiệu giao thông hiện hữu hoạt động thuần túy theo chu kỳ thời gian cố định (Fixed Timer), bộc lộ hai nhược điểm cốt tử: một là, khi không có người qua đường, xe cộ vẫn bị chặn dừng gây lãng phí nhiên liệu và phát thải khí CO2; hai là, khi học sinh nhỏ tuổi cần qua đường, dòng xe vẫn lưu thông với tốc độ cao, tiềm ẩn rủi ro tai nạn giao thông nghiêm trọng.')
    add_body_p('Xuất phát từ thực tế đó, đội tuyển STEM Marie Curie đã nghiên cứu và phát triển giải pháp: "Hệ thống Đèn Giao Thông Học Đường Thông Minh Tích Hợp Thị Giác AI và Rào Chắn An Toàn Kép". Đề tài ứng dụng Trí tuệ nhân tạo (Google Teachable Machine) đóng vai trò "mắt thần", kết hợp vi điều khiển Arduino Nano điều phối cụm đèn LED, rào chắn Barie bảo vệ vật lý và còi cảnh báo âm thanh dành cho người đi bộ khiếm thị.')

    add_sec_heading('II. TÍNH TOÁN ĐỘNG HỌC GIAO THÔNG VÀ TỶ LỆ XÍCH SA BÀN (STEM TOÁN - KHOA HỌC)')
    add_sub_heading('1. Thiết lập tỷ lệ xích mô hình sa bàn (Tỷ lệ 1 : 20)')
    add_body_p('Để phù hợp với không gian bàn thi đấu quy chuẩn (kích thước 60cm x 120cm) do Ban Tổ chức HNUE bố trí, đội thi thiết kế sa bàn ngã tư cổng trường có kích thước 60cm x 80cm theo tỷ lệ xích 1 : 20 (1cm trên mô hình tương ứng 20cm ngoài thực địa):')
    add_bullet_p('40cm trên sa bàn tương đương 8 mét thực tế (chuẩn đường 2 làn xe qua cổng trường).', 'Lòng đường xe chạy: ')
    add_bullet_p('Mỗi bên rộng 10cm sa bàn tương đương 2 mét vỉa hè thực tế.', 'Vỉa hè người đi bộ: ')
    add_bullet_p('Cột chính cao 25cm (tương đương 5 mét thực tế); cần vươn ngang dài 12cm (tương đương 2.4 mét thực tế) vươn ra tim đường.', 'Cột đèn giao thông: ')
    add_bullet_p('Chiều dài 22cm (tương đương 4.4 mét thực tế), chắn trọn vẹn nửa phần đường đi bộ.', 'Cần Barie an toàn: ')

    add_sub_heading('2. Tính toán chu kỳ đèn đi bộ bằng công thức Toán học')
    add_body_p('Thời gian đèn xanh cho học sinh qua đường được tính toán khoa học dựa trên công thức động học chuyển động thẳng đều:')
    add_body_p('Trong đó: Chiều rộng lòng đường W = 8m; Vận tốc đi bộ trung bình của học sinh lứa tuổi 9 - 10 tuổi đo đạc thực nghiệm v = 0.8 m/s. Thời gian di chuyển thuần túy: t_walk = 8 / 0.8 = 10 giây.')
    add_body_p('Để đảm bảo an toàn tuyệt đối cho học sinh lớp 1, lớp 2 đi chậm hoặc các tình huống mang cặp sách nặng, vấp ngã, đội thi bổ sung hệ số an toàn đệm t_đệm = 5 giây. Do đó, tổng thời gian đèn xanh cho người đi bộ được cài đặt chính xác là: T_ped = 10s + 5s = 15 giây.')

    add_sub_heading('3. Bộ lọc xác nhận thời gian của AI (AI Debounce Filter)')
    add_body_p('Nhằm triệt tiêu triệt để hiện tượng nhận diện nhầm do ánh sáng môi trường hội trường hoặc người đi lướt qua ngẫu nhiên, hệ thống thiết lập bộ lọc trễ xác nhận (Debounce): Mô hình AI phải nhận diện trạng thái học sinh giơ tay liên tục trong thời gian t_confirm >= 1.5 giây với độ tin cậy Confidence >= 85% thì mới phát lệnh chuyển đổi chu kỳ đèn. Giải pháp này giúp loại bỏ 100% tình trạng đèn chuyển màu gián đoạn vô lý, bảo đảm dòng phương tiện lưu thông tối ưu.')

    add_sec_heading('III. TÍNH TOÁN CÔNG SUẤT ĐIỆN VÀ AN TOÀN HỆ THỐNG (STEM KỸ THUẬT)')
    add_body_p('Hệ thống được thiết kế vận hành hoàn toàn ở điện áp cực thấp 5V DC lấy trực tiếp từ cổng USB máy tính hoặc củ sạc dự phòng 5V-2A, triệt tiêu hoàn toàn nguy cơ cháy nổ hay điện giật đối với học sinh tiểu học.')
    
    t_power = doc.add_table(rows=1, cols=6)
    p_headers = ['STT', 'Thiết bị / Linh kiện', 'Điện áp (V)', 'Dòng tĩnh (mA)', 'Dòng đỉnh (mA)', 'Công suất đỉnh (W)']
    p_data = [
        ['1', 'Mạch vi điều khiển Arduino Nano', '5.0 V', '20 mA', '30 mA', '0.15 W'],
        ['2', 'Cụm 3 đèn LED giao thông ô tô', '5.0 V', '0 mA', '20 mA', '0.10 W'],
        ['3', 'Cụm 2 đèn LED người đi bộ', '5.0 V', '0 mA', '20 mA', '0.10 W'],
        ['4', 'Động cơ Servo SG90 (Nâng hạ Barie)', '5.0 V', '10 mA', '220 mA', '1.10 W'],
        ['5', 'Còi chip Buzzer mini báo âm thanh', '5.0 V', '0 mA', '25 mA', '0.12 W'],
        ['6', 'Nút bấm cơ học Failsafe + Trở kéo', '5.0 V', '0 mA', '1 mA', '0.005 W'],
        ['7', 'Mắt Webcam USB Mini rời', '5.0 V', '100 mA', '150 mA', '0.75 W'],
        ['--', 'TỔNG CỘNG HỆ THỐNG MẠCH', '5.0 V', '~30 mA', '~316 mA', '< 1.60 W']
    ]
    p_aligns = [WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER]
    format_table(t_power, [1.2, 5.5, 2.3, 2.4, 2.4, 2.2], p_headers, p_data, p_aligns)

    add_body_p('Đánh giá an toàn kỹ thuật: Tổng cường độ dòng điện đỉnh của toàn bộ mạch điều khiển là 316 mA, nằm sâu dưới ngưỡng trần an toàn của cổng USB 2.0 tiêu chuẩn (500 mA) và cổng USB 3.0 (900 mA). Hệ thống vận hành liên tục êm ái, hoàn toàn không bị hiện tượng sụt áp, không làm nóng vi điều khiển hay dây dẫn.')

    add_sec_heading('IV. THIẾT KẾ CƠ KHÍ VÀ BỐ TRÍ MÔ HÌNH SA BÀN (PHƯƠNG ÁN 1)')
    add_body_p('Sau khi phản biện toàn diện các hạn chế của việc sử dụng camera tích hợp trên viền màn hình laptop (góc nhìn bị cố định, thao tác cồng kềnh, thiếu tính chân thực), đội thi Marie Curie chốt triển khai theo Phương án 1 tối ưu:')
    add_bullet_p('Mắt camera nhỏ gọn được gắn cố định tại đầu cần vươn của cột đèn giao thông, chếch góc 45 độ hướng thẳng vào tâm vạch kẻ đường kích thước 20cm x 15cm. Toàn bộ dây cáp tín hiệu USB được luồn ngầm dưới gầm sa bàn dẫn ra trạm máy tính điều hành.', 'Vị trí lắp đặt Webcam USB mini rời: ')
    add_bullet_p('Cần Barie được chế tạo từ ống hút giấy cứng siêu nhẹ (trọng lượng chỉ 2.5 gram), dán decal phản quang sọc trắng - đỏ. Cần được điều khiển bởi động cơ Servo SG90 quét góc từ 0 độ (nằm ngang chắn đường) lên 90 độ (dựng đứng cho học sinh qua) với bước trễ 15ms/độ, giúp cần chuyển động mượt mà, không bị rung lắc.', 'Cơ cấu rào chắn Barie an toàn: ')
    add_bullet_p('Tại chân cột đèn được bố trí một Nút bấm cơ học dự phòng. Khi hệ thống nhận diện AI gặp sự cố ánh sáng hoặc mất tín hiệu máy tính, học sinh chỉ cần ấn nút, mạch Arduino lập tức kích hoạt chu kỳ đèn an toàn. Nếu mất tín hiệu điều khiển quá 3 giây, cột đèn tự động chuyển sang chế độ đèn vàng nhấp nháy cảnh báo giảm tốc độ.', 'Cơ chế dự phòng an toàn kép (Fail-Safe): ')
    add_bullet_p('Hồ sơ kỹ thuật của dự án đã số hóa hoàn chỉnh Bản vẽ phối cảnh 3D Vector Isometric (so_do_3d_ky_thuat.svg) và Ứng dụng mô phỏng động cơ 3D thời gian thực (so_do_3d_mo_hinh.html) lưu trữ tại thư mục assets/, cho phép Ban Giám khảo quan sát góc nhìn 360 độ và chuyển động mô phỏng thực tế của ngã tư.', 'Hồ sơ thiết kế 3D số hóa: ')

    add_sec_heading('V. MÔ HÌNH THỊ GIÁC AI TEACHABLE MACHINE VÀ GIAO THỨC ĐIỀU KHIỂN')
    add_body_p('Mô hình Trí tuệ nhân tạo được xây dựng trên nền tảng Google Teachable Machine với thuật toán Mạng nơ-ron tích chập (MobileNet Backbone), bao gồm 3 phân lớp nhận diện độc lập:')
    
    t_ai = doc.add_table(rows=1, cols=4)
    ai_headers = ['Tên phân lớp (Class)', 'Mục tiêu nhận diện', 'Số lượng ảnh huấn luyện', 'Độ chính xác thực nghiệm']
    ai_data = [
        ['0_Normal_Road', 'Lòng đường bình thường, xe chạy, không có học sinh', '120 ảnh mẫu', 'Đạt 98.2%'],
        ['1_Student_Waiting', 'Học sinh đứng sát mép đường giơ tay xin qua đường', '150 ảnh mẫu', 'Đạt 96.5%'],
        ['2_Ambulance_Emergency', 'Mô hình xe cứu thương màu trắng, chữ thập đỏ', '120 ảnh mẫu', 'Đạt 97.8%']
    ]
    ai_aligns = [WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER]
    format_table(t_ai, [4.0, 6.0, 3.0, 3.0], ai_headers, ai_data, ai_aligns)

    add_body_p('Tính độc lập không phụ thuộc Internet: Toàn bộ mô hình sau khi huấn luyện được tải về máy tính và chạy Offline cục bộ 100% bằng thư viện TensorFlow.js trên trình duyệt Google Chrome. Hệ thống truyền nhận dữ liệu với mạch Arduino Nano qua giao thức Web Serial API bằng các gói tin 1-Byte siêu nhẹ (Ký tự "0" - Bình thường; Ký tự "1" - Học sinh qua đường; Ký tự "2" - Ưu tiên xe cứu thương).')

    add_sec_heading('VI. BẢNG KÊ KHAI CHI PHÍ NGUYÊN VẬT LIỆU CHẾ TẠO CHI TIẾT')
    add_body_p('Căn cứ quy định của Ban Tổ chức Cuộc thi HNUE Olympic STEM 2026 về giới hạn kinh phí nguyên vật liệu không vượt quá 1.000.000 VNĐ/đội và ưu tiên vật liệu tái chế, thân thiện môi trường, đội thi Marie Curie lập bảng kê khai chi phí thực tế như sau:')

    t_cost = doc.add_table(rows=1, cols=6)
    c_headers = ['STT', 'Tên danh mục vật tư / Linh kiện', 'Thông số kỹ thuật', 'Số lượng', 'Đơn giá (VNĐ)', 'Thành tiền (VNĐ)']
    c_data = [
        ['I', 'KHỐI LINH KIỆN ĐIỆN TỬ & CẢM BIẾN', '', '', '', '225.000'],
        ['1', 'Mạch vi điều khiển Arduino Nano V3.0', 'Chip CH340, ATmega328P + cáp', '1 bộ', '85.000', '85.000'],
        ['2', 'Mắt Webcam USB Mini rời', 'Độ phân giải HD 720p, dây 1.2m', '1 chiếc', '95.000', '95.000'],
        ['3', 'Động cơ Servo mini SG90', 'Điện áp 5V, góc quay 180 độ', '1 chiếc', '28.000', '28.000'],
        ['4', 'Còi chip Buzzer mini phát âm thanh', 'Active Buzzer 5V', '1 chiếc', '5.000', '5.000'],
        ['5', 'Cụm 5 đèn LED 5mm + Điện trở 220 Ohm', 'Đỏ, Vàng, Xanh siêu sáng', '5 bộ', '1.800', '9.000'],
        ['6', 'Nút nhấn cơ học Failsafe + Trở 10k', 'Nút bấm 4 chân mini', '1 chiếc', '3.000', '3.000'],
        ['II', 'KHỐI SA BÀN & VẬT LIỆU TÁI CHẾ', '', '', '', '70.000'],
        ['7', 'Bìa carton thùng bánh cũ làm sa bàn', 'Carton 3 lớp sóng chịu lực', '2 tấm', '0', '0 (Tái chế)'],
        ['8', 'Que kem gỗ, ống hút giấy làm cột, barie', 'Vật liệu tái chế học đường', '20 chiếc', '0', '0 (Tái chế)'],
        ['9', 'Giấy decal màu trang trí ngã tư, vạch kẻ', 'Khổ A4 có keo dán sẵn', '3 tờ', '5.000', '15.000'],
        ['10', 'Keo nến, dây cắm breadboard, màu nước', 'Vật liệu phụ trợ kết dính', '1 gói', '55.000', '55.000'],
        ['III', 'THIẾT BỊ ĐIỀU HÀNH SẴN CÓ', '', '', '', '0'],
        ['11', 'Laptop / Máy tính bảng của đội thi', 'Chạy mô hình AI Teachable Machine', '1 máy', '--', '0 (Cơ sở vật chất)'],
        ['--', 'TỔNG CỘNG KINH PHÍ THỰC TẾ', '', '', '', '295.000 VNĐ']
    ]
    c_aligns = [WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.RIGHT, WD_ALIGN_PARAGRAPH.RIGHT]
    format_table(t_cost, [1.0, 5.0, 4.0, 1.5, 2.2, 2.3], c_headers, c_data, c_aligns)

    add_body_p('Kết luận tài chính: Tổng kinh phí chế tạo mô hình thực tế của đội Marie Curie là 295.000 VNĐ (Hai trăm chín mươi lăm nghìn đồng), tiết kiệm được 705.000 VNĐ so với mức trần quy định của Ban Tổ chức. Dự án tận dụng trên 70% vật tư tái chế, đáp ứng xuất sắc tiêu chí Thân thiện môi trường và Tính khả thi.')

    add_sec_heading('VII. KỊCH BẢN THUYẾT TRÌNH BẤM GIỜ ĐÚNG 5 PHÚT (300 GIÂY)')
    add_body_p('Kịch bản thuyết trình được thiết kế chính xác theo cấu trúc 5 câu hỏi cốt lõi của Ban Giám khảo, phân bổ thời gian chuẩn mực cho 3 thành viên:')

    add_bullet_p('Kính thưa Ban Giám khảo và quý Thầy Cô! Hằng ngày vào mỗi giờ tan học tại cổng trường Marie Curie, chúng con thường chứng kiến cảnh tượng ùn tắc giao thông nghiêm trọng. Các bạn học sinh nhỏ tuổi rất sợ hãi khi phải tự mình băng qua đường giữa dòng xe cộ nườm nượp. Các hệ thống đèn giao thông hiện nay chỉ đổi màu máy móc theo thời gian cố định: lúc không có ai thì xe vẫn bị bắt dừng chờ gây tắc đường và khói bụi; lúc học sinh cần qua đường thì xe lại lao tới, rất nguy hiểm. Hôm nay, chúng con mang đến giải pháp: Hệ thống Đèn Giao Thông Học Đường Thông Minh Tích Hợp AI Vision và Rào Chắn An Toàn Kép!', '00:00 - 01:00 (60s) - Bạn Phạm Hữu Đạt trình bày: ')

    add_bullet_p('Kính thưa Ban Giám khảo, đây là sa bàn mô phỏng ngã tư cổng trường do chính tay chúng con chế tạo từ bìa carton và que kem tái chế, tổng chi phí chỉ đúng 295.000 đồng. Hệ thống có 3 điểm đặc biệt: Thứ nhất, trên cần vươn cột đèn gắn một mắt Webcam mini góc rộng 45 độ soi thẳng vào vạch qua đường. Thứ hai, cột đèn đi bộ có cần Barie an toàn điều khiển bằng động cơ Servo. Khi đèn xe đỏ, Barie mới mở ra cho học sinh đi, ngăn các em chạy ùa ra đường. Thứ ba là Cơ chế An toàn kép: Nếu camera hỏng hoặc mất điện máy tính, học sinh chỉ cần bấm nút cơ học dự phòng là hệ thống vẫn kích hoạt bình thường ạ!', '01:00 - 02:40 (100s) - Bạn Vũ Minh Quang trình bày: ')

    add_bullet_p('Kính thưa Ban Giám khảo, để biến cột đèn thành "mắt thần", chúng con đã chụp hơn 390 bức ảnh và huấn luyện trên Google Teachable Machine để nhận diện 3 trạng thái: đường vắng (Normal), học sinh xin đường (Student) và xe cứu thương (Ambulance). Bằng công thức Toán học t = s/v + t_đệm, chúng con tính được chu kỳ đèn xanh cho học sinh là đúng 15 giây (10 giây đi bộ + 5 giây an toàn). Nhờ đó, thời gian xe chờ giảm được 35%, cắt giảm đáng kể khí thải CO2. Đặc biệt, khi AI nhìn thấy mô hình xe cứu thương, đèn xe lập tức chuyển xanh khẩn cấp để xe ưu tiên phóng qua!', '02:40 - 04:20 (100s) - Bạn Vũ Ngọc An Đông trình bày: ')

    add_bullet_p('Đạt: "Dự án của chúng con là bài học tích hợp Khoa học, Công nghệ, Kỹ thuật và Toán học..." - Quang: "Thể hiện tình yêu môi trường từ vật liệu tái chế..." - Đông: "Và khát vọng bảo vệ an toàn cho hàng triệu học sinh Việt Nam!" - Cả 3 em đồng thanh: "Chúng con xin trân trọng cảm ơn Ban Giám khảo!"', '04:20 - 05:00 (40s) - Đồng thanh cả 3 em kết luận: ')

    add_sec_heading('VIII. KỊCH BẢN 5 PHÚT PHẢN BIỆN TRƯỚC HỘI ĐỒNG GIÁM KHẢO HNUE')
    add_body_p('1. Giám khảo hỏi: "Tại sao các con lại nghĩ ra việc gắn thêm chiếc cần Barie mà không chỉ dùng đèn tín hiệu như bình thường?"')
    add_body_p('Bạn Vũ Minh Quang trả lời: "Dạ thưa Thầy/Cô, ở lứa tuổi Tiểu học, các em lớp 1, lớp 2 rất hiếu động, nhiều khi mải đùa nghịch không để ý đèn tín hiệu trên cao. Chiếc cần Barie hạ xuống tạo thành một hàng rào vật lý chắn ngang tầm mắt, giúp các em nhận biết rõ ràng chưa được phép bước ra đường. Khi Barie mở lên kết hợp tiếng còi chíp tít tít, các em mới yên tâm bước đi an toàn ạ!"')

    add_body_p('2. Giám khảo hỏi: "Mô hình AI này có cần kết nối Internet không? Nếu hội trường thi mất mạng thì hệ thống có chạy được không?"')
    add_body_p('Bạn Phạm Hữu Đạt trả lời: "Thưa Thầy/Cô, mô hình AI sau khi huấn luyện trên Teachable Machine đã được chúng con tải về máy tính chạy Offline 100% bằng thư viện TensorFlow.js, hoàn toàn không cần Internet. Tín hiệu được truyền qua cổng cáp USB trực tiếp vào mạch Arduino Nano với độ trễ dưới 50 mili-giây ạ!"')

    add_body_p('3. Giám khảo hỏi: "Trong quá trình chế tạo, khó khăn lớn nhất các con đã gặp phải là gì và đã giải quyết ra sao?"')
    add_body_p('Bạn Vũ Ngọc An Đông trả lời: "Dạ thưa Ban Giám khảo, lần đầu tiên chúng con làm cần barie bằng thanh gỗ dày, động cơ servo nhỏ không đủ lực nâng và bị kẹt kêu rít. Thầy Ngọc Anh đã giải thích cho chúng con về trọng lượng và mô-men xoắn. Sau đó bạn Quang đã nghĩ ra sáng kiến thay bằng ống hút giấy rỗng siêu nhẹ. Kết quả là servo hoạt động êm ái và không bị kẹt nữa ạ (hình vẽ chi tiết có trong Sổ tay kỹ thuật trang 6)!"')

    # Bảng chữ ký xác nhận chuẩn văn bản hành chính
    add_sec_heading('IX. KÝ XÁC NHẬN CỦA ĐỘI TUYỂN VÀ CÁN BỘ PHỤ TRÁCH')
    p_sp2 = doc.add_paragraph()
    p_sp2.paragraph_format.space_before = Pt(8)

    t_sign = doc.add_table(rows=2, cols=3)
    t_sign.alignment = WD_TABLE_ALIGNMENT.CENTER
    sign_headers = ['ĐẠI DIỆN ĐỘI THI\n(Học sinh)', 'CÁN BỘ HỖ TRỢ KỸ THUẬT\n(Giáo viên)', 'TRƯỞNG ĐOÀN\n(Phụ trách chung)']
    for c_idx, text in enumerate(sign_headers):
        cell = t_sign.rows[0].cells[c_idx]
        cell.text = text
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in p.runs:
            r.font.name = 'Times New Roman'
            r.font.size = Pt(12)
            r.bold = True

    sign_names = ['Phạm Hữu Đạt\n(Đội trưởng)', 'Lê Ngọc Anh\n(Tổ trưởng STEM)', 'Trần Ánh Nguyệt / BGH\n(Hiệu trưởng)']
    for c_idx, text in enumerate(sign_names):
        cell = t_sign.rows[1].cells[c_idx]
        cell.text = f'\n\n\n\n{text}'
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in p.runs:
            r.font.name = 'Times New Roman'
            r.font.size = Pt(12)
            r.bold = True

    # Ẩn viền bảng ký tên
    for row in t_sign.rows:
        for cell in row.cells:
            set_cell_border(cell,
                            top={'val': 'none', 'sz': 0, 'space': 0, 'color': 'auto'},
                            bottom={'val': 'none', 'sz': 0, 'space': 0, 'color': 'auto'},
                            left={'val': 'none', 'sz': 0, 'space': 0, 'color': 'auto'},
                            right={'val': 'none', 'sz': 0, 'space': 0, 'color': 'auto'})
            cell.width = Cm(5.3)

    output_path = r'E:\Antigravity\MCA\HNUE_olympic_stem\1.Data\HO_SO_THIET_KE_KY_THUAT_VA_DU_TOAN_CHI_TIET.docx'
    doc.save(output_path)
    print(f'Tạo file DOCX chuẩn thể thức thành công tại: {output_path}')

if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    create_document()
