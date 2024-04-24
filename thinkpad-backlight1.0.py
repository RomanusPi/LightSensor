#!/usr/bin/env python

import glob
import os.path
import sys
import math
import time

# 0-50 000>  value of light sensor
#max_brtness 937

#min value of light sensor 
MIN_SENSOR = 10  
#min value of brightness 
MIN_BRTNESS = 15
#factor of backlight value multiply log function
FACTOR_1 =185  #150
# scaling factor of backlight log function
FACTOR = 0.084 #0.004415
# minimum change in sensor intensity before backlight intensity is changed
CHANGE = 105
# time in seconds between successive sensor reads
SLEEP_TIME = 0.4 #!

SAMPLE_MEASURED = 9 #How many previous mesured save

#os.system(' sudo -S ls') #start as a root when needed a parmision to file
sensor_dir = None
for f in glob.glob('/sys/bus/iio/devices/iio:device*/name'):
    if 'als' in open(f).read():
        sensor_dir = os.path.dirname(f)
       
if not sensor_dir:
    print('sensor not found')
    sys.exit(-1)

#read max brightens from a file 
max_brtness = int(open('/sys/class/backlight/intel_backlight/'
                      'max_brightness').read())
print ("max_bl",max_brtness)
#min_brtness = max(int(SCALE * math.exp(EXP * LS_LOW)), 0)
min_brtness  = MIN_BRTNESS
#max_brtness = min(int(SCALE * math.exp(EXP * LS_HIGH)), max_bl)
#max_brtness = max_bl

previous_brtness = 0 

collect_ls_val=[] #! #mesured sample
#take first samples from light sensor
with open(os.path.join(sensor_dir, 'in_intensity_both_raw')) as ls_file:
        ls_val = int(ls_file.readline().strip())
for _ in range( SAMPLE_MEASURED ):
    collect_ls_val.append(ls_val)

while 1:
    with open(os.path.join(sensor_dir, 'in_intensity_both_raw')) as ls_file:
        ls_val = int(ls_file.readline().strip())

    collect_ls_val.pop(0)
    collect_ls_val.append(ls_val)
    
    ls_val = max(ls_val,MIN_SENSOR)
    
    print("****ls_val",ls_val)

    av_ls_val = 0
    number_measured = 0
    min_measured = 0
    max_measured = 0
    for val in collect_ls_val:
        av_ls_val +=val
        number_measured = number_measured + 1
        min_measured =min(min_measured, number_measured)
        max_measured =max(max_measured, number_measured)
    av_ls_val = (av_ls_val - min_measured - max_measured) // (number_measured-2)     
    print("av_ls_val ", av_ls_val) 
    brtness_val = int(FACTOR_1 * math.log(FACTOR * av_ls_val/2)-300)
    print("counted brtness_val",brtness_val)
    brtness_val = max(brtness_val, min_brtness)
    brtness_val = min(brtness_val, max_brtness)
   

    if abs(brtness_val - previous_brtness) >= CHANGE: #change intensivity when bigger then  CHANGE
        with open('/sys/class/backlight/intel_backlight/brightness', 'w') as bl_file:
            bl_file.write('%s\n' % (brtness_val))
        #print (" min_brtness",min_brtness, " max_brtness",max_brtness,)      
        print ("ls_val", ls_val,"Changed britness_val", brtness_val)
    
        previous_brtness = brtness_val
   
    
    time.sleep(SLEEP_TIME)  
   


