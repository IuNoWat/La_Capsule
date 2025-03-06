import RPi.GPIO as GPIO

import time

CLK=21
DT=20
SW=16

GPIO.setmode(GPIO.BCM)

GPIO.setup(CLK, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(DT, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(SW, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Pull-up for button

# Variables
counter = 0
last_clk = GPIO.input(CLK)

try:
    while True:
        # Read current state of CLK
        current_clk = GPIO.input(CLK)
        current_dt = GPIO.input(DT)

        if current_clk != last_clk:  # Detect a change in CLK
            if current_dt != current_clk:
                counter += 1  # Clockwise
            else:
                counter -= 1  # Counter-clockwise
            print(f"Counter: {counter}")

        last_clk = current_clk

        # Check button press
        if GPIO.input(SW) == GPIO.LOW:
            print("Button pressed!")
            time.sleep(0.3)  # Debounce delay

        time.sleep(0.01)  # Small delay to stabilize readings

except KeyboardInterrupt:
    print("\nExiting...")

finally:
    GPIO.cleanup()
