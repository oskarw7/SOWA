# SOWA
[![Python](https://img.shields.io/badge/python-3.13-3776ab?logo=python&logoColor=white)](https://www.python.org/)
[![Ultralytics](https://img.shields.io/badge/Ultralytics-YOLO-082e79?logo=ultralytics&logoColor=white)](https://docs.ultralytics.com/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.11.0-5C3EE8?logo=opencv&logoColor=white)](https://opencv.org/)
[![Jetson](https://img.shields.io/badge/Hardware-Nvidia%20Jetson-76B900?logo=nvidia&logoColor=white)](https://www.nvidia.com/en-us/autonomous-machines/embedded-systems/)
[![ESP32](https://img.shields.io/badge/Hardware-ESP32-e7352c?logo=espressif&logoColor=white)](https://www.espressif.com/en/products/socs/esp32)
[![License: MIT](https://img.shields.io/badge/License-MIT-black.svg)](https://opensource.org/licenses/MIT)

## Table of Contents
* [Project Overview](#project-overview)
* [Project Status](#project-status)
* [Multimedia Gallery](#multimedia-gallery)
* [Modules Description](#modules-description)
    * [Jetson Detection Module](#jetson-detection-module-detection_jetson)
    * [Middle Module](#middle-module-middle-module)
    * [Rotation Mechanism](#rotation-mechanism-driver)
    * [Gniazdo Simulation Environment](#gniazdo-simulation-environment-gniazdo)
    * [Detection Module (PC)](#detection-module-pc-detection)
    * [Documentation & Hardware](#documentation--hardware-docs)
* [Team](#team)
* [License](#license)

---

## Project Overview
The project aims to develop a high-precision tracking system for maintaining a stable communication link with autonomous vehicles. By combining GPS data for approximate localization and AI-powered computer vision for precise visual tracking, SOWA ensures a directional antenna is always pointed accurately at its target. The system is specifically engineered for outdoor fieldwork. Its robust 3D-printed construction and edge computing allow it to maintain signal links in remote areas where traditional infrastructure is unavailable.

---

## Project Status
**Current Stage:** Fully integrated and under active development.

The system is fully integrated across all its modules and consists of several functional core components:
* **Jetson Detection Module:** The production vision module, featuring hardware-accelerated inference specifically optimized for Nvidia Jetson using DeepStream and TensorRT.
* **Middle Module:** A C++ based integration layer facilitating communication between software modules and the hardware.
* **Rotation Mechanism:** A custom-designed, 3D-printed hardware controller for precise 2-axis positioning able to hold camera and antenna.
* **Gniazdo (Nest):** A Python-based simulation environment managing RTSP streams and simulated data for system testing.
* **Detection Module (PC):** A prototype computer vision system based on YOLO for autonomous object recognition, used for testing and benchmarking on PC environments.

---

## Multimedia Gallery
<details open>
  <summary>Gallery</summary>

  ### Detection Module
  ![detection](https://drive.google.com/uc?export=view&id=1YoXf2ZV2ZGZMKBD5Lw5D1eoEN8Btz77M)

  ---

  ### Rotation Mechanism
  ![mechanism](https://drive.google.com/uc?export=view&id=1cAZD1GclJ1NSZbfLoPzHjMn5gEtWo8uk)
  ![mechanism_scheme](https://drive.google.com/uc?export=view&id=1-eY8NJg5deBWDQLhOuHweFCVcFPKO_1F)
  ![mechanism_driver](https://drive.google.com/uc?export=view&id=12MBB_JnVovjM_gP1cwSug3CR4oAvuw1S)

</details>

---

## Modules Description

### Jetson Detection Module (/detection_jetson)
The production edge-optimized vision layer deployed on Nvidia Jetson for hardware-accelerated processing in the field.

<details open>
  <summary>Technical Details</summary>

  * Implements Nvidia DeepStream SDK for high-performance video analytics and streaming.
  * Utilizes custom C++ and CUDA implementations for YOLO inference with TensorRT optimization.
  * Features scripts to compile and export various YOLO models (v5, v7, v8, v9, v10, etc.) to efficient engine formats.
  * Includes optimization analysis and hardware-specific benchmarking tools for Jetson devices.

</details>

### Middle Module (/middle-module)
The C++ communication and integration layer.

<details open>
  <summary>Technical Details</summary>

  * Built with CMake and C++ for robust performance.
  * Acts as a middleware facilitating integration and data flow between the detection modules, the hardware driver, and other system components.

</details>

### Rotation Mechanism (/driver)
The control module is responsible for precise mechanical movement and master system communication.

<details open>
  <summary>Technical Details</summary>

  * The entire mechanical structure was designed and 3D printed by the team.
  * The chassis is customized to hold the integrated camera and antenna assembly.
  * The software is written in C++ using the FastAccelStepper library for smooth motor control.
  * The module supports universal adjustment of mechanical gear ratios to accommodate different hardware transmissions.
  * Software-defined movement limits are fully configurable to protect hardware integrity across different physical setups.

</details>

### Gniazdo Simulation Environment (/Gniazdo)
A Python-based simulation environment serving as the central hub for RTSP streaming and testing.

<details open>
  <summary>Technical Details</summary>

  * Employs an `rtsp-simple-server` (via Docker) to broadcast and manage video streams.
  * Includes mock modules for Camera, Drone, and Scene to simulate real-world conditions.
  * Provides a Makefile-driven workflow for easy setup and simulation runs (`make run-server`, `make sim`).
  * Ideal for testing detection models and system integration without requiring outdoor hardware setup.

</details>

### Detection Module (PC) (/detection)
The prototype vision layer, designed as a processing pipeline for real-time object recognition and spatial analysis during testing and development.

<details open>
  <summary>Technical Details</summary>

  * The module utilizes the Ultralytics YOLO framework for object detection.
  * A tiled inference mechanism processes high-resolution images in overlapping segments to detect small objects without detail loss.
  * Native support for RTSP streams is handled by a multi-threaded camera implementation to minimize latency.
  * It supports batch processing of image folders and various video file formats.
  * The visualization system overlays bounding boxes, class labels, and confidence scores, providing real-time diagnostic tools like an FPS counter.
  * Performance is tracked by measuring inference and frame capture times for baseline benchmarking.

</details>

### Documentation & Hardware (/docs)
Contains project documentation and all 3D-printable files.

<details open>
  <summary>Technical Details</summary>

  * Includes presentation files and comprehensive project documentation.
  * Provides STL files for all 3D printed components such as the base plate, bearing mounts, belt drives, and camera/antenna mounts.

</details>

---

## Team
* **Oskar Wiśniewski (oskarw7)**
* **Mikołaj Wiszniewski (Weeshsh)**
* **Michał Wojciechowski (Kertzy86)**
* **Franciszek Fabiński (fist-it)**

---

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
