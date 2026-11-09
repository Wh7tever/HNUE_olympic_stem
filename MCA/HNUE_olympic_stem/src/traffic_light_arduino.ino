/*
 * ==============================================================================
 * DỰ ÁN: HỆ THỐNG ĐÈN GIAO THÔNG HỌC ĐƯỜNG THÔNG MINH AI - MARIE CURIE ACADEMY
 * CUỘC THI: HNUE OLYMPIC STEM 2026 - BẢNG TIỂU HỌC
 * ------------------------------------------------------------------------------
 * MẠCH ĐIỀU KHIỂN: Arduino Nano (ATmega328P) / Uno
 * TÁC GIẢ: Đội tuyển STEM MCA (Phạm Hữu Đạt, Vũ Minh Quang, Vũ Ngọc An Đông)
 * CÁN BỘ HỖ TRỢ: Thầy Lê Ngọc Anh
 * ==============================================================================
 * SƠ ĐỒ CHÂN NỐI DÂY (PIN MAPPING):
 * - D2: Nút bấm cơ học dự phòng (Failsafe Button - INPUT_PULLUP)
 * - D3: Đèn ô tô - XANH (Car Green LED)
 * - D4: Đèn ô tô - VÀNG (Car Yellow LED)
 * - D5: Đèn ô tô - ĐỎ   (Car Red LED)
 * - D6: Đèn đi bộ - XANH (Pedestrian Green LED)
 * - D7: Đèn đi bộ - ĐỎ   (Pedestrian Red LED)
 * - D8: Còi chip cảnh báo (Active Buzzer 5V)
 * - D9: Động cơ Servo mini SG90 điều khiển cần Barie
 * ==============================================================================
 */

#include <Servo.h>

// Định nghĩa các chân điều khiển
const int PIN_BTN_FAILSAFE = 2; // Chân ngắt INT0
const int PIN_CAR_GREEN    = 3;
const int PIN_CAR_YELLOW   = 4;
const int PIN_CAR_RED      = 5;
const int PIN_PED_GREEN    = 6;
const int PIN_PED_RED      = 7;
const int PIN_BUZZER       = 8;
const int PIN_SERVO        = 9;

// Khởi tạo đối tượng Servo
Servo barieServo;

// Góc xoay cần Barie
const int BARIE_CLOSED_ANGLE = 0;   // 0 độ: Nằm ngang chắn học sinh
const int BARIE_OPEN_ANGLE   = 90;  // 90 độ: Dựng đứng cho học sinh qua

// Các trạng thái của máy trạng thái FSM (State Machine)
enum SystemState {
  STATE_NORMAL,           // TH 1: Đường vắng, xe chạy thông suốt
  STATE_YELLOW_WARNING,   // TH 2A: Đèn vàng cảnh báo xe dừng (3s)
  STATE_PED_CROSSING,     // TH 2B: Xe đỏ, người xanh, barie mở 90 độ (15s)
  STATE_AMBULANCE,        // TH 3: Ưu tiên xe cứu thương khẩn cấp
  STATE_WATCHDOG_SAFE     // TH 5: Mất kết nối USB máy tính (nhấp nháy vàng)
};

SystemState currentState = STATE_NORMAL;
unsigned long stateStartTime = 0;
unsigned long lastHeartbeatTime = 0;
unsigned long lastBuzzerToggle = 0;
bool buzzerState = false;

// Cờ ngắt nút bấm dự phòng
volatile bool buttonTriggered = false;

// Hàm ngắt phần cứng khi học sinh ấn nút Failsafe
void onButtonPress() {
  buttonTriggered = true;
}

void setup() {
  // Khởi tạo giao tiếp Serial với máy tính qua cáp USB
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

  // Gắn chân điều khiển Servo
  barieServo.attach(PIN_SERVO);
  setBarieAngle(BARIE_CLOSED_ANGLE); // Ban đầu barie đóng

  // Khởi tạo trạng thái ban đầu: TH 1
  setTrafficLights(HIGH, LOW, LOW, LOW, HIGH); // Xe: Xanh, Người: Đỏ
  lastHeartbeatTime = millis();

  Serial.println(F("[SYSTEM_READY] MCA Smart Traffic Light Ready."));
}

void loop() {
  unsigned long now = millis();

  // 1. ĐỌC LỆNH TỪ MÁY TÍNH (MÔ HÌNH TEACHABLE MACHINE AI)
  if (Serial.available() > 0) {
    char cmd = Serial.read();
    lastHeartbeatTime = now; // Cập nhật nhịp sống còn (Heartbeat)

    if (cmd == '1') {
      // AI nhận diện học sinh giơ tay xin qua đường
      if (currentState == STATE_NORMAL) {
        startYellowWarning();
      }
    } else if (cmd == '2') {
      // AI nhận diện xe cứu thương khẩn cấp -> Ngắt ưu tiên lập tức
      triggerEmergencyAmbulance();
    } else if (cmd == '0') {
      // Đường bình thường
      if (currentState == STATE_WATCHDOG_SAFE) {
        setNormalState();
      }
    }
  }

  // 2. KIỂM TRA NÚT BẤM DỰ PHÒNG CƠ HỌC (FAILSAFE)
  if (buttonTriggered) {
    buttonTriggered = false;
    Serial.println(F("[FAILSAFE_BUTTON_ACTIVATED] Manual Override."));
    if (currentState == STATE_NORMAL) {
      startYellowWarning();
    }
  }

  // 3. KIỂM TRA BẢO VỆ WATCHDOG (NẾU MẤT TÍN HIỆU USB > 5 GIÂY)
  if (now - lastHeartbeatTime > 5000 && currentState != STATE_PED_CROSSING && currentState != STATE_YELLOW_WARNING) {
    currentState = STATE_WATCHDOG_SAFE;
  }

  // 4. QUẢN LÝ CÁC TRẠNG THÁI HOẠT ĐỘNG
  switch (currentState) {
    case STATE_NORMAL:
      // Giữ đèn xe Xanh, người Đỏ, barie đóng
      setTrafficLights(HIGH, LOW, LOW, LOW, HIGH);
      digitalWrite(PIN_BUZZER, LOW);
      break;

    case STATE_YELLOW_WARNING:
      // Đèn xe Vàng trong 3 giây
      if (now - stateStartTime >= 3000) {
        startPedestrianCrossing();
      }
      break;

    case STATE_PED_CROSSING:
      // Cho học sinh qua đường trong đúng 15 giây
      handlePedestrianCrossing(now);
      break;

    case STATE_AMBULANCE:
      // Xe cứu thương đi qua: giữ xe Xanh, Barie hạ đóng, kêu còi dài
      if (now - stateStartTime >= 6000) { // Sau 6 giây xe cứu thương qua hẳn
        setNormalState();
      }
      break;

    case STATE_WATCHDOG_SAFE:
      // Chế độ mất kết nối: Nhấp nháy đèn vàng ô tô chu kỳ 1s, đóng barie
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
  Serial.println(F("[STATE] Car Yellow (3s warning)"));
}

// Bắt đầu pha học sinh qua đường (15 giây)
void startPedestrianCrossing() {
  currentState = STATE_PED_CROSSING;
  stateStartTime = millis();
  setTrafficLights(LOW, LOW, HIGH, HIGH, LOW); // Xe: Đỏ, Người: Xanh
  setBarieAngle(BARIE_OPEN_ANGLE);             // Mở rào chắn Barie 90 độ
  Serial.println(F("[STATE] Pedestrian Crossing Active (15s)"));
}

// Xử lý còi và đếm ngược 15 giây qua đường
void handlePedestrianCrossing(unsigned long now) {
  unsigned long elapsed = now - stateStartTime;

  if (elapsed < 15000) {
    // Kêu tít tít dẫn đường: 12 giây đầu kêu chậm (500ms), 3 giây cuối kêu dồn dập (200ms)
    unsigned long interval = (elapsed >= 12000) ? 200 : 500;
    if (now - lastBuzzerToggle >= interval) {
      lastBuzzerToggle = now;
      buzzerState = !buzzerState;
      digitalWrite(PIN_BUZZER, buzzerState ? HIGH : LOW);
    }
  } else {
    // Hết 15 giây -> Đóng barie và phục hồi
    digitalWrite(PIN_BUZZER, LOW);
    setBarieAngle(BARIE_CLOSED_ANGLE); // Hạ barie an toàn trước
    delay(500);                        // Chờ cần hạ hẳn
    setNormalState();
  }
}

// Kích hoạt chế độ khẩn cấp ưu tiên xe cứu thương
void triggerEmergencyAmbulance() {
  currentState = STATE_AMBULANCE;
  stateStartTime = millis();
  setBarieAngle(BARIE_CLOSED_ANGLE);           // Lập tức hạ barie chặn người
  setTrafficLights(HIGH, LOW, LOW, LOW, HIGH); // Xe lập tức XANH khẩn cấp
  digitalWrite(PIN_BUZZER, HIGH);              // Hú còi cảnh báo
  Serial.println(F("[EMERGENCY] Ambulance Override Activated!"));
}

// Chế độ nhấp nháy đèn vàng khi mất kết nối máy tính
void handleWatchdogBlink(unsigned long now) {
  setBarieAngle(BARIE_CLOSED_ANGLE);
  digitalWrite(PIN_CAR_GREEN, LOW);
  digitalWrite(PIN_CAR_RED, LOW);
  digitalWrite(PIN_PED_GREEN, LOW);
  digitalWrite(PIN_PED_RED, HIGH); // Người luôn đỏ
  digitalWrite(PIN_BUZZER, LOW);

  // Nhấp nháy đèn vàng xe 1Hz (500ms bật, 500ms tắt)
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
  Serial.println(F("[STATE] Normal Road (Car Green)"));
}

// Hàm hỗ trợ bật/tắt cụm đèn LED giao thông
void setTrafficLights(int carG, int carY, int carR, int pedG, int pedR) {
  digitalWrite(PIN_CAR_GREEN, carG);
  digitalWrite(PIN_CAR_YELLOW, carY);
  digitalWrite(PIN_CAR_RED, carR);
  digitalWrite(PIN_PED_GREEN, pedG);
  digitalWrite(PIN_PED_RED, pedR);
}

// Hàm quét góc quay servo êm ái, chống rung giật
void setBarieAngle(int targetAngle) {
  barieServo.write(targetAngle);
}
