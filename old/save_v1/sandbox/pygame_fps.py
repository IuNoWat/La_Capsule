#!/usr/bin/python
#coding: utf-8

#-----Dependency-----
import pygame
from pygame.locals import *

pygame.init()
pygame.font.init()

#-----SETTINGS-----
fps=30
screen_size=(1080,1920)

dirty_rect=[
    pygame.Rect((300,310),(385,88)),
    pygame.Rect((155,710),(297,45)),
    pygame.Rect((615,710),(297,45)),
    pygame.Rect((124,1009),(220,34)),
    pygame.Rect((445,1005),(115,37)),
    pygame.Rect((125,1214),(220,34)),
    pygame.Rect((450,1214),(115,37)),
    pygame.Rect((720,1000),(225,74)),
    pygame.Rect((675,1200),(192,52)),
    pygame.Rect((0,0),(396,21)),
    pygame.Rect((200,1500),(30,200))
]

def create_header(clock,my_input=None) : #Methode affichant les fps réel en haut à gauche de la fenêtre pygame
    fps=str(round(clock.get_fps(),1))
    txt=f"FPS : {fps} |  Input : {my_input}"
    font=pygame.font.SysFont("Arial", 18)
    to_blit=font.render(txt,1,pygame.Color("White"),pygame.Color("Black"))
    return to_blit

def main() :
    #-----Initialisation-----
    flags=pygame.FULLSCREEN
    Screen=pygame.display.set_mode(screen_size,flags)
    Clock = pygame.time.Clock()
    #-----MainLoop-----
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
        #-----Add Debug header-----
        header=create_header(Clock)
        Screen.blit(header,(0,0))
        #-----Show the Screen-----
        pygame.display.update()
        Clock.tick(fps)

if __name__=="__main__":
    main()
