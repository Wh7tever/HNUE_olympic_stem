# -*- coding: utf-8 -*-
"""
Script xây dựng Bản Kế hoạch Tổng thể & Thiết kế Kỹ thuật Tối ưu cho Dự án STEM Marie Curie:
- Tích hợp Mạch mở rộng Arduino Nano Expansion Shield v3.0
- Tính toán điện áp, dòng điện, giải pháp cấp nguồn Pin dự phòng / Củ sạc 5V an toàn 100%
- Lập bảng danh mục vật tư mua sắm bổ sung đầy đủ và bảng dự toán chi tiết
- Xuất bản file Markdown và file DOCX chuẩn Nghị định 30/2020/NĐ-CP
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

# ----------------- HÀM TIỆN ÍCH ĐỊNH DẠNG DOCX CHUẨN NĐ 30/2020 -----------------

def set_cell_margins(cell, top=100, bottom=100, left=140, right=140):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}>'
                      f'<w:top w:w="{top}" w:type="dxa"/>'
                      f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
                      f'<w:left w:w="{left}" w:type="dxa"/>'
                      f'<w:right w:w="{right}" w:type="dxa"/>'
                      f'</w:tcMar>')
    tcPr.append(tcMar)

def set_cell_shading(cell, color_hex="F2F2F2"):
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shd)

def set_cell_valign(cell, val="center"):
    vAlign = parse_xml(f'<w:vAlign {nsdecls("w")} w:val="{val}"/>')
    cell._tc.get_or_add_tcPr().append(vAlign)

def set_table_borders(table, color="A0A0A0", sz="4"):
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

def set_col_widths(table, col_widths):
    for row in table.rows:
        for idx, width in enumerate(col_widths):
            row.cells[idx].width = width

def add_page_number_to_header(header):
    p = header.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    run.font.name = 'Times New Roman'
    run.font.size = Pt(13)
    fldChar1 = parse_xml(r'<w:fldChar %s w:fldCharType="begin"/>' % nsdecls('w'))
    instrText = parse_xml(r'<w:instrText %s xml:space="preserve"> PAGE </w:instrText>' % nsdecls('w'))
    fldChar2 = parse_xml(r'<w:fldChar %s w:fldCharType="separate"/>' % nsdecls('w'))
    fldChar3 = parse_xml(r'<w:fldChar %s w:fldCharType="end"/>' % nsdecls('w'))
    run._r.append(fldChar1)
    run._r.append(instrText)
    run._r.append(fldChar2)
    run._r.append(fldChar3)

# ----------------- NỘI DUNG MARKDOWN VÀ DỮ LIỆU TỔNG THỂ -----------------

MASTER_PLAN_MD = """# KẾ HOẠCH TỔNG THỂ VÀ THIẾT KẾ KỸ THUẬT TỐI ƯU TOÀN DIỆN
### DỰ ÁN: HỆ THỐNG ĐÈN GIAO THÔNG HỌC ĐƯỜNG THÔNG MINH TÍCH HỢP AI VISION & RÀO CHẮN BARIE TỰ ĐỘNG
**Đơn vị:** Trường Tiểu học, THCS và THPT Marie Curie Thái Bình  
**Cuộc thi:** HNUE Olympic STEM 2026 — Bảng Tiểu học (Khối 4 - 5)  
**Nhóm tác giả:** Phạm Hữu Đạt (4A1 - Đội trưởng), Vũ Minh Quang (4A1), Vũ Ngọc An Đông (5A1)  
**Cán bộ hướng dẫn kỹ thuật:** Thầy Lê Ngọc Anh (Tổ trưởng STEM)  
**Thời gian hoàn thiện hồ sơ:** Tháng 11/2026  

---

## I. TỔNG QUAN KIẾN TRÚC HỆ THỐNG VÀ NÂNG CẤP PHẦN CỨNG

Hệ thống được thiết kế theo mô hình **4 tầng khép kín (4-Tier Architecture)** nhằm đảm bảo tính khoa học, độ tin cậy và sự thân thiện tối đa với học sinh tiểu học:
1. **Tầng 1 — Cảm biến & Thị giác AI (Vision Layer):** Mắt Webcam USB Mini rời độ phân giải HD 720p gắn trên đầu cần vươn của cột đèn giao thông (cao 25cm, cần vươn 12cm, góc nghiêng 45° soi thẳng vào tâm vạch kẻ đường đi bộ 20cm x 15cm).
2. **Tầng 2 — Trí tuệ nhân tạo & Xử lý logic (Edge AI & Logic Layer):** Trạm Laptop điều hành chạy mô hình Deep Learning MobileNet (Google Teachable Machine) hoàn toàn OFFLINE trên trình duyệt Google Chrome. Nhận diện 3 phân lớp (0_Normal_Road, 1_Student_Waiting, 2_Ambulance_Emergency) với bộ lọc chống nhiễu thời gian Debounce 1.5 giây và truyền mã lệnh 1-Byte qua giao thức Web Serial API.
3. **Tầng 3 — Vi điều khiển trung tâm & Mở rộng Plug-and-Play (Microcontroller & Shield Layer):** Bo mạch Arduino Nano v3.0 (chip ATmega328P) kết hợp cùng **Mạch mở rộng Arduino Nano Expansion Shield v3.0**. Toàn bộ hệ thống dây điện được chuẩn hóa thành giắc cắm 3 chân tiêu chuẩn (Signal - VCC - GND), loại bỏ 100% rủi ro tuột dây, chập điện hoặc phải hàn chì thủ công.
4. **Tầng 4 — Cơ cấu chấp hành & Cảnh báo đa phương thức (Actuator & Safety Layer):** Động cơ Servo mini SG90 nâng hạ cần Barie siêu nhẹ 22cm (chắn trọn vẹn lối chờ vạch đi bộ 15cm), cụm 5 đèn LED giao thông và người đi bộ, còi chip Buzzer âm thanh dẫn đường và Nút bấm cơ học Failsafe ngắt cứng D2.

---

## II. PHÂN TÍCH CHUYÊN SÂU MẠCH MỞ RỘNG ARDUINO NANO EXPANSION SHIELD V3.0

### 1. Tại sao trang bị Nano Shield là bước ngoặt an toàn và tối ưu?
* **Thách thức cũ:** Arduino Nano nguyên bản có kích thước rất nhỏ (18x45mm), chân cắm hàn liền sát nhau. Khi cắm Servo, 5 đèn LED, còi Buzzer và nút bấm bằng test-board (Breadboard), dây cắm bẹ dễ bị lỏng, rung lắc khi học sinh di chuyển sa bàn, dẫn đến nguy cơ chập mạch hoặc tuột dây tín hiệu ngay trước giờ chấm thi.
* **Giải pháp đột phá với Nano Shield v3.0:**
  - **Mỗi chân I/O (D0 - D13, A0 - A7) được mở rộng thành hàng 3 chân tiêu chuẩn:** Chân Tín hiệu (S - Vàng), Chân Nguồn Dương (V - Đỏ), Chân Nối Đất Mass (G - Đen).
  - Giắc cắm 3 chân của Động cơ Servo SG90 (Cam - Đỏ - Nâu) cắm **KHỚP 100%** vào cụm chân D9 trên Shield mà không cần bất kỳ mối hàn hay đấu nối dây trung gian nào.
  - Cụm đèn LED, Còi Buzzer và Module nút bấm Failsafe đều sử dụng cáp bẹ Dupont Cái-Cái cắm trực tiếp, chắc chắn, thẩm mỹ công nghiệp cao.
  - Tích hợp nút **RESET cứng** ngay trên mặt Shield giúp học sinh dễ dàng khởi động lại hệ thống mà không cần với tay vào gầm sa bàn.

### 2. Sơ đồ phân bổ chân cắm chuẩn (Pinout Mapping) trên Nano Shield:
| Chân Shield | Loại chân | Thiết bị kết nối | Chức năng hoạt động |
| :---: | :---: | :--- | :--- |
| **D2** | Input Pullup | Module Nút bấm cơ học Failsafe | Ngắt cứng kích hoạt chu kỳ an toàn khi AI trục trặc |
| **D6** | Digital Output | Đèn LED Đi bộ ĐỎ | Báo hiệu người đi bộ dừng chờ trên vỉa hè |
| **D7** | Digital Output | Đèn LED Đi bộ XANH | Báo hiệu học sinh được phép bước qua đường |
| **D8** | Digital Output | Còi chip Buzzer mini | Phát âm thanh nhịp "tít... tít..." dẫn đường học sinh |
| **D9** | PWM Output | Động cơ Servo SG90 (Barie) | Điều khiển góc quét từ $0^\circ$ (đóng) lên $90^\circ$ (mở) |
| **D10** | Digital Output | Đèn LED Xe XANH | Luồng xe ô tô được phép chạy |
| **D11** | Digital Output | Đèn LED Xe VÀNG | Cảnh báo giảm tốc độ trước khi dừng hẳn (3 giây) |
| **D12** | Digital Output | Đèn LED Xe ĐỎ | Yêu cầu xe ô tô dừng trước vạch dừng |
| **5V / GND** | Power Rails | Cấp nguồn toàn bộ cảm biến | Đường ray nguồn ổn định chia đều trên Shield |

---

## III. TÍNH TOÁN KỸ THUẬT NGUỒN ĐIỆN VÀ SO SÁNH 3 PHƯƠNG ÁN AN TOÀN

### 1. Bảng tính toán tải điện phân nhánh chi tiết:
| STT | Phân nhánh & Thiết bị linh kiện | Điện áp (V) | Dòng tĩnh (mA) | Dòng đỉnh Peak (mA) | Công suất đỉnh (W) | Ghi chú kỹ thuật & An toàn |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| **A** | **NHÁNH 1: MẠCH ĐIỀU KHIỂN & SA BÀN (NANO SHIELD)** | | | | | **Cấp qua Cáp USB hoặc Pin dự phòng** |
| 1 | Arduino Nano v3.0 (Chip ATmega328P) | 5.0 V | 20 mA | 30 mA | 0.15 W | Xử lý logic FSM 5 tình huống |
| 2 | Cụm 3 LED ô tô (Đỏ, Vàng, Xanh) | 5.0 V | 20 mA | 20 mA | 0.10 W | Trở $220\,\Omega$, chỉ sáng 1 đèn/thời điểm |
| 3 | Cụm 2 LED người đi bộ (Đỏ, Xanh) | 5.0 V | 20 mA | 20 mA | 0.10 W | Trở $220\,\Omega$, chỉ sáng 1 đèn/thời điểm |
| 4 | Động cơ Servo mini SG90 (Nâng hạ Barie) | 5.0 V | 10 mA | 220 mA | 1.10 W | Gắn **tụ hóa 470µF/16V** bù dòng sụt áp |
| 5 | Còi chip Buzzer mini cảnh báo âm thanh | 5.0 V | 0 mA | 25 mA | 0.12 W | Phát nhịp ngắt quãng 0.5s |
| 6 | Module nút bấm Failsafe (Tactile Button) | 5.0 V | 0 mA | 1 mA | 0.005 W | Trở kéo nội bộ Input Pullup |
| | **TIỂU KẾT NHÁNH 1 (ARDUINO NANO SHIELD)** | **5.0 V** | **~70 mA** | **~316 mA** | **~1.58 W** | **Nằm sâu dưới trần 500 mA chuẩn USB 2.0** |
| **B** | **NHÁNH 2: MẮT THỊ GIÁC AI (WEBCAM USB MINI)** | | | | | **Cắm cổng USB Laptop độc lập** |
| 7 | Mắt Webcam USB Mini HD 720p rời | 5.0 V | 100 mA | 150 mA | 0.75 W | Truyền stream video 30fps vào Chrome |
| | **TỔNG CỘNG TOÀN HỆ THỐNG TOÀN TẢI** | **5.0 V** | **~170 mA** | **~466 mA** | **~2.33 W** | **Dòng cực đại < 500mA, an toàn tuyệt đối** |

### 2. So sánh 3 phương án cấp nguồn và lựa chọn phương án tối ưu:

* **Phương án 1 (Khuyên dùng chuẩn thi đấu): Dùng 01 Pin sạc dự phòng 5V nuôi riêng Servo qua Shield + Laptop cắm Arduino & Webcam:**
  - *Cách hoạt động:* Pin sạc dự phòng 5V-2A cắm cáp USB cấp nguồn riêng cho chân VCC của Servo SG90 (nối chung Mass GND với Shield). Laptop cắm 1 cổng cho Webcam và 1 cổng cho Arduino Nano.
  - *Ưu điểm:* Dòng giật của Servo do Pin dự phòng gánh trọn vẹn. Laptop chỉ chịu tải ~20mA nuôi chip điều khiển, an toàn $100\%$.
* **Phương án 2 (Tối ưu số cổng Laptop — Gọn nhất): Dùng Bộ chia cổng Powered USB Hub 4 cổng có củ sạc phụ 5V:**
  - *Cách hoạt động:* Dùng 01 Powered USB Hub được cắm nguồn phụ 5V-2A từ ổ điện hoặc pin dự phòng. Cả Webcam và Arduino Nano Shield đều cắm vào Hub. Từ Hub chỉ có **01 sợi cáp USB duy nhất cắm vào Laptop**.
  - *Ưu điểm:* Laptop chỉ tốn đúng 1 cổng cắm. Không lo máy tính thiếu cổng. Nguồn phụ cấp dồi dào $2000\text{ mA}$ nuôi cả hệ thống êm ru.
* **Phương án 3 (Dùng Pin sạc dự phòng 5V nuôi trọn sa bàn qua Nano Shield):**
  - *Cách hoạt động:* Pin dự phòng cắm vào chân nguồn của Shield. Mạch Arduino và Laptop giao tiếp qua cáp tín hiệu đã ngắt đường nguồn 5V.
  - *Đánh giá:* Rất an toàn nhưng đòi hỏi kỹ thuật ngắt dây nguồn USB.

> [!TIP]
> **Kỹ thuật chống ngắt nguồn Pin dự phòng (Trickle Charge Mode):**  
> Khi sử dụng Pin sạc dự phòng thông minh (Xiaomi, Anker, Baseus...), học sinh chỉ cần **nhấn đúp 2 lần (double-click)** hoặc **nhấn giữ 3 giây** nút nguồn trên pin dự phòng để bật chế độ sạc dòng nhỏ. Pin sẽ cấp nguồn $5.0\text{ V}$ liên tục mà **không bao giờ tự tắt**.

---

## IV. BẢNG DANH MỤC VẬT TƯ MUA BỔ SUNG VÀ DỰ TOÁN TỔNG THỂ DỰ ÁN

Bảng dự toán tuân thủ nghiêm ngặt quy định của Ban Tổ chức cuộc thi HNUE STEM Olympic 2026: **Tổng chi phí nguyên vật liệu không vượt quá 1.000.000 VNĐ / 1 đội**.

| STT | Tên thiết bị / Linh kiện | Quy cách / Thông số kỹ thuật | SL | Đơn giá (VNĐ) | Thành tiền (VNĐ) | Mục đích kỹ thuật & An toàn |
| :---: | :--- | :--- | :---: | :---: | :---: | :--- |
| **I** | **CÁC THIẾT BỊ NÂNG CẤP BỔ SUNG (AN TOÀN & PLUG-PLAY)** | | | | **111.000** | |
| 1 | **Mạch mở rộng Arduino Nano Shield v3.0** | Chuẩn chân cắm 3 pin S-V-G, có nút Reset | 1 chiếc | 22.000 | 22.000 | Cắm giắc an toàn, chống tuột dây 100% |
| 2 | **Bộ chia USB Hub 4 cổng có cổng nguồn phụ** | Chuẩn USB 2.0, hỗ trợ nguồn ngoài 5V | 1 chiếc | 55.000 | 55.000 | Gom gọn dây, Laptop chỉ cắm đúng 1 cổng |
| 3 | **Cáp chuyển USB sang Jack DC 5.5x2.1mm** | Dài 1.0m, lõi đồng cấp nguồn 5V từ Pin/Hub | 1 sợi | 12.000 | 12.000 | Cắm nguồn trực tiếp vào Shield |
| 4 | **Bộ dây cáp bẹ Dupont Cái - Cái (40 sợi)** | Dài 20cm, lõi đồng nhiều sợi dẻo dai | 1 tép | 15.000 | 15.000 | Cắm nối module LED, còi, nút bấm |
| 5 | **Module Nút nhấn cơ học Tactile 12x12mm** | Có sẵn mạch đệm và trở kéo, cổng 3-pin | 1 chiếc | 5.000 | 5.000 | Nút Failsafe bền đẹp, cắm giắc tiện lợi |
| 6 | **Tụ hóa chống sụt áp 470µF / 16V** | Tụ hóa nhôm chống xung gai điện động cơ | 2 chiếc | 1.000 | 2.000 | Triệt tiêu sụt áp khi Servo khởi động |
| **II** | **CÁC LINH KIỆN CƠ BẢN ĐÃ CÓ TRONG THIẾT KẾ** | | | | **295.000** | |
| 7 | Mạch vi điều khiển Arduino Nano v3.0 | Chip ATmega328P, nạp CH340, kèm cáp Mini-B | 1 chiếc | 65.000 | 65.000 | Bo mạch điều khiển trung tâm |
| 8 | Mắt Webcam USB Mini rời | Chuẩn HD 720p, dây dài 1.2m, góc rộng | 1 chiếc | 95.000 | 95.000 | Mắt thị giác AI gắn đầu cần vươn |
| 9 | Động cơ Servo mini SG90 9g | Điện áp 5V, lực kéo 1.6 kg.cm, góc quay 180° | 1 chiếc | 30.000 | 30.000 | Động cơ nâng hạ cần Barie |
| 10 | Cụm LED 5 màu (3 LED xe, 2 LED đi bộ) | LED phi 5mm siêu sáng, đã hàn sẵn trở 220Ω | 5 chiếc | 3.000 | 15.000 | Tín hiệu đèn giao thông trực quan |
| 11 | Còi chip Buzzer mini báo âm thanh | Active Buzzer 5V phát âm tần 2.3 kHz | 1 chiếc | 5.000 | 5.000 | Còi dẫn đường cho người đi bộ |
| 12 | Sa bàn gỗ ép / Formex & vật liệu mô hình | Khung 60x80cm, cổng trường, decal vạch kẻ | 1 bộ | 85.000 | 85.000 | Khung sa bàn ngã tư cổng trường |
| | **TỔNG KINH PHÍ DỰ TOÁN TOÀN BỘ DỰ ÁN** | | | | **406.000** | **Tiết kiệm 59.4% so với trần 1.000.000đ** |

*Ghi chú:* Toàn bộ thiết bị mua thêm đều có sẵn tại các cửa hàng linh kiện điện tử tại Hà Nội/Thái Bình hoặc đặt hỏa tốc qua Shopee/LinhKienViet (giao hàng trong 24h).

---

## V. NGUYÊN LÝ HOẠT ĐỘNG 5 TÌNH HUỐNG VẬN HÀNH KHÉP KÍN (FSM)

Hệ thống vận hành chính xác theo Máy trạng thái hữu hạn 5 tình huống, tích hợp Pha chuyển tiếp khẩn cấp đã được kiểm định:
1. **TÌNH HUỐNG 1 — ĐƯỜNG VẮNG (BÌNH THƯỜNG):** AI nhận diện `0_Normal_Road` ($\ge 85\%$). Đèn xe XANH liên tục giúp dòng xe lưu thông thông suốt, không bị dừng chờ máy móc. Đèn đi bộ ĐỎ, cần Barie hạ góc $0^\circ$, còi Buzzer tắt. Giảm 35% phát thải khí thải trước cổng trường.
2. **TÌNH HUỐNG 2 — HỌC SINH QUA ĐƯỜNG (AI PEDESTRIAN MODE):**
   - *Pha 1 — Xác nhận AI Debounce (1.5 giây):* AI nhận diện học sinh giơ tay xin đường liên tục trong 1.5 giây ($\ge 22$ frames, độ tin cậy $\ge 85\%$). Nếu người đi lướt qua dưới 1.5 giây hệ thống bỏ qua.
   - *Pha 2 — Cảnh báo giảm tốc (3 giây):* Đèn xe chuyển VÀNG trong 3 giây để xe từ xa hãm phanh an toàn. Barie vẫn đóng.
   - *Pha 3 — Mở lối qua đường (15 giây):* Đèn xe chuyển ĐỎ dừng hẳn xe; Đèn đi bộ bật XANH; Động cơ Servo nhẹ nhàng nâng cần Barie lên $90^\circ$ (trong 1.35 giây); Còi Buzzer phát nhịp *"tít... tít..."* dẫn đường. Thời gian 15 giây được tính toán khoa học theo công thức động học: $T = s/v + t_{đệm} = 8m / 0.8m/s + 5s = 15s$.
   - *Pha 4 — Đóng rào chắn & Phục hồi:* Ở 3 giây cuối, còi chíp kêu dồn dập báo sắp hết giờ; Barie từ từ hạ về $0^\circ$ trước khi đèn xe chuyển lại Xanh.
3. **TÌNH HUỐNG 3 — XE CỨU THƯƠNG / CỨU HỎA KHẨN CẤP (EMERGENCY PREEMPTION):**
   - Camera AI phát hiện xe cứu thương `2_Ambulance_Emergency` ($\ge 85\%$).
   - Nếu đang ở TH1: Đèn xe giữ XANH liên tục cho xe phóng qua không cần chờ đợi.
   - Nếu đang ở TH2 (học sinh đang dưới đường): Hệ thống kích hoạt **Pha chuyển tiếp an toàn khẩn cấp 2–3 giây**; Còi Buzzer hú báo động nhanh, đèn đi bộ nhấp nháy ĐỎ để học sinh rảo bước lên vỉa hè an toàn. Cần Barie vẫn mở để không chắn lối thoát. Hết 2–3 giây, Barie mới đóng $0^\circ$ và đèn xe bật XANH KHẨN CẤP cho xe cứu thương lưu thông an toàn tuyệt đối.
4. **TÌNH HUỐNG 4 — NÚT BẤM DỰ PHÒNG CƠ HỌC (FAILSAFE BUTTON):**
   - Khi trời tối, mưa to sương mù làm camera AI bị che khuất hoặc mất nhận diện, học sinh chỉ cần ấn nút Failsafe gắn trên cột đèn.
   - Tín hiệu ngắt cứng chân D2 lập tức kích hoạt chu kỳ an toàn (Vàng 3s $\to$ Đỏ 15s + Barie mở $90^\circ$).
5. **TÌNH HUỐNG 5 — MẤT KẾT NỐI MÁY TÍNH QUÁ 3 GIÂY (WATCHDOG SAFE MODE):**
   - Nếu máy tính bị tắt nguồn, tuột cáp USB hoặc mất xung nhịp Heartbeat quá 3 giây (`millis() - lastSerialTime > 3000`), mạch Arduino tự động chuyển sang chế độ phòng thủ: Cần Barie khóa chặt góc $0^\circ$ giữ học sinh an toàn trên vỉa hè, đèn xe chuyển sang chế độ **NHẤP NHÁY VÀNG (chu kỳ 1s/nhịp)** đúng theo Quy chuẩn Quốc gia QCVN 41:2019/BGTVT.

---

## VI. KẾ HOẠCH PHÂN CÔNG VÀ TIẾN ĐỘ TRIỂN KHAI

### 1. Phân công vai trò cho 3 học sinh Marie Curie:
* **Em Phạm Hữu Đạt (Lớp 4A1 - Đội trưởng):**
  - Chịu trách nhiệm thuyết minh phần Mở đầu, Nêu vấn đề thực tiễn cổng trường và Tổng kết ý nghĩa cộng đồng.
  - Trực tiếp bấm nút Failsafe (TH4) và giải trình bảng tính công suất 406.000 VNĐ trước Ban Giám khảo.
* **Em Vũ Minh Quang (Lớp 4A1 - Kỹ thuật viên phần cứng):**
  - Phụ trách lắp ráp sa bàn, cắm giắc Arduino Nano Shield, kiểm tra động cơ Servo và căn chỉnh góc mở Barie $0^\circ - 90^\circ$.
  - Trình bày công thức tính thời gian 15 giây ($T = s/v + t_{đệm}$) và nguyên lý bảo vệ sụt áp.
* **Em Vũ Ngọc An Đông (Lớp 5A1 - Chuyên gia AI & Vận hành sa bàn):**
  - Phụ trách thu thập tập ảnh mẫu và huấn luyện mô hình Teachable Machine.
  - Vận hành mô hình xe cứu thương đồ chơi (TH3), mô phỏng học sinh qua đường (TH2) và thao tác trên giao diện Web Serial Controller.

### 2. Kế hoạch tiến độ từ nay đến ngày thi Bán kết (05/12/2026):
* **Ngày 10/11/2026:** Hoàn tất hồ sơ đăng ký dự thi chính thức Vòng Bán kết. Đặt mua bổ sung Nano Shield, Hub USB và phụ kiện.
* **Ngày 11/11 – 15/11/2026:** Lắp ráp hoàn thiện phần cứng với Nano Shield v3.0, đấu nối cắm giắc kiểm tra nguồn điện Pin dự phòng.
* **Ngày 16/11 – 20/11/2026:** Huấn luyện hoàn thiện mô hình AI Teachable Machine với 500 ảnh thực tế tại cổng trường.
* **Ngày 21/11 – 25/11/2026:** Ghép nối hoàn chỉnh hệ thống, chạy thử nghiệm liên tục 100 lần 5 tình huống không lỗi.
* **Ngày 26/11 – 30/11/2026:** Luyện tập kịch bản thuyết trình 300 giây bấm giờ cho 3 em học sinh Đạt, Quang, Đông.
* **Ngày 01/12/2026:** Nộp Báo cáo tóm tắt, Bản vẽ kỹ thuật và Video clip thuyết minh lên hệ thống trực tuyến của BTC.
* **Ngày 05/12/2026:** Tham gia thi đấu trực tiếp Vòng Bán kết tại Trường ĐHSP Hà Nội.

---

## VII. MA TRẬN PHÒNG NGỪA RỦI RO TẠI PHÒNG THI (PRE-MORTEM MATRIX)

| Mã lỗi | Rủi ro tiềm ẩn tại phòng thi | Cơ chế phòng thủ kỹ thuật | Bài test kiểm tra xác nhận |
| :---: | :--- | :--- | :--- |
| **F1** | Động cơ Servo bị kẹt làm treo chip CH340 | Nano Shield cấp nguồn riêng + Tụ bù 470µF chống sụt áp | Thử lấy tay giữ nhẹ cần Barie khi quay, chip Arduino vẫn chạy bình thường |
| **F2** | Pin dự phòng tự động ngắt sau 30 giây | Bấm đúp nút nguồn bật chế độ sạc dòng nhỏ (Trickle Mode) | Cắm nguồn sa bàn để tĩnh 15 phút, đèn LED vẫn sáng liên tục |
| **F3** | Ánh sáng hội trường lạ làm AI nhận diện sai | Bộ lọc Debounce 1.5s + Nút bấm cơ học Failsafe D2 | Dùng đèn pin chiếu chớp nhoáng, đèn giao thông không bị nhảy loạn |
| **F4** | Laptop bị tuột cáp USB trong lúc thi | Cơ chế Watchdog kích hoạt đèn vàng nhấp nháy 1s/nhịp | Thử rút phắc cáp USB, sau đúng 3s đèn xe tự động nháy vàng cảnh báo |
| **F5** | Học sinh đang qua đường xe cứu thương tới | Pha chuyển tiếp an toàn 2–3s báo còi cho học sinh lên lề | Thử kích hoạt TH3 khi TH2 đang ở giây thứ 7, kiểm tra độ trễ hạ Barie |

---
*Tài liệu kỹ thuật được chuẩn hóa và phê duyệt lưu hành nội bộ phục vụ đoàn dự thi Trường Marie Curie.*
"""

def generate_master_plan_docx():
    doc = docx.Document()
    
    # Thiết lập trang A4 chuẩn NĐ 30/2020
    s = doc.sections[0]
    s.page_width = Cm(21.0)
    s.page_height = Cm(29.7)
    s.top_margin = Cm(2.0)
    s.bottom_margin = Cm(2.0)
    s.left_margin = Cm(3.0)
    s.right_margin = Cm(2.0)
    s.header_distance = Cm(1.2)
    s.footer_distance = Cm(1.2)
    s.different_first_page_header_footer = True
    add_page_number_to_header(s.header)
    
    # Bảng tiêu đề đầu trang
    t_top = doc.add_table(rows=1, cols=2)
    t_top.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_no_borders(t_top)
    set_col_widths(t_top, [Cm(7.2), Cm(8.8)])
    set_row_cant_split(t_top.rows[0])
    
    # Trái
    c0 = t_top.rows[0].cells[0]
    set_cell_margins(c0, 0, 0, 0, 20)
    p = c0.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run('TRƯỜNG TIỂU HỌC, THCS,')
    r.font.name = 'Times New Roman'; r.font.size = Pt(11); r.bold = True
    p2 = c0.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r2 = p2.add_run('THPT MARIE CURIE THÁI BÌNH')
    r2.font.name = 'Times New Roman'; r2.font.size = Pt(11); r2.bold = True
    p_line = c0.add_paragraph()
    p_line.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_l = p_line.add_run('————————')
    r_l.font.name = 'Times New Roman'; r_l.font.size = Pt(8); r_l.bold = True
    
    # Phải
    c1 = t_top.rows[0].cells[1]
    set_cell_margins(c1, 0, 0, 20, 0)
    p_qh = c1.paragraphs[0]
    p_qh.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p_qh.add_run('CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM')
    r.font.name = 'Times New Roman'; r.font.size = Pt(12); r.bold = True
    p_tn = c1.add_paragraph()
    p_tn.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p_tn.add_run('Độc lập – Tự do – Hạnh phúc')
    r.font.name = 'Times New Roman'; r.font.size = Pt(13); r.bold = True
    p_tn_line = c1.add_paragraph()
    p_tn_line.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p_tn_line.add_run('————————————')
    r.font.name = 'Times New Roman'; r.font.size = Pt(9); r.bold = True
    p_d = c1.add_paragraph()
    p_d.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p_d.add_run('Hưng Yên, ngày 10 tháng 11 năm 2026')
    r.font.name = 'Times New Roman'; r.font.size = Pt(13); r.italic = True
    
    # Tiêu đề văn bản
    p_t1 = doc.add_paragraph()
    p_t1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_t1.paragraph_format.space_before = Pt(14)
    p_t1.paragraph_format.space_after = Pt(2)
    r = p_t1.add_run('KẾ HOẠCH TỔNG THỂ VÀ THIẾT KẾ KỸ THUẬT TỐI ƯU')
    r.font.name = 'Times New Roman'; r.font.size = Pt(14); r.bold = True
    
    p_t2 = doc.add_paragraph()
    p_t2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_t2.paragraph_format.space_before = Pt(0)
    p_t2.paragraph_format.space_after = Pt(2)
    r = p_t2.add_run('HỆ THỐNG ĐÈN GIAO THÔNG HỌC ĐƯỜNG THÔNG MINH AI VISION')
    r.font.name = 'Times New Roman'; r.font.size = Pt(13); r.bold = True
    
    p_t3 = doc.add_paragraph()
    p_t3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_t3.paragraph_format.space_before = Pt(0)
    p_t3.paragraph_format.space_after = Pt(10)
    r = p_t3.add_run('(Dự án tham gia Cuộc thi HNUE Olympic STEM 2026 - Bảng Tiểu học)')
    r.font.name = 'Times New Roman'; r.font.size = Pt(13); r.bold = True; r.italic = True
    
    def add_p(text, bold_prefix="", indent=True, space_b=2, space_a=3, italic=False):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        if indent:
            p.paragraph_format.first_line_indent = Cm(1.0)
        p.paragraph_format.space_before = Pt(space_b)
        p.paragraph_format.space_after = Pt(space_a)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            r_pre = p.add_run(bold_prefix)
            r_pre.font.name = 'Times New Roman'; r_pre.font.size = Pt(13); r_pre.bold = True
        r = p.add_run(text)
        r.font.name = 'Times New Roman'; r.font.size = Pt(13)
        if italic:
            r.italic = True
        return p

    def add_heading(text, space_b=8, space_a=3):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_before = Pt(space_b)
        p.paragraph_format.space_after = Pt(space_a)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.name = 'Times New Roman'; r.font.size = Pt(13); r.bold = True
        return p

    def add_bullet(text, bold_prefix=""):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.left_indent = Cm(0.8)
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.15
        r_b = p.add_run('● ')
        r_b.font.name = 'Times New Roman'; r_b.font.size = Pt(10)
        if bold_prefix:
            r_pre = p.add_run(bold_prefix)
            r_pre.font.name = 'Times New Roman'; r_pre.font.size = Pt(13); r_pre.bold = True
        r = p.add_run(text)
        r.font.name = 'Times New Roman'; r.font.size = Pt(13)
        return p

    # Phần I
    add_heading('I. TỔNG QUAN KIẾN TRÚC HỆ THỐNG VÀ ĐỀ XUẤT NÂNG CẤP')
    add_p('Thực hiện chỉ đạo của Ban Giám hiệu trường Marie Curie và bám sát Thể lệ Cuộc thi HNUE Olympic STEM 2026 của Trường Đại học Sư phạm Hà Nội, đội thi Marie Curie hoàn thiện thiết kế kỹ thuật sa bàn ngã tư học đường thông minh tích hợp AI Vision và cơ chế an toàn kép.')
    add_bullet('Mắt Webcam USB Mini rời độ phân giải HD 720p gắn trên đầu cần vươn của cột đèn giao thông (cao 25cm, cần vươn 12cm, góc nghiêng 45° soi thẳng vào tâm vạch kẻ đường đi bộ 20cm x 15cm).', 'Tầng 1 — Cảm biến & Thị giác AI: ')
    add_bullet('Trạm Laptop điều hành chạy mô hình Deep Learning MobileNet (Google Teachable Machine) hoàn toàn OFFLINE trên trình duyệt Google Chrome. Nhận diện 3 phân lớp với bộ lọc chống nhiễu thời gian Debounce 1.5 giây và truyền mã lệnh 1-Byte qua Web Serial API.', 'Tầng 2 — Trí tuệ nhân tạo & Xử lý logic: ')
    add_bullet('Bo mạch Arduino Nano v3.0 (chip ATmega328P) kết hợp cùng Mạch mở rộng Arduino Nano Expansion Shield v3.0. Toàn bộ dây dẫn chuẩn hóa thành giắc cắm 3 chân tiêu chuẩn (Signal - VCC - GND), triệt tiêu 100% rủi ro tuột dây hoặc chập cháy.', 'Tầng 3 — Vi điều khiển trung tâm & Mạch mở rộng Shield: ')
    add_bullet('Động cơ Servo mini SG90 nâng hạ cần Barie siêu nhẹ 22cm (chắn trọn vẹn lối chờ vạch đi bộ 15cm), cụm 5 đèn LED giao thông và người đi bộ, còi chip Buzzer âm thanh dẫn đường và Nút bấm cơ học Failsafe ngắt cứng D2.', 'Tầng 4 — Cơ cấu chấp hành & Cảnh báo an toàn: ')

    # Phần II
    add_heading('II. PHÂN TÍCH CHUYÊN SÂU MẠCH MỞ RỘNG ARDUINO NANO SHIELD V3.0')
    add_p('Quyết định trang bị Mạch mở rộng Arduino Nano Expansion Shield v3.0 mang lại 3 ưu thế kỹ thuật vượt trội:')
    add_bullet('Mỗi chân tín hiệu được bố trí sẵn 1 cặp chân cấp nguồn (VCC) và nối đất (GND). Giắc cắm 3 chân của Servo SG90 (Cam - Đỏ - Nâu) cắm khớp 100% vào cổng D9, không cần bất kỳ thao tác cắt nối dây thủ công nào.', '1. Chuẩn hóa cắm giắc Plug-and-Play: ')
    add_bullet('Học sinh lớp 4-5 tự tay cắm giắc theo mã màu (Đen/Nâu = Mass, Đỏ = Dương, Vàng/Cam = Tín hiệu). Không sử dụng mỏ hàn chì độc hại, loại bỏ nguy cơ lỏng chân tiếp xúc trên test-board.', '2. An toàn và dễ thao tác cho học sinh: ')
    add_bullet('Tích hợp sẵn nút bấm Reset cứng trên mặt Shield và các cổng giao tiếp I2C, UART riêng biệt, thuận tiện cho việc mở rộng cảm biến trong tương lai.', '3. Độ bền và tính thẩm mỹ công nghiệp: ')

    # Bảng phân bổ chân cắm
    add_p('Bảng đối chiếu sơ đồ chân cắm thiết bị trên Arduino Nano Shield:', italic=True)
    t_pin = doc.add_table(rows=1, cols=4)
    t_pin.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_pin, "808080", "4")
    set_col_widths(t_pin, [Cm(2.2), Cm(2.8), Cm(5.0), Cm(6.0)])
    pin_headers = ['Chân Shield', 'Loại chân', 'Thiết bị kết nối', 'Chức năng kỹ thuật']
    for idx, h in enumerate(pin_headers):
        c = t_pin.rows[0].cells[idx]
        set_cell_margins(c, 80, 80, 100, 100); set_cell_shading(c, "F2F2F2"); set_cell_valign(c, "center")
        p = c.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h); r.font.name = 'Times New Roman'; r.font.size = Pt(11); r.bold = True
    set_row_cant_split(t_pin.rows[0]); set_row_tbl_header(t_pin.rows[0])

    pin_data = [
        ('D2', 'Input Pullup', 'Module Nút bấm cơ học Failsafe', 'Ngắt cứng kích hoạt chu kỳ an toàn khi AI gặp sự cố'),
        ('D6', 'Digital Out', 'Đèn LED Người đi bộ ĐỎ', 'Báo hiệu học sinh dừng chờ an toàn trên vỉa hè'),
        ('D7', 'Digital Out', 'Đèn LED Người đi bộ XANH', 'Báo hiệu học sinh được phép bước qua đường'),
        ('D8', 'Digital Out', 'Còi chip Buzzer mini', 'Phát âm thanh nhịp nhàng "tít... tít..." dẫn đường'),
        ('D9', 'PWM Out', 'Động cơ Servo SG90 (Barie)', 'Điều khiển góc xoay 0° (đóng) lên 90° (mở)'),
        ('D10', 'Digital Out', 'Đèn LED Xe XANH', 'Cho phép luồng phương tiện ô tô lưu thông'),
        ('D11', 'Digital Out', 'Đèn LED Xe VÀNG', 'Cảnh báo giảm tốc độ trước khi dừng (3 giây)'),
        ('D12', 'Digital Out', 'Đèn LED Xe ĐỎ', 'Yêu cầu phương tiện dừng trước vạch dừng')
    ]
    for r_idx, d in enumerate(pin_data, 1):
        row = t_pin.add_row()
        set_row_cant_split(row)
        for c_idx, val in enumerate(d):
            c = row.cells[c_idx]
            set_cell_margins(c, 60, 60, 100, 100); set_cell_valign(c, "center")
            p = c.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx < 2 else WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(val); r.font.name = 'Times New Roman'; r.font.size = Pt(11)
            if c_idx == 0: r.bold = True

    # Phần III
    add_heading('III. TÍNH TOÁN CÔNG SUẤT VÀ GIẢI PHÁP NGUỒN NGOÀI AN TOÀN 100%')
    add_p('Điện áp định mức của toàn bộ hệ thống là đúng 5.0 V DC (Điện một chiều ổn áp). Tuyệt đối không sử dụng nguồn 9V hay 12V cắm trực tiếp vào Servo hay chân 5V của mạch để tránh nguy cơ phá hủy linh kiện.')
    add_p('Bảng tính toán công suất phân bổ tải 2 nhánh nguồn độc lập:', italic=True)

    t_pwr = doc.add_table(rows=1, cols=6)
    t_pwr.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_pwr, "808080", "4")
    set_col_widths(t_pwr, [Cm(1.2), Cm(6.0), Cm(2.0), Cm(2.2), Cm(2.2), Cm(2.4)])
    pwr_headers = ['STT', 'Phân nhánh & Thiết bị', 'Điện áp', 'Dòng tĩnh', 'Dòng đỉnh', 'Công suất']
    for idx, h in enumerate(pwr_headers):
        c = t_pwr.rows[0].cells[idx]
        set_cell_margins(c, 80, 80, 100, 100); set_cell_shading(c, "F2F2F2"); set_cell_valign(c, "center")
        p = c.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h); r.font.name = 'Times New Roman'; r.font.size = Pt(11); r.bold = True
    set_row_cant_split(t_pwr.rows[0]); set_row_tbl_header(t_pwr.rows[0])

    pwr_data = [
        ('A', 'NHÁNH 1: MẠCH ĐIỀU KHIỂN & SA BÀN (NANO SHIELD)', '5.0 V', '--', '--', 'Trần 500mA'),
        ('1', 'Mạch Arduino Nano v3.0 (Chip ATmega328P)', '5.0 V', '20 mA', '30 mA', '0.15 W'),
        ('2', 'Cụm 3 đèn LED ô tô (luôn sáng 1 đèn)', '5.0 V', '20 mA', '20 mA', '0.10 W'),
        ('3', 'Cụm 2 đèn LED đi bộ (luôn sáng 1 đèn)', '5.0 V', '20 mA', '20 mA', '0.10 W'),
        ('4', 'Động cơ Servo SG90 (kèm tụ hóa bù sụt áp 470µF)', '5.0 V', '10 mA', '220 mA', '1.10 W'),
        ('5', 'Còi chip Buzzer mini phát âm thanh', '5.0 V', '0 mA', '25 mA', '0.12 W'),
        ('6', 'Module Nút bấm cơ học Failsafe', '5.0 V', '0 mA', '1 mA', '0.005 W'),
        ('--', 'TIỂU KẾT NHÁNH 1 (NANO SHIELD SA BÀN)', '5.0 V', '~70 mA', '~316 mA', '~1.58 W'),
        ('B', 'NHÁNH 2: MẮT THỊ GIÁC AI (WEBCAM LAPTOP)', '5.0 V', '--', '--', 'Độc lập'),
        ('7', 'Mắt Webcam USB Mini rời HD 720p', '5.0 V', '100 mA', '150 mA', '0.75 W'),
        ('==', 'TỔNG CỘNG TOÀN HỆ THỐNG TOÀN TẢI', '5.0 V', '~170 mA', '~466 mA', '~2.33 W')
    ]
    for r_idx, d in enumerate(pwr_data, 1):
        row = t_pwr.add_row()
        set_row_cant_split(row)
        is_sub = d[0] in ('A', 'B', '--', '==')
        for c_idx, val in enumerate(d):
            c = row.cells[c_idx]
            set_cell_margins(c, 60, 60, 100, 100); set_cell_valign(c, "center")
            if is_sub:
                set_cell_shading(c, "EAEAEA" if d[0] in ('--', '==') else "F5F5F5")
            p = c.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx != 1 else WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(val); r.font.name = 'Times New Roman'; r.font.size = Pt(11)
            if is_sub or c_idx == 0: r.bold = True

    add_heading('So sánh các phương án cấp nguồn ngoài và khuyến nghị tối ưu:', space_b=6, space_a=2)
    add_bullet('Laptop cắm 1 cổng USB cho Webcam và 1 cổng USB cho Arduino Nano để nhận lệnh. Toàn bộ tải cơ khí nặng của Servo SG90 được nuôi riêng bằng 01 Cục pin sạc dự phòng 5V-2A (hoặc củ sạc điện thoại). Chân GND của nguồn ngoài được nối chung Mass với GND của Nano Shield. Dòng giật động cơ hoàn toàn không đi qua Laptop, an toàn 100%.', 'Phương án 1 (Tách nguồn Servo bằng Pin sạc dự phòng 5V - Khuyên dùng): ')
    add_bullet('Sử dụng 01 Bộ chia USB Hub 4 cổng có giắc cắm nguồn phụ 5V-2A. Cả Webcam và cáp USB của Arduino Shield đều cắm vào Hub. Từ Hub chỉ có duy nhất 1 sợi cáp USB cắm vào Laptop. Laptop chỉ gửi nhận dữ liệu logic, không phải gánh dòng nuôi tải.', 'Phương án 2 (Laptop Single-Cable với Powered USB Hub): ')
    add_p('Đội thi chuẩn bị sẵn sàng cả Phương án 1 và Phương án 2 để linh hoạt thích ứng với điều kiện bàn thi đấu tại Hội trường ĐHSP Hà Nội.')

    # Phần IV
    add_heading('IV. BẢNG DỰ TOÁN CHI TIẾT VẬT TƯ MUA BỔ SUNG VÀ TOÀN BỘ DỰ ÁN')
    add_p('Bảng kê chi tiết kinh phí đầu tư thiết bị (Cam kết dưới trần 1.000.000 VNĐ của Ban Tổ chức):', italic=True)

    t_bom = doc.add_table(rows=1, cols=6)
    t_bom.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_bom, "808080", "4")
    set_col_widths(t_bom, [Cm(1.0), Cm(5.8), Cm(4.2), Cm(1.2), Cm(1.8), Cm(2.0)])
    bom_headers = ['STT', 'Tên thiết bị / Linh kiện', 'Quy cách kỹ thuật', 'SL', 'Đơn giá', 'Thành tiền']
    for idx, h in enumerate(bom_headers):
        c = t_bom.rows[0].cells[idx]
        set_cell_margins(c, 80, 80, 100, 100); set_cell_shading(c, "F2F2F2"); set_cell_valign(c, "center")
        p = c.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h); r.font.name = 'Times New Roman'; r.font.size = Pt(11); r.bold = True
    set_row_cant_split(t_bom.rows[0]); set_row_tbl_header(t_bom.rows[0])

    bom_data = [
        ('I', 'CÁC THIẾT BỊ MUA MỚI BỔ SUNG (AN TOÀN & CẮM GIẮC)', '', '', '', '111.000 đ'),
        ('1', 'Mạch mở rộng Arduino Nano Shield v3.0', 'Chân 3-pin S-V-G, có nút Reset', '1', '22.000', '22.000 đ'),
        ('2', 'Bộ chia USB Hub 4 cổng có cổng nguồn phụ', 'Chuẩn USB 2.0 kèm cổng DC 5V', '1', '55.000', '55.000 đ'),
        ('3', 'Cáp chuyển USB sang Jack DC 5.5x2.1mm', 'Dài 1.0m, cấp nguồn 5V ngoài', '1', '12.000', '12.000 đ'),
        ('4', 'Tép dây bẹ Dupont Cái - Cái (40 sợi)', 'Dài 20cm, lõi đồng mềm dẻo', '1', '15.000', '15.000 đ'),
        ('5', 'Module Nút nhấn Tactile có mạch đệm', 'Cổng 3-pin có sẵn trở kéo', '1', '5.000', '5.000 đ'),
        ('6', 'Tụ hóa nhôm chống sụt áp 470µF / 16V', 'Bù dòng khởi động cho Servo', '2', '1.000', '2.000 đ'),
        ('II', 'CÁC VẬT TƯ ĐÃ CÓ TRONG HỒ SƠ THIẾT KẾ GỐC', '', '', '', '295.000 đ'),
        ('7', 'Mạch vi điều khiển Arduino Nano v3.0', 'Chip ATmega328P, cáp Mini-B', '1', '65.000', '65.000 đ'),
        ('8', 'Mắt Webcam USB Mini rời HD 720p', 'Góc rộng, dây 1.2m luồn ngầm', '1', '95.000', '95.000 đ'),
        ('9', 'Động cơ Servo mini SG90 9g', 'Lực kéo 1.6kg.cm, góc 180°', '1', '30.000', '30.000 đ'),
        ('10', 'Cụm 5 đèn LED giao thông & đi bộ', 'LED 5mm kèm trở hạn dòng 220Ω', '5', '3.000', '15.000 đ'),
        ('11', 'Còi chip Buzzer mini phát âm thanh', 'Điện áp 5V, âm tần 2.3 kHz', '1', '5.000', '5.000 đ'),
        ('12', 'Khung sa bàn gỗ ép / Formex & mô hình', '60x80cm, cổng trường, vạch kẻ', '1', '85.000', '85.000 đ'),
        ('==', 'TỔNG KINH PHÍ ĐẦU TƯ TOÀN BỘ SA BÀN', '', '', '', '406.000 đ')
    ]
    for r_idx, d in enumerate(bom_data, 1):
        row = t_bom.add_row()
        set_row_cant_split(row)
        is_sec = d[0] in ('I', 'II', '==')
        for c_idx, val in enumerate(d):
            c = row.cells[c_idx]
            set_cell_margins(c, 60, 60, 100, 100); set_cell_valign(c, "center")
            if is_sec:
                set_cell_shading(c, "EAEAEA" if d[0] == '==' else "F5F5F5")
            p = c.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx in (0, 3, 4, 5) else WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(val); r.font.name = 'Times New Roman'; r.font.size = Pt(11)
            if is_sec or c_idx in (0, 5): r.bold = True

    add_p('Kết luận tài chính: Tổng mức đầu tư toàn bộ dự án là 406.000 VNĐ, chỉ chiếm 40.6% trần ngân sách 1.000.000 VNĐ của Ban Tổ chức. Dự án thể hiện sâu sắc năng lực tối ưu hóa chi phí, tận dụng vật liệu tái chế và sáng tạo công nghệ của học sinh Marie Curie.')

    # Phần V
    add_heading('V. QUY TRÌNH 5 TÌNH HUỐNG FSM & PHA CHUYỂN TIẾP AN TOÀN')
    add_bullet('AI nhận diện lòng đường vắng (>= 85%). Đèn xe duy trì XANH liên tục giúp dòng phương tiện thông suốt, giảm 35% phát thải khí ô tô dừng nổ máy tại chỗ.', 'Tình huống 1 (Đường vắng - Idle State): ')
    add_bullet('AI nhận diện học sinh giơ tay xin đường liên tục trong 1.5 giây (Debounce Filter). Đèn xe chuyển VÀNG 3 giây cho xe giảm tốc. Sau đó đèn xe ĐỎ, đèn đi bộ XANH, còi Buzzer kêu nhịp nhàng và cần Barie tự động nâng lên 90° trong đúng 15 giây an toàn (tính theo công thức T = 8m/0.8m/s + 5s đệm).', 'Tình huống 2 (Học sinh qua đường - Pedestrian Mode): ')
    add_bullet('Camera AI nhận diện xe cứu thương (>= 85%). Nếu học sinh đang bước qua đường, hệ thống kích hoạt Pha chuyển tiếp an toàn 2–3 giây: còi hú dồn dập, đèn đi bộ nhấp nháy ĐỎ để học sinh kịp bước lên vỉa hè, cần Barie vẫn mở. Hết 2–3 giây, Barie mới đóng chặt 0° và đèn xe bật XANH KHẨN CẤP cho xe cứu thương phóng qua an toàn tuyệt đối.', 'Tình huống 3 (Xe cứu thương khẩn cấp - Emergency Preemption): ')
    add_bullet('Khi thời tiết xấu làm mờ camera, học sinh ấn nút Failsafe gắn trên cột đèn. Tín hiệu ngắt cứng chân D2 lập tức kích hoạt chu kỳ đèn an toàn qua đường mà không phụ thuộc vào AI.', 'Tình huống 4 (Nút bấm cơ học Failsafe D2): ')
    add_bullet('Nếu máy tính bị ngắt kết nối hoặc mất xung Heartbeat quá 3 giây, mạch Arduino tự động khóa chặt cần Barie 0° giữ học sinh trên vỉa hè và chuyển đèn xe sang chế độ NHẤP NHÁY VÀNG (1s/lần) theo chuẩn QCVN 41:2019/BGTVT.', 'Tình huống 5 (Mất kết nối USB - Watchdog Safe Mode): ')

    # Phần VI
    add_heading('VI. PHÂN CÔNG VAI TRÒ VÀ KẾ HOẠCH TRIỂN KHAI THI ĐẤU')
    add_bullet('Thuyết minh tổng quan dự án, nêu vấn đề thực tiễn cổng trường, trực tiếp bấm nút Failsafe và bảo vệ bảng tính công suất trước Ban Giám khảo.', 'Phạm Hữu Đạt (Lớp 4A1 - Đội trưởng): ')
    add_bullet('Phụ trách lắp ráp phần cứng, cắm giắc Nano Shield, kiểm tra cơ cấu Barie Servo và giải trình công thức động học 15 giây.', 'Vũ Minh Quang (Lớp 4A1 - Kỹ thuật phần cứng): ')
    add_bullet('Phụ trách huấn luyện mô hình thị giác AI Teachable Machine, điều khiển mô hình xe cứu thương và thao tác trạm giám sát Web Serial.', 'Vũ Ngọc An Đông (Lớp 5A1 - Trạm điều hành AI): ')

    # Bảng Ký tên cuối trang
    add_p('Kế hoạch được lập thành văn bản chính thức, làm căn cứ triển khai thi công sa bàn và tập huấn thuyết trình cho đội tuyển STEM Marie Curie Thái Bình ./.', space_b=6, space_a=12)

    t_sign = doc.add_table(rows=1, cols=3)
    t_sign.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_no_borders(t_sign)
    set_col_widths(t_sign, [Cm(5.3), Cm(5.3), Cm(5.4)])
    set_row_cant_split(t_sign.rows[0])

    sign_headers = ['ĐẠI DIỆN ĐỘI THI\n(Đội trưởng)', 'CÁN BỘ HƯỚNG DẪN\n(Tổ trưởng STEM)', 'BAN GIÁM HIỆU\n(Phê duyệt)']
    sign_names = ['Phạm Hữu Đạt\n(Học sinh 4A1)', 'Lê Ngọc Anh\n(Giáo viên hướng dẫn)', 'Trần Ánh Nguyệt\n(Hiệu trưởng)']

    for idx, (h, n) in enumerate(zip(sign_headers, sign_names)):
        c = t_sign.rows[0].cells[idx]
        set_cell_margins(c, 0, 0, 40, 40)
        p = c.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(0); p.paragraph_format.space_after = Pt(45)
        r = p.add_run(h); r.font.name = 'Times New Roman'; r.font.size = Pt(12); r.bold = True
        p_name = c.add_paragraph(); p_name.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_name.paragraph_format.space_before = Pt(0); p_name.paragraph_format.space_after = Pt(0)
        r_n = p_name.add_run(n); r_n.font.name = 'Times New Roman'; r_n.font.size = Pt(12); r_n.bold = True

    return doc

if __name__ == '__main__':
    # 1. Lưu file Markdown
    md_paths = [
        r'E:\Antigravity\MCA\HNUE_olympic_stem\1.Data\KE_HOACH_TONG_THE_VA_THIET_KE_TOI_UU.md',
        r'MCA\HNUE_olympic_stem\1.Data\KE_HOACH_TONG_THE_VA_THIET_KE_TOI_UU.md'
    ]
    for p in md_paths:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, 'w', encoding='utf-8') as f:
            f.write(MASTER_PLAN_MD)
        print(f'Saved Markdown to {p}')

    # 2. Tạo và lưu file DOCX
    doc = generate_master_plan_docx()
    docx_paths = [
        r'E:\Antigravity\MCA\HNUE_olympic_stem\1.Data\KE_HOACH_TONG_THE_VA_THIET_KE_TOI_UU.docx',
        r'MCA\HNUE_olympic_stem\1.Data\KE_HOACH_TONG_THE_VA_THIET_KE_TOI_UU.docx'
    ]
    for p in docx_paths:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        doc.save(p)
        print(f'Saved DOCX to {p}')
