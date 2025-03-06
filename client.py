#!/usr/bin/python
#coding: utf-8

import time

import RPi.GPIO as GPIO
import krpc

import pygame
from pygame.locals import *
pygame.init()
pygame.font.init()

from pilots import encoder

#CONSTANTS
HOME_WIFI_IP="192.168.1.159"
RPC_PORT=50008
FPS=30
SCREEN_SIZE=(1080, 1920)
BACKGROUND_PATH="assets/bg16-9.png"

#COLORS
WHITE=pygame.Color("White")
BLACK=pygame.Color("Black")

class Main() :
    def __init__(self) :
        #vars
        self.fps=FPS
        self.size=SCREEN_SIZE

        #working
        self.on=False
        self.clock=pygame.time.Clock()
        self.screen=pygame.display.set_mode(self.size,pygame.FULLSCREEN)
        self.bg=pygame.image.load(BACKGROUND_PATH).convert_alpha()
        self.bg=pygame.transform.scale(self.bg,SCREEN_SIZE)
        self.fps_font=font=pygame.font.SysFont("Arial", 30)

    def launch(self) :
        self.on=True
        self.screen.blit(self.bg,(0,0))
        while self.on :
            #Start of loop
            #self.screen.blit(self.bg,(0,0))

            #Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            #Add header
            self.update_header()

            #End of loop
            pygame.display.flip()
            self.clock.tick(self.fps)
        
        pygame.quit()
    
    def update_header(self) :
        fps=str(round(self.clock.get_fps(),1))
        txt=f"SCREEN_FPS : {fps}"
        to_blit=self.fps_font.render(txt,1,WHITE,BLACK)
        self.screen.blit(to_blit,(0,0))


tele=Main()

tele.launch()