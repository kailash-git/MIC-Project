import serial
import pandas as pd
import threading

# Serial setup
ser = serial.Serial('COM5', 115200)

data = []   # temporary storage
stop_flag = False


# Thread to detect Enter key
def stop_on_enter():
    global stop_flag
    input("Press ENTER to stop...\n")
    stop_flag = True


threading.Thread(target=stop_on_enter, daemon=True).start()

print("Reading data...\n")

while not stop_flag:
    line = ser.readline().decode().strip()
    print(line)

    try:
        # Extract number from "distance: XX cm"
        value = float(line.split()[1])
        data.append(value)
    except Exception:
        pass


# Convert to pandas Series
distance_series = pd.Series(data, name="distance_cm")

# Save to CSV
distance_series.to_csv("distance_data.csv", index=False)

print("\nSaved to distance_data.csv ✅")

