# Eiger Detector GUI

## Overview
The Eiger Detector GUI is a Python-based graphical user interface specifically designed for interacting with Eiger detectors through the Simplon API version 1.8.0. This intuitive and efficient GUI allows users to easily configure detector settings, initiate data acquisition, and monitor the detector's status in real-time. It has been tested and validated on the EIGER2 R 500K, ensuring reliable and user-friendly operation.

## Features
- **Parameter Configuration**: Easily manage and modify various detector settings, such as beam center, count time, threshold values, and more.
- **Data Interface Options**: Provides versatile options for interfacing with the detector data, facilitating easy access and manipulation of measurement results.
- **Real-Time Status Monitoring**: Continuously track the operational status of the detector, including current measuring activities.
- **Error Handling**: Robust error handling mechanisms provide clear feedback in case of configuration or connection issues.
- **User-Friendly Design**: The GUI's straightforward layout makes it accessible for users of varying expertise levels.

## How to Use

1. **Starting the Application**: Launch the application by double-clicking the executable or running the script with

    `python EigerGUI.py`

2. **entering the IP-Address of the Detector Control Unit**: enter the IP-Address in the COnnection Widget

    ![Connection Widget](/screenshots/connection.png)

3. **Main window**: configure the detector parameters, choose the data interface and start the data aquisition

    ![Eiger GUI](/screenshots/main.png)


## Requirements
- Python 3.x
- Requests library


## License
This project is licensed under the [GNU General Public License v3.0](/LICENSE.md) - see the [LICENSE.md](LICENSE.md) file for details.
