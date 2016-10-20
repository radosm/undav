#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
@file    runner.py
@author  Martin Rados
@date    2016-04-08

Prueba de ruteo y detencion
"""
import os, sys, subprocess, math
from time import sleep
import scipy.stats as stats

PORT = 8813

####################################################
# Levanta SUMO
####################################################
 
ret = subprocess.Popen(["sumo-gui", "-c", "ave.sumo.cfg" , "--step-length", "1" , "--remote-port" , str(PORT)])
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

########################################
########################################

#
# Tiempo de simulacion (en segundos)
#
TS=7200

#
# Lee cuáles son las paradas existentes
#
PARADAS=[]
f=open("mediciones/paradas.txt","r")
for l in f:
  p=int(l)
  PARADAS.append(p)
f.close()

#
# Lee cuáles son las líneas existentes
#
LINEAS=[]
PARADAS_LINEA={}
f=open("mediciones/lineas.txt","r")
for l in f:
  li=int(l)
  LINEAS.append(li)
  PARADAS_LINEA[li]=[]
f.close()

#
# Lee cuáles son las paradas de cada linea
#
f=open("mediciones/paradas_lineas.txt","r")
for l in f:
  s=l.split(',')
  p=int(s[0])   # parada
  li=int(s[1])  # linea
  PARADAS_LINEA[li].append(p)
f.close()

#
# Lee para cada parada cuál es el lambda de arribo de personas
#
LAMBDAS_PARADAS={}
s=subprocess.Popen([ 'bash','./mediciones/calcula_lambdas_paradas' ], stdout=subprocess.PIPE)
for l in s.stdout:
  s=l.split(',')
  p=int(s[0])     # parada
  la=float(s[1])  # lambda
  LAMBDAS_PARADAS[p]=la
  
#
# Lee para cada linea cuál es el lambda de arribo a su primer parada
#
LAMBDAS_LINEAS={}
s=subprocess.Popen([ 'bash','./mediciones/calcula_lambdas_lineas' ], stdout=subprocess.PIPE)
for l in s.stdout:
  s=l.split(',')
  li=int(s[0])   # linea
  la=float(s[1]) # lambda
  LAMBDAS_LINEAS[li]=la

#
# Lee para cada combinación de parada y linea el lambda de gente que sube
#
LAMBDAS_PARADAS_LINEAS={}
s=subprocess.Popen([ 'bash','./mediciones/calcula_lambdas_paradas_lineas' ], stdout=subprocess.PIPE)
for l in s.stdout:
  s=l.split(',')
  pa=int(s[0])   # parada
  li=int(s[1])   # linea
  la=float(s[2]) # lambda
  LAMBDAS_PARADAS_LINEAS[pa,li]=la
  
#
# Lee lambda de tiempo que demora una persona en subir
#
s=subprocess.Popen( ['bash','./mediciones/lambda_tiempo_subir'],stdout=subprocess.PIPE)
for l in s.stdout:
  LAMBDA_TIEMPO_SUBIR=float(l)

#
# Lee cuáles son las primeras paradas de cada linea
#
PRIMER_PARADA={}
s=subprocess.Popen( ['bash','./mediciones/calcula_primeras_paradas'],stdout=subprocess.PIPE)
for l in s.stdout:
  s=l.split(',')
  l=int(s[0]) # linea
  p=int(s[1]) # primer parada
  PRIMER_PARADA[l]=p

#
# Lee valores para la distribución normal que se usará para
# calcular la cantidad inicial de personas en cada parada
#
MU={}
S2={}
MAX={}
s=subprocess.Popen( ['bash','./mediciones/calcula_s2'],stdout=subprocess.PIPE)
for l in s.stdout:
  s=l.split(',')
  p=int(s[0])    # parada
  mu=float(s[1]) # mu
  s2=float(s[2]) # s^2
  mx=int(s[3])   # cantidad máxima de personas observada
  MU[p]=mu
  S2[p]=s2
  MAX[p]=mx

#
# Calcula array AP
#
AP={}
for p in PARADAS:
  remanente=0
  for seg in range (1,TS):
    va=stats.expon.rvs(scale=LAMBDAS_PARADAS[p])
    llegan,r=divmod(va+remanente,1)
    remanente=va+remanente-llegan
    AP[p,seg]=llegan

#
# Estado inicial
#

PP={}
TANT={}
TULT={}
DELTA=[]
TPANT={}
TPULT={}
DELTAP=[]
PROXIMO={}
PARO_VECES={}
PARO_ULTIMA={}

for p in PARADAS:
  PP[p]=int(round(stats.norm.rvs()*math.sqrt(S2[p])+MU[p],0))
  if PP[p] < 0:
    PP[p]=0
  if PP[p] > MAX[p]:
    PP[p]=MAX[p]

for l in LINEAS:
    va=stats.expon.rvs(scale=LAMBDAS_LINEAS[l])
    PROXIMO[l]=int(va)

try:
  #
  # Ciclo principal
  #
  for seg in range (1,TS):

    traci.simulationStep()

    for p in PARADAS:
      PP[p]+=AP[p,seg]
    
    # Ve si hay que inyectar un nuevo colectivo
    # -----------------------------------------
    for l in LINEAS:
  
      # Partida de un colectivo
      # -----------------------
      if seg==PROXIMO[l]:
        # 1) inyecta colectivo
        print "seg="+str(seg)+" linea="+str(l)
        vid=str(l)+"."+str(seg)
        rid="linea_"+str(l)
        PARO_VECES[vid]=0
        PARO_ULTIMA[vid]=""
        if l!=178:
          traci.vehicle.add(vehID=vid, routeID=rid, typeID="colectivo")
        # 2) calcula el próximo
        va=stats.expon.rvs(scale=LAMBDAS_LINEAS[l])
        PROXIMO[l]=int(va)+seg
        # 3) cálculos para determinar factor de contracción
        if l not in TANT:
          TANT[l]=seg
        else:
          DELTA.append(seg-TANT[l])
          TANT[l]=seg
  
    # Llegada de colectivos a parada
    # ------------------------------
    for v in traci.vehicle.getIDList():
      if traci.vehicle.isAtBusStop(v):
        #print PARO_ULTIMA[v]+" - "+traci.vehicle.getRoadID(v)
        if PARO_ULTIMA[v]!=traci.vehicle.getRoadID(v):
          PARO_ULTIMA[v]=traci.vehicle.getRoadID(v)

          l=int(v.partition(".")[0])
          p=PARADAS_LINEA[l][PARO_VECES[v]]
          ps="p%02d" % p
          PARO_VECES[v]=PARO_VECES[v]+1
      
          if (p,l) not in TULT: # Es la primer llegada de la linea a la parada
            TULT[p,l]=0
      
          # tt significa tiempo transcurrido
          tt=seg-TULT[p,l]
      
          suben=round(stats.expon.rvs(scale=LAMBDAS_PARADAS_LINEAS[p,l]*tt),0)
          tdet=round(stats.expon.rvs(scale=LAMBDA_TIEMPO_SUBIR*suben),0)

          print "seg="+str(seg)+" vehiculo "+v+" en su parada nro "+str(PARO_VECES[v])+", la parada es la "+ps+" tdet="+str(tdet)+" suben="+str(suben)
      
          # Cálculos para determinar factor de contracción
          if p==PRIMER_PARADA[l]:
            if l not in TPANT:
              TPANT[l]=seg
            else:
              DELTAP.append(seg-TPANT[l])
              TPANT[l]=seg
      
          # Establecer detención
          cuadra=traci.vehicle.getRoadID(v)
          carril=traci.vehicle.getLaneIndex(v)
          tipo=traci.vehicle.getTypeID(v)
          velocidad=traci.vehicle.getSpeed(v)
          posicion=traci.vehicle.getLanePosition(v)
          print "Estableciendo detención, linea="+str(l)+" carril="+cuadra+"_"+str(carril)+" velocidad="+str(velocidad)
          traci.vehicle.setBusStop(v,ps,tdet*1000)
      
          if PP[p] < suben:
            PP[p]=0
          else:
            PP[p]-=suben

except traci.FatalTraCIError:
    print ""

########################################
########################################


# try:
#     while step < 6000:
#         step += 1
#         traci.simulationStep()
#         print "STEP: ", step
# 
#         parados_100=0
# 
#         for v in traci.vehicle.getIDList():
#             cuadra=traci.vehicle.getRoadID(v)
#             carril=traci.vehicle.getLaneIndex(v)
#             tipo=traci.vehicle.getTypeID(v)
#             velocidad=traci.vehicle.getSpeed(v)
#             posicion=traci.vehicle.getLanePosition(v)
#             linea=v.partition(".")[0]
#             nro=int(v.partition(".")[2])
# 
#             if nro <=5 and velocidad < 0.01 and posicion > 30 and not traci.vehicle.isAtBusStop(v):
#                 if linea=="linea100":
#                     # aca iria un setStop
#                     #traci.vehicle.setStop(v,cuadra,posicion+0.1,carril,5000)
#                     parados_100=parados_100+1
# 
#             if traci.vehicle.isAtBusStop(v):
#                 if linea=="linea100":
#                     ya_paro[nro]=True
#                     parados_100=parados_100+1
# 
#                 if linea=="linea101":
#                     if nro>=ult101:
#                       ult101=ult101+1
#                       traci.vehicle.setBusStop(v,'p2',000)
# 
#             print linea+" "+str(nro)+" "+cuadra+" "+str(carril)+" "+tipo+" "+str(velocidad)
#             print "cant parados:"+str(parados_100)
#             
#             if nro <= 5 and posicion > 30 and linea=="linea100" and parados_100 < 2:
#                if parados_100 < 1:
#                    try:
#                        if not parada_solicitada[nro]:
#                            parada_solicitada[nro]=True
#                            traci.vehicle.setBusStop(v,'p1',5000)
#                            # Si llega acá es porque va a parar
#                            parada_aceptada[nro]=True
#                    except:
#                        print linea+" "+str(nro)+" "+"no va a parar"
#                else:
#                    print "ya hay suficientes parados" 
# 
# except traci.FatalTraCIError:
#     print ""

traci.close()
