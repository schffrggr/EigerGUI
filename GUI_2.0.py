import tkinter as tk
from tkinter import ttk
from tkinter import Label
import requests
import ast
import time
from urllib.parse import quote



# List of changable configuration parameters for the DEiger detector
config_params = ['beam_center_x', 'beam_center_y', 'count_time', 'counting_mode', 'detector_distance', 'detector_orientation', 'element', 'fast_arm', 'frame_time', 'incident_energy', 'nimages', 'ntrigger', 'photon_energy', 'roi_mode', 'sample_name', 'threshold/1/energy', 'threshold/1/mode', 'threshold/2/energy', 'threshold/2/mode', 'threshold/difference/mode', 'threshold_energy', 'trigger_mode', 'detector_translation', 'kappa_increment', 'kappa_start', 'mask_to_zero', 'omega_increment', 'omega_start', 'phi_increment', 'phi_start', 'total_flux', 'trigger_start_delay', 'two_theta_increment', 'two_theta_start', 'virtual_pixel_correction_applied']


class ConnectionWidget:
    def __init__(self, root, config_params, callback, default_ip=""):
        self.root = root
        self.root.title("Eiger Connection")

        self.ip_address_var = tk.StringVar()
        self.ip_address_var.set("127.0.0.1")  # Set the default IP address

        self.create_widgets(config_params, callback)

    def create_widgets(self, config_params, callback):
        self.ip_address_label = ttk.Label(self.root, text="Enter IP Address:")
        self.ip_address_label.pack()

        self.ip_address_entry = ttk.Entry(self.root, textvariable=self.ip_address_var)
        self.ip_address_entry.pack()

        self.connect_button = ttk.Button(self.root, text="Connect", command=lambda: callback(self.ip_address_var.get()))
        self.connect_button.pack()

# Modify the connect_and_fetch function to pass the default IP address
def connect_and_fetch(ip_address):
    root_conn = tk.Tk()
    connection_widget = ConnectionWidget(root_conn, config_params, lambda ip: create_gui(ip, root_conn), ip_address)
    root_conn.mainloop()


class DEigerGUI:
    def __init__(self, root, ip_address):
        self.root = root
        self.root.title("Eiger GUI")

        self.ip_address = ip_address

        self.old_param_values = {}

        self.create_widgets()

    def create_widgets(self):
        self.status_label = ttk.Label(self.root, text="Status:")
        self.status_label.pack()

        self.config_frame = ttk.Frame(self.root)
        self.config_frame.pack()

        self.param_entries = {}

        self.fetch_params()

        for row, param in enumerate(config_params):
            col = row % 3  # Determine the column (0, 1, or 2)
            label = ttk.Label(self.config_frame, text=param.replace("_", " ").title())
            label.grid(row=row // 3, column=col * 2, padx=5, pady=5, sticky=tk.W)

            
            entry = ttk.Entry(self.config_frame)
            entry.grid(row=row // 3, column=col * 2 + 1, padx=5, pady=5)
            self.param_entries[param] = entry

            value = self.fetched_data.get(param)["value"]
            entry.insert(0, value)

        self.set_config_button = ttk.Button(self.root, text="Set Configuration", command=self.set_configuration)
        self.set_config_button.pack()

        # Data Interface section
        self.data_interface_frame = ttk.LabelFrame(self.root, text="Data Interface")
        self.data_interface_frame.pack(fill="both", expand="yes", padx=10, pady=10)

        self.enable_filewriter_button = ttk.Button(self.data_interface_frame, text="Enable Filewriter",
                                                   command=lambda: self.set_filewriter_mode('enabled'))
        self.enable_filewriter_button.grid(row=0, column=0, padx=5, pady=5)

        self.disable_filewriter_button = ttk.Button(self.data_interface_frame, text="Disable Filewriter",
                                                    command=lambda: self.set_filewriter_mode('disabled'))
        self.disable_filewriter_button.grid(row=0, column=1, padx=5, pady=5)

        self.enable_monitor_button = ttk.Button(self.data_interface_frame, text="Enable Monitor",
                                                command=lambda: self.set_monitor_mode('enabled'))
        self.enable_monitor_button.grid(row=1, column=0, padx=5, pady=5)

        self.disable_monitor_button = ttk.Button(self.data_interface_frame, text="Disable Monitor",
                                                 command=lambda: self.set_monitor_mode('disabled'))
        self.disable_monitor_button.grid(row=1, column=1, padx=5, pady=5)

        self.file_name_label = ttk.Label(self.data_interface_frame, text="File Name Pattern:")
        self.file_name_label.grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)

        self.file_name_entry = ttk.Entry(self.data_interface_frame)
        self.file_name_entry.grid(row=0, column=3, padx=5, pady=5)

        self.set_file_name_button = ttk.Button(self.data_interface_frame, text="Set File Name",
                                               command=self.set_file_name)
        self.set_file_name_button.grid(row=0, column=4, padx=5, pady=5)


       # Arm and Trigger section
        self.arm_trigger_frame = ttk.LabelFrame(self.root, text="Arm and Trigger")
        self.arm_trigger_frame.pack(fill="both", expand="yes", padx=10, pady=10)

        # Make a style for the bigger, green button
        style = ttk.Style()
        style.configure("BigGreen.TButton", font=("Helvetica", 12), foreground="black", background="green", padding=(20, 10))


        self.arm_trigger_button = ttk.Button(self.arm_trigger_frame, text="Arm and Trigger", command=self.perform_arm_trigger, style="BigGreen.TButton")
        self.arm_trigger_button.grid(row=0, column=0, padx=5, pady=5, columnspan=3, sticky=tk.E)

        self.disarm_button = ttk.Button(self.arm_trigger_frame, text="Disarm", command=self.disarm)
        self.disarm_button.grid(row=1, column=0, padx=5, pady=5, columnspan=3, sticky=tk.E)

        self.pause_label = ttk.Label(self.arm_trigger_frame, text="Pause Between Triggers (s):")
        self.pause_label.grid(row=0, column=4, padx=5, pady=5, sticky=tk.W)

        self.pause_entry = ttk.Entry(self.arm_trigger_frame)
        self.pause_entry.grid(row=0, column=5, padx=5, pady=5, sticky=tk.W)

        self.num_triggers_label = ttk.Label(self.arm_trigger_frame, text="Number of Triggers (integer):")
        self.num_triggers_label.grid(row=1, column=4, padx=5, pady=5, sticky=tk.W)

        self.num_triggers_entry = ttk.Entry(self.arm_trigger_frame)
        self.num_triggers_entry.grid(row=1, column=5, padx=5, pady=5, sticky=tk.W)

        self.trigger_button = ttk.Button(self.arm_trigger_frame, text="Arm and Trigger", command=self.trigger_detector)
        self.trigger_button.grid(row=1, column=6, padx=5, pady=5, sticky=tk.W)

        
        # Clear Buffer and Filewriter Storage section
        self.clear_frame = ttk.LabelFrame(self.root, text="Clear Buffer and Filewriter Storage")
        self.clear_frame.pack(fill="both", expand="yes", padx=10, pady=10)

        # Make a style for the small, red button
        style = ttk.Style()
        style.configure("SmallRed.TButton", font=("Helvetica", 8), foreground="red", background="red")

        # Clear Buffer button
        self.clear_buffer_button = ttk.Button(self.clear_frame, text="Clear Buffer", command=self.clear_buffer)
        self.clear_buffer_button.grid(row=0, column=0, padx=5, pady=5)

        # Clear Filewriter Storage button
        self.clear_filewriter_button = ttk.Button(self.clear_frame, text="!! Clear Filewriter Storage !!", command=self.clear_filewriter, style="SmallRed.TButton")
        self.clear_filewriter_button.grid(row=0, column=1, padx=5, pady=5)

        # Interrupt Measurement button
        self.interrupt_measurement_button = ttk.Button(self.clear_frame, text="Abort Measurement", command=self.interrupt_measurement)
        self.interrupt_measurement_button.grid(row=0, column=2, padx=5, pady=5)



    def fetch_params(self):
        self.fetched_data = self.fetch_param_values(config_params, self.ip_address)
        for param, value in self.fetched_data.items():
            self.old_param_values[param] = value

        self.update_status("Parameters fetched successfully.")
    
    
    def fetch_param_values(self, params, ip_address):
        fetched_data = {}

        for param in params:
            # URL encode the parameter name
            encoded_param = quote(param)

            # Construct the URL with the encoded parameter name
            url = f"http://{ip_address}/detector/api/1.8.0/config/{encoded_param}"
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()
                fetched_data[param] = {
                    "value": str(data.get("value", "Error")),
                    "value_type": data.get("value_type", "string")  # Default to string
                }
            else:
                fetched_data[param] = {
                    "value": "Error",
                    "value_type": "string"
                }

        return fetched_data

    def set_configuration(self):
        try:
            # Construct the base URL for setting detector configuration
            base_url = f"http://{self.ip_address}/detector/api/1.8.0/config/"

            for param in config_params:
                entry = self.param_entries[param]
                new_value = entry.get()
                old_data = self.old_param_values.get(param, {})

                fetched_value = old_data.get("value")
                fetched_value_type = old_data.get("value_type")

                if new_value != fetched_value:
                    if fetched_value_type == "bool":
                        new_value = ast.literal_eval(new_value)
                    elif fetched_value_type == "float":
                        new_value = float(new_value)
                    elif fetched_value_type == "uint":
                        new_value = int(new_value)

                    # Construct the specific URL for setting the parameter
                    url = f"{base_url}{param}"

                    # Make the PUT request for setting the detector configuration parameter
                    response = requests.put(url, json={"value": new_value})

                    # Check if the request was successful 
                    if response.status_code // 100 == 2:
                        self.old_param_values[param] = {
                            "value": new_value,
                            "value_type": fetched_value_type
                        }
                        self.update_status(f"Configuration set successfully for parameter: {param}")
                    else:
                        self.update_status(f"Error setting configuration for parameter {param}. Status code: {response.status_code}")
                else:
                    self.update_status(f"No change for parameter: {param}")

        except Exception as e:
            # Handle other exceptions or errors here
            self.update_status(f"Error setting configuration: {str(e)}")

    
    def clear_buffer(self):
        # Send command to clear the buffer
        url = f"http://{self.ip_address}/monitor/api/1.8.0/command/clear"
        response = requests.put(url)

        if response.status_code == 200:
            self.update_status("Buffer cleared.")
        else:
            self.update_status("Failed to clear buffer.")

    def clear_filewriter(self):
        # Send command to clear filewriter storage
        url = f"http://{self.ip_address}/filewriter/api/1.8.0/command/clear"
        response = requests.put(url)

        if response.status_code == 200:
            self.update_status("Filewriter storage cleared.")
        else:
            self.update_status("Failed to clear filewriter storage.")

    def set_filewriter_mode(self, mode):
        try:
            # Construct the URL for setting filewriter mode
            url = f"http://{self.ip_address}/filewriter/api/1.8.0/config/mode"

            # Prepare the data for the PUT request
            data = {"value": mode}

            # Make the PUT request using the requests library
            response = requests.put(url, json=data)

            # Check if the request was successful (status code 2xx)
            if response.status_code // 100 == 2:
                # Update the status in the GUI
                self.update_status(f"Filewriter mode set to: {mode.capitalize()}")
            else:
                # If the request was not successful, update the status with an error message
                self.update_status(f"Error setting filewriter mode. Status code: {response.status_code}")
        except Exception as e:
            # Handle other exceptions or errors here
            self.update_status(f"Error setting filewriter mode: {str(e)}")

    def set_monitor_mode(self, mode):
        try:
            # Construct the URL for setting monitor mode
            url = f"http://{self.ip_address}/monitor/api/1.8.0/config/mode"

            # Prepare the data for the PUT request
            data = {"value": mode}

            # Make the PUT request using the requests library
            response = requests.put(url, json=data)

            # Check if the request was successful 
            if response.status_code // 100 == 2:
                # Update the status in the GUI
                self.update_status(f"Monitor mode set to: {mode.capitalize()}")
            else:
                # If the request was not successful, update the status with an error message
                self.update_status(f"Error setting monitor mode. Status code: {response.status_code}")
        except Exception as e:
            # Handle other exceptions or errors here
            self.update_status(f"Error setting monitor mode: {str(e)}")

    def set_file_name(self):
        try:
            # Construct the URL for setting the file name
            url = f"http://{self.ip_address}/filewriter/api/1.8.0/config/name_pattern"

            # Get the new file name from the entry widget in your GUI 
            new_file_name = self.file_name_entry.get()

            # Prepare the data for the PUT request
            data = {"value": new_file_name}

            # Make the PUT request using the requests library
            response = requests.put(url, json=data)

            # Check if the request was successful 
            if response.status_code // 100 == 2:
                # Update the status in the GUI
                self.update_status(f"File name pattern set: {new_file_name}")
            else:
                # If the request was not successful, update the status with an error message
                self.update_status(f"Error setting file name pattern. Status code: {response.status_code}")
        except Exception as e:
            # Handle other exceptions or errors here
            self.update_status(f"Error setting file name pattern: {str(e)}")

    
    def arm_detector(self):
        try:
            # Construct the URL for arming the detector
            url = f"http://{self.ip_address}/detector/api/1.8.0/command/arm"

            # Make the PUT request for arming the detector
            response = requests.put(url)

            # Check if the request was successful 
            if response.status_code // 100 == 2:
                # Update the status in the GUI
                self.update_status("Detector armed.")
            else:
                # If the request was not successful, update the status with an error message
                self.update_status(f"Error arming the detector. Status code: {response.status_code}")
        except Exception as e:
            # Handle other exceptions or errors here
            self.update_status(f"Error arming the detector: {str(e)}")

    def trigger_detector(self):
        try:
            self.pause_between_triggers = float(self.pause_entry.get())
            self.num_triggers = int(self.num_triggers_entry.get())

            if self.num_triggers > 0:
                self.trigger_loop()

            else:
                # Construct the URL for triggering the detector
                url = f"http://{self.ip_address}/detector/api/1.8.0/command/trigger"

                # Make the PUT request for triggering the detector
                response = requests.put(url)

            # Check if the request was successful 
            if response.status_code // 100 == 2:
                # Update the status in the GUI
                self.update_status("Detector triggered.")
            else:
                # If the request was not successful, update the status with an error message
                self.update_status(f"Error triggering the detector. Status code: {response.status_code}")
        except Exception as e:
            # Handle other exceptions or errors here
            self.update_status(f"Error triggering the detector: {str(e)}")

    def interrupt_measurement(self):
        try:
            # Construct the URL for interrupting the measurement
            url = f"http://{self.ip_address}/detector/api/1.8.0/command/abort"

            # Make the PUT request for interrupting the measurement
            response = requests.put(url)

            # Check if the request was successful 
            if response.status_code // 100 == 2:
                # Update the status in the GUI
                self.update_status("Measurement aborted.")
            else:
                # If the request was not successful, update the status with an error message
                self.update_status(f"Error aborting the measurement. Status code: {response.status_code}")
        except Exception as e:
            # Handle other exceptions or errors here
            self.update_status(f"Error aborting the measurement: {str(e)}")

    def perform_arm_trigger(self):
        self.arm_detector()
        self.trigger_detector()


    def trigger_loop(self):
        count_time = float(self.old_param_values.get('count_time', {}).get('value', 0))
        url = f"http://{self.ip_address}/detector/api/1.8.0/config/nimages"
        requests.put(url, json={"value": 1})

        for _ in range(self.num_triggers):
            requests.put(url, json={"value": 1})
            self.perform_arm_trigger()

            self.update_status("Trigger command sent.")
            print(self.pause_between_triggers + count_time)
            time.sleep(self.pause_between_triggers + count_time)

    def disarm(self):
        try:
            # Construct the URL for disarming the detector
            url = f"http://{self.ip_address}/detector/api/1.8.0/command/disarm"

            # Make the PUT request for disarming the detector
            response = requests.put(url)

            # Check if the request was successful 
            if response.status_code // 100 == 2:
                # Update the status in the GUI
                self.update_status("Detector disarmed.")
            else:
                # If the request was not successful, update the status with an error message
                self.update_status(f"Error disarming the detector. Status code: {response.status_code}")
        except Exception as e:
            # Handle other exceptions or errors here
            self.update_status(f"Error disarming the detector: {str(e)}")

    def update_status(self, text):
        self.status_label.config(text="Status: " + text)

    def check_detector_status(self):
        # method to check if the detector is measuring or not
        status_url = f"http://{self.ip_address}/detector/api/1.8.0/status/state"
        try:
            response = requests.get(status_url)
            if response.status_code == 200:
                status_data = response.json()
                detector_state = status_data.get("value", "unknown")
                
                if detector_state.lower() == 'acquire':
                    self.update_status("Detector is measuring.")
                else:
                    self.update_status("Detector is not measuring.")
            else:
                self.update_status("Error fetching detector status.")
        except Exception as e:
            self.update_status(f"Error: {e}")

    def refresh_status(self):

        self.check_detector_status()
        # Schedule the next status update (1000 milliseconds is just an example) 
        self.after(1000, self.refresh_status)


def create_gui(ip_address, root_conn):
    root_conn.destroy()
    root_main = tk.Tk()
    DEigerGUI(root_main, ip_address)
    root_main.mainloop()


if __name__ == "__main__":
    connect_and_fetch("")
