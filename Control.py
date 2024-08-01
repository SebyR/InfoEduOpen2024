import tkinter as tk
from tkinter import ttk
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

# Function to transform angle to the desired range for servo 1
def transform_angle_to_range(angle, new_min=0, new_max=180):
    scaled_angle = new_min + ((angle + 180) / 360) * (new_max - new_min)
    return scaled_angle

# Function to calculate servo value for a desired distance
def calculate_servo_value_for_distance(distance):
    # Define the minimum and maximum distances
    min_distance = 0.2  # Minimum distance in meters
    max_distance = 1.4  # Maximum distance in meters

    # Define the servo value range
    min_servo_value = 130
    max_servo_value = 0

    # Check bounds
    if distance >= max_distance:
        return max_servo_value
    elif distance <= min_distance:
        return min_servo_value
    else:
        # Linear interpolation
        # We reverse the scaling to get a decreasing value with increasing distance
        servo_value = min_servo_value - (distance - min_distance) * (min_servo_value - max_servo_value) / (max_distance - min_distance)
        return max(0, min(servo_value, 100))

# Function to calculate the angle based on x, y coordinates
def calculate_angle(x, y):
    angle_radians = math.atan2(y, x)  # Calculate the angle in radians
    angle_degrees = math.degrees(angle_radians)  # Convert to degrees
    return angle_degrees + 90

# Function to calculate and set the servo values based on X, Y coordinates
def set_target_position():
    try:
        x = float(x_entry.get())
        y = float(y_entry.get())

        # Calculate the angle for servo 1
        angle = calculate_angle(x, y)
        transformed_angle = angle
        print(angle)
        slider1.set(transformed_angle)

        # Calculate the distance for servo 2
        distance = math.sqrt(x**2 + y**2)
        servo_value = calculate_servo_value_for_distance(distance)
        slider2.set(servo_value)

        # Update status labels
        angle_label.config(text=f"Angle: {angle:.2f}° -> Servo 1: {transformed_angle:.2f}")
        distance_label.config(text=f"Distance: {distance:.2f} meters -> Servo 2: {servo_value:.2f}")

        # Update the rectangle orientation
        update_rectangle_orientation()

    except ValueError:
        angle_label.config(text="Invalid input! Please enter numbers.")
        distance_label.config(text="")

# Function to update rectangle orientation
def update_rectangle_orientation():
    angle = slider1.get()  # Get the angle from the slider

    # Correct the angle if reversed
    angle = -angle  # Reverse the angle direction if needed

    canvas.delete("all")  # Clear the canvas

    # Define rectangle dimensions (short side is height)
    rect_width = 30
    rect_height = 10

    # Define the center of the canvas
    center_x = canvas.winfo_width() / 2
    center_y = canvas.winfo_height() / 2

    # Initialize the rectangle with its short side up
    initial_angle = 90  # Start with the short side facing up

    # Calculate the rotation angle of the short side to align with (x, y)
    angle_radians = math.radians(angle + initial_angle)

    # Rectangle points relative to the center (short side aligned with y-axis)
    points = [
        (-rect_height / 2, -rect_width / 2),
        (rect_height / 2, -rect_width / 2),
        (rect_height / 2, rect_width / 2),
        (-rect_height / 2, rect_width / 2),
    ]

    # Rotate points
    rotated_points = [
        (
            center_x + x * math.cos(angle_radians) - y * math.sin(angle_radians),
            center_y + x * math.sin(angle_radians) + y * math.cos(angle_radians)
        )
        for x, y in points
    ]

    # Draw the rotated rectangle
    canvas.create_polygon(rotated_points, fill="blue", outline="black")

    # Draw the red dot at the specified (x, y) position
    try:
        x = float(x_entry.get())
        y = float(y_entry.get())

        # Convert (x, y) from meters to canvas coordinates
        dot_y = center_x - x * 100  # Assume 1 meter = 100 pixels
        dot_x = center_y - y * 100  # Invert y-axis for correct orientation

        # Draw the red dot
        dot_radius = 5
        canvas.create_oval(dot_x - dot_radius, dot_y - dot_radius,
                           dot_x + dot_radius, dot_y + dot_radius, fill="red", outline="black")

    except ValueError:
        pass  # If input is invalid, just skip drawing the dot

# Function to send data continuously
def send_data(ip, port, data):

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((ip, port))
        data_string = ','.join(data)
        client_socket.sendall(data_string.encode('utf-8'))
        client_socket.close()


# Function to send data continuously
def send_data_continuously():
    while running:
        # Get current values from the sliders
        value1 = int(slider1.get())
        value2 = int(slider2.get())

        # Use the current shoot value (10 or 90)
        value3 = shoot_value

        # Create the data string with spaces
        data_string = f"{value1} {value2} {value3}\n"

        # Send the data via serial
        try:
            ser.write(data_string.encode('utf-8'))
        except:
            pass

        # Update the status label (in a thread-safe manner)
        status_label.config(text=f"Sent: {data_string.strip()}")
        print(data_string.strip())

        # Brief delay to avoid overwhelming the serial port and keep the UI responsive
        time.sleep(0.1)
        data = [str(value1), str(value2), str(x_entry.get()), str(y_entry.get())]
        try:
            send_data(ip, ipport, data)
        except: pass

        #print("am trimis")
# Function to start sending data
def start_sending():
    global running
    if not running:  # Start only if not already running
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

# New function to set up the catapult interface
def setup_catapult_interface():
    # Create the main window
    root = tk.Tk()
    root.title("Serial Data Sender")

    # Create and place widgets for sliders
    label1 = ttk.Label(root, text="Servo 1 (Rotation, 5-175):")
    label1.grid(row=0, column=0, padx=10, pady=5)
    global slider1
    slider1 = ttk.Scale(root, from_=5, to=175, orient="horizontal")
    slider1.set(90)  # Set initial value to 90
    slider1.grid(row=0, column=1, padx=10, pady=5)

    label2 = ttk.Label(root, text="Servo 2 (Shooting, 10-190):")
    label2.grid(row=1, column=0, padx=10, pady=5)
    global slider2
    slider2 = ttk.Scale(root, from_=0, to=190, orient="horizontal")
    slider2.set(90)  # Set initial value to 90
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

    # Run the main loop
    root.mainloop()

    # Close the serial connection when done
    ser.close()



# Call the new function to set up the interface
setup_catapult_interface()
