  #include <ESP32Servo.h>

Servo servo;

// ==============================
// PIN CONFIG
// ==============================
const int servoPin = 18;  // Change if needed

// ==============================
// PID PARAMETERS (TUNE THESE)
// ==============================
float Kp = 1.2;
float Ki = 0.0;
float Kd = 0.0;

// ==============================
// VARIABLES
// ==============================
float setpoint = 0.0;     // want ball at center
float position = 0.0;
float error = 0.0;
float prev_error = 0.0;
float integral = 0.0;
float derivative = 0.0;
float maxStep = 1.5;

// Servo
float theta = 0.0;        // angle (relative)
float servoAngle = 80;    // neutral position

// Limits
const float SERVO_MIN = 66;
const float SERVO_MAX = 130;

// ==============================
// SETUP
// ==============================
void setup() {
  Serial.begin(115200);

  servo.setPeriodHertz(50);   // standard servo freq
  servo.attach(servoPin, 500, 2400);

  servo.write(80);  // neutral
}

// ==============================
// LOOP
// ==============================
void loop() {

  // ==============================
  // READ FROM PYTHON
  // ==============================
  if (Serial.available()) {
    position = Serial.parseFloat();  // cm input

    // ==============================
    // CONVERT SERVO ANGLE → THETA
    // θ = 0 at 88°
    // ==============================
    theta = (servoAngle - 80) * PI / 180.0;

    float cos_theta = cos(theta);

    // Avoid divide by zero
    if (abs(cos_theta) < 0.1) cos_theta = 0.1;

    // ==============================
    // ERROR
    // ==============================
    error = position / cos_theta;

    // ==============================
    // PID
    // ==============================
    integral += error;
    integral = constrain(integral,-15,15);
    derivative = error - prev_error;

    float output = Kp * error + Ki * integral + Kd * derivative;

    prev_error = error;

    // ==============================
    // UPDATE SERVO ANGLE
    // ==============================
    float targetAngle = 80 - output;

// Apply limits to target (optional but good)
    if (targetAngle > SERVO_MAX) targetAngle = SERVO_MAX;
    if (targetAngle < SERVO_MIN) targetAngle = SERVO_MIN;

// Rate limiting (smooth motion)
  // try 0.8–2.0

    if (targetAngle > servoAngle + maxStep)
      servoAngle += maxStep;
    else if (targetAngle < servoAngle - maxStep)
      servoAngle -= maxStep;
    else
      servoAngle = targetAngle;

    // ==============================
    // LIMITS (IMPORTANT)
    // ==============================
    if (servoAngle > SERVO_MAX) servoAngle = SERVO_MAX;
    if (servoAngle < SERVO_MIN) servoAngle = SERVO_MIN;

    // ==============================
    // MOVE SERVO
    // ==============================
    servo.write(servoAngle);

    // ==============================
    // DEBUG PRINT
    // ==============================
    Serial.print("Pos: ");
    Serial.print(position);
    Serial.print(" | Error: ");
    Serial.print(error);
    Serial.print(" | Angle: ");
    Serial.println(servoAngle);
  }
}