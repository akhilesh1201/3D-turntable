#!/usr/bin/env python3
import gpiod
import time
import threading
from fastapi import FastAPI, Query
from enum import Enum
import uvicorn

# GPIO config
H_DIR, H_STEP = 19, 26
V_DIR, V_STEP = 20, 21
STEPS_PER_DEG = 32
STEP_DELAY = 0.0008

# State tracking
current_angles = {
    "horizontal": 0,
    "vertical": 0,
}

# Setup GPIO chip (Raspberry Pi 5)
chip = gpiod.Chip('gpiochip4')
h_dir_line = chip.get_line(H_DIR)
h_step_line = chip.get_line(H_STEP)
v_dir_line = chip.get_line(V_DIR)
v_step_line = chip.get_line(V_STEP)

for line, name in zip([h_dir_line, h_step_line, v_dir_line, v_step_line],
                      ["h_dir", "h_step", "v_dir", "v_step"]):
    line.request(consumer=name, type=gpiod.LINE_REQ_DIR_OUT)

# FastAPI app
app = FastAPI()

class Motor(str, Enum):
    horizontal = "horizontal"
    vertical = "vertical"

class Direction(str, Enum):
    cw = "cw"
    ccw = "ccw"

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

    t = threading.Thread(target=rotate_and_update)
    t.start()

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
    target_angle: int = Query(..., ge=0, le=359)
):
    current_angle = current_angles[motor]
    diff = (target_angle - current_angle + 360) % 360

    # Choose shortest direction
    if diff <= 180:
        direction = "cw"
        steps = diff * STEPS_PER_DEG
        clockwise = True
    else:
        direction = "ccw"
        steps = (360 - diff) * STEPS_PER_DEG
        clockwise = False

    dir_line, step_line = (
        (h_dir_line, h_step_line) if motor == "horizontal"
        else (v_dir_line, v_step_line)
    )

    def rotate_and_update():
        rotate_motor(dir_line, step_line, int(steps), clockwise)
        current_angles[motor] = target_angle

    t = threading.Thread(target=rotate_and_update)
    t.start()

    return {
        "status": "setting absolute angle",
        "motor": motor,
        "from_angle": current_angle,
        "to_angle": target_angle,
        "direction": direction,
        "steps": int(steps)
    }

@app.get("/status")
def get_angles():
    return {
        "horizontal_angle": current_angles["horizontal"],
        "vertical_angle": current_angles["vertical"]
    }

@app.on_event("shutdown")
def cleanup():
    for line in [h_dir_line, h_step_line, v_dir_line, v_step_line]:
        line.release()
    chip.close()
    print("GPIO cleaned up.")