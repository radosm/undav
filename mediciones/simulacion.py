#!/usr/bin/env python
# -*- coding: utf8 -*-

import os, sys, subprocess
from time import sleep
import scipy.stats as stats

#
# Tiempo de simulacion (en segundos)
#
TS=50

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
# Lee para cada parada cuál es el lambda de arribo de personas
#
LAMBDAS_PARADAS={}
f=open("lambdas_paradas.txt","r")
for l in f:
  s=l.split(',')
  p=int(s[0])   # parada
  l=float(s[1]) # lambda
  LAMBDAS_PARADAS[p]=l
f.close()
  
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

for seg in range (1,TS):
  a=0
