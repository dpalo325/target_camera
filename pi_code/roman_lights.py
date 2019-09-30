#!/usr/bin/python
import sys
import os
from sys import stdin
import datetime
import numpy as np
import time

#import RPi.GPIO as GPIO

#def UtcNow():
#    now = datetime.utcnow()     
#    now_seconds = now
#    print now
#    duration = (now - datetime(2018, 1, 1))
#    duration_seconds = duration
#    print duration
#    return(now_seconds,duration_seconds)

def grab_name(num):
    if num == 0:
        return 'PETER'
    elif num == 1:
        return 'UCI'
    elif num == 2:
        return 'ROME'
    else:
        return ''


def lights(light, curr_on_time_sec, intensity):
# light is the light number: 1 for UCI, 2 for Rome
# ontime is the requestd on time in seconds limited
# intensity is the intensity on a scale of 1-10

# check that the limits on intensity, and ontime are respected
    #print ("")
    #print ("")
    #print ("")
    #print ("")
    #print ("-----------------------starting the lights script-------------------------------")
    print ("light =", light)
    print ("ontime =", ontime)
    print ("intensity =", intensity)

    intensity_limit = 10
    ontime_limit = 10

    #print (intensity, intensity_limit) 
    #print (ontime, ontime_limit)

    if (intensity > intensity_limit):
        print ("intensity is limited to maximum value =", intensity_limit)
    if (ontime > ontime_limit):
        print ("light on-time is limited to maximum ", ontime_limit, "seconds")
    if (ontime > ontime_limit or intensity > intensity_limit):
        exit()
        print ("failed to exit")

# FOLLOWING JUST TO SETUP THE ARRAY
    if 'camera_data.csv' not in os.listdir():
        camera_data = np.array([[0,0,0,0,0,3],[0,0,0,0,0,3]])
        np.savetxt('camera_data.csv', camera_data, delimiter=',')

    curr_on_time_sec = ontime
    wait = 0

# read the camera data file and increase the number of rows of 3 by 1
    #print ("read the existing data from file")
    camera_data = np.genfromtxt('camera_data.csv',delimiter=',')

    length = len(camera_data)
    i=0
    for i in range (0,length):
        i0 = int(camera_data[i,0])
        i1 = int(camera_data[i,1])
        i2 = int(camera_data[i,2])
        i3 = int(camera_data[i,3])
        i4 = int(camera_data[i,4])
        i5 = grab_name(int(camera_data[i,5]))
        #print ('{0:4d} {1:10d} {2:10d} {3:4d} {4:4d}'.format(i0,i1,i2,i3,i4),i5)
        i +=1
    camera_data.resize(length+1,6) 


# get the time in seconds since the beginning of the year
    t0                = datetime.datetime(2018,1,1)
    now               = datetime.datetime.now()
    dt = now - t0
    time_now_sec      = dt.days*24*3600 + dt.seconds

# check the recent history of the light
# 1. only allow the light to come on if the previous lit period corresponds to 
#    a duty factor since the beginning of the previous lit perid is less than df_s_max 
# 2.
# some time up to look_back_time before now, don't turn the light on 
    df_s_max = 0.20            # maximum recent duty factor to allow light on 
    df_l_max = 0.05            # maximum recent duty factor to allow light on
    lookback_time_sec = 3600   # time to lookback in seconds
    short_lookback_time_sec = 120
    wait_s_time_sec = 0
    wait_l_time_sec = 0

    index =            length-1                 # look at last on period
    prev_st_time_sec = camera_data[index,1]     # start time of last on period
    prev_on_time_sec = camera_data[index,0]     # on time of last on period
    prev_user = camera_data[index,5]

    allow_light_on = 1  # default is allow, modify below
    short_lookback_time = time_now_sec - short_lookback_time_sec
    #print("short look back time", short_lookback_time)
    #print ("")
    #print ("current on time", curr_on_time_sec)
    #print ("previous on time", prev_on_time_sec)
    #print ("time now", time_now_sec)
    #print ("prev start time", prev_st_time_sec)
    print ("current user", grab_name(2))

#  don't turn on light if light still on from last period
    #print ("")
    #print ("check if light is still on/disabled")
    if prev_user == 0:
        if (prev_st_time_sec + prev_on_time_sec > time_now_sec):
            allow_light_on = 0
            wait_vs_time = prev_st_time_sec + prev_on_time_sec - time_now_sec
            wait = wait_vs_time
            print ("light still on/disabled, need to wait ", wait_vs_time, " seconds")
            
    elif(prev_st_time_sec + prev_on_time_sec > time_now_sec):
        allow_light_on = 0
        wait_vs_time = prev_st_time_sec + prev_on_time_sec - time_now_sec + prev_on_time_sec/df_s_max
        wait = wait_vs_time
        print ("light still on/disabled, need to wait ", wait_vs_time, " seconds")
    else:
        print ("light NOT disabled because it is still on")
        a = 1
    #  don't turn on light if df since beginning of last on period is not too big unless last on time was short
        #print ("")
        #print ("check if light on for too long and too recently last time on")

    #    don't check short-time duty factor if last user disabled light
    if prev_user !=0:
        short_light_on_time = 0
        for i in range(len(camera_data)):
            if camera_data[i, 1] > short_lookback_time:
                short_light_on_time += camera_data[i, 0]
        df = (short_light_on_time / short_lookback_time_sec) # duty factor after time_on
        if((df > df_s_max) and (prev_on_time_sec > ontime_limit/2.)):
            allow_light_on = 0
            print ("light disabled due to short-time duty factor", df)
            wait_s_time_sec = prev_on_time_sec/df_s_max + (prev_st_time_sec - time_now_sec)
            #print ("need to wait ", wait_s_time_sec, " seconds")
        else:
            print ("light NOT disabled due to short-time duty factor", df)
            a = 1
    #------------------------------here the light satisfies duty factor, can turn on----------------
    if (allow_light_on == 1):
        now        = datetime.datetime.now()
        dt         = now - t0
        start_time = dt.days*24*3600 + dt.seconds
        
        #print ("light duty factor OK at ", now, " for ", curr_on_time_sec, " seconds")


        camera_data[length,0] = curr_on_time_sec                     # write total time on
        camera_data[length,1] = start_time                           # wr1te time light goes on
        camera_data[length,2] = curr_on_time_sec+start_time          # write time light goes off
        camera_data[length,3] = light                                # write which light is on
        camera_data[length,4] = intensity                            # write intensity
        camera_data[length,5] = 2
        
        np.savetxt('camera_data.csv', camera_data, delimiter=',')

#----------here is the call to the light with delay ----------------------
#
#   RPi IP = 169.234.35.85
# scp filepath pi@169.234.35.85:~/Desktop
# 
#     
        RPi = True # check that we are running on the RPi
        freq = 100       # chopping frequency on LED
        pinUCI = 12      # RPi pin for UCI camera
        pinRome = 12     # RPi pin for UCI camera
        import time 
        dutycycle = intensity*10.
        
        if (RPi):
            import RPi.GPIO as GPIO
            GPIO.setwarnings(False)
            GPIO.setmode(GPIO.BOARD)
            GPIO.setup(12,GPIO.OUT)
            
        
        if(light == 2):
            
            if (RPi):
                print ("LED ", light, " turned on")
                camera_led = GPIO.PWM(pinRome,freq)
                camera_led.start(dutycycle)                    
                time.sleep(curr_on_time_sec)
            if (RPi):
                camera_led.stop()
                GPIO.cleanup()
                print ("LED ", light, " turned off")
#---------here is the end of call to the light with delay ----------------

        now     = datetime.datetime.now()
        dt      = (now-t0)
        stop_time = dt.days*24*3600 + dt.seconds 
        #print ("stop time since 1/1/2018  =", stop_time)
        
        on_time = stop_time - start_time
        #print ("most recent on time       =", on_time)


        i=0
        for i in range (0,length+1):
            i0 = int(camera_data[i,0])
            i1 = int(camera_data[i,1])
            i2 = int(camera_data[i,2])
            i3 = int(camera_data[i,3])
            i4 = int(camera_data[i,4])
            i5 = grab_name(int(camera_data[i,5]))
            #print ('{0:4d} {1:10d} {2:10d} {3:4d} {4:4d}'.format(i0,i1,i2,i3,i4),i5)
            i +=1

#-----------------------end lights.py-------------------------------------


#-------------------here is the main program------------------------------
if __name__ == "__main__":
    light        = 2
    ontime       = int(sys.argv[1])
    intensity    = int(sys.argv[2])
    '''
    DELL_username = 'meg'
    DELL_password = 'Mu2e+gamma!'
    DELL_hostname = 'megon'
    
    
    DELLssh = paramiko.SSHClient()
    DELLssh.load_system_host_keys()
    DELLssh.set_missing_host_key_policy(paramiko.WarningPolicy)
    DELLssh.connect(DELL_hostname,username=DELL_username,password = DELL_password)
    print('Connected to Dell')
    path = '"Equipment/Target_Camera/Variables/HotPixb[0]\"'
    odbedit_cmd ="'set \%s 1'"%(path)
    linux_cmd="'odbedit -c %s'"%(odbedit_cmd)
    dellanastdin, dellanastdout, dellanastderr = DELLssh.exec_command(linux_cmd)
    '''
    lights(light, ontime, intensity)
    '''
    odbedit_cmd ="'set \%s 0'"%(path)
    linux_cmd="'odbedit -c %s'"%(odbedit_cmd)
    dellanastdin, dellanastdout, dellanastderr = DELLssh.exec_command(linux_cmd)
    '''







