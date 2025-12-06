import os
from Adafruit_IO import MQTTClient
import RPi.GPIO as GPIO
import time

# CHANGE THESE
AIO_USERNAME = "HugoMaster"
AIO_KEY = "YOUR_AIO_KEY"
FEED_KEY = "sinterklaas-suprise"

# --- GPIO SETUP ---
GPIO.setmode(GPIO.BCM)

# Servo setup
GPIO.setup(18, GPIO.OUT)
servo = GPIO.PWM(18, 50)
servo.start(0)

def set_servo(angle):
    duty = 2 + (angle / 18)
    servo.ChangeDutyCycle(duty)
    time.sleep(0.3)

# --- Passive Piezo Buzzer ---
BUZZ = 17
GPIO.setup(BUZZ, GPIO.OUT)
pwm = GPIO.PWM(BUZZ, 440)

# --- REAL ZELDA FANFARE ---
zelda_notes = [1046, 1174, 1318, 1567, 2093]
zelda_lengths = [0.15, 0.15, 0.15, 0.30, 0.60]

def play_zelda():
    for freq, dur in zip(zelda_notes, zelda_lengths):
        pwm.ChangeFrequency(freq)
        pwm.start(50)
        time.sleep(dur)
        pwm.stop()
        time.sleep(0.03)

# --- EVENTS ---
def unlock():
    print("Unlock received! Opening...")
    set_servo(90)
    play_zelda()

def lock():
    print("Lock received! Closing...")
    set_servo(0)

def shutdown_pi():
    print("Shutdown command received! Shutting down safely...")
    servo.stop()
    pwm.stop()
    GPIO.cleanup()
    time.sleep(1)
    os.system("sudo shutdown -h now")

# --- MQTT ---
def connected(client):
    print("Connected to Adafruit IO!")
    client.subscribe(FEED_KEY)

def message(client, feed_id, payload):
    print("Feed:", feed_id, "Value:", payload)

    if payload == "1":
        unlock()

    elif payload == "0":
        lock()

    elif payload == "3":
        shutdown_pi()  # 🠔 trigger safe shutdown

client = MQTTClient(AIO_USERNAME, AIO_KEY)
client.on_connect = connected
client.on_message = message

try:
    client.connect()
    client.loop_blocking()

except KeyboardInterrupt:
    pass

finally:
    servo.stop()
    pwm.stop()
    GPIO.cleanup()
    print("GPIO cleaned up - exiting")
