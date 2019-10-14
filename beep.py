import RPi.GPIO as GPIO
from time import sleep
buzzer=21
GPIO.setmode(GPIO.BCM)
GPIO.setup(buzzer,GPIO.OUT)
GPIO.output(buzzer,GPIO.HIGH)
sleep(0.5)
GPIO.output(buzzer,GPIO.LOW)
GPIO.cleanup()
