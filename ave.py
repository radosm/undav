#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
@file    Ave.py
@author  Martin Rados
@date    2016-04-08

Simulación Avellaneda
"""
import os, sys, subprocess, math
from time import sleep
import scipy.stats as stats

####################################################
# Levanta SUMO
####################################################
 
PORT = 8813
ret = subprocess.Popen(["sumo-gui", "-c", "ave.sumo.cfg" , "--start", "--quit-on-end", "--time-to-teleport", "-1", "--step-length", "1" , "--remote-port" , str(PORT)])
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

#
# Tiempo de simulación (en segundos)
#
t0=900
t1=1800
t2=2700
t3=3600
TS=4500
p_ini=0.8

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
# Array que contiene en qué cuadra está cada parada
#
CUADRA_PARADA={}
CUADRA_PARADA[1]=belgrano+'#2'
CUADRA_PARADA[2]=belgrano+'#3'
CUADRA_PARADA[3]=belgrano+'#3'
CUADRA_PARADA[4]=belgrano+'#3'
CUADRA_PARADA[5]=belgrano+'#4'
CUADRA_PARADA[6]=belgrano+'#4'
CUADRA_PARADA[7]=belgrano+'#4'
CUADRA_PARADA[8]=belgrano+'#4'
CUADRA_PARADA[9]=belgrano+'#5'
CUADRA_PARADA[10]=belgrano+'#5'
CUADRA_PARADA[11]=belgrano+'#6'
CUADRA_PARADA[12]=belgrano+'#6'

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
  s=l.split(',')
  mu=float(s[0])    # mu
  si2=float(s[1])   # sigma^2
  MU_TIEMPO_SUBIR=mu
  SIGMA2_TIEMPO_SUBIR=si2 ## /4

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
# Lee probabilidad de ocupación de cada línea en su primer parada
#
OCUPACION={}
prob={}
s=subprocess.Popen( ['bash','./mediciones/calcula_ocupacion_lineas'],stdout=subprocess.PIPE)
for l in s.stdout:
  s=l.split(',')
  li=int(s[0])   # linea
  prob[0]=round(float(s[1]),2) # proba vacío
  prob[1]=round(float(s[2]),2) # proba asientos libres
  prob[2]=round(float(s[3]),2) # proba sin asientos libres
  prob[3]=round(float(s[4]),2) # completo

  sum=0
  OCUPACION[li]={}
  for i in range(0,4):
    if sum+prob[i]>1:
      prob[i]=1-sum

    sum+=prob[i]

    OCUPACION[li][i]=prob[i]*100

  OCUPACION[li][4]=round(1-sum,2)*100 # Tan completo que no se detiene

#
# Lee parámetros de distribución normal de cant de personas que suben a un colectivo
#
s=subprocess.Popen( ['bash','./mediciones/normal_suben'],stdout=subprocess.PIPE)
for l in s.stdout:
  s=l.split(',')
  mu_normal_suben=float(s[0])   # mu
  s2_normal_suben=float(s[1])   # sigma^2

#
# Calcula array AP
#
AP={}
for p in PARADAS:
  remanente=0
  for seg in range (1,TS +1):
    # Factor para ajustar lambda de llegada de personas
    # -------------------------------------------------
    if seg <= t0:
      factor=p_ini
    elif seg <= t1:
      factor=p_ini+(1-p_ini)*(float(seg)-t0)/float(t1-t0)
    elif seg <= t2:
      factor=float(1)
    elif seg <= t3:
      factor=1-(1-p_ini)*float(seg-t2)/float(t3-t2)
    else:
      factor=p_ini

    factor=0.857

    va=stats.expon.rvs(scale=LAMBDAS_PARADAS[p]*factor)
    llegan,r=divmod(va+remanente,1)
    remanente=va+remanente-llegan
    AP[p,seg]=llegan

#
# Estado inicial
#

PP={}
TANT={}
TULT={}
DELTA={}
TPANT={}
TPULT={}
DELTAP={}
PROXIMO={}
LLEGARON={}
PARO_VECES={}
GENTE={}
PARADA_ESPERADA={}
PARO_ULTIMA={}
EMPEZO_RECORRIDO={}

for p in PARADAS:
  PP[p]=0
  ##PP[p]=int(round(stats.norm.rvs()*math.sqrt(S2[p])+MU[p],0))
  ##if PP[p] < 0:
    ##PP[p]=0
  ##if PP[p] > MAX[p]:
    ##PP[p]=MAX[p]

for l in LINEAS:
    va=stats.expon.rvs(scale=LAMBDAS_LINEAS[l])
    PROXIMO[l]=int(va)
    DELTA[l]=[]
    DELTAP[l]=[]
    LLEGARON[l]=0

try:
  primer_cuadra=belgrano+"#1"
  ultima_cuadra=belgrano+"#7"
  total_colectivos=0
  total_gente=0
  total_arribo_gente=0
  total_arribo_gente_sin_restricciones=0
  paradas_salteadas=0
  terminaron_recorrido=0
  tiempo_en_hacer_recorrido=0
  llegaron_a_primer_parada=0
  f={}
  for p in PARADAS:
    f[p]=open("personas_parada"+str(p)+".txt","w")

  tr=open("tiempo_recorrido.txt","w")

  #
  # Ciclo principal
  #
  for seg in range (1,TS +1):


    # Transcurre 1 segundo en la simulación
    # -------------------------------------
    traci.simulationStep()

    # Arribo de personas
    # ------------------
    for p in PARADAS:
      PPA=PP[p]

      PP[p]+=AP[p,seg]
      #print int(AP[p,seg]),
      if PP[p] < 0:
        PP[p]=0
      ####if PP[p] > MAX[p]:
        ####print "parada "+str(p)+" saturada!, maxima cantidad observada="+str(MAX[p])
        ####PP[p]=MAX[p]
    
      total_arribo_gente+=PP[p]-PPA
      total_arribo_gente_sin_restricciones+=AP[p,seg]

    # Ve si hay que inyectar un nuevo colectivo
    # -----------------------------------------
    for l in LINEAS:
  
      # Partida de un colectivo
      # -----------------------
      if seg==PROXIMO[l]:
        LLEGARON[l]+=1
        # 1) inyecta colectivo
        print "seg="+str(seg)+" linea="+str(l)
        vid=str(l)+"."+str(seg)
        rid="linea_"+str(l)
        PARO_VECES[vid]=0
        # Setea ocupación inicial
        ocupacion=int(stats.uniform.rvs()*100)+1
        tope=0
        for i in range(0,5):
          if OCUPACION[l][i]>0:
            tope+=OCUPACION[l][i]
            if ocupacion<=tope:
              ocupacion_inicial=i
          
        if ocupacion_inicial==0:
          GENTE[vid]=int(stats.uniform.rvs()*6)      # [0,5]
        elif ocupacion_inicial==1:
          GENTE[vid]=int(stats.uniform.rvs()*20)+6   # [6,20]
        elif ocupacion_inicial==2:
          GENTE[vid]=int(stats.uniform.rvs()*15)+26  # [26,40]
        elif ocupacion_inicial==3:
          GENTE[vid]=int(stats.uniform.rvs()*24)+41  # [41,64]
        else:
          GENTE[vid]=65

        print "Colectivo="+vid+" ocupacion inicial="+str(ocupacion_inicial)+" #personas="+str(GENTE[vid])

        PARADA_ESPERADA[vid]=0
        PARO_ULTIMA[vid]=""
        traci.vehicle.add(vehID=vid, routeID=rid, typeID="colectivo")
        total_colectivos+=1
        # 2) calcula el próximo
        va=stats.expon.rvs(scale=LAMBDAS_LINEAS[l])
        PROXIMO[l]=int(va)+seg
        # 3) cálculos para determinar factor de contracción
        if l not in TANT:
          TANT[l]=seg
        else:
          DELTA[l].append(seg-TANT[l])
          TANT[l]=seg
  
    # Procesamiento de vehiculos
    # --------------------------
    for v in traci.vehicle.getIDList():
      l=int(v.split(".")[0])
      seg_partida=int(v.split(".")[1])
      cuadra=traci.vehicle.getRoadID(v)
      carril=traci.vehicle.getLaneIndex(v)
      tipo=traci.vehicle.getTypeID(v)
      velocidad=traci.vehicle.getSpeed(v)
      posicion=traci.vehicle.getLanePosition(v)

      # Llegada de colectivos a parada
      # ------------------------------
      if traci.vehicle.isAtBusStop(v):
        if PARO_ULTIMA[v]!=cuadra:
          
          PARO_ULTIMA[v]=cuadra

          for i in range (0,len(PARADAS_LINEA[l])):
            j=PARADAS_LINEA[l][i]
             
            if CUADRA_PARADA[j]==cuadra:
              p=j
              break

          if i!=PARADA_ESPERADA[v]:
            print "vehiculo "+v+" se salteó "+str(i-PARADA_ESPERADA[v])+" parada/s"
            paradas_salteadas+=i-PARADA_ESPERADA[v]

          PARADA_ESPERADA[v]=i+1

          ps="p%02d" % p
          PARO_VECES[v]=PARO_VECES[v]+1
      
          if (p,l) not in TULT: # Es la primer llegada de la linea a la parada
            TULT[p,l]=0
      
          # tt significa tiempo transcurrido
          tt=seg-TULT[p,l]
      
          suben=round(stats.expon.rvs(scale=LAMBDAS_PARADAS_LINEAS[p,l]*tt),0)
          suben_normal=round(stats.norm.rvs()*math.sqrt(s2_normal_suben)+mu_normal_suben,0)

          if suben_normal<0:
            suben_normal=round(mu_normal_suben,0)

          ##if suben > suben_normal:
            ##suben=round(0.25*suben+0.75*suben_normal,0)

          if suben > 75-GENTE[v]:
            suben=75-GENTE[v]

          if suben>PP[p]:
            suben=PP[p]
          
          GENTE[v]+=suben

          total_gente+=suben

          ##tdet=round((suben-5)*(stats.norm.rvs()*math.sqrt(SIGMA2_TIEMPO_SUBIR)+MU_TIEMPO_SUBIR),0)
          ##tdet=(14.0/50)*((suben*(suben+1)) / 2)
          ##tdet=(0.6)*((suben*(suben+1)) / 2)
          tdet=30
          if tdet<1:
            tdet=1

          print "seg="+str(seg)+" vehiculo "+v+" en su detención nro "+str(PARO_VECES[v])+", la parada es la "+ps+" tdet="+str(tdet)+" suben="+str(suben)
      
          # Cálculos para determinar factor de contracción
          if p==PRIMER_PARADA[l]:
            if l not in TPANT:
              TPANT[l]=seg
            else:
              DELTAP[l].append(seg-TPANT[l])
              TPANT[l]=seg
      
          # Establecer detención
          traci.vehicle.setBusStop(v,ps,tdet*1000)
      
          PP[p]-=suben

      # Verificar si empezaron o terminaron el recorrido
      # ------------------------------------------------
      if cuadra==primer_cuadra:
        EMPEZO_RECORRIDO[v]=1

      if cuadra==ultima_cuadra:
        traci.vehicle.remove(v)
        terminaron_recorrido+=1
        tiempo_en_hacer_recorrido+=seg-seg_partida
        print "seg="+str(seg)+" el vehiculo "+v+" llegó al final del recorrido, demoró "+str(seg-seg_partida)+" segundos."
        tr.write(str(seg)+" "+str(seg-seg_partida)+"\n")


    # Para grafico de PP
    # ------------------
    for p in PARADAS:
      f[p].write(str(seg)+" "+str(int(PP[p]))+"\n")

except traci.FatalTraCIError:
    print ""

for p in PARADAS:
    f[p].close()

tr.close()

print
print "FIN SIMULACION!"
print
for v in GENTE:
  marca=""
  if GENTE[v]>75:
    marca="*** "
  print marca+"vehiculo="+v+" cantidad de personas="+str(GENTE[v])
print
print "TOTALES:"
print
print "cantidad total de colectivos que ingresan=",
print total_colectivos
print "cantidad total de personas que suben a algún colectivo=",
print total_gente
print "cantidad total de personas que arriba a paradas=",
print total_arribo_gente
print "cantidad total de personas que arriba a paradas (sin restricciones)=",
print total_arribo_gente_sin_restricciones
print "vehiculos que empezaron el recorrido=",
print len(EMPEZO_RECORRIDO)
print "vehiculos que terminaron el recorrido=",
print terminaron_recorrido
print "tiempo promedio en terminar el recorrido=",
print tiempo_en_hacer_recorrido/terminaron_recorrido
print "paradas salteadas=",
print paradas_salteadas
print "arribo de colectivos=",
print LLEGARON

traci.close()
