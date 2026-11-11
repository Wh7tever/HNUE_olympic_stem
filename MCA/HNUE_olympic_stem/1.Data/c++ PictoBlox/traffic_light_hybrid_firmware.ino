/*
 =========================================================================================
   DỰ ÁN STEM: HỆ THỐNG ĐÈN GIAO THÔNG HỌC ĐƯỜNG THÔNG MINH MARIE CURIE
   CUỘC THI: HNUE OLYMPIC STEM 2026 - BẢNG TIỂU HỌC
   ---------------------------------------------------------------------------------------
   MÔ-ĐUN: FIRMWARE LAI ĐA TẦNG (HYBRID C++ & PICTOBLOX SERIAL CONTROLLER)
   Tác giả: Nhóm học sinh STEM Trường Tiểu học, THCS và THPT Marie Curie Thái Bình
   Vi điều khiển: Arduino Nano v3.0 (ATmega328P) + Nano Sensor Shield v3.0
   ---------------------------------------------------------------------------------------
   SƠ ĐỒ PHÂN BỔ CHÂN NỐI DÂY CHUẨN SHIELD V3.0 (GVS 3-PIN):
   - Chân D2:  Nút bấm cơ học Failsafe khẩn cấp (Ngắt cứng INT0, Input Pullup)
   - Chân D6:  Đèn LED Người đi bộ ĐỎ (Báo học sinh dừng chờ trên vỉa hè)
   - Chân D7:  Đèn LED Người đi bộ XANH (Báo học sinh sang đường an toàn)
   - Chân D8:  Còi chip Active Buzzer 5V (Âm thanh cảnh báo / dẫn đường)
   - Chân D9:  Động cơ Servo SG90 điều khiển Barie người đi bộ (PWM)
   - Chân D10: Đèn LED Ô tô XANH (Dòng xe cơ giới lưu thông)
   - Chân D11: Đèn LED Ô tô VÀNG (Cảnh báo giảm tốc 3 giây)
   - Chân D12: Đèn LED Ô tô ĐỎ (Dừng phương tiện trước vạch ngựa vằn)
   - 5V / GND: 02 Tụ bù hóa nhôm 470uF / 16V chống sụt áp tức thời cho Servo
 =========================================================================================
*/

#include <Servo.h>

// 1. ĐỊNH NGHĨA CHÂN NGOẠI VI
const int PIN_BTN_FAILSAFE = 2;   // Ngắt ngoài INT0
const int PIN_PED_RED      = 6;   // LED Đi bộ Đỏ
const int PIN_PED_GREEN    = 7;   // LED Đi bộ Xanh
const int PIN_BUZZER       = 8;   // Còi Buzzer 5V
const int PIN_SERVO        = 9;   // Servo SG90 Barie
const int PIN_CAR_GREEN    = 10;  // LED Ô tô Xanh
const int PIN_CAR_YELLOW   = 11;  // LED Ô tô Vàng
const int PIN_CAR_RED      = 12;  // LED Ô tô Đỏ

// 2. GÓC ĐẶT SERVO BARIE (CHUẨN THỰC TẾ)
const int BARIE_CLOSED_ANGLE = 0;   // 0 độ: Nằm ngang chắn lối người đi bộ trên vỉa hè
const int BARIE_OPEN_ANGLE   = 90;  // 90 độ: Dựng đứng mở lối cho học sinh qua đường

// 3. ĐỊNH NGHĨA 5 TRẠNG THÁI MÁY FSM (FINITE STATE MACHINE)
enum SystemState {
  STATE_NORMAL_IDLE,       // TH1: Đường vắng - Xe chạy Xanh liên tục, Đi bộ Đỏ, Barie Đóng
  STATE_CAR_YELLOW_TRANS,  // Chuyển tiếp: Đèn xe Vàng 3 giây cảnh báo dừng xe
  STATE_PEDESTRIAN_CROSS,  // TH2: Học sinh qua đường - Xe Đỏ, Đi bộ Xanh, Barie Mở 90° (15s)
  STATE_EMERGENCY_CLEAR,   // Chuyển tiếp dọn đường khẩn cấp: 2.5s khi có xe cứu thương
  STATE_AMBULANCE_PASS,    // TH3: Xe cứu thương ưu tiên - Xe Xanh, Đi bộ Đỏ, Barie Đóng, Còi hú
  STATE_WATCHDOG_SAFE      // TH5: An toàn tự hành khi mất kết nối USB máy tính
};

// 4. BIẾN TOÀN CỤC & ĐIỀU KHIỂN THỜI GIAN (MILLIS KHÔNG BLOCKING)
SystemState currentState = STATE_NORMAL_IDLE;
Servo barieServo;

volatile bool failsafePressed = false; // Cờ báo ngắt cứng Failsafe
unsigned long stateStartTime = 0;
unsigned long lastHeartbeatTime = 0;
unsigned long lastBuzzerToggleTime = 0;
bool buzzerState = false;

// 5. NGUYÊN MẪU HÀM
void IRAM_ATTR handleFailsafeInterrupt();
void setTrafficLights(bool carG, bool carY, bool carR, bool pedG, bool pedR, int servoAngle);
void enterState(SystemState newState);
void processSerialCommands();
void updateFSM();

// =========================================================================================
// HÀM KHỞI TẠO (SETUP)
// =========================================================================================
void setup() {
  // Cấu hình chân Output
  pinMode(PIN_CAR_GREEN, OUTPUT);
  pinMode(PIN_CAR_YELLOW, OUTPUT);
  pinMode(PIN_CAR_RED, OUTPUT);
  pinMode(PIN_PED_GREEN, OUTPUT);
  pinMode(PIN_PED_RED, OUTPUT);
  pinMode(PIN_BUZZER, OUTPUT);

  // Cấu hình ngắt phần cứng Failsafe INT0
  pinMode(PIN_BTN_FAILSAFE, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(PIN_BTN_FAILSAFE), handleFailsafeInterrupt, FALLING);

  // Khởi tạo Servo Barie
  barieServo.attach(PIN_SERVO);
  barieServo.write(BARIE_CLOSED_ANGLE);

  // Khởi tạo giao tiếp Serial với máy tính (PictoBlox / Laptop Web Serial)
  Serial.begin(9600);
  while (!Serial) { ; } // Chờ kết nối Serial nếu cần

  // Chuyển sang trạng thái ban đầu: Đường vắng
  enterState(STATE_NORMAL_IDLE);
  lastHeartbeatTime = millis();

  Serial.println(F("{\"status\":\"ONLINE\",\"mode\":\"HYBRID_DUAL_TIER\",\"firmware\":\"v2.0\"}"));
}

// =========================================================================================
// HÀM NGẮT CỨNG PHẦN CỨNG INT0 (CHẠY NGAY TRONG < 1 MICRO-GIÂY KHI BẤM NÚT D2)
// =========================================================================================
void handleFailsafeInterrupt() {
  static unsigned long lastInterruptTime = 0;
  unsigned long interruptTime = millis();
  // Chống rung phím cơ học 200ms (Hardware Debounce)
  if (interruptTime - lastInterruptTime > 200) {
    failsafePressed = true;
  }
  lastInterruptTime = interruptTime;
}

// =========================================================================================
// VÒNG LẶP CHÍNH (LOOP) - NON-BLOCKING DETERMINISTIC
// =========================================================================================
void loop() {
  // 1. Xử lý cờ ngắt cứng Failsafe
  if (failsafePressed) {
    failsafePressed = false;
    Serial.println(F("{\"event\":\"FAILSAFE_TRIGGERED\",\"source\":\"INT0_PIN_D2\"}"));
    if (currentState == STATE_NORMAL_IDLE || currentState == STATE_WATCHDOG_SAFE) {
      enterState(STATE_CAR_YELLOW_TRANS);
    }
  }

  // 2. Tiếp nhận và bóc tách gói tin Serial từ PictoBlox / AI Web
  processSerialCommands();

  // 3. Cập nhật máy trạng thái FSM theo thời gian
  updateFSM();

  // 4. Bảo vệ Watchdog: Tự động chuyển chế độ độc lập an toàn nếu mất tín hiệu USB > 5s
  if (millis() - lastHeartbeatTime > 5000 && currentState != STATE_WATCHDOG_SAFE) {
    enterState(STATE_WATCHDOG_SAFE);
    Serial.println(F("{\"warning\":\"WATCHDOG_TIMEOUT\",\"action\":\"AUTONOMOUS_SAFE_MODE\"}"));
  }
}

// =========================================================================================
// XỬ LÝ LỆNH SERIAL TỪ PICTOBLOX (LỆNH KÝ TỰ HOẶC BYTE)
// =========================================================================================
void processSerialCommands() {
  while (Serial.available() > 0) {
    char cmd = Serial.read();
    lastHeartbeatTime = millis(); // Nuôi Watchdog nhịp sống còn

    // Ký tự '1' hoặc byte 0x51: PictoBlox gửi khi AI thấy Học sinh qua đường
    if (cmd == '1' || cmd == 0x51) {
      if (currentState == STATE_NORMAL_IDLE) {
        enterState(STATE_CAR_YELLOW_TRANS);
      }
    }
    // Ký tự '2' hoặc byte 0x52: PictoBlox gửi khi AI thấy Xe Cứu Thương Ưu Tiên
    else if (cmd == '2' || cmd == 0x52) {
      if (currentState == STATE_PEDESTRIAN_CROSS) {
        // Nếu học sinh đang đi dở, chuyển qua dọn đường an toàn 2.5s trước khi mở đường xe
        enterState(STATE_EMERGENCY_CLEAR);
      } else if (currentState != STATE_AMBULANCE_PASS) {
        enterState(STATE_AMBULANCE_PASS);
      }
    }
    // Ký tự '0' hoặc byte 0x50: PictoBlox gửi khi Đường vắng (Normal)
    else if (cmd == '0' || cmd == 0x50) {
      if (currentState == STATE_AMBULANCE_PASS || currentState == STATE_WATCHDOG_SAFE) {
        enterState(STATE_NORMAL_IDLE);
      }
    }
    // Ký tự '4' hoặc byte 0x54: Kích hoạt nút bấm khẩn cấp qua phần mềm
    else if (cmd == '4' || cmd == 0x54) {
      if (currentState == STATE_NORMAL_IDLE || currentState == STATE_WATCHDOG_SAFE) {
        enterState(STATE_CAR_YELLOW_TRANS);
      }
    }
    // Ký tự 'H' hoặc byte 0x55: Heartbeat nuôi nhịp sống
    else if (cmd == 'H' || cmd == 0x55) {
      // Đã cập nhật lastHeartbeatTime ở trên
    }
  }
}

// =========================================================================================
// CẬP NHẬT TRẠNG THÁI FSM THEO THỜI GIAN
// =========================================================================================
void updateFSM() {
  unsigned long elapsed = millis() - stateStartTime;

  switch (currentState) {
    case STATE_NORMAL_IDLE:
      // Giữ xe Xanh liên tục, Đi bộ Đỏ, Barie Đóng
      break;

    case STATE_CAR_YELLOW_TRANS:
      // Đèn vàng cảnh báo 3 giây (3000ms)
      if (elapsed >= 3000) {
        enterState(STATE_PEDESTRIAN_CROSS);
      }
      break;

    case STATE_PEDESTRIAN_CROSS:
      // Chu kỳ đi bộ 15 giây (15000ms):
      // - 12 giây đầu: Còi bíp nhịp thưa (500ms)
      // - 3 giây cuối: Còi bíp nhịp dồn dập (200ms) giục học sinh bước nhanh
      if (elapsed < 12000) {
        if (millis() - lastBuzzerToggleTime >= 500) {
          lastBuzzerToggleTime = millis();
          buzzerState = !buzzerState;
          digitalWrite(PIN_BUZZER, buzzerState ? HIGH : LOW);
        }
      } else if (elapsed < 15000) {
        if (millis() - lastBuzzerToggleTime >= 200) {
          lastBuzzerToggleTime = millis();
          buzzerState = !buzzerState;
          digitalWrite(PIN_BUZZER, buzzerState ? HIGH : LOW);
        }
      } else {
        // Hết 15 giây đi bộ -> Trở về bình thường
        digitalWrite(PIN_BUZZER, LOW);
        enterState(STATE_NORMAL_IDLE);
      }
      break;

    case STATE_EMERGENCY_CLEAR:
      // Còi hú dồn dập, nháy đèn đỏ đi bộ nhắc dọn đường trong 2.5 giây (2500ms)
      if (millis() - lastBuzzerToggleTime >= 150) {
        lastBuzzerToggleTime = millis();
        buzzerState = !buzzerState;
        digitalWrite(PIN_BUZZER, buzzerState ? HIGH : LOW);
        digitalWrite(PIN_PED_RED, buzzerState ? HIGH : LOW);
      }
      if (elapsed >= 2500) {
        enterState(STATE_AMBULANCE_PASS);
      }
      break;

    case STATE_AMBULANCE_PASS:
      // Còi kêu liên tục cảnh báo xe cứu thương chạy qua
      digitalWrite(PIN_BUZZER, HIGH);
      // Nếu sau 8 giây không có lệnh giữ tiếp thì hoàn trả giao thông
      if (elapsed >= 8000) {
        enterState(STATE_NORMAL_IDLE);
      }
      break;

    case STATE_WATCHDOG_SAFE:
      // Mất tín hiệu máy tính: Nhấp nháy đèn vàng ô tô tần số 1Hz để đảm bảo an toàn
      if (millis() - lastBuzzerToggleTime >= 500) {
        lastBuzzerToggleTime = millis();
        buzzerState = !buzzerState;
        digitalWrite(PIN_CAR_YELLOW, buzzerState ? HIGH : LOW);
      }
      break;
  }
}

// =========================================================================================
// CHUYỂN TRẠNG THÁI & ĐIỀU KHIỂN CHÂN PHẦN CỨNG ĐỒNG BỘ
// =========================================================================================
void enterState(SystemState newState) {
  currentState = newState;
  stateStartTime = millis();
  digitalWrite(PIN_BUZZER, LOW); // Tắt còi trước khi đổi trạng thái

  switch (currentState) {
    case STATE_NORMAL_IDLE:
      // Xe Xanh (D10=1, D11=0, D12=0), Đi bộ Đỏ (D6=1, D7=0), Barie Đóng (0 độ)
      setTrafficLights(HIGH, LOW, LOW, LOW, HIGH, BARIE_CLOSED_ANGLE);
      Serial.println(F("{\"state\":\"IDLE_CAR_GREEN\",\"ped\":\"RED\",\"barie\":\"CLOSED\"}"));
      break;

    case STATE_CAR_YELLOW_TRANS:
      // Xe Vàng (D10=0, D11=1, D12=0), Đi bộ Đỏ (D6=1, D7=0), Barie Đóng (0 độ)
      setTrafficLights(LOW, HIGH, LOW, LOW, HIGH, BARIE_CLOSED_ANGLE);
      Serial.println(F("{\"state\":\"CAR_YELLOW_WARNING\",\"ped\":\"RED\",\"barie\":\"CLOSED\"}"));
      break;

    case STATE_PEDESTRIAN_CROSS:
      // Xe Đỏ (D10=0, D11=0, D12=1), Đi bộ Xanh (D6=0, D7=1), Barie Mở (90 độ)
      setTrafficLights(LOW, LOW, HIGH, HIGH, LOW, BARIE_OPEN_ANGLE);
      Serial.println(F("{\"state\":\"PEDESTRIAN_CROSSING\",\"car\":\"RED\",\"barie\":\"OPEN\"}"));
      break;

    case STATE_EMERGENCY_CLEAR:
      // Xe Đỏ dừng tạm, Barie hạ nhanh về 0 độ chắn lối vào
      setTrafficLights(LOW, LOW, HIGH, LOW, HIGH, BARIE_CLOSED_ANGLE);
      Serial.println(F("{\"state\":\"EMERGENCY_CLEARANCE\",\"ped\":\"CLEARING\",\"barie\":\"CLOSING\"}"));
      break;

    case STATE_AMBULANCE_PASS:
      // Xe Xanh ưu tiên (D10=1, D11=0, D12=0), Đi bộ Đỏ (D6=1, D7=0), Barie Đóng (0 độ)
      setTrafficLights(HIGH, LOW, LOW, LOW, HIGH, BARIE_CLOSED_ANGLE);
      Serial.println(F("{\"state\":\"AMBULANCE_PRIORITY\",\"car\":\"GREEN\",\"barie\":\"CLOSED\"}"));
      break;

    case STATE_WATCHDOG_SAFE:
      // Nháy đèn Vàng an toàn, Đi bộ Đỏ, Barie Đóng
      setTrafficLights(LOW, LOW, LOW, LOW, HIGH, BARIE_CLOSED_ANGLE);
      Serial.println(F("{\"state\":\"WATCHDOG_STANDALONE\",\"car\":\"FLASH_YELLOW\",\"barie\":\"CLOSED\"}"));
      break;
  }
}

// =========================================================================================
// HÀM GHI ĐỒNG LOẠT TRẠNG THÁI CÁC CHÂN TÍN HIỆU
// =========================================================================================
void setTrafficLights(bool carG, bool carY, bool carR, bool pedG, bool pedR, int servoAngle) {
  digitalWrite(PIN_CAR_GREEN, carG);
  digitalWrite(PIN_CAR_YELLOW, carY);
  digitalWrite(PIN_CAR_RED, carR);
  digitalWrite(PIN_PED_GREEN, pedG);
  digitalWrite(PIN_PED_RED, pedR);
  barieServo.write(servoAngle);
}
