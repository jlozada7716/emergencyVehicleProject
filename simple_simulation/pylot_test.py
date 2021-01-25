# -*- coding: utf-8 -*-
"""
Created on Fri Feb 15 15:59:06 2019

@author: hchintakunta
"""

import matplotlib.pyplot as plt 
import time 


plt.figure()
plt.ion()

for i in range(5):
    plt.plot(i,2,'ro')
    plt.axis([0,5,0,5])
    plt.draw()
    time.sleep(1)
    
    
