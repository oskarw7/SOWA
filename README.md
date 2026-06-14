![logo](https://drive.google.com/uc?export=view&id=18_huUnP8kr6bEUsrmvbKbSnZ9zv0W_SC)

[![Python](https://img.shields.io/badge/python-3.13-3776ab?logo=python&logoColor=white)](https://www.python.org/)
[![Ultralytics](https://img.shields.io/badge/Ultralytics-YOLO-082e79?logo=ultralytics&logoColor=white)](https://docs.ultralytics.com/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.11.0-5C3EE8?logo=opencv&logoColor=white)](https://opencv.org/)
[![Jetson](https://img.shields.io/badge/Hardware-Nvidia%20Jetson-76B900?logo=nvidia&logoColor=white)](https://www.nvidia.com/en-us/autonomous-machines/embedded-systems/)
[![ESP32](https://img.shields.io/badge/Hardware-ESP32-e7352c?logo=espressif&logoColor=white)](https://www.espressif.com/en/products/socs/esp32)
[![License: MIT](https://img.shields.io/badge/License-MIT-black.svg)](https://opensource.org/licenses/MIT)
## Table of Contents
* [Project Overview](#project-overview)
* [System Architecture](#system-architecture)
* [Project Status](#project-status)
* [Field Test Results](#field-test-results)
* [Multimedia Gallery](#multimedia-gallery)
* [Modules Description](#modules-description)
    * [Jetson Detection Module](#jetson-detection-module-detection_jetson)
    * [Middle Module](#middle-module-middle-module)
    * [Rotation Mechanism](#rotation-mechanism-driver)
    * [Gniazdo Simulation Environment](#gniazdo-simulation-environment-gniazdo)
    * [Detection Module (PC)](#detection-module-pc-detection)
    * [Documentation](#documentation-docs)
* [Technology Stack](#technology-stack)
* [Team](#team)
* [License](#license)
---
 
## Project Overview
SOWA is a complete, portable autonomous tracking system designed to maintain a stable communication link with unmanned and radio-controlled vehicles such as drones and boats. It combines GPS-based coarse localization with AI-powered real-time computer vision for precise visual tracking, keeping a directional antenna continuously pointed at a moving target. The system was entirely designed and built from scratch by the team.
 
**Key characteristics:**
- **Edge AI, no cloud required** — all inference runs locally on an NVIDIA Jetson Orin Nano Super, making the system fully self-contained and independent of any external network infrastructure.
- **Real-time performance** — the vision pipeline processes video at over 30 frames per second thanks to hardware-accelerated inference via NVIDIA DeepStream SDK and TensorRT.
- **High-precision movement** — the custom pan/tilt platform achieves angular resolution of ~0.078° in azimuth (full 360°) and ~0.12° in elevation (−20° to +80°), driven by NEMA23 stepper motors with microstepping control.
- **Proven field range** — field tests confirmed continuous drone tracking up to 120 m and stable directional antenna signal reception up to 90 m, vastly outperforming omnidirectional antennas (~15 m).
- **Truly portable** — the entire system was designed to be carried and set up easily, making it ready for remote outdoor deployment.
- **Modular & testable** — a built-in simulation environment (Gniazdo) generates synthetic RTSP streams so every module can be developed and validated independently, without physical hardware.
 
The project was selected as a finalist and recieved a honorable mention in the nationwide **IT is ME Student Innovation Competition** organized by AGH University of Kraków (May 2026).

![product](https://drive.google.com/uc?export=view&id=160hVvnYBe09-R68OZMG0LiXCIbEty_Yd)
 
---

## System Architecture
 
SOWA is built around three cooperating modules and a dedicated testing environment:
 
```
Camera (RTSP) ──► Jetson Detection Module ──► Middle Module ──► ESP32 Driver ──► Stepper Motors
                  (YOLO / DeepStream)         (Named Pipes)     (Serial/UART)    (Pan/Tilt)
                                                    ▲
                                                GPS Signal
```
 
- **Video stream** from the Milesight 5G Pro Bullet Plus camera is delivered over RTSP.
- **The Jetson Detection Module** runs a YOLO model via NVIDIA DeepStream SDK and outputs a deviation matrix (detected object coordinates relative to frame center).
- **The Middle Module** fuses the deviation data with incoming GPS coordinates and computes target pan/tilt commands.
- **Commands are sent over Serial (UART)** using a custom 8-byte binary protocol (with XOR checksum) to the ESP32 microcontroller, which drives the stepper motors.
- **The Gniazdo environment** can replace the camera and drone with a synthetic RTSP stream for development and testing without physical hardware.

---

## Project Status
**Current Stage:** Complete — all requirements met and field-tested.
 
All five project stages (A–E) have been successfully completed:
 
| Stage | Description | Status |
|-------|-------------|--------|
| A | System architecture & block diagrams | ✅ Done |
| B | Object detection module (PC prototype) | ✅ Done |
| C | Rotation mechanism (hardware + firmware) | ✅ Done |
| D | Data processing module & full integration | ✅ Done |
| E | Field testing | ✅ Done |
 
The fully integrated system consists of several functional core components, last two being separate from the product:
* **Jetson Detection Module:** Production vision pipeline with hardware-accelerated inference on Nvidia Jetson Orin Nano Super using DeepStream and TensorRT. Achieves over 30 FPS for YOLO models compiled to FP16 precision.
* **Middle Module:** C++ integration layer that correlates detection data with GPS input and sends motor commands via the custom binary protocol.
* **Rotation Mechanism:** Custom-designed, 3D-printed pan/tilt platform with NEMA23 stepper motors, TB6600 controllers and timing belts. Angular precision of ~0.078° (azimuth) and ~0.12° (elevation).
* **Gniazdo (Nest):** Python-based simulation environment generating synthetic RTSP streams for closed-loop system testing without outdoor hardware.
* **Detection Module (PC):** Prototype YOLO-based vision system used for early development, benchmarking and model evaluation on desktop GPUs.

---

## Field Test Results
 
Two field tests were conducted using a remote-controlled drone as the tracking target, proving that the system meets all the needs of the client and is ready for work.
 
### Tracking Quality Test (22 May 2026)
The complete hardware-software system was tested outdoors with no external infrastructure (powered from a portable power station only).
 
* **Continuous drone detection range:** ~120 m
* **Tracking accuracy:** The drone was kept in the centre of the frame for the majority of the flight. Target loss occurred only when occluded by dense tree crowns, or when it flew outside the elevation range.
* **System stability:** No restarts, no overheating, no connectivity issues throughout the test.
### Communication Quality Test (31 May 2026)
The directional antenna mounted on the system was compared against a reference omnidirectional antenna using a Tektronix RSA306B spectrum analyzer at 5.77 GHz.
 
* **Directional antenna signal range:** stable reception up to 90 m; signal still observed at 120 m.
* **Omnidirectional antenna signal range:** signal lost at ~15 m.
* **SOWA wins:** The system successfully overcomes the fundamental advantage of omnidirectional antennas by keeping the directional antenna continuously pointed at the target. The tracking and communication ranges are well-balanced with no bottlenecks.

![spectrum](https://drive.google.com/uc?export=view&id=1uOBcAx1nSi-fdY2meESXUIhddjS3gbYo)

---


## Multimedia Gallery
<details open>
  <summary>Gallery</summary>

  ### Detection Module
  
<p align="center">
   <img src="https://drive.google.com/uc?export=view&id=1-m6CVnaXWLUwfofO4aJCarpE38-R8Dhp" width="600">
</p>

  ---

  ### Rotation Mechanism
  ![mechanism](https://drive.google.com/uc?export=view&id=1cAZD1GclJ1NSZbfLoPzHjMn5gEtWo8uk)
  ![mechanism_scheme](https://drive.google.com/uc?export=view&id=1-eY8NJg5deBWDQLhOuHweFCVcFPKO_1F)
  ![mechanism_driver](https://drive.google.com/uc?export=view&id=12MBB_JnVovjM_gP1cwSug3CR4oAvuw1S)

</details>

---

## Modules Description

### Jetson Detection Module (/detection_jetson)
The production edge-optimized vision layer deployed on the Nvidia Jetson Orin Nano Super for hardware-accelerated real-time processing in the field.
 
<details open>
  <summary>Technical Details</summary>
   
  * Implements NVIDIA DeepStream SDK via a production C++ pipeline, offloading work to dedicated Jetson hardware blocks: **NVDEC** (video decoding), **GPU** (AI inference), and **VIC/NVMM** (video scaling and memory management without CPU involvement).
  * Applies the hardware-accelerated **NvDCF tracker**, which uses visual correlations to maintain target tracking through brief occlusions and allows inference to be skipped every other frame while preserving continuity.
  * Includes scripts to compile YOLO models (v5, v7, v8, v9, v10, v26, etc.) to TensorRT `.engine` format with FP16 quantization, as well as benchmarking tools to identify the optimal model/resolution configuration.
  * Performance example: YOLO26s at FP16, 1536×1536 window — improved from 10 FPS (Python/Ultralytics) to over 30 FPS (DeepStream pipeline with GUI).
  * A minimalist production variant is included that omits all visualization and debug output, keeping only optional logging.
  * Jetson performance mode (maximum power and locked clocks) is enabled at runtime for peak throughput.

</details>


### Middle Module (/middle-module)
he C++ communication and data processing layer — the "brain" of the system.
 
<details open>
  <summary>Technical Details</summary>
   
  * Built with CMake and C++; depends on the Boost library collection (`boost::asio` for async serial I/O, `boost::geometry` for vector and spherical calculations).
  * Receives object detection data from the Jetson Detection Module via **Named Pipes** (IPC on Linux), minimizing latency and eliminating the need for network interfaces on the same device.
  * Fuses detection deviations with GPS coordinates and current mechanism orientation to compute target pan/tilt angles.
  * Communicates with the ESP32 driver using a custom **8-byte binary protocol**: 1-byte header, name, auxiliary info, 4-byte float value, XOR checksum — ensuring data consistency and easy synchronization.
  * Supports a **console debug mode** (prints to stdout) and a **production mode** (sends to serial port).
    
</details>


### Rotation Mechanism (/driver)
The hardware execution layer responsible for precise 2-axis camera and antenna positioning.
 
<details open>
  <summary>Technical Details</summary>
   
  * The entire mechanical structure was designed in **Autodesk Fusion 360** with a focus on minimizing the moment of inertia of the loaded assembly (camera + antenna).
  * All custom parts were **3D-printed in PLA**; structural rigidity is provided by **aluminium profiles** and **ball bearings** for smooth, low-friction movement.
  * Two **NEMA23 stepper motors** (1.2 Nm horizontal, 1.0 Nm vertical) transmit power via **SPZ-type timing belts** and are controlled by **TB6600 drivers** at 6400 microsteps/revolution.
  * Angular resolution: **~0.078°** (azimuth, full 360°) and **~0.12°** (elevation, −20° to +80°).
  * Firmware written in C++ using the **FastAccelStepper** library for smooth acceleration ramps and non-blocking motor control.
  * Runs on an **ESP32-S3** microcontroller (Arduino framework), chosen for its low power consumption and ease of maintenance.
  * Movement limits are software-configurable to protect hardware integrity across different physical setups.
  * The module supports universal adjustment of mechanical gear ratios.
    
</details>


### Gniazdo Simulation Environment (/Gniazdo)
A Python-based simulation environment serving as the central hub for closed-loop system testing without physical hardware.
 
<details open>
  <summary>Technical Details</summary>
   
  * Generates synthetic scene images using **OpenCV** (cv2), including moving objects (drones) with configurable trajectories, speeds and behaviours.
  * Converts the synthetic scene to an **RTSP stream via FFmpeg**, plugging directly into the existing detection pipeline without any module modifications.
  * Simulates camera movement, enabling testing under dynamic perspective changes.
  * Operates in real time, preserving actual timing constraints and system latencies for realistic performance evaluation.
  * Supports **repeatable, parameterized test scenarios** for rapid iteration and algorithm tuning.
  * Includes mock modules for Camera, Drone, and Scene, as well as a Makefile-driven workflow (`make run-server`, `make sim`) for easy setup.

</details>


### Detection Module (PC) (/detection)
The prototype vision layer used during early development, testing, and benchmarking on desktop GPU hardware.
 
<details open>
  <summary>Technical Details</summary>
   
  * Built on the **Ultralytics YOLO** framework; supports models from YOLOv5 through the latest generations.
  * Implements **tiled inference** (configurable tile size and overlap) for high-resolution images, enabling detection of small objects without resolution loss. Includes NMS post-processing to remove duplicates from overlapping tiles.
  * Supports **batch processing** for parallel multi-frame inference.
  * Native support for **RTSP streams**, video recordings, image folders and single images, handled by a multi-threaded camera reader to minimize latency.
  * Visualization overlays bounding boxes, class labels and confidence scores; includes an FPS counter and per-frame inference timing for benchmarking.
  * Includes a custom training workflow on domain-specific datasets (e.g. drone images) for model fine-tuning and accuracy comparison.
    
</details>


### Documentation (/docs)
Contains project documentation and all 3D-printable files.
 
<details open>
  <summary>Technical Details</summary>
   
  * Includes presentation files and comprehensive project documentation (DTP, DPP, information folder).
  * Provides STL files for all 3D-printed components: base plate, bearing mounts, belt drives, camera mount and antenna mount.
    
</details>


---

## Technology Stack
 
| Layer | Technology |
|-------|-----------|
| Edge AI compute | NVIDIA Jetson Orin Nano Super (Ampere GPU) |
| Vision pipeline | NVIDIA DeepStream SDK (C++) |
| AI inference | YOLO family models, TensorRT |
| Object tracking | NvDCF (hardware-accelerated) |
| Prototype detection | Python, Ultralytics YOLO, OpenCV |
| Data processing | C++, Boost (asio, geometry) |
| Microcontroller | ESP32-S3 (Arduino / C++) |
| Motor control | FastAccelStepper, TB6600, NEMA23 |
| Inter-module comms | Named Pipes (IPC), Serial/UART, RTSP |
| Custom protocol | 8-byte binary with XOR checksum |
| Simulation | Python, OpenCV, FFmpeg |
| CAD | Autodesk Fusion 360 |
| Build / VCS | CMake, Git, GitHub |
 
---

## Team
* **Oskar Wiśniewski (oskarw7)**
* **Mikołaj Wiszniewski (Weeshsh)**
* **Michał Wojciechowski (Kertzy86)**
* **Franciszek Fabiński (fist-it)**
  
Project supervised by Dr Eng. Krzysztof Gierłowski, Department of Teleinformation Networks, WETI, Gdańsk University of Technology.

---

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
