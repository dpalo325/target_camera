#!/usr/bin/python
import sys
import os
from sys import stdin
import datetime
import numpy as np
import time
import paramiko

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
    #----------here is the call to the light with delay ----------------------
#
#   RPi IP = 169.234.35.85
# scp filepath pi@169.234.35.85:~/Desktop
#       
        t0 = datetime.datetime(2018,1,1)
        now               = datetime.datetime.now()
        dt = now - t0
        time_now_sec      = dt.days*24*3600 + dt.seconds

        start_time = dt.days*24*3600 + dt.seconds 
        
        freq = 100       # chopping frequency on LED
        if light == 1:
            pin = 12      # RPi pin for LED1
            pin2 = 0
        elif light == 2:
            pin = 16     # RPi pin for LED2
            pin2 =0
        elif light == 3:
            pin = 12
            pin2 = 16
        import time 
        dutycycle = intensity*10.
        
        import RPi.GPIO as GPIO
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(pin,GPIO.OUT)

        print ("LED ", light, " turned on")
        camera_led = GPIO.PWM(pin,freq)
        camera_led.start(dutycycle)
        if (pin2 != 0):
            GPIO.setup(pin2,GPIO.OUT)
            camera_led2 = GPIO.PWM(pin2,freq)
            camera_led2.start(dutycycle)
        time.sleep(curr_on_time_sec)
        image_list = []
        '''
        for i in range(number_photos):
            dellstdin, dellstdout, dellstderr = DELLssh.exec_command("call capture_images.bat")
            image_name = dellstdout.read()
            image_name = str(image_name)
            index = image_name.rfind('UCI')
            if index == -1:
                print('Failed to capture image')
                continue
            image_name = image_name[index:index+13]
            print('image captured:',image_name)
            image_list.append(image_name)
        '''
        camera_led.stop()
        GPIO.cleanup()
       # print ("LED ", light, " turned off")
#---------here is the end of call to the light with delay ----------------

        camera_data = np.genfromtxt('camera_data.csv',delimiter=',')
        length = len(camera_data)

        now     = datetime.datetime.now()
        dt      = (now-t0)
        stop_time = dt.days*24*3600 + dt.seconds 
        #print ("stop time since 1/1/2018  =", stop_time)
        
        on_time = stop_time - start_time
        #print ("most recent on time       =", on_time)


        i=0
        for i in range (0,length):
            i0 = int(camera_data[i,0])
            i1 = int(camera_data[i,1])
            i2 = int(camera_data[i,2])
            i3 = int(camera_data[i,3])
            i4 = int(camera_data[i,4])
            i5 = grab_name(int(camera_data[i,5]))
           # print ('{0:4d} {1:10d} {2:10d} {3:4d} {4:4d}'.format(i0,i1,i2,i3,i4),i5)
            i +=1
        new_row = np.zeros(6)
        camera_data = np.vstack((camera_data, new_row))
        camera_data[length,0] =-( start_time-stop_time)                     # write total time on
        camera_data[length,1] = start_time                           # wr1te time light goes on
        camera_data[length,2] = stop_time          # write time light goes off
        camera_data[length,3] = light                                # write which light is on
        camera_data[length,4] = intensity                            # write intensity
        camera_data[length,5] = 1
        
        np.savetxt('camera_data.csv', camera_data, delimiter=',')
        return image_list

#-------------------here is the main program------------------------------
if __name__ == "__main__":
    light        = int(sys.argv[1])
    ontime       = int(sys.argv[2])
    intensity    = int(sys.argv[3])
    exposure     = int(sys.argv[4])
    number_photos= int(sys.argv[5])
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
    odbedit_cmd ="'set %s 1'"%(path)
    linux_cmd="odbedit -c %s"%(odbedit_cmd)
    print(linux_cmd)
    dellanastdin, dellanastdout, dellanastderr = DELLssh.exec_command(linux_cmd)

    #print('Failed to connect to Camera')
    
    image_list = lights(light, ontime, intensity, exposure, number_photos)
    odbedit_cmd ="'set %s 0'"%(path)
    linux_cmd="odbedit -c %s"%(odbedit_cmd)
    dellanastdin, dellanastdout, dellanastderr = DELLssh.exec_command(linux_cmd)

    #if len(image_list)>0:
    #    analysis(image_list)
    #else:
    #    print('Images not captured')
    #DELLssh.close()
    '''
    image_list = lights(light, ontime, intensity, exposure, number_photos)


