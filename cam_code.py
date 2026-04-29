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
# SERIAL SETUP (ADDED)
# ==============================
ser = serial.Serial('COM5', 115200)
time.sleep(2)

# ==============================
# ✅ PID INPUT (ONLY ONCE)
# ==============================
print("Enter PID values:")

Kp = float(input("Enter Kp: "))
Ki = float(input("Enter Ki: "))
Kd = float(input("Enter Kd: "))

pid_string = f"P,{Kp},{Ki},{Kd}\n"
ser.write(pid_string.encode())

print("PID sent to Arduino!")
time.sleep(1)

# ==============================
# ORIGINAL CODE STARTS (UNCHANGED)
# ==============================
stream_url = "http://192.168.0.145:81/stream"
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

    cv2.putText(
        frame,
        "Press ENTER to select ROI",
        (20, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 255),
        2
    )

    cv2.imshow("Live Feed", frame)

    key = cv2.waitKey(1) & 0xFF

    if key == 13:  # ENTER
        freeze_frame = frame.copy()
        break
    elif key == 27:  # ESC
        cap.release()
        cv2.destroyAllWindows()
        exit()

# ==============================
# STEP 2: SELECT ROI
# ==============================
roi = cv2.selectROI(
    "Select ROI",
    freeze_frame,
    fromCenter=False,
    showCrosshair=True
)
cv2.destroyWindow("Select ROI")

x_roi, y_roi, w_roi, h_roi = roi

# ==============================
# DEFINE ORIGIN (CENTER OF ROI)
# ==============================
origin_x = x_roi + w_roi // 2
origin_y = y_roi + h_roi // 2

print(f"Origin (ROI center): ({origin_x}, {origin_y})")

# ==============================
# MAIN LOOP
# ==============================
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.resize(frame, (640, 480))

    # Crop ROI
    roi_frame = frame[y_roi:y_roi + h_roi, x_roi:x_roi + w_roi]

    # ==============================
    # COLOR FILTER (GREY BALL)
    # ==============================
    blur = cv2.GaussianBlur(roi_frame, (5, 5), 0)
    hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

    lower = np.array([0, 0, 60])
    upper = np.array([180, 40, 160])

    mask = cv2.inRange(hsv, lower, upper)

    # Clean mask
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    # ==============================
    # APPLY MASK
    # ==============================
    masked = cv2.bitwise_and(roi_frame, roi_frame, mask=mask)

    gray = cv2.cvtColor(masked, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (9, 9), 2)

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
        circles = sorted(circles[0], key=lambda c: c[2], reverse=True)

        found = False

        for (x, y, r) in circles:
            if 20.1 < r < 33.5:
                x, y, r = int(x), int(y), int(r)
                found = True
                break

        if found:
            x_full = int(x + x_roi)
            y_full = int(y + y_roi)

            rel_x = x_full - origin_x
            rel_y = origin_y - y_full

            position_cm = m * rel_x + c

            print(f"Position: {position_cm:.2f} cm")

            ser.write(f"{position_cm}\n".encode())

            cv2.circle(frame, (x_full, y_full), r, (0, 255, 0), 2)
            cv2.circle(frame, (x_full, y_full), 4, (0, 0, 255), -1)

            cv2.putText(
                frame,
                f"{position_cm:.2f} cm",
                (x_full + 10, y_full),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )
    # ==============================
    # DRAW ROI + ORIGIN
    # ==============================
    cv2.rectangle(
        frame,
        (x_roi, y_roi),
        (x_roi + w_roi, y_roi + h_roi),
        (255, 0, 0),
        2
    )

    cv2.circle(frame, (origin_x, origin_y), 5, (255, 255, 0), -1)
    cv2.putText(
        frame,
        "Origin",
        (origin_x + 5, origin_y - 5),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (255, 255, 0),
        2
    )

    cv2.imshow("Tracking", frame)
    cv2.imshow("Mask", mask)
    cv2.imshow("Masked ROI", masked)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
ser.close()
cv2.destroyAllWindows()