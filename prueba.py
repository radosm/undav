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
import scipy.stats as stats

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

belgrano="-9468"

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

siguiente=1
try:
    while step < 6000:
        step += 1
        if step==siguiente:
            nuevoID="100."+str(step)
            traci.vehicle.add(vehID=nuevoID, routeID="linea100", typeID="bus_100")
            # el 2000 en realidad debe salir de una v.a.
            traci.vehicle.setBusStop(vehID=nuevoID, stopID="p1", duration=2000)
            # es * 600 porque el step_length es 0.1s // 2.72 es el lambda calculado
            siguiente=int(stats.expon.rvs(scale=1/2.72)*600)+step
            print siguiente

        for v in traci.vehicle.getIDList():
            if traci.vehicle.isAtBusStop(v):
                print v," esta en la parada"

        traci.simulationStep()
        print "STEP: ", step, " SIGUIENTE: ", siguiente


except traci.FatalTraCIError:
    print ""

traci.close()
