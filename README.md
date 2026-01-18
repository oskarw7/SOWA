# SOWA

## Project Status
**Current Stage:** Under active development.

The system currently consists of two functional core components:
* **Detection Module:** A computer vision system based on YOLO for autonomous object recognition. The module is currently tested on PC but will be deployed to Nvidia Jetson.
* **Rotation Mechanism:** A custom-designed, 3D-printed hardware controller for precise 2-axis positioning.

---

## Tech Stack

### Detection Module
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Ultralytics](https://img.shields.io/badge/ultralytics-%23111F68.svg?style=for-the-badge&logo=ultralytics&logoColor=white)
![OpenCV](https://img.shields.io/badge/opencv-%23white.svg?style=for-the-badge&logo=opencv&logoColor=white)

### Rotation Mechanism
![Arduino](https://img.shields.io/badge/-Arduino-00979D?style=for-the-badge&logo=Arduino&logoColor=white)
![ESP32](https://img.shields.io/badge/ESP32-E7352C?style=for-the-badge&logo=espressif&logoColor=white)

---

## Multimedia Gallery
Below are the visual materials showcasing the SOWA system.

### Detection Module

![detection](https://drive.google.com/uc?export=view&id=1YoXf2ZV2ZGZMKBD5Lw5D1eoEN8Btz77M)
---

### Rotation Mechanism
![mechanism](https://drive.google.com/uc?export=view&id=1cAZD1GclJ1NSZbfLoPzHjMn5gEtWo8uk)
![mechanism_scheme](https://drive.google.com/uc?export=view&id=1-eY8NJg5deBWDQLhOuHweFCVcFPKO_1F)
![mechanism_driver](https://drive.google.com/uc?export=view&id=12MBB_JnVovjM_gP1cwSug3CR4oAvuw1S)

---

## Modules Overview
### Detection Module (/detection)
The vision layer is a processing pipeline designed for real-time object recognition and spatial analysis.

* The system utilizes the Ultralytics YOLO framework.
* A tiled inference mechanism is implemented to process high-resolution images in overlapping 640-pixel segments, which enables the effective detection of small objects without losing detail.
* Support for multiple input data sources includes RTSP streams handled by a multi-threaded camera implementation to minimize latency, as well as batch processing of image folders and video files.
* The visualization system overlays bounding boxes, class labels, and detection confidence scores on the image, while providing an FPS counter and diagnostic tools for debugging inference coverage.
* The module automatically measures inference and frame capture times, allowing for the generation of performance plots for different computing units such as GPU or CPU.

### Rotation Mechanism (/driver)
The control module is responsible for precise mechanical movement and handling communication with the master system.

* The entire mechanical structure was designed and 3D printed by the team.
* The chassis and frame were customized to securely hold and direct the camera and antenna assembly.
* The logical layer is based on a microcontroller with software written in C++ using the FastAccelStepper library, allowing for smooth control of stepper motors.
* The mechanism implements movement in two axes while accounting for mechanical gear ratios of 1.39 for the horizontal axis and 2.15 for the vertical axis.
* Hardware integrity is ensured by software-defined movement range limits for the vertical axis, set between -20 and 80 degrees.

---

## Team
* **Oskar Wiśniewski (oskarw7)**
* **Mikołaj Wiszniewski ()**
* **Michał Wojciechowski ()**
* **Franciszek Fabiński ()**

---
