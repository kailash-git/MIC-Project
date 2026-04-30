import cv2
import numpy as np
import serial
import time

# ==============================
# CALIBRATION CONSTANTS
# ==============================
m = 0.07637346825836035
c = -0.06364455688196972

# ==============================
# SERIAL SETUP
# ==============================
ser = serial.Serial('COM5', 115200, timeout=0.01)
time.sleep(2)

# ==============================
# HOLD SERVO HORIZONTAL
# ==============================
print("Holding motor at horizontal...")
for _ in range(30):
    ser.write(b"0\n")
    time.sleep(0.05)
time.sleep(1)

# ==============================
# PID INPUT
# ==============================
while True:
    try:
        user_pid = input("Enter Kp,Ki,Kd: ")
        if ',' in user_pid:
            Kp, Ki, Kd = map(float, user_pid.split(','))
            break
    except:
        pass
    print("Invalid input")

prev_error = 0
integral = 0
last_time = time.time()

# ==============================
# CAMERA STREAM
# ==============================
stream_url = "http://10.201.224.126:81/stream"
cap = cv2.VideoCapture(stream_url)

print("Press ENTER to capture frame and select ROI")

# ==============================
# STEP 1: LIVE FEED
# ==============================
while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        exit()

    frame = cv2.resize(frame, (640, 480))

    cv2.putText(frame, "Press ENTER to select ROI",
                (20, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 255), 2)

    cv2.imshow("Live Feed", frame)

    key = cv2.waitKey(1) & 0xFF

    if key == 13:
        freeze_frame = frame.copy()
        break
    elif key == 27:
        cap.release()
        cv2.destroyAllWindows()
        exit()

# ==============================
# STEP 2: SELECT ROI
# ==============================
roi = cv2.selectROI("Select ROI", freeze_frame, False, True)
cv2.destroyWindow("Select ROI")

x_roi, y_roi, w_roi, h_roi = roi

origin_x = x_roi + w_roi // 2
origin_y = y_roi + h_roi // 2

print(f"Origin: ({origin_x}, {origin_y})")

# ==============================
# MAIN LOOP
# ==============================
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.resize(frame, (640, 480))

    # ROI
    roi_frame = frame[y_roi:y_roi + h_roi, x_roi:x_roi + w_roi]

    # ==============================
    # MEDIAN FILTER
    # ==============================
    # roi_frame = cv2.medianBlur(roi_frame, 5)
    roi_frame = cv2.blur(roi_frame, (5, 5))

    # ==============================
    # COLOR FILTER (GREY BALL)
    # ==============================
    blur = cv2.GaussianBlur(roi_frame, (5, 5    ), 0)
    hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

    lower = np.array([0, 0, 80])
    upper = np.array([180, 60, 200])

    mask = cv2.inRange(hsv, lower, upper)
    mask = cv2.erode(mask, None, 2)
    mask = cv2.dilate(mask, None, 2)

    masked = cv2.bitwise_and(roi_frame, roi_frame, mask=mask)

    gray = cv2.cvtColor(masked, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (9, 9), 2)

#     # ==============================
# # COLOR FILTER (ORANGE BALL)
# # ==============================
# blur = cv2.GaussianBlur(roi_frame, (5, 5), 0)
# hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

# # ORANGE RANGE (tune if needed)
# lower = np.array([5, 120, 120])
# upper = np.array([20, 255, 255])

# mask = cv2.inRange(hsv, lower, upper)

# # Clean mask
# mask = cv2.erode(mask, None, iterations=2)
# mask = cv2.dilate(mask, None, iterations=2)

# # Apply mask
# masked = cv2.bitwise_and(roi_frame, roi_frame, mask=mask)

# gray = cv2.cvtColor(masked, cv2.COLOR_BGR2GRAY)
# gray = cv2.GaussianBlur(gray, (9, 9), 2)

    # ==============================
    # HOUGH CIRCLES
    # ==============================
    circles = cv2.HoughCircles(
        gray,
        cv2.HOUGH_GRADIENT,
        dp=1.2,
        minDist=50,
        param1=50,
        param2=20,
        minRadius=5,
        maxRadius=60
    )

    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        circles = sorted(circles, key=lambda c: c[2], reverse=True)

        x, y, r = circles[0]

        x_full = x + x_roi
        y_full = y + y_roi

        # ==============================
        # POSITION (cm)
        # ==============================
        rel_x = x_full - origin_x
        position_cm = m * rel_x + c

        # ==============================
        # PID → THETA
        # ==============================
        current_time = time.time()
        dt = current_time - last_time
        last_time = current_time
# ==============================
# POSITION DEADBAND (±1 cm)
# ==============================
        deadband = 0.3

        if position_cm > deadband:
            error = position_cm - deadband
        elif position_cm < -deadband:
            error = position_cm + deadband
        else:
            error = position_cm * (abs(position_cm) / deadband)
        integral += error * dt
        # Clamp integral
        integral = max(min(integral, 10), -10)
        derivative = (error - prev_error) / dt if dt > 0 else 0

        theta = Kp * error + Ki * integral + Kd * derivative
        prev_error = error

        print(f"Pos: {position_cm:.2f} cm | Theta: {theta:.2f}")

        # ==============================
        # SEND THETA
        # ==============================
        ser.write(f"{theta}\n".encode())

        # ==============================
        # DRAW
        # ==============================
        cv2.circle(frame, (x_full, y_full), r, (0, 255, 0), 2)
        cv2.circle(frame, (x_full, y_full), 4, (0, 0, 255), -1)

        cv2.putText(frame, f"{theta:.2f}",
                    (x_full + 10, y_full),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6, (0, 255, 0), 2)

    # ==============================
    # DRAW ROI + ORIGIN
    # ==============================
    cv2.rectangle(frame,
                  (x_roi, y_roi),
                  (x_roi + w_roi, y_roi + h_roi),
                  (255, 0, 0), 2)

    cv2.circle(frame, (origin_x, origin_y), 5, (255, 255, 0), -1)

    # ==============================
    # DISPLAY
    # ==============================
    cv2.imshow("Tracking", frame)
    cv2.imshow("Mask", mask)

    # ==============================
    # KEYBOARD CONTROL
    # ==============================
    key = cv2.waitKey(1) & 0xFF

    if key == ord('p'):
        try:
            user_pid = input("Update Kp,Ki,Kd: ")
            if ',' in user_pid:
                Kp, Ki, Kd = map(float, user_pid.split(','))
                print(f"Updated PID: {Kp}, {Ki}, {Kd}")
        except:
            print("Invalid PID")

    elif key == 27:
        break

    time.sleep(0.02)  # stabilize loop

# ==============================
# CLEANUP
# ==============================
cap.release()
ser.close()
cv2.destroyAllWindows()