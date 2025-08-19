#!/usr/bin/env python3
import gpiod
import time
import threading
from fastapi import FastAPI, Query
from enum import Enum
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

# =========================
# Motor GPIO config
# =========================
H_DIR, H_STEP = 19, 26
V_DIR, V_STEP = 20, 21
STEPS_PER_DEG = 32
STEP_DELAY = 0.0008

# =========================
# Button GPIO config (change as per wiring)
# =========================
BTN1_PIN = 16   # Horizontal control
BTN2_PIN = 13   # Vertical control
BTN3_PIN = 12   # Reset angles

# =========================
# State tracking
# =========================
current_angles = {
    "horizontal": 0,
    "vertical": 0,
}
zero_angles = {
    "horizontal": 0,
    "vertical": 0,
}

# =========================
# Setup GPIO chip
# =========================
chip = gpiod.Chip('gpiochip4')

# Output lines for motors
h_dir_line = chip.get_line(H_DIR)
h_step_line = chip.get_line(H_STEP)
v_dir_line = chip.get_line(V_DIR)
v_step_line = chip.get_line(V_STEP)

for line, name in zip([h_dir_line, h_step_line, v_dir_line, v_step_line],
                      ["h_dir", "h_step", "v_dir", "v_step"]):
    line.request(consumer=name, type=gpiod.LINE_REQ_DIR_OUT)

# Input lines for buttons
btn1_line = chip.get_line(BTN1_PIN)
btn2_line = chip.get_line(BTN2_PIN)
btn3_line = chip.get_line(BTN3_PIN)

for line, name in zip([btn1_line, btn2_line, btn3_line],
                      ["btn1", "btn2", "btn3"]):
    line.request(consumer=name, type=gpiod.LINE_REQ_DIR_IN)

# =========================
# FastAPI app
# =========================
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Motor(str, Enum):
    horizontal = "horizontal"
    vertical = "vertical"

class Direction(str, Enum):
    cw = "cw"
    ccw = "ccw"

# =========================
# Motor functions
# =========================
def rotate_motor(dir_line, step_line, steps, clockwise=True):
    dir_line.set_value(1 if clockwise else 0)
    for _ in range(steps):
        step_line.set_value(1)
        time.sleep(STEP_DELAY)
        step_line.set_value(0)
        time.sleep(STEP_DELAY)

def update_angle(motor: str, angle_delta: int, clockwise: bool):
    if clockwise:
        current_angles[motor] = (current_angles[motor] + angle_delta) % 360
    else:
        current_angles[motor] = (current_angles[motor] - angle_delta) % 360

def set_absolute_angle(motor: str, target_angle: int):
    current_angle = current_angles[motor]
    diff = (target_angle - current_angle + 360) % 360

    if diff <= 180:
        steps = diff * STEPS_PER_DEG
        clockwise = True
    else:
        steps = (360 - diff) * STEPS_PER_DEG
        clockwise = False

    dir_line, step_line = (
        (h_dir_line, h_step_line) if motor == "horizontal"
        else (v_dir_line, v_step_line)
    )

    rotate_motor(dir_line, step_line, int(steps), clockwise)
    current_angles[motor] = target_angle

# =========================
# Button monitoring
# =========================
def button_monitor():
    btn3_pressed_time = None

    while True:
        # Horizontal motor control
        if btn1_line.get_value() == 1:  # Button held down
            h_dir_line.set_value(1)  # CW direction
            h_step_line.set_value(1)
            time.sleep(STEP_DELAY)
            h_step_line.set_value(0)
            time.sleep(STEP_DELAY)
            update_angle("horizontal", 1 / STEPS_PER_DEG, True)

        # Vertical motor control
        if btn2_line.get_value() == 1:  # Button held down
            v_dir_line.set_value(1)  # CW direction
            v_step_line.set_value(1)
            time.sleep(STEP_DELAY)
            v_step_line.set_value(0)
            time.sleep(STEP_DELAY)
            update_angle("vertical", 1 / STEPS_PER_DEG, True)

        # BTN3 press detection
        if btn3_line.get_value() == 1:
            if btn3_pressed_time is None:
                btn3_pressed_time = time.time()  # start timing press
        else:
            # BTN3 released
            if btn3_pressed_time is not None:
                press_duration = time.time() - btn3_pressed_time

                if press_duration >= 3:
                    # Long press → store current angles as new zero
                    print("BTN3 long press → Store new zero positions")
                    zero_angles["horizontal"] = current_angles["horizontal"]
                    zero_angles["vertical"] = current_angles["vertical"]
                else:
                    # Short press → reset to stored zero angles
                    print("BTN3 short press → Reset to zero positions")
                    set_absolute_angle("horizontal", zero_angles["horizontal"])
                    set_absolute_angle("vertical", zero_angles["vertical"])

                btn3_pressed_time = None

        time.sleep(0.01)

# =========================
# FastAPI endpoints
# =========================
@app.get("/rotate")
def rotate(
    motor: Motor = Query(...),
    angle: int = Query(..., ge=0, le=360),
    direction: Direction = Query(...)
):
    steps = angle * STEPS_PER_DEG
    clockwise = direction == "cw"

    dir_line, step_line = (
        (h_dir_line, h_step_line) if motor == "horizontal"
        else (v_dir_line, v_step_line)
    )

    def rotate_and_update():
        rotate_motor(dir_line, step_line, steps, clockwise)
        update_angle(motor, angle, clockwise)

    threading.Thread(target=rotate_and_update).start()

    return {
        "status": "rotating",
        "motor": motor,
        "angle_change": angle,
        "direction": direction,
        "new_angle_estimate": (current_angles[motor] + angle if clockwise else current_angles[motor] - angle) % 360
    }

@app.get("/set_angle")
def set_angle(
    motor: Motor = Query(...),
    target_angle: int = Query(..., ge=0, le=360)
):
    def rotate_and_set():
        set_absolute_angle(motor, target_angle)

    threading.Thread(target=rotate_and_set).start()

    return {
        "status": "rotating_to_absolute",
        "motor": motor,
        "target_angle": target_angle,
        "current_angle_before": current_angles[motor]
    }

@app.get("/status")
def get_angles():
    return current_angles

# =========================
# Startup & Cleanup
# =========================
@app.on_event("startup")
def startup_event():
    threading.Thread(target=button_monitor, daemon=True).start()

@app.on_event("shutdown")
def cleanup():
    for line in [h_dir_line, h_step_line, v_dir_line, v_step_line, btn1_line, btn2_line, btn3_line]:
        line.release()
    chip.close()
    print("GPIO cleaned up.")

# =========================
# Main
# =========================
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
