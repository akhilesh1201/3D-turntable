import RPi.GPIO as GPIO
import time
import threading

# GPIO Pins
H_DIR = 19
H_STEP = 26
V_DIR = 20
V_STEP = 21

# Setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(True)
GPIO.setup(H_DIR, GPIO.OUT)
GPIO.setup(H_STEP, GPIO.OUT)
GPIO.setup(V_DIR, GPIO.OUT)
GPIO.setup(V_STEP, GPIO.OUT)

def rotate_motor(dir_pin, step_pin, steps, direction=True, delay=0.0008):
    GPIO.output(dir_pin, direction)
    for _ in range(steps):
        GPIO.output(step_pin, GPIO.HIGH)
        time.sleep(delay)
        GPIO.output(step_pin, GPIO.LOW)
        time.sleep(delay)

# Thread wrapper
def run_motor_threaded(dir_pin, step_pin, steps, direction):
    thread = threading.Thread(target=rotate_motor, args=(dir_pin, step_pin, steps, direction))
    thread.start()
    return thread

try:
    # Rotate both motors 360° clockwise in parallel
    t1 = run_motor_threaded(H_DIR, H_STEP, 32*360, direction=True)
    t2 = run_motor_threaded(V_DIR, V_STEP, 32*360, direction=True)

    # Wait for both to finish
    t1.join()
    t2.join()

    # Rotate both motors 360° counter-clockwise in parallel
    t3 = run_motor_threaded(H_DIR, H_STEP, 32*360, direction=False)
    t4 = run_motor_threaded(V_DIR, V_STEP, 32*360, direction=False)

    t3.join()
    t4.join()

finally:
    GPIO.cleanup()