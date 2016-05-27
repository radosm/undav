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
 
ret = subprocess.Popen(["sumo-gui", "-c", "ave.sumo.cfg" , "--step-length", "0.1" , "--remote-port" , str(PORT)])
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

belgrano="-9468"

traci.lane.setDisallowed('--9433_0','bus')

# Primera cuadra de Belgrano
traci.lane.setDisallowed(belgrano+'#1_2','bus')
traci.lane.setDisallowed(belgrano+'#1_3','bus')
# Segunda cuadra de Belgrano
traci.lane.setDisallowed(belgrano+'#2_2','bus')
traci.lane.setDisallowed(belgrano+'#2_3','bus')
# Tercera cuadra de Belgrano
traci.lane.setDisallowed(belgrano+'#3_2','bus')
traci.lane.setDisallowed(belgrano+'#3_3','bus')

parada_solicitada=[False,False,False,False,False,False]
parada_aceptada=[False,False,False,False,False,False]
ya_paro=[False,False,False,False,False,False]

try:
    while step < 6000:
        step += 1
        traci.simulationStep()
        print "STEP: ", step

        parados_100=0

        for v in traci.vehicle.getIDList():
            cuadra=traci.vehicle.getRoadID(v)
            carril=traci.vehicle.getLaneIndex(v)
            tipo=traci.vehicle.getTypeID(v)
            velocidad=traci.vehicle.getSpeed(v)
            posicion=traci.vehicle.getLanePosition(v)
            linea=v.partition(".")[0]
            nro=int(v.partition(".")[2])

            if nro <=5 and velocidad < 0.01 and posicion > 30 and not traci.vehicle.isAtBusStop(v):
                if linea=="linea100":
                    # aca iria un setStop
                    #traci.vehicle.setStop(v,cuadra,posicion+0.1,carril,5000)
                    parados_100=parados_100+1

            if traci.vehicle.isAtBusStop(v):
                if linea=="linea100":
                    ya_paro[nro]=True
                    parados_100=parados_100+1

                if linea=="linea101":
                    if nro>=ult101:
                      ult101=ult101+1
                      traci.vehicle.setBusStop(v,'p2',000)

            print linea+" "+str(nro)+" "+cuadra+" "+str(carril)+" "+tipo+" "+str(velocidad)
            print "cant parados:"+str(parados_100)
            
            if nro <= 5 and posicion > 30 and linea=="linea100" and parados_100 < 2:
               if parados_100 < 1:
                   try:
                       if not parada_solicitada[nro]:
                           parada_solicitada[nro]=True
                           traci.vehicle.setBusStop(v,'p1',5000)
                           # Si llega acá es porque va a parar
                           parada_aceptada[nro]=True
                   except:
                       print linea+" "+str(nro)+" "+"no va a parar"
               else:
                   print "ya hay suficientes parados" 

except traci.FatalTraCIError:
    print ""

traci.close()
