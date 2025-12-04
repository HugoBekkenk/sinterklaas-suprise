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

# Buzzer setup (passive piezo)
BUZZ = 17
GPIO.setup(BUZZ, GPIO.OUT)
pwm = GPIO.PWM(BUZZ, 440)  # start at A4

# Zelda notes
notes = {
    'c': 262, 'd': 294, 'e': 330, 'f': 349,
    'g': 392, 'a': 440, 'b': 494,
    'C': 523, 'D': 587, 'E': 659, 'F': 698,
    'x': 740, 'y': 784, 'z': 830, 'w': 880,
    'q': 988, 'G': 1046, 'i': 1108
}

melody = "gabygabyxzCDxzCDabywabywzCDEzCDEbywFCDEqywFGDEqi"
beats = [
    1,1,1,1, 1,1,1,1, 1,1,1,1, 1,1,1,1,
    1,1,1,1, 1,1,1,1, 1,1,1,1, 1,1,1,1,
    1,1,1,1, 1,1,1,1, 1,1,1,1, 1,1,1,1,
    1,1,1,1, 1,1,1,1, 2,3,3,16
]
tempo = 0.075  # melody speed

def play_note(note, duration):
    if note == " ":
        pwm.stop()
        time.sleep(duration)
        return
    freq = notes[note]
    pwm.ChangeFrequency(freq)
    pwm.start(50)
    time.sleep(duration)
    pwm.stop()
    time.sleep(0.01)

def play_zelda():
    for i, n in enumerate(melody):
        play_note(n, beats[i] * tempo)

# --- EVENTS ---
def unlock():
    print("Unlock received! Opening...")
    set_servo(90)
    play_zelda()

def lock():
    print("Lock received! Closing...")
    set_servo(0)

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
