# -*- coding: utf-8 -*-
"""
Script sinh file DOCX chuẩn thể thức Nghị định 30/2020/NĐ-CP (mẫu Marie Curie)
cho tài liệu: BẢN THUYẾT MINH CÁC TÌNH HUỐNG HOẠT ĐỘNG VÀ QUY TRÌNH VẬN HÀNH
"""

import sys
import docx
from docx.shared import Inches, Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
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
            set_cell_margins(cell, top=120, bottom=120, left=140, right=140)
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
    r_title = p_title.add_run('BẢN THUYẾT MINH CÁC TÌNH HUỐNG HOẠT ĐỘNG\nVÀ QUY TRÌNH VẬN HÀNH SA BÀN')
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

    # I. NGUYÊN LÝ MÁY TRẠNG THÁI HỮU HẠN
    add_sec_heading('I. NGUYÊN LÝ ĐIỀU KHIỂN THEO MÁY TRẠNG THÁI HỮU HẠN (FINITE STATE MACHINE)')
    add_body_p('Hệ thống Đèn giao thông học đường thông minh Marie Curie được thiết kế và lập trình theo mô hình Máy trạng thái hữu hạn (Finite State Machine - FSM). Toàn bộ hành vi của cột đèn tín hiệu, góc quét camera AI, động cơ Servo điều khiển rào chắn Barie an toàn và còi chip cảnh báo âm thanh được tích hợp chặt chẽ qua 5 tình huống logic khép kín, triệt tiêu hoàn toàn các xung đột logic trong quá trình vận hành thực tế.')

    # II. BẢNG ĐỐI CHIẾU TRẠNG THÁI
    add_sec_heading('II. BẢNG ĐỐI CHIẾU TRẠNG THÁI THIẾT BỊ TRONG 5 TÌNH HUỐNG')
    add_body_p('Ma trận trạng thái điều khiển thiết bị phần cứng tương ứng với từng tín hiệu đầu vào từ mô hình thị giác AI và cảm biến ngoại vi:')

    t_fsm = doc.add_table(rows=1, cols=6)
    fsm_headers = ['Tình huống', 'Camera AI nhận diện', 'Đèn Ô tô (Xe chạy)', 'Đèn Đi Bộ', 'Rào Chắn Barie (Servo)', 'Còi Buzzer Cảnh Báo']
    fsm_data = [
        ['TH 1: Đường vắng (Bình thường)', '0_Normal_Road (>= 90%)', 'XANH (Chạy)', 'ĐỎ (Dừng)', 'ĐÓNG (0 độ)', 'Tắt hoàn toàn'],
        ['TH 2: Học sinh xin qua đường', '1_Student_Waiting (>= 1.5s)', 'VÀNG (3s) -> ĐỎ (15s)', 'XANH (15s)', 'MỞ LÊN (90 độ)', 'Kêu nhịp "tít... tít..."'],
        ['TH 3: Xe cứu thương khẩn cấp', '2_Ambulance_Emergency', 'XANH KHẨN CẤP', 'ĐỎ (Chặn)', 'ĐÓNG (0 độ)', 'Kêu dài cảnh báo'],
        ['TH 4: Bấm nút Failsafe dự phòng', 'Bỏ qua nhận diện AI', 'VÀNG (3s) -> ĐỎ (15s)', 'XANH (15s)', 'MỞ LÊN (90 độ)', 'Kêu nhịp "tít... tít..."'],
        ['TH 5: Mất kết nối máy tính (> 3s)', 'Mất tín hiệu USB', 'VÀNG NHẤP NHÁY (1s/lần)', 'ĐỎ', 'ĐÓNG CHẶT (0 độ)', 'Tắt']
    ]
    fsm_aligns = [WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT]
    format_table(t_fsm, [3.2, 4.0, 2.5, 2.0, 2.3, 2.0], fsm_headers, fsm_data, fsm_aligns)

    # III. PHÂN TÍCH CHUYÊN SÂU 5 TÌNH HUỐNG
    add_sec_heading('III. PHÂN TÍCH CHUYÊN SÂU 5 TÌNH HUỐNG VẬN HÀNH THỰC TẾ')

    add_sub_heading('1. Tình huống 1: Chế độ Đường vắng (Bình thường - Idle State)')
    add_body_p('Bối cảnh thực tế: Ngoài giờ cao điểm tan học hoặc tại các thời điểm không có học sinh qua lại cổng trường, lòng đường thông thoáng.')
    add_body_p('Hoạt động hệ thống: Mắt Webcam USB mini gắn trên đầu cần vươn của cột đèn (chếch góc 45 độ) liên tục quét mặt đường. Mô hình AI nhận diện trạng thái 0_Normal_Road với độ tin cậy trên 98%. Đèn tín hiệu ô tô duy trì màu XANH liên tục để các phương tiện lưu thông với vận tốc tối ưu, không bị dừng chờ máy móc. Đèn đi bộ màu ĐỎ, cần Barie an toàn chốt chặt ở góc 0 độ nằm ngang trên vỉa hè, còi Buzzer tắt.')
    add_body_p('Ý nghĩa khoa học và môi trường: Giải quyết triệt để khuyết tật của đèn hẹn giờ truyền thống. Xe cộ không phải dừng chờ đèn đỏ vô lý khi đường vắng, giúp tiết kiệm xăng và cắt giảm 35% lượng khí thải độc hại (CO, CO2) ngay trước cổng trường học.')

    add_sub_heading('2. Tình huống 2: Học sinh qua đường được AI nhận diện (Pedestrian AI Mode)')
    add_body_p('Bối cảnh thực tế: Học sinh đi đến mép vỉa hè, đứng trước vạch kẻ đường và thực hiện cử chỉ giơ tay vẫy xin đường.')
    add_body_p('Hệ thống tự động thực thi chuỗi 4 pha phối hợp khép kín:')
    add_bullet_p('Camera phát hiện cử chỉ học sinh. Bộ lọc thời gian (Debounce Filter) lập tức kiểm tra: Mô hình AI phải nhận diện trạng thái 1_Student_Waiting liên tục trong 1.5 giây (khoảng 22 khung hình) với độ tin cậy Confidence >= 85%. Nếu một người chỉ đi lướt qua mép đường dưới 1.5 giây, hệ thống bỏ qua -> Không gây xáo trộn luồng xe.', 'Pha 1 — Lọc nhiễu xác nhận (1.5 giây): ')
    add_bullet_p('Máy tính gửi mã lệnh "1" qua cổng USB. Mạch Arduino chuyển đèn xe từ Xanh sang VÀNG trong đúng 3 giây. Thời gian này giúp tài xế từ xa chủ động hãm phanh an toàn trước vạch dừng, tránh hiện tượng phanh gấp. Cần Barie lúc này vẫn đóng chặt bảo vệ học sinh trên vỉa hè.', 'Pha 2 — Cảnh báo giảm tốc an toàn (3 giây): ')
    add_bullet_p('Đèn xe chuyển ĐỎ (dừng xe); Đèn đi bộ chuyển XANH; Động cơ Servo SG90 quay từ 0 độ lên 90 độ (trong 1.35s) nhẹ nhàng nâng cần Barie lên mở lối cho học sinh bước qua; Còi chip Buzzer phát âm thanh nhịp nhàng "tít... tít..." (0.5s/nhịp) hướng dẫn thính giác cho các em nhỏ hoặc người khiếm thị. Thời gian đếm ngược chính xác đúng 15 giây (tính toán khoa học: t = s/v = 8m / 0.8m/s = 10s cộng 5s đệm an toàn).', 'Pha 3 — Mở lối an toàn qua đường (15 giây): ')
    add_bullet_p('Ở 3 giây cuối cùng, còi chip kêu dồn dập cảnh báo sắp hết giờ. Sau đó, cần Barie từ từ hạ xuống góc 0 độ chắn đường trước khi đèn xe chuyển lại màu Xanh.', 'Pha 4 — Đóng rào chắn và phục hồi: ')

    add_sub_heading('3. Tình huống 3: Xe cứu thương / Xe cứu hỏa khẩn cấp đến (Emergency Override)')
    add_body_p('Bối cảnh thực tế: Trong khi học sinh đang chuẩn bị qua đường (hoặc đèn xe đang đỏ), có một chiếc xe cứu thương hú còi tiến nhanh về phía ngã tư.')
    add_body_p('Cơ chế ngắt ưu tiên tuyệt đối (Preemption): Mắt camera AI nhận diện ngay lập tức hình dáng xe cứu thương (2_Ambulance_Emergency) với độ chính xác trên 97%. Hệ thống lập tức hủy bỏ mọi chu kỳ đang chạy dở: Cần Barie lập tức hạ xuống chốt góc 0 độ để ngăn học sinh bước xuống đường; Đèn người đi bộ chuyển sang màu ĐỎ; Còi chip Buzzer phát tiếng còi dài cảnh báo nguy hiểm; Đèn ô tô lập tức bật XANH KHẨN CẤP để xe cứu thương đi qua ngã tư với thời gian chờ bằng 0!')
    add_body_p('Cơ chế bù giờ: Sau khi xe cứu thương đi qua khỏi tầm nhìn camera 3 giây, nếu trên vỉa hè vẫn còn học sinh đang chờ, hệ thống tự động bù lại một chu kỳ đèn xanh qua đường đầy đủ cho học sinh.')

    add_sub_heading('4. Tình huống 4: Sự cố mất nhận diện AI -> Nút bấm cơ học Failsafe')
    add_body_p('Bối cảnh thực tế: Vào ngày mưa lớn sương mù hoặc ánh đèn rọi hội trường chiếu thẳng vào camera khiến AI không đạt ngưỡng tin cậy 85%.')
    add_body_p('Quy trình kích hoạt dự phòng cơ học: Học sinh nhận thấy sau 3 giây đứng giơ tay mà đèn chưa chuyển -> Em chủ động nhấn vào Nút bấm cơ học màu đỏ (Failsafe Button) gắn trên cột đèn. Nút bấm nối trực tiếp vào chân ngắt phần cứng D2 của Arduino Nano. Mạch Arduino lập tức bỏ qua máy tính, tự động chạy chu kỳ an toàn: Đèn xe chuyển vàng 3s -> Đèn xe đỏ + Barie mở 15s -> Barie đóng.')
    add_body_p('Ý nghĩa kỹ thuật: Khẳng định năng lực tư duy dự phòng sự cố (Fail-Safe) chuẩn kỹ sư của đội tuyển Marie Curie, chứng minh với Ban Giám khảo rằng hệ thống không bao giờ bỏ rơi học sinh dù công nghệ có gặp sự cố.')

    add_sub_heading('5. Tình huống 5: Mất nguồn máy tính / Đứt cáp USB (Watchdog Safe State)')
    add_body_p('Bối cảnh thực tế: Máy tính laptop điều hành bị hết pin đột ngột hoặc tuột cáp kết nối USB.')
    add_body_p('Cơ chế bảo vệ tự động của Vi điều khiển (Hardware Watchdog): Giữa máy tính và Arduino luôn có một xung nhịp định kỳ (Heartbeat) truyền mỗi 1 giây. Nếu quá 3 giây Arduino không nhận được tín hiệu từ máy tính: Vi điều khiển tự xác định trung tâm AI đã mất kết nối. Cần Barie lập tức hạ xuống góc 0 độ (khóa chặt lối đi bộ để giữ học sinh an toàn trên vỉa hè). Đèn xe bật nhấp nháy màu VÀNG (1 giây/nhịp) theo đúng Quy chuẩn báo hiệu đường bộ quốc gia (QCVN 41:2019/BGTVT), cảnh báo tất cả phương tiện giảm tốc độ tối đa khi đi qua khu vực trường học.')

    # IV. KỊCH BẢN BIỂU DIỄN 4 BƯỚC
    add_sec_heading('IV. KỊCH BẢN BIỂU DIỄN THỰC CHIẾN 4 BƯỚC TẠI GIAN HÀNG THI ĐẤU')
    add_body_p('Khi Ban Giám khảo Hội đồng Sư phạm HNUE bước đến gian hàng thi đấu, 3 em học sinh Đạt, Quang, Đông sẽ phối hợp nhịp nhàng biểu diễn thực tế trên sa bàn theo 4 bước trực quan:')
    add_bullet_p('Bạn Phạm Hữu Đạt chỉ tay vào sa bàn: "Kính thưa Ban Giám khảo, khi đường vắng, camera AI nhận diện Normal Road, đèn xe luôn xanh để phương tiện chạy thông suốt, không gây ùn tắc và không xả khói bụi ạ."', 'Bước 1 — Trình diễn TH1 (Đường vắng): ')
    add_bullet_p('Bạn Đạt bước đến vạch kẻ đường giơ tay xin qua. Bạn Vũ Minh Quang chỉ vào màn hình và sa bàn: "Khi bạn Đạt giơ tay, camera AI nhận diện đúng 96% liên tục trong 1.5 giây. Đèn xe lập tức chuyển vàng 3 giây cảnh báo, sau đó đèn xe chuyển đỏ, cần Barie tự động nâng lên 90 độ mượt mà và còi chíp kêu tít tít hướng dẫn bạn Đạt qua đường an toàn trong đúng 15 giây ạ!"', 'Bước 2 — Trình diễn TH2 (Học sinh qua đường & Barie an toàn): ')
    add_bullet_p('Bạn Vũ Ngọc An Đông cầm chiếc xe cứu thương đồ chơi đẩy vào làn đường. Bạn Đông thuyết minh: "Đột nhiên có xe cứu thương tới... Camera AI lập tức nhận diện xe cứu thương, ngay lập tức cần Barie đóng sập xuống bảo vệ người đi bộ, đèn xe chuyển xanh khẩn cấp cho xe cứu thương phóng qua không phải chờ đợi một giây nào ạ!"', 'Bước 3 — Trình diễn TH3 (Ưu tiên xe cứu thương): ')
    add_bullet_p('Bạn Quang dùng tay che mắt camera lại: "Thưa Thầy Cô, nếu camera bị mờ hoặc hội trường mất mạng, con chỉ cần ấn nút đỏ này trên cột đèn. Hệ thống chạy mạch ngắt độc lập, mở Barie cho con qua đường an toàn 100% mà không phụ thuộc vào máy tính ạ!"', 'Bước 4 — Trình diễn TH4 (Nút bấm dự phòng Failsafe): ')

    # V. XÁC NHẬN CỦA ĐỘI TUYỂN
    add_sec_heading('V. KÝ XÁC NHẬN CỦA ĐỘI TUYỂN VÀ CÁN BỘ PHỤ TRÁCH')
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

    for row in t_sign.rows:
        for cell in row.cells:
            set_cell_border(cell,
                            top={'val': 'none', 'sz': 0, 'space': 0, 'color': 'auto'},
                            bottom={'val': 'none', 'sz': 0, 'space': 0, 'color': 'auto'},
                            left={'val': 'none', 'sz': 0, 'space': 0, 'color': 'auto'},
                            right={'val': 'none', 'sz': 0, 'space': 0, 'color': 'auto'})
            cell.width = Cm(5.3)

    output_path = r'E:\Antigravity\MCA\HNUE_olympic_stem\1.Data\CAC_TINH_HUONG_HOAT_DONG_CHI_TIET.docx'
    doc.save(output_path)
    print(f'Tạo file DOCX chuẩn thể thức thành công tại: {output_path}')

if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    create_document()
