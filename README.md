# 💡 Intelligent Headlight Controller — CAN Bus Simulation

A Python + Streamlit interactive simulation of a **CAN 2.0A based Intelligent Headlight Controller** system. This project demonstrates real-time communication between two distributed automotive nodes: a **Body Control Module (Node A)** and a **Headlight Actuator (Node B)** over a virtual CAN bus.

Built as part of **23ECPE16 — Automotive Electronics**, Coimbatore Institute of Technology.

---

## 📌 Problem Statement

### Node A — Data Producer (Body Control Module)

The BCM reads two inputs — an **ambient light sensor (Lux)** and a **manual switch position** — and determines the headlight command. It packs the following into a CAN frame with **ID 0x215**:

| Byte | Field | Description |
|------|-------|-------------|
| Byte 0 | Command | Headlight state (0=Off, 1=DRL, 2=Low Beam, 3=High Beam) |
| Byte 1 | Intensity | Brightness level (0–100%) |
| Byte 2 | Checksum | Byte 0 + Byte 1 (simple error check) |

### Node B — Data Consumer (Headlight Actuator)

The actuator receives the CAN message, **verifies the checksum**, and maps the command byte to a headlight mode:

- ✅ If `(Byte 0 + Byte 1) == Byte 2` → Data verified → Activate headlight mode
- ❌ If checksum fails → Data corrupted → Message discarded

---

## 🎯 Decision Logic

| Switch Position | Ambient Light | Command | Intensity |
|-----------------|---------------|---------|-----------|
| 0 (Off) | Any | 0 (Off) | 0% |
| 1 (Manual On) | Any | 2 (Low Beam) | 80% |
| 2 (Auto) | > 100 Lux (Bright) | 1 (DRL) | 50% |
| 2 (Auto) | 20–100 Lux (Moderate) | 2 (Low Beam) | 80% |
| 2 (Auto) | < 20 Lux (Dark) | 3 (High Beam) | 100% |

---

## 🖥️ Dashboard Layout

The Streamlit app is divided into three main sections:

```
┌─────────────────┬────────────────┬──────────────────┐
│   NODE A (BCM)  │   CAN BUS      │  NODE B (Actuator)│
│                 │                │                   │
│ • Lux Slider    │ • CAN ID 0x215│ • Byte Extraction │
│ • Switch Select │ • Byte Display │ • Checksum Check  │
│ • Logic Trace   │ • Hex Dump     │ • Headlight Visual│
│                 │ • Corrupt Toggle│ • Status Output  │
└─────────────────┴────────────────┴──────────────────┘
           ┌──────────────────────────────┐
           │  Message Trace Log  │  Reference Table  │
           └──────────────────────────────┘
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone or download the project**

   ```bash
   git clone <repository-url>
   cd intelligent-headlight-controller
   ```

2. **Install dependencies**

   ```bash
   pip install streamlit python-can
   ```

3. **Run the application**

   ```bash
   streamlit run app.py
   ```

4. **Open in browser**

   The app will automatically open at `http://localhost:8501`. If not, navigate there manually.

---

## 📁 Project Structure

```
intelligent-headlight-controller/
│
├── app.py                  # Main Streamlit application (Node A + CAN Bus + Node B)
├── README.md               # This file
└── Report.docx             # Detailed project report (Word document)
```

---

## 🔧 How It Works

### Step 1 — Node A: Sense & Decide

The Body Control Module reads:
- **Lux Sensor**: Ambient light level (0–500 Lux via slider)
- **Manual Switch**: Off (0), Manual On (1), Auto (2)

Based on these, it computes:
- `command` → Headlight mode (0–3)
- `intensity` → Brightness percentage (0–100)
- `checksum` → `command + intensity`

### Step 2 — CAN Bus: Pack & Transmit

The three values are packed into a `can.Message` object:

```python
msg = can.Message(
    arbitration_id=0x215,
    data=[command, intensity, checksum, 0, 0, 0, 0, 0],
    is_extended_id=False,
)
```

### Step 3 — Node B: Receive, Verify & Act

The actuator:
1. Filters for CAN ID `0x215`
2. Extracts `Byte 0`, `Byte 1`, `Byte 2`
3. Verifies: `Byte 0 + Byte 1 == Byte 2`
4. If valid → maps command to headlight mode
5. If invalid → discards message as corrupted

### Step 4 — Corruption Simulation

Toggle the **"Simulate data corruption"** checkbox to randomly flip bits in Byte 1. This causes the checksum to fail, demonstrating how the integrity check protects against erroneous actuator commands.

---

## 🧪 Test Cases

| Test | Lux | Switch | Expected Command | Expected Intensity | Checksum |
|------|-----|--------|------------------|--------------------|----------|
| Default (Dark + Auto) | 20 | 2 (Auto) | 3 (High Beam) | 100% | 103 |
| Bright + Auto | 200 | 2 (Auto) | 1 (DRL) | 50% | 51 |
| Moderate + Auto | 60 | 2 (Auto) | 2 (Low Beam) | 80% | 82 |
| Manual On | Any | 1 (Manual) | 2 (Low Beam) | 80% | 82 |
| Off | Any | 0 (Off) | 0 (Off) | 0% | 0 |
| Corruption | 20 | 2 (Auto) | — | — | FAIL |

---

## 🔑 Key Concepts Demonstrated

- **Multi-input decision logic**: Combining sensor data with manual switch position
- **CAN 2.0A message framing**: Standard 11-bit identifier, 8-byte data field
- **Multi-byte data packing**: Structuring command, intensity, and checksum into a payload
- **Application-level checksum**: Using arithmetic sum for data integrity verification
- **Command-to-state mapping**: Converting integer codes to physical actuator states
- **Fault detection**: Identifying and rejecting corrupted messages before actuation

---

## 📚 Technologies Used

| Technology | Purpose |
|------------|---------|
| **Python 3.x** | Core simulation logic |
| **Streamlit** | Interactive web dashboard |
| **python-can** | CAN bus message creation and handling |
| **HTML/CSS** | Custom dark-theme UI styling |

---

## 📝 License

This project is developed for academic purposes as part of the Automotive Electronics course (23ECPE16) at Coimbatore Institute of Technology.

