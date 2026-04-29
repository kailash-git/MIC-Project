#include <ESP32Servo.h>

Servo servo;

// ==============================
// PIN CONFIG
// ==============================
const int servoPin = 18;

// ==============================
// SERVO SETTINGS
// ==============================
float servoAngle = 97;   // horizontal neutral (UPDATED)
float deltheta = 5;
// UPDATED LIMITS
const float SERVO_MIN = servoAngle-deltheta;
const float SERVO_MAX = servoAngle+deltheta;

// ==============================
// SETUP
// ==============================
void setup() {
  Serial.begin(115200);

  servo.setPeriodHertz(50);
  servo.attach(servoPin, 500, 2400);

  // ==============================
  // HOLD HORIZONTAL AT START
  // ==============================
  servo.write(servoAngle);
  Serial.println("Holding horizontal...");
  delay(3000);  // 3 sec stable start
}

// ==============================
// LOOP
// ==============================
void loop() {

  if (Serial.available()) {

    float input = Serial.parseFloat();

    // Ignore garbage
    if (isnan(input)) return;

    // ==============================
    // PYTHON PID OUTPUT → SERVO ANGLE
    // ==============================
    float targetAngle = servoAngle - input;   // UPDATED

    // Clamp to NEW limits
    if (targetAngle > SERVO_MAX) targetAngle = SERVO_MAX;
    if (targetAngle < SERVO_MIN) targetAngle = SERVO_MIN;

    // Smooth movement (rate limit)
    float maxStep = 1;

    if (targetAngle > servoAngle + maxStep)
      servoAngle += maxStep;
    else if (targetAngle < servoAngle - maxStep)
      servoAngle -= maxStep;
    else
      servoAngle = targetAngle;

    // Final clamp
    if (servoAngle > SERVO_MAX) servoAngle = SERVO_MAX;
    if (servoAngle < SERVO_MIN) servoAngle = SERVO_MIN;

    // Move servo
    servo.write(servoAngle);

    // Debug
    Serial.print("Input: ");
    Serial.print(input);
    Serial.print(" | Angle: ");
    Serial.println(servoAngle);
  }
}