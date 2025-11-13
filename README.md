# Driver-Fatigue-Detection-IoT

Real-Time Driver Fatigue State Detection System (Deep Learning + IoT)

This repository contains the implementation and documentation for a real-time
driver fatigue detection and alert system developed using a Raspberry Pi, camera,
and IoT hardware. The project uses facial landmark analysis (EAR, MAR) to detect
drowsiness and triggers alerts (buzzer, water sprinkler) via GPIO-controlled relays.

---

## Contents
- `src/` - Python source code (detection and launcher)
- `model/` - place your trained model or download link here
- `hardware/` - wiring diagrams and components list
- `web/` - simple monitoring UI (HTML/CSS)
- `docs/` - project paper and final report (PDFs provided by the authors)
- `requirements.txt` - Python dependencies

## How to run (Raspberry Pi)
1. Copy the landmark model to repo root:
   - `shape_predictor_68_face_landmarks.dat` (download from dlib official sources)
2. Install dependencies:
   ```bash
   pip3 install -r requirements.txt
   ```
3. Run on Raspberry Pi (with camera attached):
   ```bash
   python3 src/detection.py
   ```

**Note:** This code requires running on Raspberry Pi hardware with GPIO pins and a connected camera. Do not run GPIO code on non-RPi machines (it may fail).

---

## Files from project report
Included in `docs/` folder are the project *Published Paper* and *Final Report* provided by the authors. These contain system architecture diagrams and working flowcharts referenced in the README. See:
- `docs/Published_Paper.pdf`.
- `docs/Final_Report.pdf`.

---

## Wiring & GPIO mapping (as used in code)
- Buzzer → GPIO 18 (BCM)
- Water pump relay → GPIO 26 (BCM)
- Ensure relays are properly powered and isolated. Use opto-isolated relays where possible.

---

## License & Author
Author: **Saurabh Amrutkar** (project co-author in Final Report)

