//  ============================================================
//  Stinky Bones — Data Collector
//  ============================================================
//  Hardware: micro:bit v2 (stationary — placed near the arena)
// 
//  Logs persist across power loss. Data is NOT cleared on
//  restart. Only a deliberate A+B press clears the log.
// 
//  ── LOGGED COLUMNS ────────────────────────────────────────
//  mag_x, mag_y, mag_z  — magnetic force (µT) on each axis
//  accel_x, accel_y, accel_z — acceleration (mg) on each axis
//  sonar_cm             — distance to nearest obstacle (cm)
//  dog_state            — 0=IDLE 1=SEARCHING 2=CELEBRATING 3=AVOIDING
// 
//  ── BUTTON CONTROLS ───────────────────────────────────────
//  Button A        — show total sample count
//  Button B        — show bone-spike count (samples where dog
//                    was in CELEBRATING state = bone found)
//  Button A + B    — clear the log and reset all counters
//  ============================================================
//  ────────────────────────────────────────────────────────────
//  CONSTANTS
//  ────────────────────────────────────────────────────────────
let RADIO_GROUP = 3
//  must match stinky-bones-xgo
//  ────────────────────────────────────────────────────────────
//  STATE
//  Note: these in-memory counters reset on power loss, but the
//  logged data in flash persists. Use Button A/B to re-check
//  counts from the current power-on session only.
//  ────────────────────────────────────────────────────────────
let sample_count = 0
//  total telemetry packets received this session
let spike_count = 0
//  packets where dog_state == 2 (CELEBRATING = bone found)
//  ────────────────────────────────────────────────────────────
//  HARDWARE INITIALISATION
//  ────────────────────────────────────────────────────────────
radio.setGroup(RADIO_GROUP)
//  NOTE: datalogger.set_column_titles() is intentionally omitted.
//  Calling it on every boot re-initialises the log and erases
//  previously stored data. Column names are already embedded in
//  each row via create_cv(), so the CSV downloads correctly
//  without calling set_column_titles() first.
//  Startup: scroll "LOG" to show collector is ready
basic.showString("LOG")
basic.pause(500)
basic.clearScreen()
//  ────────────────────────────────────────────────────────────
//  INCOMING TELEMETRY HANDLER
//  ────────────────────────────────────────────────────────────
radio.onReceivedBuffer(function on_radio_buffer(buf: Buffer) {
    let mag_x: number;
    let mag_y: number;
    let mag_z: number;
    let accel_x: number;
    let accel_y: number;
    let accel_z: number;
    let sonar_cm: number;
    let dog_state: number;
    /** Receive and log a 16-byte sensor snapshot from the XGO dog.

    Buffer layout (all INT16_LE, 2 bytes each):
      offset 0  : mag_x       offset 6  : accel_x
      offset 2  : mag_y       offset 8  : accel_y
      offset 4  : mag_z       offset 10 : accel_z
      offset 12 : sonar_cm    offset 14 : dog_state
    
 */
    
    if (buf.length >= 16) {
        mag_x = buf.getNumber(NumberFormat.Int16LE, 0)
        mag_y = buf.getNumber(NumberFormat.Int16LE, 2)
        mag_z = buf.getNumber(NumberFormat.Int16LE, 4)
        accel_x = buf.getNumber(NumberFormat.Int16LE, 6)
        accel_y = buf.getNumber(NumberFormat.Int16LE, 8)
        accel_z = buf.getNumber(NumberFormat.Int16LE, 10)
        sonar_cm = buf.getNumber(NumberFormat.Int16LE, 12)
        dog_state = buf.getNumber(NumberFormat.Int16LE, 14)
        datalogger.log(datalogger.createCV("mag_x", mag_x), datalogger.createCV("mag_y", mag_y), datalogger.createCV("mag_z", mag_z), datalogger.createCV("accel_x", accel_x), datalogger.createCV("accel_y", accel_y), datalogger.createCV("accel_z", accel_z), datalogger.createCV("sonar_cm", sonar_cm), datalogger.createCV("dog_state", dog_state))
        sample_count += 1
        //  A sample with dog_state == 2 means the dog is celebrating
        //  a bone find — count these as magnetometer spikes
        if (dog_state == 2) {
            spike_count += 1
        }
        
        //  Flash the top-row LED position matching dog state
        //  so you can see at a glance what the dog is doing
        led.plot(dog_state % 5, 0)
        basic.pause(60)
        led.unplot(dog_state % 5, 0)
    }
    
})
//  ────────────────────────────────────────────────────────────
//  BUTTON CONTROLS
//  ────────────────────────────────────────────────────────────
//  Button A — show total sample count this session
input.onButtonPressed(Button.A, function on_button_a() {
    basic.showNumber(sample_count)
    basic.pause(1200)
    basic.clearScreen()
})
//  Button B — show bone-spike count (dog_state == 2 samples)
input.onButtonPressed(Button.B, function on_button_b() {
    basic.showIcon(IconNames.Diamond)
    basic.pause(400)
    basic.showNumber(spike_count)
    basic.pause(1200)
    basic.clearScreen()
})
//  Button A + B — clear the log (deliberate two-button action
//  prevents accidental wipe; data survives power loss until here)
input.onButtonPressed(Button.AB, function on_button_ab() {
    
    //  Show warning icon, pause so user can release if accidental
    basic.showIcon(IconNames.No)
    basic.pause(1000)
    datalogger.deleteLog()
    sample_count = 0
    spike_count = 0
    basic.showString("CLR")
    basic.pause(600)
    basic.clearScreen()
})
//  ────────────────────────────────────────────────────────────
//  MAIN LOOP (idle — all work happens in the radio handler)
//  ────────────────────────────────────────────────────────────
basic.forever(function on_forever() {
    basic.pause(200)
})
