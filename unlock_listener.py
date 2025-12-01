from Adafruit_IO import MQTTClient
import RPi.GPIO as GPIO
import time

# CHANGE THESE
AIO_USERNAME = "YOUR_USERNAME"
AIO_KEY = "YOUR_AIO_KEY"
FEED_KEY = "unlock"

# Servo setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)
servo = GPIO.PWM(18, 50)
servo.start(0)

def set_servo(angle):
    duty = 2 + (angle / 18)
    servo.ChangeDutyCycle(duty)
    time.sleep(0.3)

def unlock():
    print("Unlock received! Opening...")
    set_servo(90)
    time.sleep(1)
    set_servo(0)

def connected(client):
    print("Connected to Adafruit IO!")
    client.subscribe(FEED_KEY)

def message(client, feed_id, payload):
    print("Feed:", feed_id, "Value:", payload)
    if payload == "1":
        unlock()

client = MQTTClient(AIO_USERNAME, AIO_KEY)
client.on_connect = connected
client.on_message = message

client.connect()
client.loop_blocking()
