/*
 * ==============================================================================
 * DỰ ÁN: HỆ THỐNG ĐÈN GIAO THÔNG HỌC ĐƯỜNG THÔNG MINH AI - MARIE CURIE ACADEMY
 * CUỘC THI: HNUE OLYMPIC STEM 2026 - BẢNG TIỂU HỌC
 * ------------------------------------------------------------------------------
 * MẠCH ĐIỀU KHIỂN: Arduino Nano v3.0 (ATmega328P) + Nano Expansion Shield v3.0
 * TÁC GIẢ: Đội tuyển STEM MCA (Phạm Hữu Đạt, Vũ Minh Quang, Vũ Ngọc An Đông)
 * CÁN BỘ HƯỚNG DẪN KỸ THUẬT: Thầy Lê Ngọc Anh (Tổ trưởng STEM)
 * ==============================================================================
 * SƠ ĐỒ PHÂN BỔ CHÂN NỐI DÂY CHUẨN TRÊN NANO SHIELD V3.0 (PINOUT MAPPING):
 * - D2 : Nút bấm cơ học Failsafe (Module Tactile 3-pin, ngắt cứng INT0)
 * - D6 : Đèn LED Đi bộ ĐỎ (Pedestrian Red LED)
 * - D7 : Đèn LED Đi bộ XANH (Pedestrian Green LED)
 * - D8 : Còi chip cảnh báo âm thanh (Active Buzzer mini 5V)
 * - D9 : Động cơ Servo mini SG90 điều khiển cần Barie (PWM)
 * - D10: Đèn LED Xe XANH (Car Green LED)
 * - D11: Đèn LED Xe VÀNG (Car Yellow LED)
 * - D12: Đèn LED Xe ĐỎ (Car Red LED)
 * ==============================================================================
 */

#include <Servo.h>

// Định nghĩa các chân điều khiển trên Nano Shield
const int PIN_BTN_FAILSAFE = 2; // Chân ngắt INT0
const int PIN_PED_RED      = 6;
const int PIN_PED_GREEN    = 7;
const int PIN_BUZZER       = 8;
const int PIN_SERVO        = 9;
const int PIN_CAR_GREEN    = 10;
const int PIN_CAR_YELLOW   = 11;
const int PIN_CAR_RED      = 12;

// Khởi tạo đối tượng Servo Barie
Servo barieServo;

// Góc xoay cần Barie
const int BARIE_CLOSED_ANGLE = 0;   // 0 độ: Nằm ngang chắn học sinh trên vỉa hè
const int BARIE_OPEN_ANGLE   = 90;  // 90 độ: Dựng đứng mở lối học sinh qua đường

// Các trạng thái của máy trạng thái hữu hạn FSM (Finite State Machine)
enum SystemState {
  STATE_NORMAL,               // TH 1: Đường vắng, xe Xanh thông suốt
  STATE_YELLOW_WARNING,       // TH 2A: Đèn vàng cảnh báo xe giảm tốc (3 giây)
  STATE_PED_CROSSING,         // TH 2B: Xe Đỏ, người Xanh, Barie mở 90 độ (15 giây)
  STATE_EMERGENCY_CLEARANCE,  // TH 3A: Pha chuyển tiếp an toàn khẩn cấp khi có cứu thương (2.5 giây)
  STATE_AMBULANCE,            // TH 3B: Ưu tiên xe cứu thương khẩn cấp qua ngã tư
  STATE_WATCHDOG_SAFE         // TH 5: Mất kết nối USB máy tính quá 3 giây (nhấp nháy vàng)
};

SystemState currentState = STATE_NORMAL;
unsigned long stateStartTime = 0;
unsigned long lastHeartbeatTime = 0;
unsigned long lastBuzzerToggle = 0;
bool buzzerState = false;

// Cờ ngắt nút bấm dự phòng Failsafe
volatile bool buttonTriggered = false;

// Hàm ngắt phần cứng khi học sinh ấn nút Failsafe
void onButtonPress() {
  buttonTriggered = true;
}

void setup() {
  // Khởi tạo giao tiếp Serial với máy tính qua cổng USB
  Serial.begin(9600);

  // Cấu hình chân Output cho đèn LED và còi
  pinMode(PIN_CAR_GREEN, OUTPUT);
  pinMode(PIN_CAR_YELLOW, OUTPUT);
  pinMode(PIN_CAR_RED, OUTPUT);
  pinMode(PIN_PED_GREEN, OUTPUT);
  pinMode(PIN_PED_RED, OUTPUT);
  pinMode(PIN_BUZZER, OUTPUT);

  // Cấu hình chân Input kéo lên nội bộ cho nút bấm dự phòng
  pinMode(PIN_BTN_FAILSAFE, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(PIN_BTN_FAILSAFE), onButtonPress, FALLING);

  // Gắn chân điều khiển Servo Barie
  barieServo.attach(PIN_SERVO);
  setBarieAngle(BARIE_CLOSED_ANGLE); // Ban đầu barie luôn đóng

  // Khởi tạo trạng thái ban đầu: TH 1 (Đường vắng, xe Xanh, người Đỏ)
  setTrafficLights(HIGH, LOW, LOW, LOW, HIGH);
  lastHeartbeatTime = millis();

  Serial.println(F("[SYSTEM_READY] MCA Smart Traffic Light Ready on Nano Shield v3.0."));
}

void loop() {
  unsigned long now = millis();

  // 1. ĐỌC LỆNH TỪ MÁY TÍNH (MÔ HÌNH GOOGLE TEACHABLE MACHINE)
  if (Serial.available() > 0) {
    char cmd = Serial.read();
    lastHeartbeatTime = now; // Cập nhật nhịp sống còn (Heartbeat)

    if (cmd == '1') {
      // AI nhận diện học sinh xin qua đường (Class 1)
      if (currentState == STATE_NORMAL) {
        startYellowWarning();
      }
    } else if (cmd == '2') {
      // AI nhận diện xe cứu thương khẩn cấp (Class 2)
      triggerAmbulanceRequest();
    } else if (cmd == '0') {
      // Nhịp sống còn / Đường bình thường
      if (currentState == STATE_WATCHDOG_SAFE) {
        setNormalState();
      }
    }
  }

  // 2. KIỂM TRA NÚT BẤM DỰ PHÒNG CƠ HỌC (FAILSAFE D2)
  if (buttonTriggered) {
    buttonTriggered = false;
    Serial.println(F("[FAILSAFE_BUTTON_ACTIVATED] Manual Override Triggered!"));
    if (currentState == STATE_NORMAL) {
      startYellowWarning();
    }
  }

  // 3. KIỂM TRA BẢO VỆ WATCHDOG (NẾU MẤT TÍN HIỆU USB > 3 GIÂY)
  if (now - lastHeartbeatTime > 3000 && 
      currentState != STATE_PED_CROSSING && 
      currentState != STATE_YELLOW_WARNING &&
      currentState != STATE_EMERGENCY_CLEARANCE) {
    currentState = STATE_WATCHDOG_SAFE;
  }

  // 4. QUẢN LÝ CÁC TRẠNG THÁI HOẠT ĐỘNG (FSM ENGINE)
  switch (currentState) {
    case STATE_NORMAL:
      // Giữ đèn xe Xanh, người Đỏ, Barie đóng
      setTrafficLights(HIGH, LOW, LOW, LOW, HIGH);
      digitalWrite(PIN_BUZZER, LOW);
      break;

    case STATE_YELLOW_WARNING:
      // Đèn xe Vàng trong 3 giây trước khi dừng xe
      if (now - stateStartTime >= 3000) {
        startPedestrianCrossing();
      }
      break;

    case STATE_PED_CROSSING:
      // Cho học sinh qua đường trong đúng 15 giây
      handlePedestrianCrossing(now);
      break;

    case STATE_EMERGENCY_CLEARANCE:
      // Pha chuyển tiếp 2.5s: Hú còi giục học sinh lên lề an toàn trước khi mở xe
      handleEmergencyClearance(now);
      break;

    case STATE_AMBULANCE:
      // Xe cứu thương đi qua: Giữ xe Xanh, Barie hạ đóng, còi hú dài
      if (now - stateStartTime >= 6000) { // Sau 6 giây xe cứu thương qua hẳn
        setNormalState();
      }
      break;

    case STATE_WATCHDOG_SAFE:
      // Chế độ mất kết nối: Nhấp nháy đèn vàng ô tô chu kỳ 1s (chuẩn QCVN 41:2019)
      handleWatchdogBlink(now);
      break;
  }
}

// ==============================================================================
// CÁC HÀM XỬ LÝ CHUYỂN TRẠNG THÁI CHI TIẾT
// ==============================================================================

// Bắt đầu pha đèn vàng cảnh báo (3 giây)
void startYellowWarning() {
  currentState = STATE_YELLOW_WARNING;
  stateStartTime = millis();
  setTrafficLights(LOW, HIGH, LOW, LOW, HIGH); // Xe: Vàng, Người: Đỏ
  Serial.println(F("[STATE] Car Yellow Warning (3s)"));
}

// Bắt đầu pha học sinh qua đường (15 giây)
void startPedestrianCrossing() {
  currentState = STATE_PED_CROSSING;
  stateStartTime = millis();
  setTrafficLights(LOW, LOW, HIGH, HIGH, LOW); // Xe: Đỏ, Người: Xanh
  setBarieAngle(BARIE_OPEN_ANGLE);             // Nâng rào chắn Barie 90 độ
  Serial.println(F("[STATE] Pedestrian Crossing Active (15s)"));
}

// Xử lý còi và đếm ngược 15 giây qua đường
void handlePedestrianCrossing(unsigned long now) {
  unsigned long elapsed = now - stateStartTime;

  if (elapsed < 15000) {
    // Kêu tít tít dẫn đường: 12 giây đầu kêu chậm (500ms), 3 giây cuối dồn dập (200ms)
    unsigned long interval = (elapsed >= 12000) ? 200 : 500;
    if (now - lastBuzzerToggle >= interval) {
      lastBuzzerToggle = now;
      buzzerState = !buzzerState;
      digitalWrite(PIN_BUZZER, buzzerState ? HIGH : LOW);
    }
  } else {
    // Hết 15 giây -> Đóng barie và phục hồi đường bình thường
    digitalWrite(PIN_BUZZER, LOW);
    setBarieAngle(BARIE_CLOSED_ANGLE); // Hạ barie an toàn trước
    delay(400);                        // Chờ cần hạ hẳn
    setNormalState();
  }
}

// Yêu cầu ưu tiên xe cứu thương thông minh (Loại trừ xung đột người đi bộ)
void triggerAmbulanceRequest() {
  if (currentState == STATE_PED_CROSSING) {
    // Nếu học sinh đang qua đường -> BẮT BUỘC vào pha giải tỏa 2.5s an toàn
    currentState = STATE_EMERGENCY_CLEARANCE;
    stateStartTime = millis();
    // Giữ xe ĐỎ, người ĐỎ nhấp nháy, Barie vẫn MỞ để học sinh chạy thoát lên lề
    setTrafficLights(LOW, LOW, HIGH, LOW, HIGH);
    Serial.println(F("[EMERGENCY] Pedestrian on crosswalk! Entering 2.5s Emergency Clearance Interval..."));
  } else if (currentState != STATE_EMERGENCY_CLEARANCE && currentState != STATE_AMBULANCE) {
    // Nếu đường vắng hoặc đang đèn vàng -> Lập tức ưu tiên xe cứu thương
    activateAmbulancePass();
  }
}

// Pha giải tỏa an toàn khẩn cấp 2.5 giây
void handleEmergencyClearance(unsigned long now) {
  unsigned long elapsed = now - stateStartTime;

  // Còi hú dồn dập 100ms cảnh báo học sinh rảo bước lên vỉa hè
  if (now - lastBuzzerToggle >= 100) {
    lastBuzzerToggle = now;
    buzzerState = !buzzerState;
    digitalWrite(PIN_BUZZER, buzzerState ? HIGH : LOW);
    // Nhấp nháy đèn người đi bộ ĐỎ
    digitalWrite(PIN_PED_RED, buzzerState ? HIGH : LOW);
  }

  if (elapsed >= 2500) {
    // Hết 2.5 giây: Học sinh đã lên vỉa hè an toàn -> Hạ Barie và bật đèn Xe XANH
    setBarieAngle(BARIE_CLOSED_ANGLE);
    delay(300);
    activateAmbulancePass();
  }
}

// Bật ưu tiên xe cứu thương qua ngã tư
void activateAmbulancePass() {
  currentState = STATE_AMBULANCE;
  stateStartTime = millis();
  setBarieAngle(BARIE_CLOSED_ANGLE);
  setTrafficLights(HIGH, LOW, LOW, LOW, HIGH); // Xe: XANH khẩn cấp, Người: ĐỎ
  digitalWrite(PIN_BUZZER, HIGH);              // Còi kêu liên tục cảnh báo
  Serial.println(F("[EMERGENCY] Ambulance High-Priority Green Wave Activated!"));
}

// Chế độ nhấp nháy đèn vàng khi mất kết nối máy tính (Watchdog Safe Mode)
void handleWatchdogBlink(unsigned long now) {
  setBarieAngle(BARIE_CLOSED_ANGLE);
  digitalWrite(PIN_CAR_GREEN, LOW);
  digitalWrite(PIN_CAR_RED, LOW);
  digitalWrite(PIN_PED_GREEN, LOW);
  digitalWrite(PIN_PED_RED, HIGH); // Người luôn Đỏ
  digitalWrite(PIN_BUZZER, LOW);

  // Nhấp nháy đèn vàng xe chu kỳ 1s (500ms sáng, 500ms tắt)
  if (now % 1000 < 500) {
    digitalWrite(PIN_CAR_YELLOW, HIGH);
  } else {
    digitalWrite(PIN_CAR_YELLOW, LOW);
  }
}

// Phục hồi về trạng thái bình thường (TH 1)
void setNormalState() {
  currentState = STATE_NORMAL;
  setTrafficLights(HIGH, LOW, LOW, LOW, HIGH);
  setBarieAngle(BARIE_CLOSED_ANGLE);
  digitalWrite(PIN_BUZZER, LOW);
  Serial.println(F("[STATE] Normal Road Restored (Car Green)"));
}

// Hàm hỗ trợ bật/tắt cụm đèn LED giao thông
void setTrafficLights(int carG, int carY, int carR, int pedG, int pedR) {
  digitalWrite(PIN_CAR_GREEN, carG);
  digitalWrite(PIN_CAR_YELLOW, carY);
  digitalWrite(PIN_CAR_RED, carR);
  digitalWrite(PIN_PED_GREEN, pedG);
  digitalWrite(PIN_PED_RED, pedR);
}

// Hàm điều khiển góc quay Servo
void setBarieAngle(int targetAngle) {
  barieServo.write(targetAngle);
}
