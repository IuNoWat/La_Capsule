import time

import RPi.GPIO as GPIO

#This pilot allow the use of a rotary encoder :
# 1 - Setting the GPIO to connect to the rotary encoder
# 2 - Declaration of the methods to call when the encoder is turned right, left, or clicked
# 3 - IDK what is going on here
# 4 - Adding the callback to the methods declared before

# 1 - Setting the GPIO to connect to the rotary encoder

#GPIO Pins (BCM MODE)
CLK=21
DT=20
SW=16
#GPIO SETUP
GPIO.setmode(GPIO.BCM)
GPIO.setup(CLK, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(DT, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(SW, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Pull-up for button

# 2 - Declaration of the methods to call when the encoder is turned right, left, or clicked

def coucou(txt) :
    print(f"coucou {txt}")

#Methods that are called when an action is detected
GAUCHE=coucou
DROITE=coucou
BOUTTON=coucou

# 3 - IDK what is going on here

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

# 4 - Adding the callback to the methods declared before

#Callback link
GPIO.add_event_detect(SW, GPIO.FALLING,callback=callback_boutton,bouncetime=300)
GPIO.add_event_detect(DT, GPIO.RISING,callback=callback_click,bouncetime=100)
GPIO.add_event_detect(CLK, GPIO.RISING,callback=callback_click,bouncetime=100)

#TEST
#while True :
#    time.sleep(1)