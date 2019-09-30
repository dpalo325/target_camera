#!/usr/bin/python
import sys
import os
from sys import stdin
import datetime
import numpy as np
import time
import paramiko

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


def lights(light, curr_on_time_sec, intensity, exposure, number_photos):
# light is the light number: 1 for UCI, 2 for Rome
# ontime is the requestd on time in seconds limited
# intensity is the intensity on a scale of 1-10

# check that the limits on intensity, and ontime are respected
##    print ("")
##    print ("")
##    print ("")
##    print ("")
##    print ("-----------------------starting the lights script-------------------------------")
##    print ("light =", light)
##    print ("ontime =", ontime)
##    print ("intensity =", intensity)

    intensity_limit = 10
    ontime_limit = 10

##    print (intensity, intensity_limit) 
##    print (ontime, ontime_limit)

##    if (intensity > intensity_limit):
##        print ("intensity is limited to maximum value =", intensity_limit)
##    if (ontime > ontime_limit):
##        print ("light on-time is limited to maximum ", ontime_limit, "seconds")
##    if (ontime > ontime_limit or intensity > intensity_limit):
##        exit()
##        print ("failed to exit")

# FOLLOWING JUST TO SETUP THE ARRAY
    if 'camera_data.csv' not in os.listdir():
        camera_data = np.array([[0,0,0,0,0,3],[0,0,0,0,0,3]])
        np.savetxt('camera_data.csv', camera_data, delimiter=',')

    curr_on_time_sec = ontime
    wait = 0

# read the camera data file and increase the number of rows of 3 by 1
##    print ("read the existing data from file")
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
##        print ('{0:4d} {1:10d} {2:10d} {3:4d} {4:4d}'.format(i0,i1,i2,i3,i4),i5)
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
    df_s_max = 0.10            # maximum recent duty factor to allow light on 
    df_l_max = 0.05            # maximum recent duty factor to allow light on
    lookback_time_sec = 3600   # time to lookback in seconds

    wait_s_time_sec = 0
    wait_l_time_sec = 0

    index =            length-1                 # look at last on period
    prev_st_time_sec = camera_data[index,1]     # start time of last on period
    prev_on_time_sec = camera_data[index,0]     # on time of last on period
    prev_user = camera_data[index,5]

    allow_light_on = 1  # default is allow, modify below

##    print ("")
##    print ("current on time", curr_on_time_sec)
##    print ("previous on time", prev_on_time_sec)
##    print ("time now", time_now_sec)
##    print ("prev start time", prev_st_time_sec)
##    print ("current user", grab_name(2))

#  don't turn on light if light still on from last period
##    print ("")
##    print ("check if light is still on/disabled")
    if prev_user == 0:
        if (prev_st_time_sec + prev_on_time_sec > time_now_sec):
            allow_light_on = 0
            wait_vs_time = prev_st_time_sec + prev_on_time_sec - time_now_sec
            wait = wait_vs_time
##            print ("light still on/disabled, need to wait ", wait_vs_time, " seconds")
            
    elif(prev_st_time_sec + prev_on_time_sec > time_now_sec):
        allow_light_on = 0
        wait_vs_time = prev_st_time_sec + prev_on_time_sec - time_now_sec + prev_on_time_sec/df_s_max
        wait = wait_vs_time
##        print ("light still on/disabled, need to wait ", wait_vs_time, " seconds")
    else:
##        print ("light NOT disabled because it is still on")

#  don't turn on light if df since beginning of last on period is not too big unless last on time was short 
##        print ("")
##        print ("check if light on for too long and too recently last time on")

#  don't check short-time duty factor if last user disabled light
        if prev_user !=0:
            df = (prev_on_time_sec) / (time_now_sec - prev_st_time_sec) # duty factor after time_on
            if((df > df_s_max) and (prev_on_time_sec > ontime_limit/2.)):
                allow_light_on = 0
                print ("light disabled due to short-time duty factor", df)
                wait_s_time_sec = prev_on_time_sec/df_s_max + (prev_st_time_sec - time_now_sec)
##                print ("need to wait ", wait_s_time_sec, " seconds")
##            else:
##                print ("light NOT disabled due to short-time duty factor", df)


# check the history of the light up to one hour previous
# only allow the light to come on if the duty factor over that period is less than some 
# value df_l_max, which is less than the short term duty factor limit (df_s_max)

##        print ("")
##        print ("check if light is on for too large a duty factor over longer recent period") 
        total_on_time_sec = 0      # sum this for up to pasttime before now
        df = 0                     # initialize the duty factor to 0

#--loop over the entries in the file containing the on time of the light
        index = length      # work backwards in the file of on-time for the light
        while 1:            
            index = index-1                        # sequentially get information from previous on times
            if camera_data[index,5] == 0:
                continue
            prev_st_time_sec = camera_data[index,1]     # start time of this period
            prev_on_time_sec = camera_data[index,0]     # on time of this period
##            print ("prev on     ", prev_on_time_sec)
##            print ("prev start  ", prev_st_time_sec)
##            print ("time now sec", time_now_sec)
            dt_sec = time_now_sec - prev_st_time_sec
##            print ("dt to prev start", dt_sec)
            if (dt_sec > lookback_time_sec):       # this on time more than some limit earlier 
##                print ("light NOT disabled due to long-time duty factor", df)
                break

            total_on_time_sec = total_on_time_sec + curr_on_time_sec     # increment the total on time
            dt_sec = time_now_sec - prev_st_time_sec                     # total time since first turnon
            df = total_on_time_sec/dt_sec
            if( df > df_l_max):
                allow_light_on = 0
                wait_l_time_sec = total_on_time_sec/df_l_max + (prev_st_time_sec - time_now_sec)
                print ("light disabled due to long-time duty factor", df)
##                print ("need to wait ", wait_l_time_sec, " seconds")
                break
        wait = wait_s_time_sec
    if(wait_l_time_sec > wait):
        wait = wait_l_time_sec
    print ("")
    print ("final wait time/time allowed to start:"+str(wait)+":"+str(int(time.time()+wait+468731))+":    :    :")
#--end loop over previous on periods to check long term duty factor   


#------------------------------here the light satisfies duty factor, can turn on----------------
    if(allow_light_on == 1):
        now        = datetime.datetime.now()
        dt         = now - t0
        start_time = dt.days*24*3600 + dt.seconds
        
##        print ("light duty factor OK at ", now, " for ", curr_on_time_sec, " seconds")


        camera_data[length,0] = curr_on_time_sec                     # write total time on
        camera_data[length,1] = start_time                           # wr1te time light goes on
        camera_data[length,2] = curr_on_time_sec+start_time          # write time light goes off
        camera_data[length,3] = light                                # write which light is on
        camera_data[length,4] = intensity                            # write intensity
        camera_data[length,5] = 1
        
        np.savetxt('camera_data.csv', camera_data, delimiter=',')


#-------------------here is the main program------------------------------
if __name__ == "__main__":
    light        = int(sys.argv[1])
    ontime       = int(sys.argv[2])
    intensity    = int(sys.argv[3])
    exposure     = int(sys.argv[4])
    number_photos= int(sys.argv[5])

    #print('Failed to connect to Camera')
        
    lights(light, ontime, intensity, exposure, number_photos)










