/*
 =========================================================================================
   DỰ ÁN STEM: HỆ THỐNG ĐÈN GIAO THÔNG HỌC ĐƯỜNG THÔNG MINH MARIE CURIE
   CUỘC THI: HNUE OLYMPIC STEM 2026 - BẢNG TIỂU HỌC (KHỐI 4 - 5)
   CHỦ ĐỀ: "FUTURE INNOVATORS - NHỮNG NHÀ KIẾN TẠO TƯƠNG LAI"
   ---------------------------------------------------------------------------------------
   MÔ-ĐUN: FIRMWARE LAI ĐA TẦNG (HYBRID C++ & PICTOBLOX CONTROLLER) - BẢN V2.3 FINAL
   Vi điều khiển: Arduino Nano v3.0 (ATmega328P) + Nano Sensor Shield v3.0
   Cán bộ hướng dẫn: Thầy/Cô hướng dẫn (Phụ trách STEM) - Marie Curie Academy
   Tác giả học sinh: Phạm Hữu Đạt (4A1), Vũ Minh Quang (4A1), Vũ Ngọc An Đông (5A1)
 =========================================================================================
*/

#include <Arduino.h>
#include <Servo.h>

// 1. ĐỊNH NGHĨA CHÂN NGOẠI VI (CHUẨN SHIELD V3.0 GVS)
const int PIN_BTN_FAILSAFE = 2;   // Ngắt ngoài INT0 (Input Pullup làm nút cứu hộ vỉa hè)
const int PIN_PED_RED      = 6;   // Đèn LED Đi bộ ĐỎ
const int PIN_PED_GREEN    = 7;   // Đèn LED Đi bộ XANH
const int PIN_BUZZER       = 8;   // Còi chip Active Buzzer 5V
const int PIN_SERVO        = 9;   // Động cơ Micro Servo SG90 Barie
const int PIN_CAR_GREEN    = 10;  // Đèn LED Ô tô XANH
const int PIN_CAR_YELLOW   = 11;  // Đèn LED Ô tô VÀNG
const int PIN_CAR_RED      = 12;  // Đèn LED Ô tô ĐỎ

// 2. GÓC ĐẶT VÀ ĐIỀU KHIỂN QUÉT MƯỢT SERVO BARIE (NON-BLOCKING SOFT-RAMP)
const int BARIE_CLOSED_ANGLE = 0;   // 0 độ: Đóng chắn ngang vỉa hè ngăn học sinh tràn xuống đường
const int BARIE_OPEN_ANGLE   = 90;  // 90 độ: Mở dựng đứng cho phép học sinh an toàn qua đường

int currentBariePos  = BARIE_CLOSED_ANGLE;
int targetBarieAngle = BARIE_CLOSED_ANGLE;
unsigned long lastServoStepTime = 0;

// 3. ĐỊNH NGHĨA 6 TRẠNG THÁI MÁY FSM
enum SystemState {
  STATE_NORMAL_IDLE,       // TH1: Đường vắng - Ô tô Xanh, Đi bộ Đỏ, Barie Đóng (0°)
  STATE_CAR_YELLOW_TRANS,  // Chuyển tiếp an toàn: Đèn xe Vàng 3s giảm tốc trước khi mở Barie
  STATE_PEDESTRIAN_CROSS,  // TH2 & TH4: Học sinh qua đường 15s - Ô tô Đỏ, Đi bộ Xanh, Barie Mở (90°)
  STATE_EMERGENCY_CLEAR,   // Dọn đường khẩn cấp 2.5s: Giữ mở Barie cho học sinh rút lên lề, còi hú dồn dập
  STATE_AMBULANCE_PASS,    // TH3: Xe cứu thương ưu tiên 8s - Ô tô Xanh, Đi bộ Đỏ, Barie Đóng (0°), Còi hú
  STATE_WATCHDOG_SAFE      // TH5: Tự hành nháy vàng 1Hz khi mất kết nối USB > 5s
};

// 4. BIẾN TOÀN CỤC & ĐIỀU KHIỂN THỜI GIAN THỰC (NON-BLOCKING)
SystemState currentState = STATE_NORMAL_IDLE;
Servo barieServo;

volatile bool failsafePressed = false;
volatile unsigned long lastInterruptTime = 0;
const unsigned long DEBOUNCE_DELAY_MS = 300;

unsigned long stateStartTime = 0;
unsigned long lastHeartbeatTime = 0;
unsigned long lastToggleTime = 0;
bool blinkPulseState = false;

// 5. NGUYÊN MẪU HÀM
void handleFailsafeInterrupt();
void setTrafficLights(bool carG, bool carY, bool carR, bool pedG, bool pedR, int servoAngle);
void enterState(SystemState newState);
void processSerialCommands();
void processFailsafeTrigger();
void updateFSM();
void updateServoSmooth();

void setup() {
  pinMode(PIN_CAR_GREEN, OUTPUT);
  pinMode(PIN_CAR_YELLOW, OUTPUT);
  pinMode(PIN_CAR_RED, OUTPUT);
  pinMode(PIN_PED_GREEN, OUTPUT);
  pinMode(PIN_PED_RED, OUTPUT);
  pinMode(PIN_BUZZER, OUTPUT);

  pinMode(PIN_BTN_FAILSAFE, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(PIN_BTN_FAILSAFE), handleFailsafeInterrupt, FALLING);

  // Ghi góc 0° trước khi attach() để triệt tiêu xung giật cần Barie lúc cấp nguồn
  barieServo.write(BARIE_CLOSED_ANGLE);
  barieServo.attach(PIN_SERVO);
  currentBariePos  = BARIE_CLOSED_ANGLE;
  targetBarieAngle = BARIE_CLOSED_ANGLE;

  Serial.begin(9600);

  enterState(STATE_NORMAL_IDLE);
  lastHeartbeatTime = millis();

  Serial.println(F("{\"status\":\"ONLINE\",\"mode\":\"HYBRID_DUAL_TIER\",\"firmware\":\"v2.3_FINAL\"}"));
}

// =========================================================================================
// HÀM NGẮT CỨNG INT0: CHỐNG DỘI PHÍM BẰNG THỜI GIAN MILLIS()
// =========================================================================================
void handleFailsafeInterrupt() {
  unsigned long interruptTime = millis();
  if ((lastInterruptTime == 0 || (interruptTime - lastInterruptTime > DEBOUNCE_DELAY_MS))
      && (digitalRead(PIN_BTN_FAILSAFE) == LOW)) {
    failsafePressed = true;
    lastInterruptTime = interruptTime;
  }
}

// =========================================================================================
// VÒNG LẶP CHÍNH (LOOP): VẬN HÀNH THỜI GIAN THỰC PHI CHẶN (NON-BLOCKING)
// =========================================================================================
void loop() {
  // 1. Quét chuyển động Servo mượt phi chặn (chống giật dòng và chống rung cần)
  updateServoSmooth();

  // 2. Xử lý sự kiện ngắt nút bấm khẩn cấp Failsafe D2
  if (failsafePressed) {
    failsafePressed = false;
    processFailsafeTrigger();
  }

  // 3. Đọc và xử lý lệnh Serial từ PictoBlox qua cổng USB
  processSerialCommands();

  // 4. Cập nhật máy trạng thái FSM
  updateFSM();

  // 5. Cơ chế Watchdog: Nếu mất Heartbeat từ máy tính > 5000ms khi đang ở trạng thái rảnh
  if (currentState == STATE_NORMAL_IDLE && (millis() - lastHeartbeatTime > 5000)) {
    enterState(STATE_WATCHDOG_SAFE);
  }
}

// =========================================================================================
// ĐIỀU KHIỂN CHUYỂN ĐỘNG SERVO MƯỢT TỪNG BƯỚC 3 ĐỘ MỖI 20MS (NON-BLOCKING SOFT-RAMP)
// =========================================================================================
void updateServoSmooth() {
  if (currentBariePos == targetBarieAngle) return;
  if (millis() - lastServoStepTime >= 20) {
    lastServoStepTime = millis();
    if (currentBariePos < targetBarieAngle) {
      currentBariePos = min(currentBariePos + 3, targetBarieAngle);
    } else {
      currentBariePos = max(currentBariePos - 3, targetBarieAngle);
    }
    barieServo.write(currentBariePos);
  }
}

// =========================================================================================
// XỬ LÝ NÚT BẤM CƠ HỌC KHẨN CẤP FAILSAFE (D2)
// =========================================================================================
void processFailsafeTrigger() {
  // Nếu đang trong pha xe cứu thương, ưu tiên cứu thương tuyệt đối, không nhận nút bấm
  if (currentState == STATE_AMBULANCE_PASS || currentState == STATE_EMERGENCY_CLEAR) {
    Serial.println(F("{\"event\":\"FAILSAFE_IGNORED\",\"reason\":\"AMBULANCE_ACTIVE\"}"));
    return;
  }

  // Bấm nút khẩn cấp: Chuyển đèn vàng 3s cảnh báo dừng xe rồi mở lối an toàn cho học sinh
  if (currentState == STATE_NORMAL_IDLE || currentState == STATE_WATCHDOG_SAFE) {
    Serial.println(F("{\"event\":\"FAILSAFE_TRIGGERED\",\"action\":\"CAR_YELLOW_WARNING\"}"));
    enterState(STATE_CAR_YELLOW_TRANS);
  }
}

// =========================================================================================
// XỬ LÝ TRUYỀN THÔNG SERIAL TỪ PICTOBLOX: TÁCH BIỆT HEARTBEAT 'H' VÀ ƯU TIÊN TUYỆT ĐỐI
// =========================================================================================
void processSerialCommands() {
  char latestCmd = '\0';
  bool hasEmergencyCmd = false;

  while (Serial.available() > 0) {
    char c = Serial.read();
    if (c == 'H') {
      lastHeartbeatTime = millis(); // Nuôi nhịp sống còn, KHÔNG ghi đè lệnh điều khiển
    } else if (c == '0' || c == '1' || c == '2') {
      lastHeartbeatTime = millis();
      if (c == '1') {
        hasEmergencyCmd = true;     // Đánh dấu ưu tiên tối cao khi có mã cứu thương '1'
      }
      latestCmd = c;
    }
  }

  // Ưu tiên cứu thương tuyệt đối nếu xuất hiện ký tự '1' trong bộ đệm
  if (hasEmergencyCmd) {
    latestCmd = '1';
  }

  if (latestCmd == '\0') return;

  // Lệnh '1': Xe cứu thương khẩn cấp
  if (latestCmd == '1') {
    // Chỉ kích hoạt 2.5s dọn đường khi Barie thực sự đang mở 90° (học sinh đang qua đường)
    if (currentState == STATE_PEDESTRIAN_CROSS) {
      enterState(STATE_EMERGENCY_CLEAR);
    } else if (currentState != STATE_AMBULANCE_PASS && currentState != STATE_EMERGENCY_CLEAR) {
      // Nếu đang đèn Vàng 3s hoặc đường vắng (Barie đang đóng 0°), bật Xanh cứu thương ngay lập tức
      enterState(STATE_AMBULANCE_PASS);
    } else if (currentState == STATE_AMBULANCE_PASS) {
      stateStartTime = millis(); // Gia hạn nếu xe cứu thương vẫn còn trong khung hình
    }
  }
  // Lệnh '2': Học sinh xin qua đường
  else if (latestCmd == '2') {
    if (currentState == STATE_NORMAL_IDLE || currentState == STATE_WATCHDOG_SAFE) {
      enterState(STATE_CAR_YELLOW_TRANS);
    }
  }
  // Lệnh '0': Đường vắng thông suốt
  else if (latestCmd == '0') {
    if (currentState == STATE_WATCHDOG_SAFE) {
      enterState(STATE_NORMAL_IDLE);
    } else if (currentState == STATE_AMBULANCE_PASS && (millis() - stateStartTime >= 3000)) {
      enterState(STATE_NORMAL_IDLE);
    }
  }
}

// =========================================================================================
// CẬP NHẬT TRẠNG THÁI FSM THEO THỜI GIAN THỰC (NON-BLOCKING)
// =========================================================================================
void updateFSM() {
  unsigned long now = millis();
  unsigned long elapsed = now - stateStartTime;

  switch (currentState) {
    case STATE_NORMAL_IDLE:
      break;

    case STATE_CAR_YELLOW_TRANS:
      if (elapsed >= 3000) {
        enterState(STATE_PEDESTRIAN_CROSS);
      }
      break;

    case STATE_PEDESTRIAN_CROSS:
      // 12 giây đầu: Còi phát nhịp bíp chậm (500ms) báo lối đi an toàn
      if (elapsed < 12000) {
        if (now - lastToggleTime >= 500) {
          lastToggleTime = now;
          blinkPulseState = !blinkPulseState;
          digitalWrite(PIN_BUZZER, blinkPulseState ? HIGH : LOW);
        }
      } 
      // 3 giây cuối: Còi tăng tốc nhịp bíp nhanh (200ms) giục học sinh bước lên lề
      else if (elapsed < 15000) {
        if (now - lastToggleTime >= 200) {
          lastToggleTime = now;
          blinkPulseState = !blinkPulseState;
          digitalWrite(PIN_BUZZER, blinkPulseState ? HIGH : LOW);
        }
      } else {
        digitalWrite(PIN_BUZZER, LOW);
        enterState(STATE_NORMAL_IDLE);
      }
      break;

    case STATE_EMERGENCY_CLEAR:
      // Nháy còi & đèn đi bộ đỏ 150ms trong 2.5s để học sinh rút hết lên vỉa hè trước khi đóng Barie
      if (now - lastToggleTime >= 150) {
        lastToggleTime = now;
        blinkPulseState = !blinkPulseState;
        digitalWrite(PIN_BUZZER, blinkPulseState ? HIGH : LOW);
        digitalWrite(PIN_PED_RED, blinkPulseState ? HIGH : LOW);
      }
      if (elapsed >= 2500) {
        enterState(STATE_AMBULANCE_PASS); // Đóng Barie 0° và bật đèn Xanh cho xe cứu thương
      }
      break;

    case STATE_AMBULANCE_PASS:
      digitalWrite(PIN_BUZZER, HIGH); // Hú còi liên tục cảnh báo xe ưu tiên
      if (elapsed >= 8000) {
        enterState(STATE_NORMAL_IDLE);
      }
      break;

    case STATE_WATCHDOG_SAFE:
      // Tự hành: Nhấp nháy đèn vàng ô tô tần số 1Hz (500ms ON / 500ms OFF) theo QCVN 41:2019
      if (now - lastToggleTime >= 500) {
        lastToggleTime = now;
        blinkPulseState = !blinkPulseState;
        digitalWrite(PIN_CAR_YELLOW, blinkPulseState ? HIGH : LOW);
      }
      break;
  }
}

// =========================================================================================
// THIẾT LẬP ĐỒNG BỘ ĐÈN TÍN HIỆU & GÓC BARIE KHI CHUYỂN PHA
// =========================================================================================
void enterState(SystemState newState) {
  // Nếu đang ở pha học sinh qua đường mà chuyển sang dọn đường khẩn cấp, giữ nguyên góc Barie hiện tại (90°)
  int currentBarieAngle = (currentState == STATE_PEDESTRIAN_CROSS) ? BARIE_OPEN_ANGLE : BARIE_CLOSED_ANGLE;

  currentState = newState;
  stateStartTime = millis();
  lastToggleTime = millis();
  blinkPulseState = false;
  digitalWrite(PIN_BUZZER, LOW);

  switch (currentState) {
    case STATE_NORMAL_IDLE:
      setTrafficLights(HIGH, LOW, LOW, LOW, HIGH, BARIE_CLOSED_ANGLE);
      Serial.println(F("{\"state\":\"IDLE_CAR_GREEN\",\"ped\":\"RED\",\"barie\":\"CLOSED\"}"));
      break;

    case STATE_CAR_YELLOW_TRANS:
      setTrafficLights(LOW, HIGH, LOW, LOW, HIGH, BARIE_CLOSED_ANGLE);
      Serial.println(F("{\"state\":\"CAR_YELLOW_WARNING\",\"ped\":\"RED\",\"barie\":\"CLOSED\"}"));
      break;

    case STATE_PEDESTRIAN_CROSS:
      setTrafficLights(LOW, LOW, HIGH, HIGH, LOW, BARIE_OPEN_ANGLE);
      Serial.println(F("{\"state\":\"PEDESTRIAN_CROSSING\",\"car\":\"RED\",\"barie\":\"OPEN\"}"));
      break;

    case STATE_EMERGENCY_CLEAR:
      // Giữ đèn xe ĐỎ và giữ mở Barie trong 2.5s để học sinh thoát khỏi lòng đường an toàn
      setTrafficLights(LOW, LOW, HIGH, LOW, HIGH, currentBarieAngle);
      Serial.println(F("{\"state\":\"EMERGENCY_CLEARANCE\",\"ped\":\"CLEARING\",\"barie\":\"HOLD_FOR_EXIT\"}"));
      break;

    case STATE_AMBULANCE_PASS:
      // Hết 2.5s dọn đường: Hạ Barie về 0° và mở làn XANH cho xe cứu thương phóng qua
      setTrafficLights(HIGH, LOW, LOW, LOW, HIGH, BARIE_CLOSED_ANGLE);
      Serial.println(F("{\"state\":\"AMBULANCE_PRIORITY\",\"car\":\"GREEN\",\"barie\":\"CLOSED\"}"));
      break;

    case STATE_WATCHDOG_SAFE:
      setTrafficLights(LOW, LOW, LOW, LOW, HIGH, BARIE_CLOSED_ANGLE);
      Serial.println(F("{\"state\":\"WATCHDOG_STANDALONE\",\"car\":\"FLASH_YELLOW\",\"barie\":\"CLOSED\"}"));
      break;
  }
}

void setTrafficLights(bool carG, bool carY, bool carR, bool pedG, bool pedR, int servoAngle) {
  digitalWrite(PIN_CAR_GREEN, carG);
  digitalWrite(PIN_CAR_YELLOW, carY);
  digitalWrite(PIN_CAR_RED, carR);
  digitalWrite(PIN_PED_GREEN, pedG);
  digitalWrite(PIN_PED_RED, pedR);
  targetBarieAngle = servoAngle; // Cập nhật góc đích để updateServoSmooth() quét mượt mà
}
