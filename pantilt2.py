import msvcrt
import threading
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Parameters
frequency = 20  # Frequency in Hz
sampling_rate = 60  # Sampling rate in Hz
window_length = 5  # Display window length in seconds
amplitude = 100

def fileCheck():
    global frequency
    global amplitude
    while True:
        with open("config.txt", "r") as f:
            new_frequency = float(f.readline().strip())
            new_amplitude = float(f.readline().strip())
            if frequency != new_frequency or amplitude != new_amplitude:
                frequency = new_frequency
                amplitude = new_amplitude
        time.sleep(0.01)

# Initialize figure and axis
fig, ax = plt.subplots()
ax.set_xlim(0, window_length)
ax.set_ylim(-amplitude - 10, amplitude + 10)
line, = ax.plot([], [], lw=2)
plt.title("Sinusoidal")
plt.xlabel("Time (s)")
plt.ylabel("Amplitude")

# Initialize data arrays
x_data = np.arange(0, window_length, 1/sampling_rate)
y_data = np.zeros_like(x_data)

# Function to initialize the plot
def init():
    line.set_data([], [])
    return line,

# Function to update the plot
def update(frame):
    global x_data, y_data
    global sampling_rate
    
    # Compute the new sample
    current_time = frame / sampling_rate
    new_y = np.sin(2 * np.pi * frequency * current_time) * amplitude
    
    # Shift the y_data array to the left by one sample
    y_data = np.roll(y_data, -1)
    y_data[-1] = new_y
    
    # Update the x_data array
    x_data = np.linspace(current_time - window_length, current_time, len(y_data))

    print(max(y_data))
    # Update the axis limits
    ax.set_xlim(current_time - window_length, current_time)
    ax.set_ylim(min(y_data) * 1.1, max(y_data) * 1.1)
    
    # Update the plot data
    line.set_data(x_data, y_data)
    return line,

# Creating the Animation object
line_ani = animation.FuncAnimation(fig, update, frames=np.arange(0, frequency * 1000), init_func=init, interval=1000 / sampling_rate, blit=False)

check_thread = threading.Thread(target=fileCheck)
check_thread.start()

plt.show()