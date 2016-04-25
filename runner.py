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
            if traci.vehicle.isAtBusStop(v):
                print "************************* En parada:"+v
                if linea=="linea100":
                    if nro>=ult100:
                      ult100=ult100+1
                      traci.vehicle.setBusStop(v,'p1',3000)
                if linea=="linea101":
                    if nro>=ult101:
                      ult101=ult101+1
                      traci.vehicle.setBusStop(v,'p2',2000)
            

except traci.FatalTraCIError:
    print ""

traci.close()
