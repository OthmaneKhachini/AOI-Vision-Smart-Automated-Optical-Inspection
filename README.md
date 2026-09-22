# AOI Vision: Smart Automated Optical Inspection

AOI Vision is a small automated optical inspection line. When a part passes an infrared sensor, a webcam takes a picture of it, an AI model decides whether the part is a **PASS** or a **DEFECT**, and the result appears live on a web dashboard with statistics, charts, history and exportable reports.

The whole project is made of **two programs**: `factory.ino` (Arduino) and `web.py` (Python / Streamlit), plus a model trained with Google Teachable Machine.

---

## 1. How it works

```
IR sensor ──> Arduino ──USB serial──> web.py ──> Webcam frame ──> AI model ──> PASS / DEFECT ──> Dashboard
              "DETECTED" (9600 baud)   (Streamlit)                (Keras)
```

1. The IR sensor detects a part. The Arduino prints `DETECTED` on the serial port (9600 baud).
2. `web.py` reads the message and takes the current frame from the webcam.
3. The frame is prepared (center crop, 224x224, values from -1 to 1) and given to the Teachable Machine model.
4. The part is a **PASS only if the model is confident it is a pass** (Pass Threshold). Anything else is a **DEFECT**.
5. The result is recorded, and the dashboard, charts, thumbnails and reports are updated in real time.

---

## 2. Features

- Live webcam video with a moving laser scan line and FPS counter
- PASS / DEFECT decision with a confidence percentage drawn on the captured frame
- Adjustable **Pass Threshold** and **Yield Target** (sidebar sliders)
- KPI cards: total inspected, passed, defects, yield rate, inspection rate, model confidence
- Charts: yield trend, defect distribution (pie), production per minute, yield gauge
- Thumbnails of the last inspections, recent inspections list, analyzed frame
- System health panel (camera, Arduino, vision engine, laser scanner, production line)
- Alert when the yield drops below the target, sound alerts and pop-up notifications
- Emergency stop button
- English / Chinese interface switch
- Exports: CSV (all, passed, failed), HTML reports (charts only, full report) and a ZIP of the rejected frames
- Automatic detection of the working camera and of the Arduino port

---

## 3. What we used

### Hardware

| Item | Use |
|---|---|
| Arduino board (USB) | Reads the sensor and sends `DETECTED` to the PC |
| IR obstacle sensor (digital output on pin 2) | Detects a part in front of it (output is LOW when an object is detected) |
| USB webcam | Takes the picture of each part |
| PC running Windows | Runs `web.py` and the AI model |

### Software

| Tool | Use |
|---|---|
| Python 3.11 + VS Code + `.venv` | Development environment |
| Arduino IDE | Upload `factory.ino` to the Arduino |
| Google Teachable Machine | Train the image model (classes `pass` and `defect`) and export it as Keras |
| TensorFlow 2.15 (Keras) | Load the exported `keras_model.h5` and run predictions |
| Streamlit | Web dashboard |
| OpenCV (`opencv-python`) | Camera capture, image processing and drawing |
| NumPy | Image arrays and model input |
| Pandas | Tables for the CSV exports |
| Plotly | Charts and the charts in the HTML reports |
| PySerial | Serial communication with the Arduino |
| Python standard library | `os`, `io`, `zipfile`, `base64`, `time`, `datetime`, `winsound` (Windows only) |

`tf_keras` is optional. `web.py` uses it if it is installed, and otherwise falls back to the Keras included in TensorFlow. Do not install a `tf_keras` version that does not match your TensorFlow version (it would upgrade TensorFlow).

---

## 4. Project files

```
project folder/
├── web.py           Streamlit application (camera, AI, data, dashboard)
├── factory.ino      Arduino sketch (IR sensor -> serial message)
├── keras_model.h5   Model exported from Teachable Machine
├── labels.txt       Class names: "0 pass" and "1 defect"
└── .venv/           Python virtual environment
```

`keras_model.h5` and `labels.txt` must be in the same folder as `web.py`.

---

## 5. Installation

### 5.1 Python environment

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install tensorflow==2.15.0
python -m pip install streamlit opencv-python pandas plotly pyserial
```

TensorFlow 2.15 works with NumPy 1.x (`numpy<2`). If pip reports a NumPy conflict with OpenCV, install an older `opencv-python` release.

To check that everything is installed:

```bash
python -c "import importlib.util as u; print([m for m in ['streamlit','cv2','numpy','pandas','plotly','serial','tensorflow'] if not u.find_spec(m)])"
```

An empty list `[]` means nothing is missing.

### 5.2 Arduino

1. Wire the IR sensor: VCC to 5 V, GND to GND, OUT to digital pin 2.
2. Open `factory.ino` in the Arduino IDE and upload it to the board.
3. Close the Arduino IDE Serial Monitor afterwards, because only one program can use the serial port at a time.

### 5.3 Model (Teachable Machine)

1. Create an **Image Project** with two classes named `pass` and `defect`.
2. `pass`: 100+ images of good parts in different positions, taken with the final camera, position and lighting.
3. `defect`: defective parts **and everything that is not a good part** (empty belt, hand, other objects). Teachable Machine has no "unknown" class, so this is how unknown things end up as defects.
4. Train, then **Export Model > TensorFlow > Keras**.
5. Put `keras_model.h5` and `labels.txt` next to `web.py`. `labels.txt` must contain `0 pass` and `1 defect`.

---

## 6. Run

```bash
streamlit run web.py
```

Then open the address shown in the terminal (usually `http://localhost:8501`).

The sidebar shows:

- `Camera index`: the camera that `web.py` is using
- `Arduino port`: the COM port that `web.py` is using
- `Sensor`: the last message received from the Arduino (you should see `DETECTED` when you put a part or your hand in front of the sensor)

---

## 7. Configuration

At the top of `web.py`:

```python
CAMERA_INDEX = None       # None = auto (first camera that works), or force 0, 1, 2 ...
CAMERA_BACKEND = "DSHOW"  # "DSHOW" | "MSMF" | "ANY"
ARDUINO_PORT = None       # None = auto-detect, or force "COM3", "COM5" ...
```

In the sidebar while the app runs:

| Control | Meaning |
|---|---|
| Pass Threshold (%) | The part is a PASS only if the pass probability is above this value (default 80). Raise it to be stricter |
| Yield Target (%) | An alert appears when the yield is below this value (default 95) |
| Sound Alerts | Beep on pass (high) and on defect (low) |
| Emergency Stop | Halts the system |
| Reset Data | Clears all recorded results |

The camera is opened at 640x480. The model input size is read from the model (224x224 for Teachable Machine).

---

## 8. How `web.py` is organized

| Section | Content |
|---|---|
| 1. Page config + CSS | Streamlit page settings and the dark theme |
| 2. Translation | `LANG` dictionary (English and Chinese) |
| 3. Session state | Counters, history, recent parts, failed frames (`S`) |
| 4. Sidebar | Language switch, emergency stop, sliders, reset, health panel |
| 5. Header + emergency stop | Title, chips and the halt screen |
| 6. Layout | Columns, containers and placeholders updated by the loop |
| 7. Helpers | Image encoding, `stats()`, charts, HTML report, CSV, ZIP, downloads |
| 8. Render functions | Live header, status banner, thumbnails, KPI cards, charts |
| 9. Hardware init + AI | `find_arduino_port()`, `open_camera()`, `load_ai()`, `preprocess()`, `inspect_image()` |
| 10. Continuous loop | Read frame, show live video, wait for `DETECTED`, classify, record, refresh |

### Decision logic

```python
p_prob = probability of the "pass" class (in %)
is_defect = p_prob < pass_threshold      # PASS only if the model is sure
```

### Arduino sketch (`factory.ino`)

The sketch reads the sensor on pin 2. When the value changes from HIGH to LOW (a new object), it prints `DETECTED` and waits 500 ms to avoid double detections. Serial speed is 9600 baud.

---

## 9. Team split

The Arduino and hardware are given to one member. The Python code is split into four concepts, one per member. Each member writes an individual report about their concept.

| Member | Concept | Part of the project |
|---|---|---|
| 1 | Hardware & Arduino | `factory.ino` + the serial part of `web.py` |
| 2 | AI Model (Teachable Machine) | `keras_model.h5`, `labels.txt`, `load_ai()`, `preprocess()`, `inspect_image()` |
| 3 | Camera & Live Vision | `open_camera()`, the live video loop, camera release |
| 4 | Data, Statistics & Reports | session state, `stats()`, charts, CSV / HTML / ZIP exports |
| 5 | Dashboard Interface | page config, CSS, translations, sidebar, layout, render functions |

---

## 10. Troubleshooting

| Problem | What to do |
|---|---|
| "Camera not found" or the wrong camera is used | Set `CAMERA_INDEX` to the right number (0, 1, 2 ...). Indexes can change after a restart or after disabling the built-in camera. Close any app or browser tab that is using the webcam. Check Windows **Settings > Privacy & security > Camera** (desktop apps must be allowed). Try `CAMERA_BACKEND = "MSMF"` |
| To use the webcam as the main camera | Disable the built-in PC camera in **Device Manager > Cameras** |
| "Arduino disconnected" | Check the USB cable, close the Arduino IDE Serial Monitor, check the COM port in **Device Manager > Ports**, or set `ARDUINO_PORT` |
| Nothing happens when the sensor is triggered | Look at the `Sensor` line in the sidebar. If `DETECTED` never appears, check the wiring, the sensor sensitivity screw and that `factory.ino` is uploaded |
| Everything is classified as PASS | The `defect` class needs more images: defective parts and everything that is not a good part (empty belt, hand, other objects). Then retrain, export again and raise the Pass Threshold |
| Too many good parts are rejected | Lower the Pass Threshold, or add more `pass` images taken with the final setup |
| Model fails to load | Check that `keras_model.h5` and `labels.txt` are next to `web.py` and that TensorFlow 2.15 is installed. Do not install a mismatching `tf_keras` |
| pip starts downloading a new TensorFlow | Press `Ctrl + C`. A `tf_keras` release that does not match your TensorFlow tries to upgrade it |
| First start is slow | TensorFlow and the model take 30 to 60 seconds to load after a PC restart. It is faster afterwards |
| Charts are missing in an exported HTML report | The report loads Plotly from the internet, so open it while online |

---

## 11. Notes and limits

- Windows only: `winsound`, the DirectShow camera backend and COM ports are Windows features.
- Results are kept in memory for the current session. Export the reports before closing the page.
- The dashboard keeps the last 100 rejected frames.
- The quality of the decision depends on using the **same camera, position and lighting** for the training images and for the final system.
