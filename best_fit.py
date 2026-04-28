import numpy as np
import matplotlib.pyplot as plt

# ==============================
# DATA
# ==============================
pixels = np.array([-157, -198, -260, 166, 200, 254])
cm = np.array([-12, -15, -20, 12, 15, 20])

# ==============================
# BEST FIT LINE
# ==============================
m, c = np.polyfit(pixels, cm, 1)

print(f"Slope (m): {m}")
print(f"Intercept (c): {c}")

# ==============================
# GENERATE LINE
# ==============================
x_line = np.linspace(min(pixels)-50, max(pixels)+50, 100)
y_line = m * x_line + c

# ==============================
# PLOT
# ==============================
plt.figure()

# Scatter points
plt.scatter(pixels, cm, label="Measured Data")

# Best fit line
plt.plot(x_line, y_line, label=f"Fit: y = {m:.4f}x + {c:.4f}")

# Axis labels
plt.xlabel("Pixels")
plt.ylabel("Distance (cm)")
plt.title("Pixel to Distance Calibration")

# Origin lines
plt.axhline(0)
plt.axvline(0)

# Grid + legend
plt.grid()
plt.legend()

# ==============================
# SHOW
# ==============================
plt.show()