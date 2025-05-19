# Motion-Activated Photo Display

A custom-built interactive photo frame that displays images on a TFT screen and changes pictures when motion is detected. This project combines hardware and software to create a personal, interactive gift. I originally created this as a gift for a loved one, and it was a fun project to work on. The goal was to create a simple, low-power device that could display images and change them based on motion detection. It serves as a household decoration. 

## Overview

This project uses an ESP32 microcontroller connected to a TFT display (ILI9341) and an MPU6050 motion sensor. When the device detects motion (like being picked up or shaken), it transitions smoothly between photos using a fade animation.

## Features

- Motion detection using MPU6050 accelerometer/gyroscope
- Smooth fade transitions between images
- 3D printed enclosure designed in FreeCAD (CAD files can be found in this repository in the `cad` directory)
- Low power consumption for extended use

## Hardware Components

- ESP32 microcontroller
- ILI9341 TFT display
- MPU6050 accelerometer/gyroscope
- Custom 3D printed enclosure

## Software Components

- MicroPython implementation
- Custom MPU6050 driver
- Image handling and display functions
- PWM-controlled backlight for smooth transitions

## Implementation Details

The system works by:

1. Continuously monitoring the MPU6050 for motion that exceeds a threshold
2. When motion is detected, transitioning to the next image with a fade-out/fade-in animation
3. Displaying images stored on the ESP32's file system

The code handles:
- SPI communication with the display
- I2C communication with the motion sensor
- Timer-based motion detection
- PWM control for the display backlight
- File system access for image data

## Future Improvements

This version was created as a prototype with time constraints, but several improvements are planned for future iterations:

1. Custom PCB design instead of breadboard/perfboard implementation
2. WiFi connectivity to enable:
   - Remote image updating
   - Adding new images without physical access
   - Web interface for configuration
3. Additional transition effects beyond simple fade

## Installation

1. Flash MicroPython to ESP32
2. Copy the files from this repository to the ESP32
3. Create a `/pictures` directory and add your images (converted to the appropriate raw format)
4. Connect the hardware according to the pin definitions in `main.py`

## Usage

Once powered on, the device will display the first image. Simply shake or move the device to trigger the motion sensor and advance to the next image.

# Acknowledgements
This project includes the [ILI9341 MicroPython driver by rdagger](https://github.com/rdagger/micropython-ili9341/blob/master/ili9341.py), licensed under the MIT License. See [ili9341.py](./src/ili9341.py) and [LICENSE](./LICENSE) for details.

The specific ESP32 board that was used in this project is the [Adafruit ESP32 Feather V2](https://learn.adafruit.com/adafruit-esp32-feather-v2?view=all)