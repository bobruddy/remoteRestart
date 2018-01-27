import RPi.GPIO as GPIO
import time

LedPin = 11

def setup():
	GPIO.setmode(GPIO.BOARD)  # num by location
	GPIO.setup(LedPin, GPIO.OUT) # outbound pin
	GPIO.output(LedPin, GPIO.HIGH) # set pine high to turn on

def blink():
	while True:
		GPIO.output( LedPin, GPIO.HIGH)
		time.sleep(1)
		GPIO.output(LedPin, GPIO.LOW)
		time.sleep(1)

def destroy():
	GPIO.output(LedPin, GPIO.LOW)
	GPIO.cleanup()

if __name__ == '__main__':
	setup()
	try:
		blink()
	except KeyboardInterrupt:
		destroy()

