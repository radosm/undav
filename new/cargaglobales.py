#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
@file    cargaglobales.py
@author  Martin Rados
@date    2017-07-22

Variables globales para Simulación Avellaneda
"""
import os,sys,subprocess,math
import scipy.stats as stats

#
# Tiempo de simulación (en segundos)
#
t1=1500.0
t2=2250.0
t3=3000.0
t4=4500.0
TS=4500
a=1.5
b=(t4*(2-a))/(t3-t1)

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
belgrano="-9468"
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
    if seg <= t1:
      factor=(a/t1)*seg
    elif seg <= t2:
      factor=(a*(seg-t2))/(t1-t2)+(b*(seg-t1))/(t2-t1)
    elif seg <= t3:
      factor=(b*(seg-t3))/(t2-t3)+(a*(seg-t2))/(t3-t2)
    else:
      factor=(a*(seg-t4))/(t3-t4)

    factor=factor*(3000.0/3400)

    va=stats.expon.rvs(scale=LAMBDAS_PARADAS[p]*factor)
    llegan,r=divmod(va+remanente,1)
    remanente=va+remanente-llegan
    AP[p,seg]=llegan
