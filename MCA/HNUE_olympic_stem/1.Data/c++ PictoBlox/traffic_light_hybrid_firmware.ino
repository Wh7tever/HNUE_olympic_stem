/*
 =========================================================================================
   DỰ ÁN STEM: HỆ THỐNG ĐÈN GIAO THÔNG HỌC ĐƯỜNG THÔNG MINH MARIE CURIE
   CUỘC THI: HNUE OLYMPIC STEM 2026 - BẢNG TIỂU HỌC
   ---------------------------------------------------------------------------------------
   MÔ-ĐUN: FIRMWARE LAI ĐA TẦNG (HYBRID C++ & PICTOBLOX SERIAL CONTROLLER) - BẢN V2.2 PRODUCTION
   Tác giả: Nhóm học sinh STEM Trường Tiểu học, THCS và THPT Marie Curie Thái Bình
   Vi điều khiển: Arduino Nano v3.0 (ATmega328P) + Nano Sensor Shield v3.0
   ---------------------------------------------------------------------------------------
   CẢI TIẾN TRỌNG YẾU BẢN V2.2 (THEO THẨM ĐỊNH KỸ THUẬT ARGON REVIEW):
   1. [An toàn Giao thông] Nút bấm khẩn cấp D2 chuyển qua đèn Vàng 3s để xe kịp phanh an toàn.
   2. [Khóa Ưu tiên] Nút D2 không ngắt ngang khi xe cứu thương đang dọn đường hoặc phóng qua.
   3. [Chống Buffer Bloat] Đọc cạn bộ đệm UART lấy lệnh AI mới nhất, chống trễ pha hình ảnh.
   4. [Chống dội phím kép] ISR kiểm tra mức logic digitalRead == LOW chống nảy khi nhả phím.
   5. [Khởi động mượt] Hỗ trợ bấm nút ngay từ ms đầu tiên sau khi bật nguồn (lastInterruptTime == 0).
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

#include <Arduino.h>
#include <Servo.h>

// 1. ĐỊNH NGHĨA CHÂN NGOẠI VI (CHUẨN SHIELD V3.0 GVS)
const int PIN_BTN_FAILSAFE = 2;   // Ngắt ngoài INT0 (Input Pullup)
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

// 3. ĐỊNH NGHĨA 6 TRẠNG THÁI MÁY FSM (FINITE STATE MACHINE)
enum SystemState {
  STATE_NORMAL_IDLE,       // TH1: Đường vắng - Xe Xanh, Đi bộ Đỏ, Barie Đóng (0°)
  STATE_CAR_YELLOW_TRANS,  // Chuyển tiếp an toàn: Đèn xe Vàng 3 giây cảnh báo giảm tốc trước khi mở Barie
  STATE_PEDESTRIAN_CROSS,  // TH2 & TH4: Học sinh qua đường an toàn - Xe Đỏ, Đi bộ Xanh, Barie Mở (90°)
  STATE_EMERGENCY_CLEAR,   // Chuyển tiếp dọn đường khẩn cấp 2.5s khi có xe cứu thương
  STATE_AMBULANCE_PASS,    // TH3: Xe cứu thương ưu tiên - Xe Xanh, Đi bộ Đỏ, Barie Đóng (0°), Còi hú
  STATE_WATCHDOG_SAFE      // TH5: Tự hành nháy vàng an toàn khi mất kết nối USB > 5s
};

// 4. BIẾN TOÀN CỤC & ĐIỀU KHIỂN THỜI GIAN (MILLIS KHÔNG BLOCKING)
SystemState currentState = STATE_NORMAL_IDLE;
Servo barieServo;

// Biến ngắt dùng trong ISR khai báo volatile
volatile bool failsafePressed = false;
volatile unsigned long lastInterruptTime = 0;
const unsigned long DEBOUNCE_DELAY_MS = 300;

unsigned long stateStartTime = 0;
unsigned long lastHeartbeatTime = 0;
unsigned long lastBuzzerToggleTime = 0;
bool buzzerState = false;

// 5. NGUYÊN MẪU HÀM
void handleFailsafeInterrupt();
void setTrafficLights(bool carG, bool carY, bool carR, bool pedG, bool pedR, int servoAngle);
void enterState(SystemState newState);
void processSerialCommands();
void processFailsafeTrigger();
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

  // Cấu hình ngắt ngoài phần cứng INT0 trên chân D2
  pinMode(PIN_BTN_FAILSAFE, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(PIN_BTN_FAILSAFE), handleFailsafeInterrupt, FALLING);

  // Khởi tạo Servo Barie về trạng thái đóng 0 độ
  barieServo.attach(PIN_SERVO);
  barieServo.write(BARIE_CLOSED_ANGLE);

  // Khởi tạo giao tiếp Serial ở baudrate 9600 tiêu chuẩn (non-blocking)
  Serial.begin(9600);

  // Chuyển sang trạng thái ban đầu: Đường vắng an toàn
  enterState(STATE_NORMAL_IDLE);
  lastHeartbeatTime = millis();

  // Phát tín hiệu chào đón định dạng JSON cho giao diện máy tính
  Serial.println(F("{\"status\":\"ONLINE\",\"mode\":\"HYBRID_DUAL_TIER\",\"firmware\":\"v2.2_PRODUCTION\"}"));
}

// =========================================================================================
// HÀM NGẮT CỨNG PHẦN CỨNG INT0 (CHỐNG DỘI PHÍM KÉP & CHỐNG NHẢ PHÍM GIẢ)
// =========================================================================================
void handleFailsafeInterrupt() {
  unsigned long interruptTime = millis();
  // Khắc phục lỗi khởi động (lastInterruptTime == 0) và chống rung phím cơ học khi nhả nút
  if ((lastInterruptTime == 0 || (interruptTime - lastInterruptTime > DEBOUNCE_DELAY_MS))
      && (digitalRead(PIN_BTN_FAILSAFE) == LOW)) {
    failsafePressed = true;
    lastInterruptTime = interruptTime;
  }
}

// =========================================================================================
// VÒNG LẶP CHÍNH (LOOP) - NON-BLOCKING DETERMINISTIC
// =========================================================================================
void loop() {
  // 1. Xử lý cờ ngắt Failsafe D2 (Atomic & An toàn giao thông)
  processFailsafeTrigger();

  // 2. Tiếp nhận và bóc tách gói tin Serial từ PictoBlox (Chống Buffer Bloat)
  processSerialCommands();

  // 3. Cập nhật máy trạng thái FSM theo thời gian thực
  updateFSM();

  // 4. Bảo vệ Watchdog: Tự động chuyển chế độ tự hành an toàn nếu mất USB > 5s
  if (millis() - lastHeartbeatTime > 5000 &&
      currentState != STATE_WATCHDOG_SAFE &&
      currentState != STATE_PEDESTRIAN_CROSS &&
      currentState != STATE_CAR_YELLOW_TRANS) {
    enterState(STATE_WATCHDOG_SAFE);
    Serial.println(F("{\"warning\":\"WATCHDOG_TIMEOUT\",\"action\":\"AUTONOMOUS_SAFE_MODE\"}"));
  }
}

// =========================================================================================
// XỬ LÝ AN TOÀN NÚT BẤM D2: BẮT BUỘC QUA ĐÈN VÀNG & KHÔNG CẮT NGANG XE CỨU THƯƠNG
// =========================================================================================
void processFailsafeTrigger() {
  noInterrupts();
  bool isTriggered = failsafePressed;
  failsafePressed = false;
  interrupts();

  if (isTriggered) {
    lastHeartbeatTime = millis(); // Nuôi nhịp sống kết nối
    Serial.println(F("{\"event\":\"FAILSAFE_D2\",\"action\":\"TRIGGERED\"}"));

    // An toàn tuyệt đối: Không mở rào chắn cho người đi bộ nếu xe cứu thương đang chạy qua
    if (currentState != STATE_EMERGENCY_CLEAR && currentState != STATE_AMBULANCE_PASS) {
      if (currentState == STATE_NORMAL_IDLE || currentState == STATE_WATCHDOG_SAFE) {
        // Tuân thủ động học giao thông: Chuyển qua đèn VÀNG 3s để xe kịp phanh an toàn trước khi mở Barie
        enterState(STATE_CAR_YELLOW_TRANS);
      }
    }
  }
}

// =========================================================================================
// XỬ LÝ LỆNH SERIAL TỪ PICTOBLOX (RÚT CẠN BỘ ĐỆM ĐỂ LẤY LỆNH AI MỚI NHẤT)
// =========================================================================================
void processSerialCommands() {
  char latestCmd = '\0';
  while (Serial.available() > 0) {
    char c = Serial.read();
    if (c == '0' || c == '1' || c == '2' || c == 'H') {
      latestCmd = c;
      lastHeartbeatTime = millis(); // Nuôi nhịp sống còn Watchdog
    }
  }

  if (latestCmd == '\0') return;

  // Lệnh '1': AI nhận diện Xe cứu thương khẩn cấp (Ưu tiên số 1)
  if (latestCmd == '1') {
    if (currentState == STATE_PEDESTRIAN_CROSS) {
      // Đang có người đi qua: Chuyển sang dọn đường khẩn cấp 2.5s trước khi mở làn xe
      enterState(STATE_EMERGENCY_CLEAR);
    } else if (currentState != STATE_AMBULANCE_PASS && currentState != STATE_EMERGENCY_CLEAR) {
      enterState(STATE_AMBULANCE_PASS);
    } else if (currentState == STATE_AMBULANCE_PASS) {
      stateStartTime = millis(); // Gia hạn thời gian nếu xe cứu thương vẫn trong vùng camera
    }
  }
  // Lệnh '2': AI nhận diện Học sinh vẫy tay xin qua đường
  else if (latestCmd == '2') {
    if (currentState == STATE_NORMAL_IDLE || currentState == STATE_WATCHDOG_SAFE) {
      enterState(STATE_CAR_YELLOW_TRANS);
    }
  }
  // Lệnh '0': Đường vắng bình thường (Chỉ thoát chế độ cứu thương sau tối thiểu 3 giây chống nhiễu)
  else if (latestCmd == '0') {
    if (currentState == STATE_WATCHDOG_SAFE) {
      enterState(STATE_NORMAL_IDLE);
    } else if (currentState == STATE_AMBULANCE_PASS && (millis() - stateStartTime >= 3000)) {
      enterState(STATE_NORMAL_IDLE);
    }
  }
  // Lệnh 'H': Gói tin Heartbeat định kỳ từ PictoBlox (Đã cập nhật lastHeartbeatTime)
}

// =========================================================================================
// CẬP NHẬT TRẠNG THÁI FSM THEO THỜI GIAN THỰC (NON-BLOCKING)
// =========================================================================================
void updateFSM() {
  unsigned long elapsed = millis() - stateStartTime;

  switch (currentState) {
    case STATE_NORMAL_IDLE:
      // Đường vắng thông suốt: Xe Xanh, Đi bộ Đỏ, Barie Đóng (0°)
      break;

    case STATE_CAR_YELLOW_TRANS:
      // Đèn vàng cảnh báo ô tô giảm tốc trong 3 giây trước khi dừng hẳn
      if (elapsed >= 3000) {
        enterState(STATE_PEDESTRIAN_CROSS);
      }
      break;

    case STATE_PEDESTRIAN_CROSS:
      // Học sinh qua đường trong 15 giây: Xe Đỏ, Đi bộ Xanh, Barie Mở 90°
      // 12 giây đầu: Còi bíp nhịp thưa (chu kỳ 500ms)
      if (elapsed < 12000) {
        if (millis() - lastBuzzerToggleTime >= 500) {
          lastBuzzerToggleTime = millis();
          buzzerState = !buzzerState;
          digitalWrite(PIN_BUZZER, buzzerState ? HIGH : LOW);
        }
      }
      // 3 giây cuối: Còi bíp dồn dập (chu kỳ 200ms) hối thúc khẩn trương
      else if (elapsed < 15000) {
        if (millis() - lastBuzzerToggleTime >= 200) {
          lastBuzzerToggleTime = millis();
          buzzerState = !buzzerState;
          digitalWrite(PIN_BUZZER, buzzerState ? HIGH : LOW);
        }
      }
      // Hết 15 giây an toàn: Tắt còi và quay về trạng thái đường vắng
      else {
        digitalWrite(PIN_BUZZER, LOW);
        enterState(STATE_NORMAL_IDLE);
      }
      break;

    case STATE_EMERGENCY_CLEAR:
      // Dọn đường khẩn cấp 2.5s: Nháy còi và đèn đi bộ đỏ cảnh báo người nhanh chóng lên lề
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
      // Xe cứu thương đi qua: Còi hú liên tục, xe Xanh thông suốt
      digitalWrite(PIN_BUZZER, HIGH);
      if (elapsed >= 8000) {
        enterState(STATE_NORMAL_IDLE);
      }
      break;

    case STATE_WATCHDOG_SAFE:
      // Chế độ tự hành mất kết nối: Nháy đèn vàng ô tô tần số 1Hz (500ms)
      if (millis() - lastBuzzerToggleTime >= 500) {
        lastBuzzerToggleTime = millis();
        buzzerState = !buzzerState;
        digitalWrite(PIN_CAR_YELLOW, buzzerState ? HIGH : LOW);
      }
      break;
  }
}

// =========================================================================================
// CHUYỂN TRẠNG THÁI & THIẾT LẬP PHẦN CỨNG ĐỒNG BỘ
// =========================================================================================
void enterState(SystemState newState) {
  currentState = newState;
  stateStartTime = millis();
  lastBuzzerToggleTime = millis();
  buzzerState = false;
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
      setTrafficLights(LOW, LOW, HIGH, LOW, HIGH, BARIE_CLOSED_ANGLE);
      Serial.println(F("{\"state\":\"EMERGENCY_CLEARANCE\",\"ped\":\"CLEARING\",\"barie\":\"CLOSING\"}"));
      break;

    case STATE_AMBULANCE_PASS:
      setTrafficLights(HIGH, LOW, LOW, LOW, HIGH, BARIE_CLOSED_ANGLE);
      Serial.println(F("{\"state\":\"AMBULANCE_PRIORITY\",\"car\":\"GREEN\",\"barie\":\"CLOSED\"}"));
      break;

    case STATE_WATCHDOG_SAFE:
      setTrafficLights(LOW, LOW, LOW, LOW, HIGH, BARIE_CLOSED_ANGLE);
      Serial.println(F("{\"state\":\"WATCHDOG_STANDALONE\",\"car\":\"FLASH_YELLOW\",\"barie\":\"CLOSED\"}"));
      break;
  }
}

// =========================================================================================
// ĐIỀU KHIỂN ĐỒNG THỜI TOÀN BỘ CỤM ĐÈN VÀ ĐỘNG CƠ BARIE
// =========================================================================================
void setTrafficLights(bool carG, bool carY, bool carR, bool pedG, bool pedR, int servoAngle) {
  digitalWrite(PIN_CAR_GREEN, carG);
  digitalWrite(PIN_CAR_YELLOW, carY);
  digitalWrite(PIN_CAR_RED, carR);
  digitalWrite(PIN_PED_GREEN, pedG);
  digitalWrite(PIN_PED_RED, pedR);
  barieServo.write(servoAngle);
}
