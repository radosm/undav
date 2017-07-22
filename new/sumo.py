#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
@file    clases.py
@author  Martin Rados
@date    2017-07-20

Clase Sumo
"""

import os,sys

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

import subprocess, traci
from time import sleep

class Sumo:
  def __init__(self):

    # Levanta SUMO e inicia control con traci
    # ---------------------------------------
    ret = subprocess.Popen(["sumo-gui", "-c", "ave.sumo.cfg" , "--start", \
          "--quit-on-end", "--time-to-teleport", "-1", "--step-length", "1" ,\
          "--remote-port" , "8813" ])
    sleep(1)
    traci.init(8813)

    # Deshabilita para los omnibus los carriles de autos
    # --------------------------------------------------
    belgrano="-9468"

    traci.lane.setDisallowed('--9433_0',"bus")
    # Primera cuadra de Belgrano
    traci.lane.setDisallowed(belgrano+'#1_2',"bus")
    traci.lane.setDisallowed(belgrano+'#1_3',"bus")
    # Segunda cuadra de Belgrano
    traci.lane.setDisallowed(belgrano+'#2_2',"bus")
    traci.lane.setDisallowed(belgrano+'#2_3',"bus")
    # Tercera cuadra de Belgrano
    traci.lane.setDisallowed(belgrano+'#3_2',"bus")
    traci.lane.setDisallowed(belgrano+'#3_3',"bus")
    # Cuarta cuadra de Belgrano
    traci.lane.setDisallowed(belgrano+'#4_2',"bus")
    traci.lane.setDisallowed(belgrano+'#4_3',"bus")
    # Quinta cuadra de Belgrano
    traci.lane.setDisallowed(belgrano+'#5_2',"bus")
    traci.lane.setDisallowed(belgrano+'#5_3',"bus")
    # Sexta cuadra de Belgrano
    traci.lane.setDisallowed(belgrano+'#6_2',"bus")
    traci.lane.setDisallowed(belgrano+'#6_3',"bus")
 
    self.seg=0
    self.pasajeros={}
  
  def __del__(self):
    traci.close()

  def agregarVehiculo(self,linea,pasajeros=0):
    vid=str(linea)+"."+str(self.seg)
    rid="linea_"+str(linea)
    traci.vehicle.add(vehID=vid, routeID=rid, typeID="colectivo")
    self.pasajeros[vid]=pasajeros
    return vid

  def recrearVehiculo(self,v):
    r=self.rutaVehiculo(v)
    i=self.indiceRutaVehiculo(v)
    c=self.carrilVehiculo(v)
    p=self.posicionVehiculo(v)
    rid=v+"."+str(self.seg)
    traci.route.add(rid,[r[x] for x in range(i,len(r))])
    traci.vehicle.remove(v)
    traci.vehicle.add(vehID=v, routeID=rid, lane=c, pos=p, typeID="colectivo")

  def listaVehiculos(self):
    return traci.vehicle.getIDList()

  def agregarPasajerosVehiculo(self,v,p):
    self.pasajeros[v]+=p

  def tiempoDetenidoVehiculo(self,v):
    return traci.vehicle.getWaitingTime(v)

  def pasajerosVehiculo(self,v):
    return self.pasajeros[v]

  def vehiculoEnParada(self,v):
    return traci.vehicle.isAtBusStop(v)

  def cuadraVehiculo(self,v):
    return traci.vehicle.getRoadID(v)

  def carrilVehiculo(self,v):
    return traci.vehicle.getLaneIndex(v)

  def posicionVehiculo(self,v):
    return traci.vehicle.getLanePosition(v)

  def velocidadVehiculo(self,v):
    return traci.vehicle.getSpeed(v)

  def rutaVehiculo(self,v):
    return traci.vehicle.getRoute(v)

  def indiceRutaVehiculo(self,v):
    return traci.vehicle.getRouteIndex(v)

  def cambiarRutaVehiculo(self,v,r):
    return traci.vehicle.setRoute(v,r)

  def setParadaVehiculo(self,v,p,d,u=-1):
    return traci.vehicle.setBusStop(v,p,d,u)

  def continuarVehiculo(self,v):
    return traci.vehicle.resume(v)

  def lineaVehiculo(self,v):
    return int(v.split(".")[0])

  def partidaVehiculo(self,v):
    return int(v.split(".")[1])

  def step(self,seg):
    self.seg=seg
    traci.simulationStep()
