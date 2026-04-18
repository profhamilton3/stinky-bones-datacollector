# ============================================================
# Stinky Bones — Data Collector
# ============================================================
# Hardware: micro:bit v2 (stationary — placed near the arena)
#
# Logs persist across power loss. Data is NOT cleared on
# restart. Only a deliberate A+B press clears the log.
#
# ── LOGGED COLUMNS ────────────────────────────────────────
# mag_x, mag_y, mag_z  — magnetic force (µT) on each axis
# accel_x, accel_y, accel_z — acceleration (mg) on each axis
# sonar_cm             — distance to nearest obstacle (cm)
# dog_state            — 0=IDLE 1=SEARCHING 2=CELEBRATING 3=AVOIDING
#
# ── BUTTON CONTROLS ───────────────────────────────────────
# Button A        — show total sample count
# Button B        — show bone-spike count (samples where dog
#                   was in CELEBRATING state = bone found)
# Button A + B    — clear the log and reset all counters
# ============================================================


# ────────────────────────────────────────────────────────────
# CONSTANTS
# ────────────────────────────────────────────────────────────
RADIO_GROUP = 3   # must match stinky-bones-xgo


# ────────────────────────────────────────────────────────────
# STATE
# Note: these in-memory counters reset on power loss, but the
# logged data in flash persists. Use Button A/B to re-check
# counts from the current power-on session only.
# ────────────────────────────────────────────────────────────
sample_count = 0   # total telemetry packets received this session
spike_count  = 0   # packets where dog_state == 2 (CELEBRATING = bone found)


# ────────────────────────────────────────────────────────────
# HARDWARE INITIALISATION
# ────────────────────────────────────────────────────────────
radio.set_group(RADIO_GROUP)

# NOTE: datalogger.set_column_titles() is intentionally omitted.
# Calling it on every boot re-initialises the log and erases
# previously stored data. Column names are already embedded in
# each row via create_cv(), so the CSV downloads correctly
# without calling set_column_titles() first.

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
    global sample_count, spike_count
    if len(buf) >= 16:
        mag_x     = buf.get_number(NumberFormat.INT16_LE, 0)
        mag_y     = buf.get_number(NumberFormat.INT16_LE, 2)
        mag_z     = buf.get_number(NumberFormat.INT16_LE, 4)
        accel_x   = buf.get_number(NumberFormat.INT16_LE, 6)
        accel_y   = buf.get_number(NumberFormat.INT16_LE, 8)
        accel_z   = buf.get_number(NumberFormat.INT16_LE, 10)
        sonar_cm  = buf.get_number(NumberFormat.INT16_LE, 12)
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

        # A sample with dog_state == 2 means the dog is celebrating
        # a bone find — count these as magnetometer spikes
        if dog_state == 2:
            spike_count += 1

        # Flash the top-row LED position matching dog state
        # so you can see at a glance what the dog is doing
        led.plot(dog_state % 5, 0)
        basic.pause(60)
        led.unplot(dog_state % 5, 0)

radio.on_received_buffer(on_radio_buffer)


# ────────────────────────────────────────────────────────────
# BUTTON CONTROLS
# ────────────────────────────────────────────────────────────

# Button A — show total sample count this session
def on_button_a():
    basic.show_number(sample_count)
    basic.pause(1200)
    basic.clear_screen()
input.on_button_pressed(Button.A, on_button_a)


# Button B — show bone-spike count (dog_state == 2 samples)
def on_button_b():
    basic.show_icon(IconNames.DIAMOND)
    basic.pause(400)
    basic.show_number(spike_count)
    basic.pause(1200)
    basic.clear_screen()
input.on_button_pressed(Button.B, on_button_b)


# Button A + B — clear the log (deliberate two-button action
# prevents accidental wipe; data survives power loss until here)
def on_button_ab():
    global sample_count, spike_count
    # Show warning icon, pause so user can release if accidental
    basic.show_icon(IconNames.NO)
    basic.pause(1000)
    datalogger.delete_log()
    sample_count = 0
    spike_count  = 0
    basic.show_string("CLR")
    basic.pause(600)
    basic.clear_screen()
input.on_button_pressed(Button.AB, on_button_ab)


# ────────────────────────────────────────────────────────────
# MAIN LOOP (idle — all work happens in the radio handler)
# ────────────────────────────────────────────────────────────

def on_forever():
    basic.pause(200)

basic.forever(on_forever)
