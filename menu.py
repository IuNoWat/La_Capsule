#!/usr/bin/python
#coding: utf-8

# Menu is used to create a specific menu controlled by a rotary encoder
# It allow to add selectable buttons in the menu, and to connect any method to it

import time

import pygame
from pygame.locals import *

from pilots import encoder

pygame.init()
pygame.font.init()

COLOR_BG=pygame.Color(22,13,34,255)
COLOR_HL=pygame.Color(255,255,255,255)
NUM_FONT_PATH="assets/DS-DIGI.TTF"
TXT_FONT_PATH="assets/Rubik-VariableFont_wght.ttf"

# To add a button, you need to define its name, the method it need to call, and eventually the necessary arguments

class Button() :
    def __init__(self,name,the_thing,args) :
        self.name=name
        self.the_thing=the_thing
        self.args=args
    def do_the_thing(self) :
        self.the_thing(self.args)

class Menu() :
    def __init__(self,pos,font_size=27,color_bg=COLOR_BG,color_hl=COLOR_HL,font_path=TXT_FONT_PATH) :
        #vars
        self.pos=pos
        self.font=pygame.font.Font(font_path,font_size)
        self.font.bold=True
        self.color_bg=color_bg
        self.color_hl=color_hl

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
        self.buttons[self.cursor].do_the_thing()

    def update_btn_size(self) :
        longer=""
        for i,btn in enumerate(self.buttons) :
            if len(btn.name)>len(longer) :
                longer=btn.name
        self.button_size=self.font.size(longer)

    def render_menu(self) :
        #self.update_btn_size() #To use if you want the menu to adapt to the longest button text
        rect_buttons=[]
        #rect_buttons.append(self.font.render("Menu",1,self.color_hl).convert_alpha())        
        for i,btn in enumerate(self.buttons) :
            if i==self.cursor :
                to_add=pygame.Surface((320,self.button_size[1]))
                to_add.fill(self.color_hl)
                txt_rect=self.font.render(btn.name,1,self.color_bg).convert_alpha()
                to_add.blit(txt_rect,(10,0))
                rect_buttons.append(to_add)
                #rect_buttons.append(self.font.render(btn.name,1,self.font_color,self.highlight_color).convert_alpha())
            else :
                to_add=pygame.Surface((320,self.button_size[1]))
                to_add.fill(self.color_bg)
                txt_rect=self.font.render(btn.name,1,self.color_hl).convert_alpha()
                to_add.blit(txt_rect,(10,0))
                rect_buttons.append(to_add)
                #rect_buttons.append(self.font.render(btn.name,1,self.font_color).convert_alpha())
        return rect_buttons

    def show(self,Screen) :
        to_blit=self.render_menu()
        for i,rect in enumerate(to_blit) :
            Screen.blit(rect,(self.pos[0],self.pos[1]+((rect.get_height()+4)*i)))
        return Screen

if __name__=="__main__" :
    
    menu=Menu((20,20))
    encoder.GAUCHE=menu.gauche
    encoder.DROITE=menu.droite
    encoder.BOUTTON=menu.click
    
    menu.add_button(
        Button("Bouton 1 - BONJOURANH",print,["un","1"])
    )
    menu.add_button(
        Button("Bouton 2",print,["deux","2"])
    )
    menu.add_button(
        Button("Bouton 3",print,["trois","3"])
    )       

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
        screen.fill(COLOR_BG)

        screen=menu.show(screen)

        # RENDER YOUR GAME HERE

        # flip() the display to put your work on screen
        pygame.display.flip()

        clock.tick(60)  # limits FPS to 60

    pygame.quit()