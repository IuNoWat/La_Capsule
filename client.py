#!/usr/bin/python
#coding: utf-8

from threading import Thread

import krpc
import pygame

HOME_WIFI_IP="192.168.1.159"
RPC_PORT=50008
FPS=10

#The API class launch a thread that follow the status of the KSP game.
#Since calls to KRPC take lots of time, we need to desynchronise it from the pygame loop if we want to acheive 30+ fps

class API(Thread) :
    def __init__(self,fps) :
        #-----Initialisation of the Screen Thread-----#
        Thread.__init__(self)
        #-----Handling of desynchronised update-----#
        self.tic=1
        self.fps=fps
        self.refresh_values=[[],[],[],[],[],[],[],[],[],[],[],]
        self.access_values={}
        #-----Handling of pygame loop-----#
        self.on=False
        self.clock=pygame.time.Clock()

        #-----Adding Values-----#
        #The methode add_value define a value that the thread is going to follow, with a name, the method that need to be called, and the refresh rate of the value

        #Refresh rate 1
        self.add_value({"name":"altitude","method":self.get_altitude},1)
        self.add_value({"name":"speed","method":self.get_speed},1)

        #Refresh rate 5
        self.add_value({"name":"g_force","method":self.get_g_force},5)
        self.add_value({"name":"temp","method":self.get_temp},5)

        #Refresh rate 10
        self.add_value({"name":"apoapsis","method":self.get_apoapsis},10)
        self.add_value({"name":"apoapsis_time","method":self.get_apoapsis_time},10)
        self.add_value({"name":"periapsis","method":self.get_periapsis},10)
        self.add_value({"name":"periapsis_time","method":self.get_periapsis_time},10)
    
        #-----Temp value-----#
        #To access the krpc API only when necessary, we cache thoose specific values that don't change often
        self.current_values={
            "sas":False,
            "rcs":True,
            "gaz":0,
        }

    def connect(self,ip=HOME_WIFI_IP) :
        self.con=krpc.connect(
            "Client",
            ip,
            RPC_PORT
        )
        self.vessel=self.con.space_center.active_vessel
        self.camera=self.con.space_center.camera
        self.control=self.vessel.control
        self.flight=self.vessel.flight()
        self.orbit=self.vessel.orbit
        self.resources=self.vessel.resources
    
    def get_fps(self) :
        return str(round(self.clock.get_fps(),1))
    
    def add_value(self,value,rate) : #The methode add_value define a value that the thread is going to follow, with a name, the method that need to be called, and the refresh rate of the value
        self.refresh_values[rate].append(value)
        self.access_values[value["name"]]=None

    def update_values(self) : #Called each loop
        for i,value in enumerate(self.refresh_values) :
            if i!=0 :
                if self.tic%i==0 :
                    for value in self.refresh_values[i] :
                        self.access_values[value["name"]]=value["method"]()

        if self.tic==self.fps :
            self.tic=1
        else :
            self.tic+=1

    def run(self) :

        self.on=True
        while self.on :
            #Start of loop

            #Update values
            self.update_values()

            #End of loop
            self.clock.tick(self.fps)


    #-----GET_VALUE METHOD-----#

    def get_altitude(self) :
        return self.flight.surface_altitude
    
    def get_speed(self) :
        return self.flight.speed
    
    def get_g_force(self) :
        return self.flight.g_force
    
    def get_temp(self) :
        return self.flight.static_air_temperature
    
    def get_apoapsis(self) :
        return self.orbit.apoapsis
    
    def get_apoapsis_time(self) :
        return self.orbit.time_to_apoapsis
    
    def get_periapsis(self) :
        return self.orbit.periapsis
    
    def get_periapsis_time(self) :
        return self.orbit.time_to_periapsis
    
    #-----SET_VALUE METHOD-----# WORK IN PROGRESS
    
    def set_SAS(self,value) :
        if self.current_values["sas"]!=value :
            self.control.sas=value
            self.current_values["sas"]=value
    
    def set_RCS(self,value) :
        if self.current_values["rcs"]!=value :
            self.control.rcs=value
            self.current_values["rcs"]=value
    
    def set_gaz(self,value) :
        if self.current_values["gaz"]!=value :
            self.control.rcs=value
            self.current_values["gaz"]=value



if __name__=="__main__" : #If launched directly, will start an API class
    api=API(fps=10)
    api.connect()
    api.start()

