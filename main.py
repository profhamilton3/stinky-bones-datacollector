# ============================================================
# Stinky Bones — Data Collector
# ============================================================
# Hardware: micro:bit v2 (stationary — placed near the arena)
#
# This microbit listens for 16-byte telemetry buffers that the
# XGO dog broadcasts every 3 seconds. It logs each sample to
# the micro:bit v2 built-in datalogger. After a session, plug
# this microbit into a computer via USB and open the MY_DATA
# drive to download the CSV file for analysis in spreadsheets
# or Python/pandas.
#
# ── LOGGED COLUMNS ────────────────────────────────────────
# mag_x, mag_y, mag_z  — magnetic force (µT) on each axis
# accel_x, accel_y, accel_z — acceleration (mg) on each axis
# sonar_cm             — distance to nearest obstacle (cm)
# dog_state            — 0=IDLE 1=SEARCHING 2=CELEBRATING 3=AVOIDING
#
# ── BUTTON CONTROLS ───────────────────────────────────────
# Button A  — display total sample count on LED matrix
# Button B  — clear the log (confirmation blink first)
# ============================================================


# ────────────────────────────────────────────────────────────
# CONSTANTS
# ────────────────────────────────────────────────────────────
RADIO_GROUP = 3   # must match stinky-bones-xgo


# ────────────────────────────────────────────────────────────
# STATE
# ────────────────────────────────────────────────────────────
sample_count = 0   # running total of samples received


# ────────────────────────────────────────────────────────────
# HARDWARE INITIALISATION
# ────────────────────────────────────────────────────────────
radio.set_group(RADIO_GROUP)

# Configure column headers — these become the CSV headers when
# the data file is downloaded from the MY_DATA USB drive
datalogger.set_column_titles(
    "mag_x", "mag_y", "mag_z",
    "accel_x", "accel_y", "accel_z",
    "sonar_cm", "dog_state"
)

# Startup: scroll "LOG" to show collector is ready
basic.show_string("LOG")
basic.pause(500)
basic.clear_screen()


# ────────────────────────────────────────────────────────────
# INCOMING TELEMETRY HANDLER
# ────────────────────────────────────────────────────────────

def on_radio_buffer(buf: Buffer):
    """Receive and log a 16-byte sensor snapshot from the XGO dog.

    Buffer layout (all INT16_LE, 2 bytes each):
      offset 0  : mag_x       offset 6  : accel_x
      offset 2  : mag_y       offset 8  : accel_y
      offset 4  : mag_z       offset 10 : accel_z
      offset 12 : sonar_cm    offset 14 : dog_state
    """
    global sample_count
    if len(buf) >= 16:
        mag_x    = buf.get_number(NumberFormat.INT16_LE, 0)
        mag_y    = buf.get_number(NumberFormat.INT16_LE, 2)
        mag_z    = buf.get_number(NumberFormat.INT16_LE, 4)
        accel_x  = buf.get_number(NumberFormat.INT16_LE, 6)
        accel_y  = buf.get_number(NumberFormat.INT16_LE, 8)
        accel_z  = buf.get_number(NumberFormat.INT16_LE, 10)
        sonar_cm = buf.get_number(NumberFormat.INT16_LE, 12)
        dog_state = buf.get_number(NumberFormat.INT16_LE, 14)

        datalogger.log(
            datalogger.create_cv("mag_x", mag_x),
            datalogger.create_cv("mag_y", mag_y),
            datalogger.create_cv("mag_z", mag_z),
            datalogger.create_cv("accel_x", accel_x),
            datalogger.create_cv("accel_y", accel_y),
            datalogger.create_cv("accel_z", accel_z),
            datalogger.create_cv("sonar_cm", sonar_cm),
            datalogger.create_cv("dog_state", dog_state)
        )
        sample_count += 1

        # Flash the top-row LED position matching dog state
        # so you can see at a glance what the dog is doing
        led.plot(dog_state % 5, 0)
        basic.pause(60)
        led.unplot(dog_state % 5, 0)

radio.on_received_buffer(on_radio_buffer)


# ────────────────────────────────────────────────────────────
# BUTTON CONTROLS
# ────────────────────────────────────────────────────────────

# Button A — show how many samples have been collected
def on_button_a():
    basic.show_number(sample_count)
    basic.pause(1200)
    basic.clear_screen()
input.on_button_pressed(Button.A, on_button_a)


# Button B — clear the log (useful between runs)
def on_button_b():
    global sample_count
    # Blink to confirm before clearing
    basic.show_icon(IconNames.NO)
    basic.pause(600)
    datalogger.delete_log()
    sample_count = 0
    basic.show_string("CLR")
    basic.pause(600)
    basic.clear_screen()
input.on_button_pressed(Button.B, on_button_b)


# ────────────────────────────────────────────────────────────
# MAIN LOOP (idle — all work happens in the radio handler)
# ────────────────────────────────────────────────────────────

def on_forever():
    basic.pause(200)

basic.forever(on_forever)
