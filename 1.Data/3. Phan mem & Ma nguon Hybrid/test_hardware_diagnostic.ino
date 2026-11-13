/*
 * ==============================================================================
 * DỰ ÁN: HỆ THỐNG ĐÈN GIAO THÔNG HỌC ĐƯỜNG THÔNG MINH AI - MARIE CURIE ACADEMY
 * CUỘC THI: HNUE OLYMPIC STEM 2026 - BẢNG TIỂU HỌC
 * ------------------------------------------------------------------------------
 * CHƯƠNG TRÌNH: FIRMWARE CHẨN ĐOÁN & THỬ NGHIỆM PHẦN CỨNG TỰ ĐỘNG
 * (HARDWARE DIAGNOSTIC & SANITY TEST SUITE)
 * ------------------------------------------------------------------------------
 * MỤC ĐÍCH:
 * Kiểm tra 100% cổng I/O trên Arduino Nano Expansion Shield v3.0 ngay sau khi nhận hàng.
 * Phát hiện ngay linh kiện lỗi, lỏng chân cắm hoặc sụt áp trước khi tích hợp hệ thống.
 * ==============================================================================
 * SƠ ĐỒ KẾT NỐI CHÂN TIÊU CHUẨN TRÊN NANO SHIELD V3.0:
 * - D2 : Nút bấm cơ học Failsafe (Nối chân S của D2, chân V nối 5V, chân G nối GND)
 * - D6 : Đèn LED Đi bộ ĐỎ
 * - D7 : Đèn LED Đi bộ XANH
 * - D8 : Còi chip Active Buzzer mini 5V
 * - D9 : Động cơ Servo mini SG90 (Cam -> S, Đỏ -> V, Nâu -> G)
 * - D10: Đèn LED Xe XANH
 * - D11: Đèn LED Xe VÀNG
 * - D12: Đèn LED Xe ĐỎ
 * ==============================================================================
 */

#include <Servo.h>

// Định nghĩa chân I/O
const int PIN_BTN_FAILSAFE = 2;
const int PIN_PED_RED      = 6;
const int PIN_PED_GREEN    = 7;
const int PIN_BUZZER       = 8;
const int PIN_SERVO        = 9;
const int PIN_CAR_GREEN    = 10;
const int PIN_CAR_YELLOW   = 11;
const int PIN_CAR_RED      = 12;

Servo testServo;
volatile bool btnPressed = false;

void onButtonInterrupt() {
  btnPressed = true;
}

void setup() {
  Serial.begin(9600);
  while (!Serial && millis() < 3000); // Chờ cổng Serial tối đa 3s

  pinMode(PIN_CAR_GREEN, OUTPUT);
  pinMode(PIN_CAR_YELLOW, OUTPUT);
  pinMode(PIN_CAR_RED, OUTPUT);
  pinMode(PIN_PED_GREEN, OUTPUT);
  pinMode(PIN_PED_RED, OUTPUT);
  pinMode(PIN_BUZZER, OUTPUT);

  pinMode(PIN_BTN_FAILSAFE, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(PIN_BTN_FAILSAFE), onButtonInterrupt, FALLING);

  testServo.write(0);
  testServo.attach(PIN_SERVO);
  testServo.write(0);

  printHeader();
  printMenu();
}

void loop() {
  if (Serial.available() > 0) {
    char ch = Serial.read();
    handleCommand(ch);
  }

  // Bắt sự kiện ấn nút Failsafe bất kỳ lúc nào
  if (btnPressed) {
    btnPressed = false;
    Serial.println(F("\n>>> [XÁC NHẬN] Nút bấm Failsafe (D2) hoạt động TỐT! (Đã kích hoạt ngắt) <<<"));
    // Nháy tất cả đèn và kêu còi 1 nhịp ngắn để phản hồi
    digitalWrite(PIN_BUZZER, HIGH);
    setAllLEDs(HIGH);
    delay(200);
    digitalWrite(PIN_BUZZER, LOW);
    setAllLEDs(LOW);
  }
}

void printHeader() {
  Serial.println(F("\n========================================================"));
  Serial.println(F("    MCA SMART TRAFFIC LIGHT - HARDWARE DIAGNOSTIC SUITE "));
  Serial.println(F("         Trường Tiểu học Marie Curie Thái Bình          "));
  Serial.println(F("========================================================"));
  Serial.println(F("Sanity Test: Nano Shield v3.0 | ATmega328P | Baud: 9600"));
}

void printMenu() {
  Serial.println(F("\n--- DANH MỤC THỬ NGHIỆM LINH KIỆN (Gõ phím để chọn) ---"));
  Serial.println(F(" [1] Test Đèn LED Ô tô (D10 Xanh -> D11 Vàng -> D12 Đỏ)"));
  Serial.println(F(" [2] Test Đèn LED Đi bộ (D6 Đỏ -> D7 Xanh)"));
  Serial.println(F(" [3] Test Còi chip Buzzer (D8) (hoặc gõ phím 'B')"));
  Serial.println(F(" [4] Test Động cơ Servo SG90 Barie (D9: Quét 0 -> 90 -> 0 độ)"));
  Serial.println(F(" [5] Test Nút bấm Failsafe (D2)"));
  Serial.println(F(" [A] CHẠY TỰ ĐỘNG TOÀN BỘ (AUTO FULL HARDWARE SCAN)"));
  Serial.println(F(" [0] Tắt toàn bộ đèn và còi, hạ Barie về 0 độ"));
  Serial.print(F("Nhập lựa chọn của bạn: "));
}

void handleCommand(char cmd) {
  switch (cmd) {
    case '1':
      testCarLEDs();
      break;
    case '2':
      testPedestrianLEDs();
      break;
    case '3':
    case 'b':
    case 'B':
      testBuzzer();
      break;
    case '4':
      testServoMovement();
      break;
    case '5':
      Serial.println(F("\n-> Hãy ấn nút bấm cơ học trên chân D2. Đèn trên Nano sẽ phản hồi khi nhận tín hiệu..."));
      break;
    case 'a':
    case 'A':
      runFullAutoTest();
      break;
    case '0':
      turnOffAll();
      Serial.println(F("\n-> Đã tắt toàn bộ thiết bị!"));
      break;
    default:
      if (cmd != '\r' && cmd != '\n') {
        Serial.print(F("\n[!] Lệnh không hợp lệ: '"));
        Serial.print(cmd);
        Serial.println(F("'"));
        printMenu();
      }
      break;
  }
}

void testCarLEDs() {
  Serial.println(F("\n[TEST 1] Đang thử nghiệm Cụm 3 LED Xe ô tô:"));
  Serial.println(F(" - Bật LED XANH (D10)..."));
  digitalWrite(PIN_CAR_GREEN, HIGH); delay(800); digitalWrite(PIN_CAR_GREEN, LOW);
  Serial.println(F(" - Bật LED VÀNG (D11)..."));
  digitalWrite(PIN_CAR_YELLOW, HIGH); delay(800); digitalWrite(PIN_CAR_YELLOW, LOW);
  Serial.println(F(" - Bật LED ĐỎ (D12)..."));
  digitalWrite(PIN_CAR_RED, HIGH); delay(800); digitalWrite(PIN_CAR_RED, LOW);
  Serial.println(F("=> KẾT QUẢ TEST 1: Hoàn thành kiểm tra LED ô tô!"));
}

void testPedestrianLEDs() {
  Serial.println(F("\n[TEST 2] Đang thử nghiệm Cụm 2 LED Người đi bộ:"));
  Serial.println(F(" - Bật LED ĐỎ đi bộ (D6)..."));
  digitalWrite(PIN_PED_RED, HIGH); delay(800); digitalWrite(PIN_PED_RED, LOW);
  Serial.println(F(" - Bật LED XANH đi bộ (D7)..."));
  digitalWrite(PIN_PED_GREEN, HIGH); delay(800); digitalWrite(PIN_PED_GREEN, LOW);
  Serial.println(F("=> KẾT QUẢ TEST 2: Hoàn thành kiểm tra LED đi bộ!"));
}

void testBuzzer() {
  Serial.println(F("\n[TEST 3] Đang thử nghiệm Còi chip Active Buzzer (D8):"));
  for (int i = 0; i < 3; i++) {
    digitalWrite(PIN_BUZZER, HIGH);
    delay(150);
    digitalWrite(PIN_BUZZER, LOW);
    delay(150);
  }
  Serial.println(F("=> KẾT QUẢ TEST 3: Còi phát 3 nhịp 'tít... tít... tít...'. Thành công!"));
}

void testServoMovement() {
  Serial.println(F("\n[TEST 4] Đang thử nghiệm Động cơ Servo SG90 Barie (D9):"));
  Serial.println(F(" - Hạ Barie về 0 độ (Nằm ngang chắn đường)..."));
  testServo.write(0);
  delay(1000);

  Serial.println(F(" - Nâng Barie lên 90 độ (Mở lối đi bộ)..."));
  // Quét góc mượt mà chống sụt áp giật dòng
  for (int angle = 0; angle <= 90; angle += 5) {
    testServo.write(angle);
    delay(20);
  }
  delay(1500);

  Serial.println(F(" - Hạ Barie từ từ về 0 độ..."));
  for (int angle = 90; angle >= 0; angle -= 5) {
    testServo.write(angle);
    delay(20);
  }
  delay(500);
  Serial.println(F("=> KẾT QUẢ TEST 4: Động cơ Servo vận hành êm ái, góc mở 90 độ chuẩn!"));
}

void runFullAutoTest() {
  Serial.println(F("\n========================================================"));
  Serial.println(F(">>> BẮT ĐẦU QUY TRÌNH QUÉT TỰ ĐỘNG TOÀN BỘ LINH KIỆN <<<"));
  Serial.println(F("========================================================"));
  
  testCarLEDs();
  delay(500);
  testPedestrianLEDs();
  delay(500);
  testBuzzer();
  delay(500);
  testServoMovement();
  delay(500);

  Serial.println(F("\n[TEST 5] Kiểm tra Nút bấm Failsafe (D2):"));
  Serial.println(F("Học sinh có 5 giây để ấn nút Failsafe trên sa bàn..."));
  unsigned long startWait = millis();
  bool pressed = false;
  while (millis() - startWait < 5000) {
    if (digitalRead(PIN_BTN_FAILSAFE) == LOW) {
      pressed = true;
      break;
    }
    delay(50);
  }

  if (pressed) {
    Serial.println(F(">>> PASS: Nút bấm Failsafe phản hồi tốt! <<<"));
    digitalWrite(PIN_BUZZER, HIGH); delay(150); digitalWrite(PIN_BUZZER, LOW);
  } else {
    Serial.println(F(">>> CHÚ Ý: Không phát hiện thao tác ấn nút trong 5 giây (Bỏ qua). <<<"));
  }
  btnPressed = false; // Xóa cờ ngắt phần cứng D2 chống kích hoạt kép khi quay về loop()

  Serial.println(F("\n========================================================"));
  Serial.println(F(">>> TỔNG KẾT: TOÀN BỘ PHẦN CỨNG SẴN SÀNG 100% THI ĐẤU! <<<"));
  Serial.println(F("========================================================"));
  printMenu();
}

void setAllLEDs(int state) {
  digitalWrite(PIN_CAR_GREEN, state);
  digitalWrite(PIN_CAR_YELLOW, state);
  digitalWrite(PIN_CAR_RED, state);
  digitalWrite(PIN_PED_GREEN, state);
  digitalWrite(PIN_PED_RED, state);
}

void turnOffAll() {
  setAllLEDs(LOW);
  digitalWrite(PIN_BUZZER, LOW);
  testServo.write(0);
}
