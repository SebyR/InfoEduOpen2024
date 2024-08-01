import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import math
# pt servo lansare 75 => 0.7m real, 0.6m simulat
# Function to calculate the projectile's trajectory and plot it
def calculate_and_plot_trajectory():
    try:
        # Get input values
        v0 = float(speed_entry.get())
        angle = float(angle_entry.get())
        height = float(height_entry.get())

        # Convert angle to radians
        angle_rad = math.radians(angle)

        # Time of flight
        g = 9.81  # Acceleration due to gravity (m/s^2)
        t_flight = (v0 * math.sin(angle_rad) + math.sqrt((v0 * math.sin(angle_rad))**2 + 2 * g * height)) / g

        # Time intervals for plotting
        t_values = [i * t_flight / 100 for i in range(101)]

        # Calculate x and y values
        x_values = [v0 * math.cos(angle_rad) * t for t in t_values]
        y_values = [height + v0 * math.sin(angle_rad) * t - 0.5 * g * t**2 for t in t_values]

        # Find the landing point
        landing_point = x_values[-1]

        # Clear the previous plot
        ax.clear()

        # Plot the trajectory
        ax.plot(x_values, y_values)
        ax.set_title("Projectile Trajectory")
        ax.set_xlabel("Distance (meters)")
        ax.set_ylabel("Height (meters)")
        ax.grid(True)

        # Annotate the landing point
        ax.annotate(f"Landing Point: {landing_point:.2f} m", xy=(landing_point, 0), xytext=(landing_point + 1, 1),
                    arrowprops=dict(facecolor='black', arrowstyle="->"))

        # Refresh the canvas
        canvas.draw()

    except ValueError:
        error_label.config(text="Invalid input! Please enter valid numbers.")

# Function to open the new window for trajectory visualization
def open_trajectory_window():
    # Create a new window
    traj_window = tk.Toplevel(root)
    traj_window.title("Projectile Trajectory")

    # Create input fields for initial speed, angle, and launch height
    tk.Label(traj_window, text="Initial Speed (m/s):").grid(row=0, column=0, padx=10, pady=5)
    global speed_entry
    speed_entry = ttk.Entry(traj_window)
    speed_entry.grid(row=0, column=1, padx=10, pady=5)
    speed_entry.insert(0, "10")

    tk.Label(traj_window, text="Launch Angle (degrees):").grid(row=1, column=0, padx=10, pady=5)
    global angle_entry
    angle_entry = ttk.Entry(traj_window)
    angle_entry.grid(row=1, column=1, padx=10, pady=5)
    angle_entry.insert(0, "45")

    tk.Label(traj_window, text="Launch Height (meters):").grid(row=2, column=0, padx=10, pady=5)
    global height_entry
    height_entry = ttk.Entry(traj_window)
    height_entry.grid(row=2, column=1, padx=10, pady=5)
    height_entry.insert(0, "0")

    # Button to calculate and plot the trajectory
    plot_button = ttk.Button(traj_window, text="Plot Trajectory", command=calculate_and_plot_trajectory)
    plot_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

    # Label to display errors or status
    global error_label
    error_label = ttk.Label(traj_window, text="")
    error_label.grid(row=4, column=0, columnspan=2, padx=10, pady=5)

    # Create a Matplotlib figure for plotting
    global fig, ax, canvas
    fig = Figure(figsize=(6, 4), dpi=100)
    ax = fig.add_subplot(111)
    canvas = FigureCanvasTkAgg(fig, master=traj_window)
    canvas.get_tk_widget().grid(row=5, column=0, columnspan=2, padx=10, pady=10)

# Create the main window
root = tk.Tk()
root.title("Serial Data Sender")

# Add a button to open the trajectory window in the main interface
trajectory_button = ttk.Button(root, text="Open Trajectory Window", command=open_trajectory_window)
trajectory_button.grid(row=11, column=0, columnspan=2, padx=10, pady=10)

# Run the main loop
root.mainloop()