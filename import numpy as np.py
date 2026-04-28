import numpy as np
import matplotlib.pyplot as plt

# Data
x = np.array([7.8, 11.8, 17.56, 22.58])
y = np.array([6.3, 13.3, 19.3, 25.3])

# Linear regression
a,b, c = np.polyfit(x, y, 2)

# Predicted values
y_pred = a* x**2+b* x + c

# Smooth line for better visualization
x_line = np.linspace(min(x), max(x), 100)
y_line = a* x_line**2+b* x_line + c

# Plot
plt.scatter(x, y, label="Data points")
plt.plot(x_line, y_line, label="Best-fit line")

# Labels
plt.xlabel("X values")
plt.ylabel("Y values")
plt.title("Linear Regression Plot")

plt.legend()
plt.grid()

plt.show()