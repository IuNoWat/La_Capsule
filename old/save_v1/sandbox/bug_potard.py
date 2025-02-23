#!/usr/local/bin/python
# coding: latin-1

import RPi.GPIO as GPIO
import time
import pygame
from pygame.locals import *
import os

#-----SETTINGS-----
os.environ['PYGAME_BLEND_ALPHA_SDL2']="1"
fps=30
screen_size=(1080,1920)
pygame_on=False
pygame.init()
pygame.font.init()
#----GPIO Setup----#
GPIO.setmode(GPIO.BCM)
#gpio=[11,13,15,33]
#GPIO.setup(gpio[0],GPIO.OUT) #GPIO du pin 4 du MCP3008
#GPIO.setup(gpio[1],GPIO.IN) #GPIO du pin 5 du MCP3008
#GPIO.setup(gpio[2],GPIO.OUT) #GPIO du pin 6 du MCP3008
#GPIO.setup(gpio[3],GPIO.OUT) #GPIO du pin 7 du MCP3008

def get_potentiometer_value() :
    GPIO.output(gpio[3], True)
    GPIO.output(gpio[0], False)  # start clock low
    GPIO.output(gpio[3], False)	 # bring CS low
    commandout = 0
    commandout |= 0x18  # start bit + single-ended bit
    commandout <<= 3	# we only need to send 5 bits here
    for i in range(5):
    	if (commandout & 0x80):
    		GPIO.output(gpio[2], True)
    	else:
    		GPIO.output(gpio[2], False)
    	commandout <<= 1
    	GPIO.output(gpio[0], True)
    	GPIO.output(gpio[0], False)
    adcout = 0
    # read in one empty bit, one null bit and 10 ADC bits
    for i in range(12):
    	GPIO.output(gpio[0], True)
    	GPIO.output(gpio[0], False)
    	adcout <<= 1
    	if (GPIO.input(gpio[1])):
    		adcout |= 0x1
    GPIO.output(gpio[3], True)
    adcout /= 2	   # first bit is 'null' so drop it
    return adcout

def new_mcp() :
    import busio
    import digitalio
    import board
    import adafruit_mcp3xxx.mcp3008 as MCP
    from adafruit_mcp3xxx.analog_in import AnalogIn
    spi=busio.SPI(clock=board.SCK,MISO=board.MISO,MOSI=board.MOSI)
    cs=digitalio.DigitalInOut(board.D5)
    mcp=MCP.MCP3008(spi,cs)
    channel=AnalogIn(mcp,MCP.P0)
    return channel

moy=[]

def moy_handler(value,limit) :
    moy.append(value)
    if len(moy)>limit :
        moy.pop(0)
    to_return=0
    for entry in moy :
        to_return+=entry
    to_return=to_return/len(moy)
    return to_return

#-----MainLoop Methods-----
def create_header(clock,value) : #Methode affichant les fps réel en haut à gauche de la fenêtre pygame
    print(value)
    fps=str(round(clock.get_fps(),1))
    txt=f"FPS : {fps} | Value : {value}"
    font=pygame.font.SysFont("Arial", 18)
    to_blit=font.render(txt,1,pygame.Color("White"),pygame.Color("Black"))
    return to_blit

def main() :
    Screen=pygame.display.set_mode(screen_size)
    Clock = pygame.time.Clock()
    while True:
        #-----Check for event and apply proper action-----
        for event in pygame.event.get(): #Check for events and apply proper action
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == KEYDOWN and event.key == K_ESCAPE :
                pygame.quit()
                quit()
        #-----Update the screen-----
        Screen.fill((0,0,0))
        #Screen.blit(bg,(0,0))
        #-----Add Debug header-----
        #header=create_header(Clock,get_potentiometer_value())
        header=create_header(Clock,chan.value)
        Screen.blit(header,(0,0))
        #-----Show the Screen-----
        pygame.display.flip()
        Clock.tick(fps)

if __name__=="__main__" :
    chan=new_mcp()
    if pygame_on :
        main()
    else :
        on=True
        while on :
            #print(get_potentiometer_value())
            print(chan.value)
            time.sleep(0.1)
