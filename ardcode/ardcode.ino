#include <ESP32Servo.h>

Servo servo;

const int servoPin = 18;

// ==============================
// CALIBRATION
// ==============================
float neutral = 58;   // YOUR FOUND CENTER
float servoAngle = 58;

const float deltheta = 7;
const float SERVO_MIN = neutral - deltheta;
const float SERVO_MAX = neutral + deltheta;

// ==============================
// SETUP
// ==============================
void setup() {
  Serial.begin(115200);

  servo.setPeriodHertz(50);

  // ✅ KEEP SAME RANGE AS WORKING CODE
  servo.attach(servoPin, 1000, 2000);

  servo.write(neutral);
  delay(2000);

  Serial.println("Stable at neutral");
}

// ==============================
// LOOP
// ==============================
void loop() {

  float input = 0;

  // ✅ Only update if real data comes
  if (Serial.available()) {
    input = Serial.parseFloat();
  } else {
    input = 0;  // no PID correction
  }

  // ==============================
  // PID OUTPUT → TARGET
  // ==============================
  float targetAngle = neutral + input;

  // Clamp
  if (targetAngle > SERVO_MAX) targetAngle = SERVO_MAX;
  if (targetAngle < SERVO_MIN) targetAngle = SERVO_MIN;

  // ==============================
  // SMOOTHING
  // ==============================
  float maxStep = 1.0;

  if (targetAngle > servoAngle + maxStep)
    servoAngle += maxStep;
  else if (targetAngle < servoAngle - maxStep)
    servoAngle -= maxStep;
  else
    servoAngle = targetAngle;

  // Move servo
  servo.write(servoAngle);

  delay(10);  // small control loop delay
}