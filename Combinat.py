import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import serial
import threading
import time
import math
import socket

ip = "127.0.0.1"
ipport = 5000

# Initialize the serial connection
try:
    ser = serial.Serial('COM15', 115200)  # Change 'COM15' to your serial port
except:
    pass

# Global variables
running = False
shoot_value = 90  # Initial value for shooting

def distance(x, y):
    return math.dist([x, y], [0, 0])

# Function to transform angle to the desired range for servo 1
def transform_angle_to_range(angle, new_min=0, new_max=180):
    scaled_angle = new_min + ((angle + 180) / 360) * (new_max - new_min)
    return scaled_angle

# Function to calculate servo value for a desired distance
def calculate_servo_value_for_distance(distance):
    min_distance = 0.2  # Minimum distance in meters
    max_distance = 1.4  # Maximum distance in meters
    min_servo_value = 130
    max_servo_value = 0
    if distance >= max_distance:
        return max_servo_value
    elif distance <= min_distance:
        return min_servo_value
    else:
        servo_value = min_servo_value - (distance - min_distance) * (min_servo_value - max_servo_value) / (max_distance - min_distance)
        return max(0, min(servo_value, 100))

# Function to calculate the angle based on x, y coordinates
def calculate_angle(x, y):
    angle_radians = math.atan2(y, x)
    angle_degrees = math.degrees(angle_radians)
    return angle_degrees + 90

# Function to calculate and set the servo values based on X, Y coordinates
def set_target_position():
    try:
        x = float(x_entry.get())
        y = float(y_entry.get())
        angle = calculate_angle(x, y)
        transformed_angle = angle
        slider1.set(transformed_angle)
        distance = math.sqrt(x**2 + y**2)
        servo_value = calculate_servo_value_for_distance(distance)
        slider2.set(servo_value)
        angle_label.config(text=f"Angle: {angle:.2f}° -> Servo 1: {transformed_angle:.2f}")
        distance_label.config(text=f"Distance: {distance:.2f} meters -> Servo 2: {servo_value:.2f}")
        update_rectangle_orientation()
    except ValueError:
        angle_label.config(text="Invalid input! Please enter numbers.")
        distance_label.config(text="")

# Function to update rectangle orientation
def update_rectangle_orientation():
    angle = slider1.get()
    angle = -angle
    canvas.delete("all")
    rect_width = 30
    rect_height = 10
    center_x = canvas.winfo_width() / 2
    center_y = canvas.winfo_height() / 2
    initial_angle = 90
    angle_radians = math.radians(angle + initial_angle)
    points = [
        (-rect_height / 2, -rect_width / 2),
        (rect_height / 2, -rect_width / 2),
        (rect_height / 2, rect_width / 2),
        (-rect_height / 2, rect_width / 2),
    ]
    rotated_points = [
        (
            center_x + x * math.cos(angle_radians) - y * math.sin(angle_radians),
            center_y + x * math.sin(angle_radians) + y * math.cos(angle_radians)
        )
        for x, y in points
    ]
    canvas.create_polygon(rotated_points, fill="blue", outline="black")
    try:
        x = float(x_entry.get())
        y = float(y_entry.get())
        dot_y = center_x - x * 100
        dot_x = center_y - y * 100
        dot_radius = 5
        canvas.create_oval(dot_x - dot_radius, dot_y - dot_radius,
                           dot_x + dot_radius, dot_y + dot_radius, fill="red", outline="black")
    except ValueError:
        pass

# Function to send data continuously
def send_data(ip, port, data):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((ip, port))
    data_string = ','.join(data)
    client_socket.sendall(data_string.encode('utf-8'))
    client_socket.close()

def send_data_continuously():
    while running:
        value1 = int(slider1.get())
        value2 = int(slider2.get())
        value3 = shoot_value
        data_string = f"{value1} {value2} {value3}\n"
        try:
            ser.write(data_string.encode('utf-8'))
        except:
            pass
        status_label.config(text=f"Sent: {data_string.strip()}")
        print(data_string.strip())
        time.sleep(0.1)
        data = [str(value1), str(value2), str(x_entry.get()), str(y_entry.get())]
        send_data(ip, ipport, data)
        print("Data sent")

# Function to start sending data
def start_sending():
    global running
    if not running:
        running = True
        threading.Thread(target=send_data_continuously, daemon=True).start()

# Function to stop sending data
def stop_sending():
    global running
    running = False
    status_label.config(text="Stopped sending data.")

# Function to toggle the shoot value
def toggle_shoot():
    global shoot_value
    shoot_value = 10 if shoot_value == 90 else 90
    shoot_button.config(text=f"Shoot Value: {shoot_value}")

# Function to calculate and plot projectile trajectory
def calculate_and_plot_trajectory():
    try:
        v0 = float(speed_entry.get())
        angle = 70  # Use a fixed angle as you mentioned 70 degrees
        height = float(height_entry.get())
        angle_rad = math.radians(angle)
        g = 9.81
        t_flight = (v0 * math.sin(angle_rad) + math.sqrt((v0 * math.sin(angle_rad))**2 + 2 * g * height)) / g
        t_values = [i * t_flight / 100 for i in range(101)]
        x_values = [v0 * math.cos(angle_rad) * t for t in t_values]
        y_values = [height + v0 * math.sin(angle_rad) * t - 0.5 * g * t**2 for t in t_values]
        landing_point = x_values[-1]
        ax.clear()
        ax.plot(x_values, y_values)
        ax.set_title("Projectile Trajectory")
        ax.set_xlabel("Distance (meters)")
        ax.set_ylabel("Height (meters)")
        ax.grid(True)
        ax.annotate(f"Landing Point: {landing_point:.2f} m", xy=(landing_point, 0), xytext=(landing_point + 1, 1),
                    arrowprops=dict(facecolor='black', arrowstyle="->"))
        canvas.draw()
    except ValueError:
        error_label.config(text="Invalid input! Please enter valid numbers.")

# Function to open the new window for trajectory visualization
def open_trajectory_window():
    traj_window = tk.Toplevel(root)
    traj_window.title("Projectile Trajectory")
    tk.Label(traj_window, text="Initial Speed (m/s):").grid(row=0, column=0, padx=10, pady=5)
    global speed_entry
    speed_entry = ttk.Entry(traj_window)
    speed_entry.grid(row=0, column=1, padx=10, pady=5)
    speed_entry.insert(0, "10")
    tk.Label(traj_window, text="Launch Height (meters):").grid(row=1, column=0, padx=10, pady=5)
    global height_entry
    height_entry = ttk.Entry(traj_window)
    height_entry.grid(row=1, column=1, padx=10, pady=5)
    height_entry.insert(0, "0")
    plot_button = ttk.Button(traj_window, text="Plot Trajectory", command=calculate_and_plot_trajectory)
    plot_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10)
    global error_label
    error_label = ttk.Label(traj_window, text="")
    error_label.grid(row=4, column=0, columnspan=2, padx=10, pady=5)
    global fig, ax, canvas
    fig = Figure(figsize=(6, 4), dpi=100)
    ax = fig.add_subplot(111)
    canvas = FigureCanvasTkAgg(fig, master=traj_window)
    canvas.get_tk_widget().grid(row=5, column=0, columnspan=2, padx=10, pady=10)

# Create the main window
root = tk.Tk()
root.title("Catapult Control and Trajectory Plotter")

# Create and place widgets for sliders
label1 = ttk.Label(root, text="Servo 1 (Rotation, 5-175):")
label1.grid(row=0, column=0, padx=10, pady=5)
global slider1
slider1 = ttk.Scale(root, from_=5, to=175, orient="horizontal")
slider1.set(90)
slider1.grid(row=0, column=1, padx=10, pady=5)

label2 = ttk.Label(root, text="Servo 2 (Shooting, 10-190):")
label2.grid(row=1, column=0, padx=10, pady=5)
global slider2
slider2 = ttk.Scale(root, from_=0, to=190, orient="horizontal")
slider2.set(90)
slider2.grid(row=1, column=1, padx=10, pady=5)

global shoot_button
shoot_button = ttk.Button(root, text="Shoot Value: 90", command=toggle_shoot)
shoot_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

start_button = ttk.Button(root, text="Start Sending", command=start_sending)
start_button.grid(row=3, column=0, padx=10, pady=10)

stop_button = ttk.Button(root, text="Stop Sending", command=stop_sending)
stop_button.grid(row=3, column=1, padx=10, pady=10)

# Create and place widgets for target position (X, Y)
x_label = ttk.Label(root, text="X Coordinate (meters):")
x_label.grid(row=4, column=0, padx=10, pady=5)
global x_entry
x_entry = ttk.Entry(root)
x_entry.grid(row=4, column=1, padx=10, pady=5)

y_label = ttk.Label(root, text="Y Coordinate (meters):")
y_label.grid(row=5, column=0, padx=10, pady=5)
global y_entry
y_entry = ttk.Entry(root)
y_entry.grid(row=5, column=1, padx=10, pady=5)

target_button = ttk.Button(root, text="Set Target Position", command=set_target_position)
target_button.grid(row=6, column=0, columnspan=2, padx=10, pady=10)

global angle_label
angle_label = ttk.Label(root, text="Angle: ")
angle_label.grid(row=7, column=0, columnspan=2, padx=10, pady=5)

global distance_label
distance_label = ttk.Label(root, text="Distance: ")
distance_label.grid(row=8, column=0, columnspan=2, padx=10, pady=5)

global status_label
status_label = ttk.Label(root, text="Status: Waiting to start...")
status_label.grid(row=9, column=0, columnspan=2, padx=10, pady=5)

# Create a canvas to draw the rectangle
global canvas
canvas = tk.Canvas(root, width=300, height=300, bg='white')
canvas.grid(row=10, column=0, columnspan=2, padx=10, pady=10)

# Initialize the rectangle orientation
update_rectangle_orientation()

# Add a button to open the trajectory window in the main interface
trajectory_button = ttk.Button(root, text="Open Trajectory Window", command=open_trajectory_window)
trajectory_button.grid(row=11, column=0, columnspan=2, padx=10, pady=10)

# Run the main loop
root.mainloop()

# Close the serial connection when done
ser.close()