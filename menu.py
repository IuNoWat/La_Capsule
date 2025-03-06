#!/usr/bin/python
#coding: utf-8

import time

import pygame
from pygame.locals import *

from pilots import encoder

pygame.init()
pygame.font.init()

class Button() :
    def __init__(self,name,the_thing,args) :
        self.name=name
        self.the_thing=the_thing
        self.args=args
    def do_the_thing(self) :
        self.the_thing(self.args)

class Menu() :
    def __init__(self,pos,font_size=20,font_color="Black",border=2) :
        #vars
        self.pos=pos
        self.font=pygame.font.SysFont("Arial",font_size)
        self.font_color=pygame.Color(font_color)
        self.highlight_color=pygame.Color("White")
        self.border=border

        #working
        self.buttons=[]
        self.cursor=0
        self.rect=False
        self.button_size=self.font.size("Menu")

    def add_button(self,button) :
        self.buttons.append(button)

    def gauche(self,meh) :
        self.cursor+=1
        self.cursor=self.cursor%len(self.buttons)

    def droite(self,meh) :
        self.cursor-=1
        self.cursor=self.cursor%len(self.buttons)

    def click(self,meh) :
        print(self.cursor)
        self.buttons[self.cursor].do_the_thing()

    def update_btn_size(self) :
        longer=""
        for i,btn in enumerate(self.buttons) :
            if len(btn.name)>len(longer) :
                longer=btn.name
        self.button_size=self.font.size(longer)

    def render_menu(self) :
        self.update_btn_size()
        rect_buttons=[]
        rect_buttons.append(self.font.render("Menu",1,self.font_color).convert_alpha())        
        for i,btn in enumerate(self.buttons) :
            if i==self.cursor :
                rect_buttons.append(self.font.render(btn.name,1,self.font_color,self.highlight_color).convert_alpha())
            else :
                rect_buttons.append(self.font.render(btn.name,1,self.font_color).convert_alpha())
        return rect_buttons

    def render_menu_border(self) :
        self.update_btn_size()
        rect_buttons=[]
        rect_buttons.append(self.font.render("Menu",1,self.font_color).convert_alpha())        
        for i,btn in enumerate(self.buttons) :
            if i==self.cursor :
                to_add=pygame.Surface((self.button_size[0]+self.border*2,self.button_size[1]+self.border*2))
                to_add.fill(self.highlight_color)
                txt_rect=self.font.render(btn.name,1,self.font_color).convert_alpha()
                to_add.blit(txt_rect,(self.border,self.border))
                rect_buttons.append(to_add)
                #rect_buttons.append(self.font.render(btn.name,1,self.font_color,self.highlight_color).convert_alpha())
            else :
                to_add=pygame.Surface((self.button_size[0]+self.border*2,self.button_size[1]+self.border*2),pygame.SRCALPHA)
                to_add.fill(pygame.Color(0,0,0,0))
                pygame.draw.rect(to_add,self.highlight_color,(0,0,self.button_size[0]+self.border*2,self.button_size[1]+self.border*2),width=self.border)
                txt_rect=self.font.render(btn.name,1,self.font_color).convert_alpha()
                to_add.blit(txt_rect,(self.border,self.border))
                rect_buttons.append(to_add)
                #rect_buttons.append(self.font.render(btn.name,1,self.font_color).convert_alpha())
        return rect_buttons
    def show(self,Screen) :
        to_blit=self.render_menu_border()
        for i,rect in enumerate(to_blit) :
            Screen.blit(rect,(self.pos[0],rect.get_height()*i))
        return Screen

menu=Menu((20,20))
menu.add_button(
    Button("Bouton 1 - BONJOURANH",print,["un","1"])
)
menu.add_button(
    Button("Bouton 2",print,["deux","2"])
)
menu.add_button(
    Button("Bouton 3",print,["trois","3"])
)       

encoder.GAUCHE=menu.gauche
encoder.DROITE=menu.droite
encoder.BOUTTON=menu.click

class 


screen = pygame.display.set_mode((768, 1366))
clock = pygame.time.Clock()
running = True

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("purple")

    screen=menu.show(screen)

    # RENDER YOUR GAME HERE

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()