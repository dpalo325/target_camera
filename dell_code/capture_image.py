import cv2,imutils
import numpy as np
import TIS
import time, sys, os
import sys
from time import gmtime, strftime
import glob
import paramiko
from scp import SCPClient


##------------------------MAIN FUNCTION TO CAPTURE IMAGES----------------
def capture_image(w,h,frame_rate,exposure,gain):
   check = True
##-- sets up the camera using values from the function call 17710265 24710376"
   Tis = TIS.TIS("17710265", w, h, frame_rate, False)
   Tis.Set_Property("Gain Auto", False)
   Tis.Set_Property("Exposure Auto", False)
   Tis.Set_Property("Exposure", exposure)
   Tis.Set_Property("Gain", gain)

##-- starts the process to capture an image
   Tis.Start_pipeline()  # Start the pipeline so the camera streams

   kernel = np.ones((5, 5), np.uint8)  # Create a Kernel for OpenCV erode function

   if Tis.Snap_image(3) is True:  # Snap an image with one second timeout
      image = Tis.Get_image()  # Get the image. It is a numpy array
      image = imutils.rotate(image, 180)
      time = strftime("%m%d%H%M%S", gmtime())
      filename = 'UCI'+time+'.jpg'
      print("", filename,":",sep="")
      cv2.imwrite('images/UCI'+time+'.jpg',image) # Saves the captured image
      check = True
                
   else:
      #print(':') # Reads out if image is not captured
      check = False # check to ensure that file is not sent if no image captured
      filename = "" 
      # Stop the pipeline and clean up
   Tis.Stop_pipeline()
   cv2.destroyAllWindows()
   return check, filename

def scp_image(latest_file):

   ssh = paramiko.SSHClient()
   ssh.load_system_host_keys()
   ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
   ssh.set_missing_host_key_policy(paramiko.WarningPolicy)
   ssh.connect('megon01.psi.ch', port = 22, username = 'meg', password ='Mu2e+gamma!')

##-- initialize the SSH connection
   stfp = ssh.open_sftp()
   t = paramiko.Transport(('megon01.psi.ch',22))
   t.connect(username='meg',password = 'Mu2e+gamma!')
   sftp = paramiko.SFTPClient.from_transport(t)


	#Compress an image and send it to the website for easier loading
	#img = cv2.imread(latest_file, cv2.IMREAD_GRAYSCALE)      #---read the image
	#img = imutils.rotate(img, 180)
	#cv2.imwrite('compressed.jpeg',img)
	#cv2.imwrite(latest_file, img)

	# cv2.imwrite('compressed.jpeg', img, [int(cv2.IMWRITE_JPEG_QUALITY), 20])
	#print('sending...')
   sftp.put('images/'+latest_file, '/home/meg/online/slowcontrol/tgtcam/images/'+latest_file, confirm=True)
   sftp.put('images/'+latest_file, '/home/meg/online/web/mhttpd/LatestTargetImage.jpg', confirm=True)

   sftp.close()
   ssh.close()




#169.234.13.151

if __name__ == '__main__':
   w = int(sys.argv[1]) 
   h = int(sys.argv[2])
   frame_rate = int(sys.argv[3])
   exposure = int(sys.argv[4]) 
   gain = int(sys.argv[5]) 
   check, filename = capture_image(w,h,frame_rate,exposure,gain)
   if check == True:
      scp_image(filename)
   if check == False:
      check, filename = capture_image(w,h,frame_rate,exposure,gain)
      if check == True:
         scp_image(filename)
      if check == False:
         print(":")


