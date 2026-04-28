import matplotlib.pyplot as plt
import re

print("Paste your data (press ENTER twice to finish):")

# ==============================
# TAKE MULTILINE INPUT
# ==============================
lines = []
while True:
    line = input()
    if line.strip() == "":
        break
    lines.append(line)

# ==============================
# PARSE DATA
# ==============================
raw_points = []
smooth_points = []

pattern = r"Raw:\s*\((\d+),\s*(\d+)\)\s*\|\s*Smoothed:\s*\((\d+),\s*(\d+)\)"

for line in lines:
    match = re.search(pattern, line)
    if match:
        rx, ry, sx, sy = map(int, match.groups())
        raw_points.append((rx, ry))
        smooth_points.append((sx, sy))

# ==============================
# EXTRACT X, Y
# ==============================
raw_x = [p[0] for p in raw_points]
raw_y = [p[1] for p in raw_points]

smooth_x = [p[0] for p in smooth_points]
smooth_y = [p[1] for p in smooth_points]

t = list(range(len(raw_points)))

# ==============================
# PLOT X
# ==============================
plt.figure()
plt.plot(t, raw_x, marker='o', label='Raw X')
plt.plot(t, smooth_x, marker='o', label='Smoothed X')
plt.title("Raw vs Smoothed (X)")
plt.xlabel("Frame")
plt.ylabel("X Position")
plt.legend()
plt.grid()

# ==============================
# PLOT Y
# ==============================
plt.figure()
plt.plot(t, raw_y, marker='o', label='Raw Y')
plt.plot(t, smooth_y, marker='o', label='Smoothed Y')
plt.title("Raw vs Smoothed (Y)")
plt.xlabel("Frame")
plt.ylabel("Y Position")
plt.legend()
plt.grid()

plt.show()