#!/usr/bin/env python3
import gpiod
import time
import threading

# GPIO BC​M pin numbers for your motors
H_DIR = 19
H_STEP = 26
V_DIR = 20
V_STEP = 21

# Hardware config
STEPS_PER_DEG = 32
STEP_DELAY    = 0.0008  # seconds

# Use the correct gpio chip (RPi5 uses gpiochip4 for header) :contentReference[oaicite:6]{index=6}
chip = gpiod.Chip('gpiochip4')

# Reserve lines
h_dir_line  = chip.get_line(H_DIR)
h_step_line = chip.get_line(H_STEP)
v_dir_line  = chip.get_line(V_DIR)
v_step_line = chip.get_line(V_STEP)

# Set directions
h_dir_line.request(consumer="h_dir",  type=gpiod.LINE_REQ_DIR_OUT)
h_step_line.request(consumer="h_step", type=gpiod.LINE_REQ_DIR_OUT)
v_dir_line.request(consumer="v_dir",  type=gpiod.LINE_REQ_DIR_OUT)
v_step_line.request(consumer="v_step", type=gpiod.LINE_REQ_DIR_OUT)

def rotate_motor(dir_line, step_line, steps, clockwise=True):
    dir_line.set_value(int(clockwise))
    for _ in range(steps):
        step_line.set_value(1)
        time.sleep(STEP_DELAY)
        step_line.set_value(0)
        time.sleep(STEP_DELAY)

def run_motor_threaded(dir_line, step_line, steps, clockwise=True):
    t = threading.Thread(
        target=rotate_motor,
        args=(dir_line, step_line, steps, clockwise)
    )
    t.start()
    return t

def rotate_both():
    print("Rotating 360° CW")
    t1 = run_motor_threaded(h_dir_line, h_step_line, STEPS_PER_DEG, True)
    t2 = run_motor_threaded(v_dir_line, v_step_line, STEPS_PER_DEG, True)
    t1.join();
    t2.join()

    print("Rotating 360° CCW")
    t3 = run_motor_threaded(h_dir_line, h_step_line, STEPS_PER_DEG, False)
    t4 = run_motor_threaded(v_dir_line, v_step_line, STEPS_PER_DEG, False)
    t3.join();
    t4.join()

if __name__ == "__main__":
    try:
        for i in range(360):
            rotate_both()
    finally:
        # release GPIO lines
        for line in [h_dir_line, h_step_line, v_dir_line, v_step_line]:
            line.release()
        chip.close()
        print("Done.")
