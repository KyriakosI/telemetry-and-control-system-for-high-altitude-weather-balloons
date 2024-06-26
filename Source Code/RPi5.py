import serial
import csv
import tkinter as tk
from tkinter import ttk
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
import webbrowser
from gmplot import gmplot  # Import gmplot library

# Initialize serial port
ser = serial.Serial('/dev/ttyUSB1', 9600, timeout=1)
ser.reset_input_buffer()

# Create Tkinter window
root = tk.Tk()
root.title("Data Display Prototype")

# Create a notebook (tabs)
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

# Create frames for each tab
data_frame = ttk.Frame(notebook)
temperature_frame = ttk.Frame(notebook)
humidity_frame = ttk.Frame(notebook)
pressure_frame = ttk.Frame(notebook)
altitude_frame = ttk.Frame(notebook)
speed_frame = ttk.Frame(notebook)
map_frame = ttk.Frame(notebook)  # Add a new frame for Google Maps
map_frame.pack(fill="both", expand=True)  # Pack the map frame to make it visible

# Add frames to notebook with corresponding tab titles
notebook.add(data_frame, text="Received Data")
notebook.add(temperature_frame, text="Temperature Plot")
notebook.add(humidity_frame, text="Humidity Plot")
notebook.add(pressure_frame, text="Pressure Plot")
notebook.add(altitude_frame, text="Altitude Plot")
notebook.add(speed_frame, text="Speed Plot")
notebook.add(map_frame, text="Google Map")  # Add Google Map tab

# Initialize data dictionary
data = {'Date': '', 'Time': '', 'Temperature': '', 'Humidity': '', 'Pressure': '', 'Latitude': '', 'Longitude': '', 'Altitude': '', 'Speed': ''}

# Define CSV file path and fieldnames
csv_file = '/home/cowcaine/Desktop/Telemetry_files/data.csv'
fieldnames = ['Date', 'Time', 'Temperature', 'Humidity', 'Pressure', 'Latitude', 'Longitude', 'Altitude', 'Speed']

# Initialize lists to store data for plotting
timestamps = []
temperatures = []
humidities = []
pressures = []
altitudes = []
speeds = []
latitudes = []  # Store latitude data for plotting route
longitudes = []  # Store longitude data for plotting route

# Initialize plot objects
fig_temperature, ax_temperature = plt.subplots(figsize=(8, 6))
fig_humidity, ax_humidity = plt.subplots(figsize=(8, 6))
fig_pressure, ax_pressure = plt.subplots(figsize=(8, 6))
fig_altitude, ax_altitude = plt.subplots(figsize=(8, 6))
fig_speed, ax_speed = plt.subplots(figsize=(8, 6))

# Initialize plot lines
line_temperature, = ax_temperature.plot([], [], marker='o', linestyle='-')
line_humidity, = ax_humidity.plot([], [], marker='o', linestyle='-')
line_pressure, = ax_pressure.plot([], [], marker='o', linestyle='-')
line_altitude, = ax_altitude.plot([], [], marker='o', linestyle='-')
line_speed, = ax_speed.plot([], [], marker='o', linestyle='-')

# Create a label for displaying unexpected messages
unexpected_message_label = ttk.Label(root, text="", font=("Helvetica", 14), foreground="red")
unexpected_message_label.pack(side=tk.BOTTOM, pady=10)

# Function to receive data from serial, update UI, and write to CSV
def receive_update_and_write():
    global last_written_data
    global data_written
    
    if ser.in_waiting > 0:
        line = ser.readline().decode('utf-8').rstrip()
        
        if line.startswith('Date'):
            data['Date'] = line.split(': ')[1]
            
        elif line.startswith('Time'):
            data['Time'] = line.split(': ')[1]
            
        elif line.startswith('Temperature'):
            data['Temperature'] = line.split(': ')[1]
            
        elif line.startswith('Humidity'):
            humidity_str = line.split(': ')[1]
            if humidity_str != 'nan':
                data['Humidity'] = humidity_str
            
        elif line.startswith('Pressure'):
            data['Pressure'] = line.split(': ')[1]
            
        elif line.startswith('Latitude'):
            latitude_str = line.split(': ')[1]
            if latitude_str != '00.000000':
                data['Latitude'] = latitude_str
                latitudes.append(float(data['Latitude']))  # Store latitude data
                
        elif line.startswith('Longitude'):
            longitude_str = line.split(': ')[1]
            if longitude_str != '00.000000':
                data['Longitude'] = longitude_str
                longitudes.append(float(data['Longitude']))  # Store longitude data
                
        elif line.startswith('Altitude'):
            altitude_str = line.split(': ')[1]
            if altitude_str != '0.00':
                data['Altitude'] = altitude_str
            
        elif line.startswith('Speed'):
            speed_str = line.split(': ')[1]
            if speed_str != '0.00':
                data['Speed'] = speed_str
            
        else:
            unexpected_message_label.config(text="Received unexpected message: " + line)  # Update unexpected message label
            
        # Reset the data_written flag when new data is received
        data_written = False
            
        update_ui()
        update_plot()
        
        # Check if the current data is complete and different from the last one written to CSV
        if data['Time'] != last_written_data.get('Time', ''):
            write_to_csv(data)
            last_written_data = data.copy()  # Update last_written_data with the current data
            data_written = True  # Set the flag to True indicating data has been written
            # Reset error message label when all data values are filled
            unexpected_message_label.config(text="")

# Function to update UI labels
def update_ui():
    for key, value in data.items():
        label_vars[key].set(f"{key}: {value}")

# Function to write data to CSV
def write_to_csv(data):
    with open(csv_file, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerow(data)

# Function to update plot data
def update_plot():

    if data['Time'] and data['Temperature'] and data['Humidity'] and data['Pressure'] and data['Altitude'] and data['Speed']:
        timestamps.append(datetime.strptime(data['Time'], "%H:%M:%S"))
        temperatures.append(float(data['Temperature'].split()[0]))
        humidities.append(float(data['Humidity'].split()[0]))
        pressures.append(float(data['Pressure'].split()[0]))
        altitudes.append(float(data['Altitude'].split()[0]))
        speeds.append(float(data['Speed'].split()[0]))
        
        plot_data()

def plot_data():
    plot_temperature()
    plot_humidity()
    plot_pressure()
    plot_altitude()
    plot_speed()


def plot_temperature():
    ax_temperature.clear()
    ax_temperature.plot(timestamps, temperatures, linestyle='-', color='brown')
    ax_temperature.set_xlabel('Time')
    ax_temperature.set_ylabel('Temperature (°C)')
    ax_temperature.set_title('Temperature/Time')
    ax_temperature.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    temperature_canvas.draw()
    
    
def plot_humidity():
    ax_humidity.clear()
    ax_humidity.plot(timestamps, humidities, linestyle='-', color='blue')
    ax_humidity.set_xlabel('Time')
    ax_humidity.set_ylabel('Humidity %)')
    ax_humidity.set_title('Humidity/Time')
    ax_humidity.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    humidity_canvas.draw()

    
def plot_pressure():
    ax_pressure.clear()
    ax_pressure.plot(timestamps, pressures, linestyle='-', color='red')
    ax_pressure.set_xlabel('Time')
    ax_pressure.set_ylabel('Pressure (hPa)')
    ax_pressure.set_title('Pressure/Time')
    ax_pressure.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    pressure_canvas.draw()


def plot_altitude():
    ax_altitude.clear()
    ax_altitude.plot(timestamps, altitudes, linestyle='-', color='green')
    ax_altitude.set_xlabel('Time')
    ax_altitude.set_ylabel('Altitude (m)')
    ax_altitude.set_title('Altitude/Time')
    ax_altitude.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    altitude_canvas.draw()


def plot_speed():
    ax_speed.clear()
    ax_speed.plot(timestamps, speeds, linestyle='-', color='orange')
    ax_speed.set_xlabel('Time')
    ax_speed.set_ylabel('Speed (km/h)')
    ax_speed.set_title('Speed/Time')
    ax_speed.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    speed_canvas.draw()

  
# Function to plot Google Maps with route
def plot_google_map():

    if len(latitudes) < 2 or len(longitudes) < 2:
        # Not enough data points to draw a route
        return

    # Initialize the Google Maps plot with the first pair of coordinates
    gmap_plot = gmplot.GoogleMapPlotter(latitudes[0], longitudes[0], 16)

    # Plot the route using consecutive pairs of latitude and longitude coordinates
    gmap_plot.plot(latitudes, longitudes, 'cornflowerblue', edge_width=10)

    # Save the map as an HTML file
    gmap_plot.draw("map_with_route.html")

    # Open the map in the default web browser
    webbrowser.open("map_with_route.html")


# Initialize last_written_data dictionary
last_written_data = {'Date': '', 'Time': '', 'Temperature': '', 'Humidity': '', 'Pressure': '', 'Latitude': '', 'Longitude': '', 'Altitude': '', 'Speed': ''}

# Create labels to display data
label_vars = {key: tk.StringVar() for key in data.keys()}
labels = {key: ttk.Label(data_frame, textvariable=label_vars[key], font=("Helvetica", 14)) for key in data.keys()}
for i, (key, label) in enumerate(labels.items()):
    label.grid(row=i, column=0, sticky="w")
    

# Create Matplotlib canvas widgets
temperature_canvas = FigureCanvasTkAgg(fig_temperature, master=temperature_frame)
humidity_canvas = FigureCanvasTkAgg(fig_humidity, master=humidity_frame)
pressure_canvas = FigureCanvasTkAgg(fig_pressure, master=pressure_frame)
altitude_canvas = FigureCanvasTkAgg(fig_altitude, master=altitude_frame)
speed_canvas = FigureCanvasTkAgg(fig_speed, master=speed_frame)

# Pack canvas widgets
temperature_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
humidity_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
pressure_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
altitude_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
speed_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# Button to plot Google Map with route
plot_map_button = ttk.Button(map_frame, text="Plot Google Map with Route", command=plot_google_map)
plot_map_button.pack(pady=10)

# Function to continuously receive, update UI, and write to CSV
def receive_update_and_write_wrapper():
    receive_update_and_write()
    root.after(100, receive_update_and_write_wrapper)

# Start receiving, updating UI, and writing to CSV
receive_update_and_write_wrapper()

# Create a spacer label for better spacing
spacer_label = ttk.Label(data_frame, text=" ", font=("Helvetica", 14))
spacer_label.grid(row=len(data), column=0, pady=10)

# Add your name label
name_label = ttk.Label(root, text="by Kyriakos Iosif", font=("Helvetica", 10))
name_label.pack(side=tk.RIGHT, padx=10, pady=10)

# Run Tkinter event loop
root.mainloop()
