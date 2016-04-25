#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
@file    runner.py
@author  Martin Rados
@date    2016-04-08

Prueba de ruteo y detencion
"""
import os, sys, subprocess
from time import sleep

PORT = 8813
step = 0

####################################################
# Levanta SUMO
####################################################
 
ret = subprocess.Popen(["sumo-gui", "-c", "conf.sumo.cfg" , "--step-length", "0.1" , "--remote-port" , str(PORT)])
sleep(1) 


####################################################
# Inicia Control
####################################################

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:   
    sys.exit("please declare environment variable 'SUMO_HOME'")

import traci
import traci.constants as tc

traci.init(PORT)

ult100=0
ult101=0

traci.lane.setDisallowed('-304664096_0','bus')

# Primera cuadra de Belgrano
traci.lane.setDisallowed('26589743#1_2','bus')
traci.lane.setDisallowed('26589743#1_3','bus')
# Segunda cuadra de Belgrano
traci.lane.setDisallowed('26589743#2_2','bus')
traci.lane.setDisallowed('26589743#2_3','bus')
# Tercera cuadra de Belgrano
traci.lane.setDisallowed('26589743#3_2','bus')
traci.lane.setDisallowed('26589743#3_3','bus')

listo=False

try:
    while step < 6000:
        step += 1
        traci.simulationStep()
        print "STEP: ", step

        for v in traci.vehicle.getIDList():
            cuadra=traci.vehicle.getRoadID(v)
            carril=traci.vehicle.getLaneIndex(v)
            tipo=traci.vehicle.getTypeID(v)
            linea=v.partition(".")[0]
            nro=int(v.partition(".")[2])
            print linea+" "+str(nro)+" "+cuadra+" "+str(carril)+" "+tipo
            if traci.vehicle.getLanePosition(v) > 40 and linea=="linea100" and nro==2 and not listo:
               listo=True
               traci.vehicle.setBusStop(v,'p1',5000)
            
            if traci.vehicle.isAtBusStop(v):
                print "************************* En parada:"+v
                #if linea=="linea100":
                #    if nro>=ult100:
                #      ult100=ult100+1
                #      traci.vehicle.setBusStop(v,'p1',000)
                if linea=="linea101":
                    if nro>=ult101:
                      ult101=ult101+1
                      traci.vehicle.setBusStop(v,'p2',000)
            

except traci.FatalTraCIError:
    print ""

traci.close()
