#!/usr/bin/python
#coding: utf-8

#-----DEPENDENCY-----#

import time
import math
import sys
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
pygame.init()
pygame.font.init()

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

#-----TODO-----#

#TODO : Etablir un plan précis des GPIO utilisés (ATTENTION, NOUS SOMMES PASSES EN GPIO.BCM !!)


#-----CONSTANT-----#

MAX_THROTTLE_VALUE=65472
default_font_size=17
HOST={
    "priam":'169.254.171.116',
    "capsule":"169.254.53.212"
}
RPC_PORT=50008

#----SETTINGS-----#

SCREEN_FPS=30
COMMAND_FPS=30
SCREEN_SIZE=(540,960)
DEBUG=True

#-----VARIABLES-----#

tic=0

command_clock=pygame.time.Clock()
#-----HARDWARE INITIALISATION-----#

#-----MCP Initialisation-----#
#spi=busio.SPI(clock=board.SCK,MISO=board.MISO,MOSI=board.MOSI)
#cs=digitalio.DigitalInOut(board.D5)
#mcp=MCP.MCP3008(spi,cs)
#channel=AnalogIn(mcp,MCP.P0)

#-----KSP COMMUNICATION-----#

#Connexion to KSP
try :
    if DEBUG :
        con=krpc.connect()
    else :
        con=krpc.connect(
            name="Client",
            address=HOST["capsule"],
            rpc_port=RPC_PORT
        )
        print("Connected to KSP successfuly")
except Exception as e :
    error=traceback.format_exc()
    print("Error while trying to connect to KSP")
    print(error)

vessel=con.space_center.active_vessel
camera=con.space_center.camera
control=vessel.control
flight=vessel.flight()
orbit=vessel.orbit
resources=vessel.resources

#-----KSP Action Groups-----#

action_groups={
    "decouplage_port_ammarage":1,
    "detach_arret_urgence":2,
    "detach_bouclier_thermique":3,
    "parachute_principaux":4,
    "parachute_freinage":5,
    "ouverture_coiffe":6
}

#-----GPIO Settings-----#

port_gpio={
    "sas":21,
    "rcs":15,
    "affichage":20,
    "legs":19,
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



#-----VALUE SYSTEM-----#

class Value() :
    def __init__(self,GPIO,rate,action_group=None) :
        self.value=None
        self.GPIO=GPIO
        self.rate=rate
        self.action_group=action_group
        self.old_values=[0,0]

#-----INPUT VALUES-----#

class Value_sas(Value) :
    def __init__(self,GPIO,rate,action_group=None) :
        Value.__init__(self,GPIO,rate,action_group)
    def refresh(self,tic) :
        if tic%self.rate==0 :
            value=GPIO.input(self.GPIO)
            control.sas=bool(value)

class Value_rcs(Value) :
    def __init__(self,GPIO,rate,action_group=None) :
        Value.__init__(self,GPIO,rate,action_group)
    def refresh(self,tic) :
        if tic%self.rate==0 :
            value=GPIO.input(self.GPIO)
            control.rcs=bool(value)

class Value_legs(Value) :
    def __init__(self,GPIO,rate,action_group=None) :
        Value.__init__(self,GPIO,rate,action_group)
    def refresh(self,tic) :
        if tic%self.rate==0 :
            value=GPIO.input(self.GPIO)
            control.legs=bool(value)

class Value_gaz(Value) :
    def __init__(self,GPIO,rate,action_group=None) :
        Value.__init__(self,GPIO,rate,action_group)
        #self.channel=AnalogIn(mcp,MCP.P0)
    def refresh(self,tic) :
        if values["arm_moteur"].value==False :
            control.throttle=0.9
        else :
            if tic%self.rate==0 :
                #new_value=self.channel.value
                value=1
                value=(value/MAX_THROTTLE_VALUE)
                control.throttle=value

class Value_generic_switch(Value) :
    def __init__(self,GPIO,rate,action_group=None) :
        Value.__init__(self,GPIO,rate,action_group)
    def refresh(self,tic) :
        if tic%self.rate==0 :
            value=GPIO.input(self.GPIO)
            self.value=bool(value)

#-----OUTPUT VALUES-----#

class Value_sea_alt(Value) :
    def __init__(self,GPIO,rate,action_group=None) :
        Value.__init__(self,GPIO,rate,action_group)
    def refresh(self,tic) :
        if tic%self.rate==0 :
            self.value=flight.mean_altitude
            self.old_values.append(self.value)
            if len(self.old_values)>2 :
                self.old_values.pop(0)
        else :
            total_dist=self.old_values[1]-self.old_values[0]
            dist=total_dist/self.rate
            self.value=self.value+dist

class Value_ground_alt(Value) :
    def __init__(self,GPIO,rate,action_group=None) :
        Value.__init__(self,GPIO,rate,action_group)
    def refresh(self,tic) :
        if tic%self.rate==0 :
            self.value=flight.surface_altitude
            self.old_values.append(self.value)
            if len(self.old_values)>2 :
                self.old_values.pop(0)
        else :
            total_dist=self.old_values[1]-self.old_values[0]
            dist=total_dist/self.rate
            self.value=self.value+dist

def get_magnitude(vector) :
    return math.sqrt(sum(pow(element,2) for element in vector))

class Value_speed(Value) :
    def __init__(self,GPIO,rate,action_group=None) :
        Value.__init__(self,GPIO,rate,action_group)
    def refresh(self,tic) :
        if tic%self.rate==0 :
            self.value=get_magnitude(vessel.velocity(vessel.orbit.body.reference_frame))
            self.old_values.append(self.value)
            if len(self.old_values)>2 :
                self.old_values.pop(0)
        else :
            total_dist=self.old_values[1]-self.old_values[0]
            dist=total_dist/self.rate
            self.value=self.value+dist

class Value_apoapsis(Value) :
    def __init__(self,GPIO,rate,action_group=None) :
        Value.__init__(self,GPIO,rate,action_group)
    def refresh(self,tic) :
        if tic%self.rate==0 :
            self.value=orbit.apoapsis
            self.old_values.append(self.value)
            if len(self.old_values)>2 :
                self.old_values.pop(0)
        else :
            total_dist=self.old_values[1]-self.old_values[0]
            dist=total_dist/self.rate
            self.value=self.value+dist

class Value_periapsis(Value) :
    def __init__(self,GPIO,rate,action_group=None) :
        Value.__init__(self,GPIO,rate,action_group)
    def refresh(self,tic) :
        if tic%self.rate==0 :
            self.value=orbit.periapsis
            self.old_values.append(self.value)
            if len(self.old_values)>2 :
                self.old_values.pop(0)
        else :
            total_dist=self.old_values[1]-self.old_values[0]
            dist=total_dist/self.rate
            self.value=self.value+dist

class Value_apoapsis_time(Value) :
    def __init__(self,GPIO,rate,action_group=None) :
        Value.__init__(self,GPIO,rate,action_group)
    def refresh(self,tic) :
        if tic%self.rate==0 :
            self.value=orbit.time_to_apoapsis
            self.old_values.append(self.value)
            if len(self.old_values)>2 :
                self.old_values.pop(0)
        else :
            total_dist=self.old_values[1]-self.old_values[0]
            dist=total_dist/self.rate
            self.value=self.value+dist

class Value_periapsis_time(Value) :
    def __init__(self,GPIO,rate,action_group=None) :
        Value.__init__(self,GPIO,rate,action_group)
    def refresh(self,tic) :
        if tic%self.rate==0 :
            self.value=orbit.time_to_periapsis
            self.old_values.append(self.value)
            if len(self.old_values)>2 :
                self.old_values.pop(0)
        else :
            total_dist=self.old_values[1]-self.old_values[0]
            dist=total_dist/self.rate
            self.value=self.value+dist

class Value_g_force(Value) :
    def __init__(self,GPIO,rate,action_group=None) :
        Value.__init__(self,GPIO,rate,action_group)
    def refresh(self,tic) :
        if tic%self.rate==0 :
            self.value=flight.g_force
            self.old_values.append(self.value)
            if len(self.old_values)>2 :
                self.old_values.pop(0)
        else :
            total_dist=self.old_values[1]-self.old_values[0]
            dist=total_dist/self.rate
            self.value=self.value+dist

class Value_temperature(Value) :
    def __init__(self,GPIO,rate,action_group=None) :
        Value.__init__(self,GPIO,rate,action_group)
    def refresh(self,tic) :
        if tic%self.rate==0 :
            self.value=flight.static_air_temperature
            self.old_values.append(self.value)
            if len(self.old_values)>2 :
                self.old_values.pop(0)
        else :
            total_dist=self.old_values[1]-self.old_values[0]
            dist=total_dist/self.rate
            self.value=self.value+dist
#-----CALLBACK COMMANDS-----#

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
    "sas":Value_sas(GPIO=port_gpio["sas"],rate=5), #done
    "rcs":Value_rcs(GPIO=port_gpio["rcs"],rate=5), #done
    "legs":Value_legs(GPIO=port_gpio["legs"],rate=5), #TODO : Fonctionnent en théorie, mais n'a pas pu être essayés en pratique
    "gaz":Value_gaz(GPIO=port_gpio["gaz"],rate=2), #TODO : Fonctionnent en théorie, mais n'a pas pu être essayés en pratique
    #"time_multi":Value(way="input",name="Multiplicateur temporel",value=False,GPIO=port_gpio["time_multi"],rate=1), #TODO : Il faut tester l'urilisation du MCP3008
    "arm_arret_urgence":Value_generic_switch(GPIO=port_gpio["arm_arret_urgence"],rate=10), #done
    "arm_moteur":Value_generic_switch(GPIO=port_gpio["arm_moteur"],rate=10), #done
    "ground_alt":Value_sea_alt(GPIO=None,rate=2),
    "sea_alt":Value_ground_alt(GPIO=None,rate=2),
    "speed":Value_speed(GPIO=None,rate=5),
    "apoapsis":Value_apoapsis(GPIO=None,rate=5),
    "periapsis":Value_periapsis(GPIO=None,rate=5),
    "time_to_apoapsis":Value_apoapsis_time(GPIO=None,rate=5),
    "time_to_periapsis":Value_periapsis_time(GPIO=None,rate=5),
    "g_force":Value_g_force(GPIO=None,rate=10),
    "temperature":Value_temperature(GPIO=None,rate=10),
}

def gpio_setup() :
    GPIO.setup(port_gpio["sas"],GPIO.IN,GPIO.PUD_DOWN)
    GPIO.setup(port_gpio["rcs"],GPIO.IN,GPIO.PUD_DOWN)
    GPIO.setup(port_gpio["stage"],GPIO.IN,GPIO.PUD_DOWN)
    GPIO.setup(port_gpio["legs"],GPIO.IN,GPIO.PUD_DOWN)
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

GPIO.add_event_detect(port_gpio["stage"],GPIO.RISING,callback_stage)
GPIO.add_event_detect(port_gpio["affichage"],GPIO.RISING,callback_affichage)
GPIO.add_event_detect(port_gpio["arret_urgence"],GPIO.RISING,callback_arret)
GPIO.add_event_detect(port_gpio["detach_arret_urgence"],GPIO.RISING,callback_detach_arret_urgence)
GPIO.add_event_detect(port_gpio["parachute_freinage"],GPIO.RISING,callback_parachute_freinage)
GPIO.add_event_detect(port_gpio["parachute_principaux"],GPIO.RISING,callback_parachute_principaux)
GPIO.add_event_detect(port_gpio["decouplage_port_ammarage"],GPIO.RISING,callback_decouplage_port_ammarage)
GPIO.add_event_detect(port_gpio["ouverture_coiffe"],GPIO.RISING,callback_ouverture_coiffe)
GPIO.add_event_detect(port_gpio["detach_bouclier_thermique"],GPIO.RISING,callback_detach_bouclier_thermique)


def update_values() :
    global tic
    if tic>COMMAND_FPS :
        tic=0
    for key in values :
        try :
            values[key].refresh(tic)
        except Exception as e :
            error=traceback.format_exc()
            print("Error while trying to refresh a key")
            print(error)
            pygame.quit()
            quit()
    tic+=1

#-----GRAPHICS-----#



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

def format_speed(value) :
    to_return=format_distance(value,2)
    return str(to_return)

def format_sea(value) :
    to_return=format_distance(value,3)
    return str(to_return)

def format_ground(value) :
    to_return=format_distance(value-6,3)
    return str(to_return)

def format_apsis(value) :
    to_return=format_distance(value-600000,3)
    return str(to_return)

def format_timeto(value) :
    to_return=format_time(value)
    return str(to_return)

def format_g(value) :
    to_return=str(round(value,3)).ljust(5,'0')
    return to_return

def format_temp(value) :
    to_return=str(round(value,2)).zfill(6)
    return to_return

format = {
    "speed":format_speed,
    "sea_alt":format_sea,
    "ground_alt":format_ground,
    "apoapsis":format_apsis,
    "time_to_apoapsis":format_timeto,
    "periapsis":format_apsis,
    "time_to_periapsis":format_timeto,
    "g_force":format_g,
    "temperature":format_temp
}

class Number_Block() : #Block used to show a number value. Meant to be used by a Layout class
    def __init__(self,type,pos,font_size=default_font_size) :
        self.type=type
        self.pos=pos
        self.font=pygame.font.Font("digit.ttf",font_size)
        self.color="Cyan"
        self.rect=False
        self.old_value=None
    def create(self,value) :
        if value!=self.old_value :
            formated_value=format[self.type](value)
            self.rect=self.font.render(formated_value,1,pygame.Color(self.color),pygame.Color(27,41,68)).convert_alpha()
            self.old_value=formated_value

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

def create_main_layout() :
    blocks=[]
    blocks.append(Number_Block("sea_alt",main_layout_position["sea_alt"],font_size=60))
    blocks.append(Number_Block("ground_alt",main_layout_position["ground_alt"],font_size=60))
    blocks.append(Number_Block("speed",main_layout_position["speed"],font_size=120))
    blocks.append(Number_Block("apoapsis",main_layout_position["apoapsis"],font_size=45))
    blocks.append(Number_Block("time_to_apoapsis",main_layout_position["time_to_apoapsis"],font_size=50))
    blocks.append(Number_Block("periapsis",main_layout_position["periapsis"],font_size=45))
    blocks.append(Number_Block("time_to_periapsis",main_layout_position["time_to_periapsis"],font_size=50))
    blocks.append(Number_Block("g_force",main_layout_position["g_force"],font_size=100))
    blocks.append(Number_Block("temperature",main_layout_position["temperature"],font_size=70))
    return blocks

class Screen_handler(Thread) :
    def __init__(self,screen_size,fps,flags=None,debug=False) :
        #-----Initialisation of the Screen Thread-----#
        Thread.__init__(self)
        #-----Creation of Screen-----#
        self.fps=fps
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
        self.blocks=create_main_layout()
    def draw(self) :
        for block in self.blocks :
            block.create(values[block.type].value)
            self.Screen.blit(block.rect,block.pos)
    def create_header(self,clock,big_clock) :
        fps=str(round(clock.get_fps(),1))
        big_clock_fps=str(round(big_clock.get_fps(),1))
        txt=f"SCREEN_FPS : {fps} | COMMAND_FPS : {big_clock_fps}"
        font=pygame.font.SysFont("Arial", 18)
        to_blit=font.render(txt,1,pygame.Color("White"),pygame.Color("Black"))
        return to_blit
    def run(self) :
        while True :
            #-----Check for event and apply proper action-----
            self.draw()
            #-----Add Debug header-----
            header=self.create_header(self.Clock,command_clock)
            self.Screen.blit(header,(0,0))
            #-----Show the Screen-----
            pygame.display.update()
            self.Clock.tick(self.fps)

def main() :
    update_values()
    #-----Initialisation-----
    gpio_setup()
    Screen=Screen_handler(SCREEN_SIZE,SCREEN_FPS,debug=DEBUG)
    Screen.start()
    #-----Refresh Loop-----
    while on :
        #-----Update Values-----
        update_values()
        command_clock.tick(COMMAND_FPS)

if __name__=="__main__":
    on=True
    main()
