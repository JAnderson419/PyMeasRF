# -*- coding: utf-8 -*-
"""
Created on Mon Apr 23 10:46:34 2018

@author: Jackson Anderson
"""
# Unit test for checking that smu voltages are interpreted 
# correctly in pnaSMU.measure() when input in various formats


import numpy as np

def test(v): 
    currentV = [None]       
    def setVoltageLoop(v,l = 1):
        
        if l >= 1:
            for i in v:
                print('{}'.format(i))
                currentV[0] = i
                setVoltageLoop(v,l-1)
        else:
          print('Setting SMU voltages. ',end='')
          for i,v in enumerate(currentV):
            print('_{}V'.format(str(v).replace('.','_')))
            
    if v.all() == None:
        print("No voltage defined.")
    else:
       setVoltageLoop(v) 

v = np.asarray(None)
test(v)
print('None test complete')
v = np.asarray([])
test(v)
print('Empty list test complete')
v = np.asarray([0,1,2])
test(v)
print('List test complete')
v = np.asarray(np.linspace(0,2,3))
test(v)
print('Ndarray test complete')
