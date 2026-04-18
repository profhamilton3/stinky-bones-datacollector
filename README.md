# Stinky Bones — Data Collector

> **THE Hamilton Essentials Foundation** | STEAM Coding Curriculum

A stationary micro:bit v2 that silently listens for sensor data
broadcast by the XGO dog over radio. Every 3 seconds the dog sends a
16-byte snapshot of its magnetometer, accelerometer, sonar, and state.
This collector logs every snapshot to the micro:bit v2 built-in
datalogger. After a bone-hunting session, plug this micro:bit into a
computer to download a CSV file for analysis.

---

## Hardware Required

| Qty | Part |
|---|---|
| 1 | micro:bit v2 (v2 required — datalogger is v2-only) |
| 1 | USB cable |

Place this micro:bit somewhere stationary near the arena —
on a table, a shelf, or taped to the wall within radio range (~10m).

---

## Loading in MakeCode

1. Go to [makecode.microbit.org](https://makecode.microbit.org)
2. Click **Import** → **Import URL**
3. Paste: `https://github.com/profhamilton3/stinky-bones-datacollector`
4. Click the **Python** tab
5. Click **Download** and copy the `.hex` to your MICROBIT drive

---

## Downloading Your Data

1. After a session, plug this micro:bit into a computer via USB
2. Open **File Explorer** (Windows) or **Finder** (Mac)
3. Look for a drive called **MY_DATA**
4. Open `MY_DATA.HTM` — it launches the MakeCode data viewer
5. Click **Download CSV** to save the file
6. Open in Excel, Google Sheets, or Python/pandas for analysis

---

## Logged Columns

| Column | Units | Description |
|---|---|---|
| `mag_x` | µT | Magnetic force, X axis |
| `mag_y` | µT | Magnetic force, Y axis |
| `mag_z` | µT | Magnetic force, Z axis |
| `accel_x` | mg | Acceleration, X axis |
| `accel_y` | mg | Acceleration, Y axis |
| `accel_z` | mg | Acceleration, Z axis |
| `sonar_cm` | cm | Distance to nearest obstacle |
| `dog_state` | 0–3 | 0=IDLE 1=SEARCHING 2=CELEBRATING 3=AVOIDING |

---

## Button Controls

| Button | Action |
|---|---|
| Button A | Show total sample count on LED matrix |
| Button B | Clear the log (blinks before clearing) |

---

## LED Indicators

| Display | Meaning |
|---|---|
| Scrolling "LOG" at startup | Collector is ready |
| Top-row dot blink | Telemetry packet received from dog |
| "CLR" scroll | Log has been cleared |

---

## Analysis Ideas for Students

After downloading the CSV, students can:

- Plot `mag_strength` over time to see peaks where bones were found
- Compare `sonar_cm` and `dog_state` to verify wall-avoidance events
- Map the bone locations using `accel_x`/`accel_y` as rough position hints
- Tune the `BONE_THRESHOLD` constant using real data from their run

---

*THE Hamilton Essentials Foundation, Inc.*
