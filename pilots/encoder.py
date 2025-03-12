import time

import RPi.GPIO as GPIO

#GPIO Pins (BCM MODE)
CLK=21
DT=20
SW=16
#GPIO SETUP
GPIO.setmode(GPIO.BCM)
GPIO.setup(CLK, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(DT, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(SW, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Pull-up for button

def coucou(txt) :
    print(f"coucou {txt}")

#Methods that are called when an action is detected
GAUCHE=coucou
DROITE=coucou
BOUTTON=coucou

#Callback handling
global last_pin
last_pin=0

def callback_boutton(pin) :
    BOUTTON("BOUTTON")

def callback_click(pin) :
    global last_pin
    if last_pin==0 :
        last_pin=pin
    else :
        if pin==21 :
            GAUCHE("gauche")
            last_pin=0
        if pin==20 :
            DROITE("droite")
            last_pin=0

#Callback link
GPIO.add_event_detect(SW, GPIO.FALLING,callback=callback_boutton,bouncetime=300)
GPIO.add_event_detect(DT, GPIO.RISING,callback=callback_click,bouncetime=100)
GPIO.add_event_detect(CLK, GPIO.RISING,callback=callback_click,bouncetime=100)

#TEST
#while True :
#    time.sleep(1)