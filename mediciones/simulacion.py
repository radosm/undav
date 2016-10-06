#!/usr/bin/env python
# -*- coding: utf8 -*-

import os, sys, subprocess, math
from time import sleep
import scipy.stats as stats

#
# Tiempo de simulacion (en segundos)
#
TS=7200

#
# Lee cuáles son las paradas existentes
#
PARADAS=[]
f=open("paradas.txt","r")
for l in f:
  p=int(l)
  PARADAS.append(p)
f.close()

#
# Lee cuáles son las líneas existentes
#
LINEAS=[]
f=open("lineas.txt","r")
for l in f:
  li=int(l)
  LINEAS.append(li)
f.close()

#
# Lee para cada parada cuál es el lambda de arribo de personas
#
LAMBDAS_PARADAS={}
s=subprocess.Popen([ 'bash','./calcula_lambdas_paradas' ], stdout=subprocess.PIPE)
for l in s.stdout:
  s=l.split(',')
  p=int(s[0])   # parada
  l=float(s[1]) # lambda
  LAMBDAS_PARADAS[p]=l
  
#
# Lee para cada linea cuál es el lambda de arribo a su primer parada
#
LAMBDAS_LINEAS={}
s=subprocess.Popen([ 'bash','./calcula_lambdas_lineas' ], stdout=subprocess.PIPE)
for l in s.stdout:
  s=l.split(',')
  li=int(s[0])   # linea
  la=float(s[1]) # lambda
  LAMBDAS_LINEAS[li]=la

#
# Lee para cada combinación de parada y linea el lambda de gente que sube
#
LAMBDAS_PARADAS_LINEAS={}
s=subprocess.Popen([ 'bash','./calcula_lambdas_paradas_lineas' ], stdout=subprocess.PIPE)
for l in s.stdout:
  s=l.split(',')
  pa=int(s[0])   # parada
  li=int(s[1])   # linea
  la=float(s[2]) # lambda
  LAMBDAS_PARADAS_LINEAS[pa,li]=la
  
#
# Lee lambda de tiempo que demora una persona en subir
#
s=subprocess.Popen( ['bash','./lambda_tiempo_subir'],stdout=subprocess.PIPE)
for l in s.stdout:
  LAMBDA_TIEMPO_SUBIR=float(l)

#
# Lee cuáles son las primeras paradas de cada linea
#
PRIMER_PARADA={}
s=subprocess.Popen( ['bash','./calcula_primeras_paradas'],stdout=subprocess.PIPE)
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
s=subprocess.Popen( ['bash','./calcula_s2'],stdout=subprocess.PIPE)
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
# Ciclo principal
#

PP={}
TANT={}
TULT={}
DELTA=[]
TPANT={}
TPULT={}
DELTAP=[]
PROXIMO={}

for p in PARADAS:
  PP[p]=int(round(stats.norm.rvs()*math.sqrt(S2[p])+MU[p],0))
  if PP[p] < 0:
    PP[p]=0
  if PP[p] > MAX[p]:
    PP[p]=MAX[p]

for l in LINEAS:
    va=stats.expon.rvs(scale=LAMBDAS_LINEAS[l])
    PROXIMO[l]=int(va)

for seg in range (1,TS):
  for p in PARADAS:
    PP[p]+=AP[p,seg]
  
  # Ve si hay que inyectar un nuevo colectivo
  # -----------------------------------------
  for l in LINEAS:

    # Partida de un colectivo
    # -----------------------
    if seg==PROXIMO[l]:
      # 1) inyecta colectivo
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
  if True==True:
    p=1  # OJO, acá hay que ver a qué parada llegó el colectivo
    l=17 # OJO, acá hay que ver a qué linea corresponde el colectivo

    if (p,l) not in TULT: # Es la primer llegada de la linea a la parada
      TULT[p,l]=0

    # tt significa tiempo transcurrido
    tt=seg-TULT[p,l]

    suben=round(stats.expon.rvs(scale=LAMBDAS_PARADAS_LINEAS[p,l]*tt),0)
    tdet=round(stats.expon.rvs(scale=LAMBDA_TIEMPO_SUBIR*tt),0)

    # Cálculos para determinar factor de contracción
    if p==PRIMER_PARADA[l]:
      if l not in TPANT:
        TPANT[l]=seg
      else:
        DELTAP.append(seg-TPANT[l])
        TPANT[l]=seg

    # Establecer detención

    if PP[p] < suben:
      PP[p]=0
    else:
      PP[p]-=suben
