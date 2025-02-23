#!/usr/bin/python
#coding: utf-8

#-----Dependency-----
import time
import math
import sys
import socket as s
import argparse
import krpc
import traceback
from threading import Thread

#import busio
#import digitalio
#import board
#import adafruit_mcp3xxx.mcp3008 as MCP
#from adafruit_mcp3xxx.analog_in import AnalogIn

import pygame
from pygame.locals import *

from PIL import Image

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
pygame.init()
pygame.font.init()

#TODOLIST
#Check for TODOes dans le code
#Ranger le code

#-----SETTINGS-----
fps=30
screen_size=(540,960)
HOST={
    "priam":'169.254.171.116',
    "capsule":"169.254.53.212"
}
RPC_PORT=50008
default_font_size=17
debug=True

#-----Action Group Settings
action_groups={
    "decouplage_port_ammarage":1,
    "detach_arret_urgence":2,
    "detach_bouclier_thermique":3,
    "parachute_principaux":4,
    "parachute_freinage":5,
    "ouverture_coiffe":6
}

#-----GPIO Settings-----

port_gpio={
    "sas":21,
    "rcs":15,
    "affichage":20,
    "trains_datterissage":19,
    "stage":16,
    "gaz":0,
    "time_multi":1,
    "arm_arret_urgence":14,
    "arm_moteur":26,
    "arret_urgence":18,
    "detach_arret_urgence":23,
    "detach_bouclier_thermique":24,
    "parachute_freinage":17,
    "parachute_principaux":22,
    "decouplage_port_ammarage":25,
    "ouverture_coiffe":12
}
#port_gpio={
#    "sas":40,
#    "rcs":10,
#    "affichage":38,
#    "trains_datterissage":35,
#    "stage":36,
#    "gaz":0,
#    "time_multi":1,
#    "arm_arret_urgence":8,
#    "arm_moteur":37,
#    "arret_urgence":12,
#    "detach_arret_urgence":16,
#    "detach_bouclier_thermique":18,
#    "parachute_freinage":24,
#    "parachute_principaux":26,
#    "decouplage_port_ammarage":22,
#    "ouverture_coiffe":32
#}


#-----MCP Method-----

def init_MCP() :
    spi=busio.SPI(clock=board.SCK,MISO=board.MISO,MOSI=board.MOSI)
    cs=digitalio.DigitalInOut(board.D5)
    mcp=MCP.MCP3008(spi,cs)
    return mcp
#channel=AnalogIn(mcp,MCP.P0)


#-----Value Handling-----

def format_distance(value,num_of_pack,decimals=None,type=None) :
    num_of_pack=num_of_pack*3
    rounded_value=round(value,decimals)
    txt=str(rounded_value).zfill(num_of_pack)
    if num_of_pack>=12 :
        txt=f"{txt[:9]}.{txt[9:]}"
    if num_of_pack>=9 :
        txt=f"{txt[:6]}.{txt[6:]}"
    if num_of_pack>=6 :
        txt=f"{txt[:3]}.{txt[3:]}"
    return txt

def format_time(value) :
    minutes=int(value/60)
    mdr=value-minutes*60
    secondes=round(mdr,None)
    txt=f"{str(minutes).zfill(2)}:{str(secondes).zfill(2)}"
    return txt

class Value() :
    def __init__(self,way,name,value,GPIO,rate,action_group=None) :
        self.way=way
        self.name=name
        self.value=value
        self.GPIO=GPIO
        self.rate=rate
        self.action_group=action_group
    def refresh(self,tic) :
        if tic%self.rate==0 :
            pass

class Value_sas(Value) :
    def __init__(self,way,name,value,GPIO,rate,action_group=None) :
        Value.__init__(self,way,name,value,GPIO,rate,action_group)
    def refresh(self,tic) :
        if tic%self.rate==0 :
            new_value=GPIO.input(self.GPIO)
            if new_value!=self.value :
                control.sas=bool(new_value)
                self.value=new_value

class Value_rcs(Value) :
    def __init__(self,way,name,value,GPIO,rate,action_group=None) :
        Value.__init__(self,way,name,value,GPIO,rate,action_group)
    def refresh(self,tic) :
        if tic%self.rate==0 :
            new_value=GPIO.input(self.GPIO)
            if new_value!=self.value :
                control.rcs=bool(new_value)
                self.value=new_value

class Value_trains_datterissage(Value) : #TODO : Fonctionnent en théorie, mais n'a pas pu être essayés en pratique
    def __init__(self,way,name,value,GPIO,rate,action_group=None) :
        Value.__init__(self,way,name,value,GPIO,rate,action_group)
    def refresh(self,tic) :
        if tic%self.rate==0 :
            new_value=GPIO.input(self.GPIO)
            if new_value!=self.value :
                control.legs=bool(new_value)
                self.value=new_value

class Value_gaz(Value) : #TODO : Fonctionnent en théorie, mais n'a pas pu être essayés en pratique
    def __init__(self,way,name,value,GPIO,rate,action_group=None) :
        Value.__init__(self,way,name,value,GPIO,rate,action_group)
        self.old_value=0
        #self.mcp=init_MCP()
        #self.channel=AnalogIn(self.mcp,MCP.P0)
    def mcp_handler(value) :
        return (value/65472)*100
    def refresh(self,tic) :
        if values["arm_moteur"].value==True :
            control.throttle=0
        else :
            if tic%self.rate==0 :
                #new_value=self.channel.value
                new_value=0
                self.value=new_value
                #if abs(new_value-self.old_value)<300 and new_value>=0 :
                #    value=1024-new_value
                #    value=(value/1024)*1.1
                #    control.throttle=value
                #    self.old_value=new_value
            #    moy.append(new_value)
            #if len(moy)>9 :
            #    moy.pop(0)
            #total=0
            #for entry in moy :
            #    total+=entry
            #moyenne=total/len(moy)
            #value=1024-moyenne
            #value=(value/1024)*1.1
            #value=1024-new_value
            #value=(value/1024)*1.1
            #control.throttle=value

class Value_generic_switch(Value) :
    def __init__(self,way,name,value,GPIO,rate,action_group=None) :
        Value.__init__(self,way,name,value,GPIO,rate,action_group)
    def refresh(self,tic) :
        if tic%self.rate==0 :
            new_value=GPIO.input(self.GPIO)
            self.value=bool(new_value)

class Value_sea_alt(Value) :
    def __init__(self,way,name,value,GPIO,rate,action_group=None) :
        Value.__init__(self,way,name,value,GPIO,rate,action_group)
    def refresh(self,tic) :
        if tic%self.rate==0 :
            new_value=flight.mean_altitude
            self.value=format_distance(new_value,3)

class Value_ground_alt(Value) :
    def __init__(self,way,name,value,GPIO,rate,action_group=None) :
        Value.__init__(self,way,name,value,GPIO,rate,action_group)
    def refresh(self,tic) :
        if tic%self.rate==0 :
            new_value=flight.surface_altitude-6
            self.value=format_distance(new_value,3)

def get_magnitude(vector) :
    return math.sqrt(sum(pow(element,2) for element in vector))

class Value_speed(Value) :
    def __init__(self,way,name,value,GPIO,rate,action_group=None) :
        Value.__init__(self,way,name,value,GPIO,rate,action_group)
    def refresh(self,tic) :
        if tic%self.rate==0 :
            #new_value=orbit.speed
            new_value=get_magnitude(vessel.velocity(vessel.orbit.body.reference_frame))
            self.value=format_distance(new_value,2)

class Value_apoapsis(Value) :
    def __init__(self,way,name,value,GPIO,rate,action_group=None) :
        Value.__init__(self,way,name,value,GPIO,rate,action_group)
    def refresh(self,tic) :
        if tic%self.rate==0 :
            new_value=orbit.apoapsis-600000
            self.value=format_distance(new_value,3)

class Value_periapsis(Value) :
    def __init__(self,way,name,value,GPIO,rate,action_group=None) :
        Value.__init__(self,way,name,value,GPIO,rate,action_group)
    def refresh(self,tic) :
        if tic%self.rate==0 :
            new_value=orbit.periapsis-600000
            self.value=format_distance(new_value,3)

class Value_apoapsis_time(Value) :
    def __init__(self,way,name,value,GPIO,rate,action_group=None) :
        Value.__init__(self,way,name,value,GPIO,rate,action_group)
    def refresh(self,tic) :
        if tic%self.rate==0 :
            new_value=orbit.time_to_apoapsis
            self.value=format_time(new_value)

class Value_periapsis_time(Value) :
    def __init__(self,way,name,value,GPIO,rate,action_group=None) :
        Value.__init__(self,way,name,value,GPIO,rate,action_group)
    def refresh(self,tic) :
        if tic%self.rate==0 :
            new_value=orbit.time_to_periapsis
            self.value=format_time(new_value)

class Value_g_force(Value) :
    def __init__(self,way,name,value,GPIO,rate,action_group=None) :
        Value.__init__(self,way,name,value,GPIO,rate,action_group)
    def refresh(self,tic) :
        if tic%self.rate==0 :
            new_value=flight.g_force
            self.value=str(round(new_value,3)).ljust(5,'0')

class Value_temperature(Value) :
    def __init__(self,way,name,value,GPIO,rate,action_group=None) :
        Value.__init__(self,way,name,value,GPIO,rate,action_group)
    def refresh(self,tic) :
        if tic%self.rate==0 :
            new_value=flight.static_air_temperature
            self.value=str(round(new_value,2)).zfill(6)

class Value_fuel1(Value) :
    def __init__(self,way,name,value,GPIO,rate,action_group=None) :
        Value.__init__(self,way,name,value,GPIO,rate,action_group)
    def refresh(self,tic) :
        if tic%self.rate==0 :
            None

#-----CallBack Declaration-----

class Callback_handler() :
    def __init__(self,waiting_time) :
        self.free=True
        self.time=waiting_time
    def block(self) :
        self.free=False
    def timer(self) :
        time.sleep(self.time)
        self.free=True

road=Callback_handler(1)

def define_callback(gpio,method) :
    GPIO.add_event_detect(gpio,GPIO.RISING,method)

def callback_stage(meh) :
    print(meh)
    if values["arm_moteur"].value and road.free :
        road.block()
        control.activate_next_stage()
        road.timer()

def callback_affichage(meh) :
    print(meh)
    if road.free :
        road.block()
        if camera.mode==con.space_center.CameraMode.automatic :
            camera.mode=con.space_center.CameraMode.map
        else :
            camera.mode=con.space_center.CameraMode.automatic
        road.timer()

def callback_arret(meh) :
    print(meh)
    if values["arm_arret_urgence"].value and road.free :
        road.block()
        control.abort=True
        road.timer()

def callback_detach_arret_urgence(meh) :
    print(meh)
    if road.free :
        road.block()
        control.set_action_group(action_groups["detach_arret_urgence"],True)
        road.timer()

def callback_parachute_freinage(meh) :
    print(meh)
    if road.free :
        road.block()
        control.set_action_group(action_groups["parachute_freinage"],True)
        road.timer()

def callback_parachute_principaux(meh) :
    print(meh)
    if road.free :
        road.block()
        control.set_action_group(action_groups["parachute_principaux"],True)
        road.timer()

def callback_decouplage_port_ammarage(meh) :
    print(meh)
    if road.free :
        road.block()
        control.set_action_group(action_groups["decouplage_port_ammarage"],True)
        road.timer()

def callback_ouverture_coiffe(meh) :
    print(meh)
    if road.free :
        road.block()
        control.set_action_group(action_groups["ouverture_coiffe"],True)
        road.timer()

def callback_detach_bouclier_thermique(meh) :
    print(meh)
    if road.free :
        road.block()
        control.set_action_group(action_groups["detach_bouclier_thermique"],True)
        road.timer()

values ={
    "sas":Value_sas(way="input",name="sas",value=False,GPIO=port_gpio["sas"],rate=10), #done
    "rcs":Value_rcs(way="input",name="rcs",value=False,GPIO=port_gpio["rcs"],rate=10), #done
    "trains_datterissage":Value_trains_datterissage(way="input",name="Trains d'Atterissage",value=False,GPIO=port_gpio["trains_datterissage"],rate=10), #TODO : Fonctionnent en théorie, mais n'a pas pu être essayés en pratique
    "gaz":Value_gaz(way="input",name="Gaz",value=False,GPIO=port_gpio["gaz"],rate=1), #TODO : Fonctionnent en théorie, mais n'a pas pu être essayés en pratique
    #"time_multi":Value(way="input",name="Multiplicateur temporel",value=False,GPIO=port_gpio["time_multi"],rate=1), #TODO : Il faut tester l'urilisation du MCP3008
    "arm_arret_urgence":Value_generic_switch(way="input",name="Armement de l'arrêt d'urgence",value=False,GPIO=port_gpio["arm_arret_urgence"],rate=10), #done
    "arm_moteur":Value_generic_switch(way="input",name="Armement des Moteurs",value=False,GPIO=port_gpio["arm_moteur"],rate=10), #done
    "ground_alt":Value_sea_alt(way="output",name="Altitude au niveau de la mer",value=0,GPIO=None,rate=2),
    "sea_alt":Value_ground_alt(way="output",name="Altitude au sol",value=0,GPIO=None,rate=2),
    "speed":Value_speed(way="output",name="Vitesse",value=0,GPIO=None,rate=1),
    "apoapsis":Value_apoapsis(way="output",name="Apoapsis",value=0,GPIO=None,rate=5),
    "periapsis":Value_periapsis(way="output",name="Periapsis",value=0,GPIO=None,rate=5),
    "time_to_apoapsis":Value_apoapsis_time(way="output",name="Temps jusqu'à l'apoapse",value=1,GPIO=None,rate=5),
    "time_to_periapsis":Value_periapsis_time(way="output",name="Temps jusqu'au periapse",value=1,GPIO=None,rate=5),
    "g_force":Value_g_force(way="output",name="G subis",value=0,GPIO=None,rate=10),
    "temperature":Value_temperature(way="output",name="Temperature exterieure",value=0,GPIO=None,rate=10),
    "fuel1":Value_fuel1(way="output",name="fuel1",value="",GPIO=None,rate=10)
}

def gpio_setup() :
    GPIO.setup(port_gpio["sas"],GPIO.IN,GPIO.PUD_DOWN)
    GPIO.setup(port_gpio["rcs"],GPIO.IN,GPIO.PUD_DOWN)
    GPIO.setup(port_gpio["stage"],GPIO.IN,GPIO.PUD_DOWN)
    GPIO.setup(port_gpio["trains_datterissage"],GPIO.IN,GPIO.PUD_DOWN)
    GPIO.setup(port_gpio["affichage"],GPIO.IN,GPIO.PUD_DOWN)
    GPIO.setup(port_gpio["arm_arret_urgence"],GPIO.IN,GPIO.PUD_DOWN)
    GPIO.setup(port_gpio["arm_moteur"],GPIO.IN,GPIO.PUD_DOWN)
    GPIO.setup(port_gpio["arret_urgence"],GPIO.IN,GPIO.PUD_DOWN)
    GPIO.setup(port_gpio["detach_arret_urgence"],GPIO.IN,GPIO.PUD_DOWN)
    GPIO.setup(port_gpio["detach_bouclier_thermique"],GPIO.IN,GPIO.PUD_DOWN)
    GPIO.setup(port_gpio["parachute_freinage"],GPIO.IN,GPIO.PUD_DOWN)
    GPIO.setup(port_gpio["parachute_principaux"],GPIO.IN,GPIO.PUD_DOWN)
    GPIO.setup(port_gpio["decouplage_port_ammarage"],GPIO.IN,GPIO.PUD_DOWN)
    GPIO.setup(port_gpio["ouverture_coiffe"],GPIO.IN,GPIO.PUD_DOWN)

gpio_setup()

define_callback(port_gpio["stage"],callback_stage)
define_callback(port_gpio["affichage"],callback_affichage)
define_callback(port_gpio["arret_urgence"],callback_arret)
define_callback(port_gpio["detach_arret_urgence"],callback_detach_arret_urgence)
define_callback(port_gpio["parachute_freinage"],callback_parachute_freinage)
define_callback(port_gpio["parachute_principaux"],callback_parachute_principaux)
define_callback(port_gpio["decouplage_port_ammarage"],callback_decouplage_port_ammarage)
define_callback(port_gpio["ouverture_coiffe"],callback_ouverture_coiffe)
define_callback(port_gpio["detach_bouclier_thermique"],callback_detach_bouclier_thermique)

#-----Connexion Handler-----

def connect(debug=True) : #Establish connexion with master
    try :
        if debug :
            con=krpc.connect()
            return con
        else :
            con=krpc.connect(
                name="Client",
                address=HOST["capsule"],
                rpc_port=RPC_PORT
            )
            print("Connected to KSP successfuly")
            return con
    except Exception as e :
        error=traceback.format_exc()
        print("Error while trying to connect to KSP")
        print(error)

tic=0

def update_values() :
    global tic
    if tic>fps :
        tic=0
    for key in values :
        try :
            values[key].refresh(tic)
        except Exception as e :
            error=traceback.format_exc()
            print("Error while trying to refresh  a key")
            print(error)
            pygame.quit()
            quit()
    tic+=1


#-----Graphics Handler-----

class Layout() : #Class describing the layout of the screen via internal Blocks
    def __init__(self,number,name,size,blocks=False) :
        self.number=number
        self.name=name
        self.blocks=blocks
    def draw(self,surface) :
        if self.blocks==False :
            print("Error ! Can't draw() without at least 1 Block in Layout")
        else :
            for block in self.blocks :
                value=values[block.type].value
                block.create(value)
                surface.blit(block.rect,block.pos)

class Static_Text_Block() :
    def __init__(self,txt,pos,font_color="White",font_type="Arial",font_size=default_font_size) :
        self.txt=txt
        self.type="sas"
        self.pos=pos
        self.font=pygame.font.SysFont(font_type,font_size)
        self.color=font_color
        self.rect=False
    def create(self,value) :
        self.rect=self.font.render(self.txt,1,pygame.Color(self.color)).convert_alpha()

class Number_Block() : #Block used to show a number value. Meant to be used by a Layout class
    def __init__(self,type,pos,font_color="Cyan",font_type="Arial",font_size=default_font_size) :
        self.type=type
        self.pos=pos
        if font_type=="Arial" :
            self.font=pygame.font.SysFont(font_type,font_size)
        else :
            self.font=pygame.font.Font(font_type,int(font_size/2))
        self.color=font_color
        self.rect=False
    def create(self,value) :
        txt=self.name+str(value)
        self.rect=self.font.render(txt,1,pygame.Color(self.color),pygame.Color(27,41,68)).convert_alpha()

class Gazs_Block(Number_Block) :
    def __init__(self,name,type,pos,font_color="White",font_type="Arial",font_size=default_font_size) :
        Number_Block.__init__(self,name,type,pos,font_color,font_type,font_size)
        self.surface=pygame.Surface((30,200))
        self.surface.fill(pygame.Color("Green"))
    def create(self,value) :
        txt=self.name+str(value)
        self.rect=self.font.render(txt,1,pygame.Color(self.color),pygame.Color(27,41,68)).convert_alpha()
        #pygame.transform.scale(self.surface,(30,self.value*200),self.rect)

#-----Initialisation Methods-----

def create_layouts() :
    main_blocks=create_main_layout()
    debug_blocks=create_debug_layout()
    layouts=[
    Layout(0,"Main",screen_size,main_blocks),
    Layout(1,"Debug",screen_size,debug_blocks)
    ]
    return layouts

main_layout_position ={
    "speed":[300,310],
    "sea_alt":[155,710],
    "ground_alt":[615,710],
    "apoapsis":[124,1009],
    "time_to_apoapsis":[445,1005],
    "periapsis":[125,1214],
    "time_to_periapsis":[450,1214],
    "g_force":[720,1000],
    "temperature":[675,1200],
    "fuel1":[200,1500]
}

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

if debug :
    for key in main_layout_position :
        for i in range(0,len(main_layout_position[key])) :
            main_layout_position[key][i]=main_layout_position[key][i]/2

def create_main_layout() :
    blocks=[]
    blocks.append(Number_Block("sea_alt",main_layout_position["sea_alt"],font_type="digit.ttf",font_size=60))
    blocks.append(Number_Block("ground_alt",main_layout_position["ground_alt"],font_type="digit.ttf",font_size=60))
    blocks.append(Number_Block("speed",main_layout_position["speed"],font_type="digit.ttf",font_size=120))
    blocks.append(Number_Block("apoapsis",main_layout_position["apoapsis"],font_type="digit.ttf",font_size=45))
    blocks.append(Number_Block("time_to_apoapsis",main_layout_position["time_to_apoapsis"],font_type="digit.ttf",font_size=50))
    blocks.append(Number_Block("periapsis",main_layout_position["periapsis"],font_type="digit.ttf",font_size=45))
    blocks.append(Number_Block("time_to_periapsis",main_layout_position["time_to_periapsis"],font_type="digit.ttf",font_size=50))
    blocks.append(Number_Block("g_force",main_layout_position["g_force"],font_type="digit.ttf",font_size=100))
    blocks.append(Number_Block("temperature",main_layout_position["temperature"],font_type="digit.ttf",font_size=70))
    return blocks

def create_debug_layout() :
    blocks=[]
    i=0
    blocks.append(Static_Text_Block("----------OUTPUT VALUES----------",(5,default_font_size+i*default_font_size*2)))
    i+=1
    for key in values :
        if values[key].way=="output" :
            blocks.append(Number_Block(values[key].name,key,(5,default_font_size+i*default_font_size*2)))
            i+=1
    blocks.append(Static_Text_Block("----------INPUT VALUES----------",(5,default_font_size+i*default_font_size*2)))
    i+=1
    for key in values :
        if values[key].way=="input" :
            blocks.append(Number_Block(values[key].name,key,(5,default_font_size+i*default_font_size*2)))
            i+=1
    return blocks



#-----Debug Methods-----

def create_tester() :
    possible_inputs=[]
    for key in values :
        if values[key].way=='input' :
            possible_inputs.append(key)
    return possible_inputs

def test(input) :
    if GPIO.values[values[input].GPIO]==False :
        GPIO.values[values[input].GPIO]=True
    else :
        GPIO.values[values[input].GPIO]=False
    print(f"The value of {input} is now {GPIO.values[values[input].GPIO]}")

#-----MainLoop Methods-----
def create_header(clock,layout,value=None,my_input=None) : #Methode affichant les fps réel en haut à gauche de la fenêtre pygame
    fps=str(round(clock.get_fps(),1))
    txt=f"FPS : {fps} | Layout : {layout.number} - {layout.name} | Selected input : {my_input} | Selected Value : {value}"
    font=pygame.font.SysFont("Arial", 18)
    to_blit=font.render(txt,1,pygame.Color("White"),pygame.Color("Black"))
    return to_blit

#-----Communication system creation-----
con=connect()
vessel=con.space_center.active_vessel
camera=con.space_center.camera
control=vessel.control
flight=vessel.flight()
orbit=vessel.orbit
resources=vessel.resources

#new_value=resources.all
#for entry in new_value :
#    print(entry.part.name)

Clock = pygame.time.Clock()

class Screen_handler(Thread) :
    def __init__(self,screen_size,fps,flags=None,debug=False) :
        #-----Initialisation of the Screen Thread-----#
        Thread.__init__(self)
        #-----Creation of Screen-----#
        if flags==None :
            self.Screen=pygame.display.set_mode(screen_size)
        else :
            self.Screen=pygame.display.set_mode(screen_size,flags)
        self.Clock=pygame.time.Clock()
        #-----Implementation of Background-----#
        if debug :
            self.bg=pygame.image.load("bg.png").convert_alpha()
        else :
            self.bg=pygame.image.load("/home/pi/Desktop/pi_connect/bg.png").convert_alpha()
        self.bg=pygame.transform.scale(self.bg,screen_size)
        self.Screen.blit(self.bg,(0,0))
        pygame.display.flip()
        #-----Layout Creation-----#
        self.current_layout=0
        self.layouts=create_layouts()
    def create_header(self,clock,layout,big_clock,value=None,my_input=None) :
        fps=str(round(clock.get_fps(),1))
        big_clock_fps=str(round(big_clock.get_fps(),1))
        txt=f"FPS : {fps} | Big Clock FPS : {big_clock_fps} | Layout : {layout.number} - {layout.name} | Selected input : {my_input} | Selected Value : {value}"
        font=pygame.font.SysFont("Arial", 18)
        to_blit=font.render(txt,1,pygame.Color("White"),pygame.Color("Black"))
        return to_blit
    def run(self) :
        while True :
            #-----Check for event and apply proper action-----
            for event in pygame.event.get(): #Check for events and apply proper action
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == KEYDOWN and event.key == K_ESCAPE :
                    pygame.quit()
                    quit()
            self.layouts[self.current_layout].draw(self.Screen)
            #-----Add Debug header-----
            header=self.create_header(self.Clock,self.layouts[self.current_layout],big_clock=Clock)
            self.Screen.blit(header,(0,0))
            #-----Show the Screen-----
            pygame.display.update()
            self.Clock.tick(fps)

def main() :
    #-----Initialisation-----
    #flags=pygame.FULLSCREEN
    #pygame.event.set_allowed([QUIT,KEYDOWN,KEYUP])
    #Screen=pygame.display.set_mode(screen_size)
    #if debug :
    #    bg=pygame.image.load("bg.png").convert()
    #else :
    #    bg=pygame.image.load("/home/pi/Desktop/pi_connect/bg.png").convert_alpha()
    #bg=pygame.transform.scale(bg,screen_size)
    #Screen.blit(bg,(0,0))
    #pygame.display.flip()
    #-----First Update-----
    update_values()
    #-----Layout system creation-----
    #current_layout=0
    #layouts=create_layouts()
    #-----Debug-----
    #possible_inputs=create_tester()
    #test_cursor=0
    #-----MainLoop-----
    Screen=Screen_handler(screen_size,fps,debug=True)
    Screen.start()
    while True:
        #-----Update the values-----
        update_values()
        Clock.tick(10)

if __name__=="__main__":
    main()
