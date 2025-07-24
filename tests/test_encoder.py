#/usr/bin/env python3 
# Test encoder rotation and button 
 
import RPi.GPIO as GPIO 
import time 
 
# Encoder pins 
CLK = 19 
DT = 13 
SW = 26 
 
GPIO.setmode(GPIO.BCM) 
GPIO.setup(CLK, GPIO.IN, pull_up_down=GPIO.PUD_UP) 
GPIO.setup(DT, GPIO.IN, pull_up_down=GPIO.PUD_UP) 
GPIO.setup(SW, GPIO.IN, pull_up_down=GPIO.PUD_UP) 
 
counter = 0 
clkLastState = GPIO.input(CLK) 
 
print("Encoder Test - Rotate and press button") 
print("Press Ctrl+C to exit") 
 
try: 
    while True: 
        clkState = GPIO.input(CLK) 
        dtState = GPIO.input(DT) 
        swState = GPIO.input(SW) 
         
        if clkState  
            if dtState  
                counter += 1 
            else: 
                counter -= 1 
            print(f"Counter: {counter}") 
 
        if swState == GPIO.LOW: 
            print("Button pressed") 
            time.sleep(0.3) 
 
        clkLastState = clkState 
        time.sleep(0.001) 
except KeyboardInterrupt: 
    GPIO.cleanup() 
    print("\nTest finished") 
