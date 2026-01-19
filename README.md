# SOWA
[![Python](https://img.shields.io/badge/python-3.13-3776ab?logo=python&logoColor=white)](https://www.python.org/)
[![Ultralytics](https://img.shields.io/badge/Ultralytics-YOLO-007ec6?logo=ultralytics&logoColor=white)](https://docs.ultralytics.com/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.11.0-5C3EE8?logo=opencv&logoColor=white)](https://opencv.org/)
[![Jetson](https://img.shields.io/badge/Hardware-Nvidia%20Jetson-76B900?logo=nvidia&logoColor=white)](https://www.nvidia.com/en-us/autonomous-machines/embedded-systems/)
[![Arduino](https://img.shields.io/badge/Hardware-Arduino_Uno-00979d?logo=arduino&logoColor=white)](https://www.arduino.cc/)
[![ESP32](https://img.shields.io/badge/Hardware-ESP32-e7352c?logo=espressif&logoColor=white)](https://www.espressif.com/en/products/socs/esp32)
[![License: MIT](https://img.shields.io/badge/License-MIT-black.svg)](https://opensource.org/licenses/MIT)

## Table of Contents
* [Project Status](#project-status)
* [Multimedia Gallery](#multimedia-gallery)
* [Modules Overview](#modules-overview)
    * [Detection Module](#detection-module-detection)
    * [Rotation Mechanism](#rotation-mechanism-driver)
* [Team](#team)
* [License](#license)

---

## Project Status
**Current Stage:** Under active development.

The system currently consists of two functional core components:
* **Detection Module:** A computer vision system based on YOLO for autonomous object recognition. The module is currently tested on PC but will be deployed to Nvidia Jetson.
* **Rotation Mechanism:** A custom-designed, 3D-printed hardware controller for precise 2-axis positioning able to hold camera and antenna.

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

## Modules Overview

### Detection Module (/detection)
<details open>
  <summary>Technical Details</summary>

  * The module utilizes the Ultralytics YOLO framework for object detection. In production environment it will obtain data from 4K camera.
  * A tiled inference mechanism processes high-resolution images in overlapping segments to detect small objects without detail loss.
  * Native support for RTSP streams is handled by a multi-threaded camera implementation to minimize latency.
  * It supports batch processing of image folders and various video file formats.
  * The visualization system overlays bounding boxes, class labels, and confidence scores, providing real-time diagnostic tools like an FPS counter.
  * Performance is tracked by measuring inference and frame capture times for hardware benchmarking.

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

---

## Team
* **Oskar Wiśniewski (oskarw7)**
* **Mikołaj Wiszniewski (Weeshsh)**
* **Michał Wojciechowski (Kertzy86)**
* **Franciszek Fabiński (fist-it)**

---

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
