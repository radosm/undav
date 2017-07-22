#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
@file    ave.py
@author  Martin Rados
@date    2017-07-20

clases para Simulación Avellaneda
"""

import os,sys,subprocess, math
from time import sleep
import scipy.stats as stats
from sumo import *
from cargaglobales import *

#print TS
#print PARADAS
#print LINEAS
#print PARADAS_LINEA
#print CUADRA_PARADA
#print LAMBDAS_PARADAS
#print LAMBDAS_LINEAS
#print LAMBDAS_PARADAS_LINEAS
#print PRIMER_PARADA
#print MU
#print S2
#print MAX
#print OCUPACION
#print AP

class Chofer:
  def __init__(self,v):
    self.vehiculo=v
 
  def getVehiculo(self):
    return self.vehiculo

  def manejar(self,s):
    return False

class Simulacion:
  def __init__(self):
    self.ParadasSimulacion={}
    self.paso=0
    self.sumo=Sumo()
    self.proximo={}
    for l in self.lineas():
      self.calcularProximoLinea(l)

  def run(self):
    for i in range(1,TS+1):
      self.step()
    
  def proximoLinea(self,l):
    return self.proximo[l]

  def calcularProximoLinea(self,l):
    va=stats.expon.rvs(scale=LAMBDAS_LINEAS[l])
    self.proximo[l]=int(va)+self.paso

  def lineas(self):
    return LINEAS

  def paradasLinea(self,l):
    return PARADAS_LINEA[l]

  def cuadrasParadaLinea(self,l):
    return [ CUADRA_PARADA[x] for x in self.paradasLinea(l) ]

  def enCuadraParada(self,v):
    l=self.sumo.lineaVehiculo(v)
    c=self.sumo.cuadraVehiculo(v)
    cp=self.cuadrasParadaLinea(l)
    return c in cp

  def saltearParada(self,v):
    l=self.sumo.lineaVehiculo(v)
    c=self.sumo.cuadraVehiculo(v)
    self.sumo.recrearVehiculo(v)
    cp=self.cuadrasParadaLinea(l)
    pa=self.paradasLinea(l)
    i=cp.index(c)
    for p in range(i+1,len(cp)):
      self.sumo.setParadaVehiculo(v,"p%02d" % pa[p],100000000)

  def insertarColectivos(self):
    if self.paso==1:
      v=self.sumo.agregarVehiculo(10)
    if self.paso==2:
      v=self.sumo.agregarVehiculo(10)
    if self.paso==3:
      v=self.sumo.agregarVehiculo(10)
    return
    for l in self.lineas():
      if self.paso==self.proximoLinea(l):
        self.sumo.agregarVehiculo(l)
        self.calcularProximoLinea(l)
      
  def step(self):
    self.paso+=1

    self.sumo.step(self.paso)

    self.insertarColectivos()

    for v in self.sumo.listaVehiculos():
      if self.sumo.tiempoDetenidoVehiculo(v) > 2 \
         and not self.sumo.vehiculoEnParada(v):
        if self.enCuadraParada(v):
          print self.paso,v
          self.saltearParada(v)
          #raw_input()


try:
  s=Simulacion()
  s.run()
except traci.FatalTraCIError:
  print ""
