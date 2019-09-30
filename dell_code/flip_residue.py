import cv2
import numpy as np
from numpy import genfromtxt
from matplotlib import pyplot as plt

import math
import glob
import os
import sys
from scipy.optimize import minimize
import paramiko
from scp import SCPClient

import matplotlib
lowlimx    = 699;
uplimx     = 3600;
lowlimy    = 300;
uplimy     = 2600;
lowlimarea = 50;
uplimarea  = 500;
lower_aspect = 0.7
upper_aspect = 1.29

#lowrefx  = [  71, 225, 378, 527, 671, 814, 953, 1091, 1223, 1350, 1476, 1600, 1721, 1838, 1954, 2066, 2178];
#highrefx = [  91, 245, 398, 547, 691, 834, 973, 1111, 1243, 1370, 1496, 1620, 1741, 1856, 1974, 2086, 2198];
#lowrefy  = [ -998, -846, -714, -467, -267, -84, 82, 252, 441]
#highrefy = [ -949, -743, -563, -396, -230, -50, 144, 335, 504]
lowrefx = [-5, 149, 300, 453, 599, 742, 883, 1022, 1154, 1280, 1406, 1530, 1651, 1769, 1886, 1998, 2111]
lowrefx = np.array(lowrefx)
highrefx = lowrefx + 10
lowrefy = [-1000, -772, -588, -404, -210, -49, 148, 318, 510]
highrefy = [-800, -681,-508, -329, -165, 4, 223, 390, 570] 
hotpixel_cnt = hotpixel_cnt1= hotpixel_cnt2= hotpixel_cnt3= hotpixel_cnt4= hotpixel_cnt5= hotpixel_cnt6= 0 #initializing hot pixel count
halflengthxpix = 1928    #--half x size of the image
halflengthypix =  1382    #--half y size of the image
pix_mm =1.67*(10**-3)  #conversion
cameraangle = 0.0819
image1 = sys.argv[1]
image2 = sys.argv[2]
threshold =int(sys.argv[3])
xf_x0 = 0
yf_y0 = 0
x0 = 0
xf = 0
yf = 0
y0= 0
zf_z0 = 0
zf= 0
z0 = 0

focal_length = float(sys.argv[4])



def dot_finder(image_name, image_number, threshold):
    #-------------------get first image------------------------------------------
    #latest_darkfield_image = max(glob.glob('*df.jpg'), key=os.path.getctime) # grabbing latest darkfield img
    global hotpixel_cnt, hotpixel_cnt1, hotpixel_cnt2, hotpixel_cnt3, hotpixel_cnt4, hotpixel_cnt5, hotpixel_cnt6
    latest_darkfield_image = 'images/UCIdark0826232801.jpg'
    darkfield = cv2.imread(latest_darkfield_image, cv2.IMREAD_GRAYSCALE) # inserting darkfield into 2d array 'darkfield'
    
    #---subtracting darkfield-------------------
    img= cv2.imread('images/%s'%(image1), 0)#, cv2.IMREAD_GRAYSCALE)    #reading in true image
    
    #backtorgb = cv2.cvtColor(img,cv2.COLOR_GRAY2RGB)
    '''
    for i in range(0, len(img)):
        for j in range(0, len(img[0])):
            if 50 >= int(darkfield[i, j]) > 10: hotpixel_cnt1= hotpixel_cnt1 + 1
            elif 100 >= int(darkfield[i, j]) > 50: hotpixel_cnt2= hotpixel_cnt2 + 1
            elif 150 >= int(darkfield[i, j]) > 100: hotpixel_cnt3= hotpixel_cnt3 + 1
            elif 200 >= int(darkfield[i, j]) > 150: hotpixel_cnt4= hotpixel_cnt4 + 1
            elif 250 >=int(darkfield[i, j]) > 200: hotpixel_cnt5= hotpixel_cnt5 + 1
            elif int(darkfield[i, j]) > 250: hotpixel_cnt6= hotpixel_cnt6 + 1
            
            
            if int(img[i, j]) - int(darkfield[i, j]) >0 :
                img[i, j] = int(img[i, j]) - int(darkfield[i, j])
            else:
                img[i, j] = 0
    cv2.imwrite('subtracted_%s.jpg'%(image_name), img)
    '''
    #src =  cv2.fastNlMeansDenoising(img,None,10,7,23)#---apply denoising filter
    #th,dst = cv2.threshold(src, 80,255,cv2.THRESH_BINARY)   #---set the black/white threshold if minimizer is used
    th,dst = cv2.threshold(img, threshold,255,cv2.THRESH_BINARY)   #---set the black/white threshold
    
    #----------------------find all contours------------------------------------------
    contours,hierarchy = cv2.findContours(dst, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    print(len(contours))
    #draw = cv2.drawContours(backtorgb,contours, -1, (0, 255, 0), 3) #draw contours onto the image
    #cv2.imwrite('02.png',draw) #write to file
    '''
    for i in range(len(contours)):
        if 50 < cv2.contourArea(contours[i]) < 300:
            cv2.drawContours(backtorgb,contours,i,(0,0,255)) #drawing contours but here resizing image and sent to screen
    imS = cv2.resize(backtorgb, (1500, 1000))
    cv2.imshow('draw contours',imS)
    cv2.waitKey(0)
    '''
    #---make empty x, y, a positions for all dots
    area_contour = np.zeros([len(contours), 1])    #--area of the countour
    x_contour = np.zeros([len(contours), 1])   #--x centroid of contour
    y_contour = np.zeros([len(contours), 1])   #--y centroid of contour
    z = np.empty([len(contours), 1])
    y = np.empty([len(contours), 1])
    h = np.empty([len(contours), 1])
    w = np.empty([len(contours), 1])
    aspect_ratio = np.empty([len(contours), 1])
    ##--loop over all the countours found in the image analysis  to fill area_contour, x_contour and x_contour
    for i in range(0, len(contours)):
        Mi = cv2.moments(contours[i])
        if Mi['m00'] != 0:
            x_contour[i]= Mi['m10']/Mi['m00']
            y_contour[i]= Mi['m01']/Mi['m00']
            area_contour[i] = cv2.contourArea(contours[i])
            z[i], y[i],w[i], h[i] = cv2.boundingRect(contours[i])
            aspect_ratio[i] = float(w[i])/h[i]

    vec_contour = np.hstack((x_contour, y_contour, area_contour, aspect_ratio)) #-- N-4 array instead of 4 N arrays
    
    #   -------------------do some selection on good dots in pic--------------------
    vec_contour = [column for column in vec_contour if (lowlimx <= column[0] <= uplimx)  and (lowlimy <= column[1] <= uplimy)  and (lowlimarea <= column[2] <= uplimarea)  and (lower_aspect <= column[3] <= upper_aspect) ] #remove vec_contour rows if outside limits
    
    #--save the contour vector for later use
    np.savetxt("vec_contour"+str(image_number)+".csv", vec_contour, delimiter=",")
    #--read the positions back in from the file we just wrote, issue unless saved as file and then read back
    vec_contour = genfromtxt('vec_contour'+str(image_number)+'.csv', delimiter=',')
    if (len(vec_contour) < 10 ):
        vec_contour = np.zeros((4, 10))
    #sorting
    print(len(vec_contour))
    idx = np.lexsort((vec_contour[:,0], vec_contour[:,0])) #lexsort sorts in terms of of x value
    vec_contour = vec_contour[idx]
    np.savetxt("vec_contour"+str(image_number)+".csv", vec_contour, delimiter=",")
    #resaving
    vec_contour = genfromtxt('vec_contour'+str(image_number)+'.csv', delimiter=',') #saved due to issue listed above
    #generating
    
    
    new_col = vec_contour.sum(1)[...,None] # None keeps (n, 1) shape
    new_col.shape
    sortedvec_contour = np.hstack((vec_contour, new_col, new_col, new_col)) #add three new columns
    #adding two index columns

    #define length of contour array
    contour_count, _= sortedvec_contour.shape
    
    #verifying dots are where they below, and assign standard x and y indices
    sortedvec_contour[0, 3] = -1
    #x indexes
    xreference = sortedvec_contour[0,0]
    xreference = 7.66E+02
    xreference = 7.75E+02
    #actually producing the index values
    for j in range(0, contour_count):
        xdata = sortedvec_contour[j,0]
        xdiff  = abs(xdata - xreference )
        sortedvec_contour[j,3] = -1
        for k in range(0,len(lowrefx)):
            if(lowrefx[k] < xdiff < highrefx[k]):
                sortedvec_contour[j,3] = k
                break
    sortedvec_contour[0, 4] = -1
    
    
    #--------ranges in y where we expect to find a dot------
    yreference = sortedvec_contour[0,1]
    yreference = 1.59E+03
    yreference =  1.55E+03
    #actually calculating y index
    for j in range(0, contour_count):
        ydata = sortedvec_contour[j,1];
        ydiff  = (ydata - yreference);
        sortedvec_contour[j,4] =-1;
        for k in range(0,len(lowrefy)):
            if ( lowrefy[k] < ydiff < highrefy[k] ):
                sortedvec_contour[j,4] = 8 - k;
                break;

    #sorting by column number and row number, sorting by x and then by y (first bunch have the same x)
    idm = np.lexsort((sortedvec_contour[:,3], sortedvec_contour[:,4]))
    sortedvec_contour = sortedvec_contour[idm]

    #--save the sorted data
    np.savetxt("sortedvec_contour"+str(image_name)+".csv", sortedvec_contour, delimiter=",")
    np.savetxt("sortedvec_contour%.0f.csv"%(threshold), sortedvec_contour, delimiter=",")
    counter = 0
    for i in range(len(sortedvec_contour)):
        if sortedvec_contour[i,3] > -0.5 and sortedvec_contour[i, 4] > -0.5:
            counter = counter + 1
    print("counter")
    print(counter)
    return counter#, hotpixel_cnt1, hotpixel_cnt2, hotpixel_cnt3, hotpixel_cnt4, hotpixel_cnt5, hotpixel_cnt6,


def two_photos(image1,image2):
    sortedvec_contour = genfromtxt('sortedvec_contour%s.csv'%(image1), delimiter=',') #get two sorted_veccontours aka the product of dot_finder
    sortedvec_contour2 = genfromtxt('sortedvec_contour%s.csv'%(image2), delimiter=',')
    contour_count = len(sortedvec_contour) #get lengths
    contour_count2 = len(sortedvec_contour2)
    #print(contour_count, contour_count2)
    
    contour_count_larger = max(contour_count,contour_count2) #get max
    twophotos = np.zeros([contour_count_larger, 9]); #make new array to be filled
    
    #halflengthxpix is length of photo in pixels in x, pix_mm is the conversion at the image plane from pix to mm
    
    
    # cobining sortedvec_contour1 and sortedvec_contour2 to make a single array that has eliminated all dots that don't exist in both photos
    for i in range(0,contour_count):
        for j in range(0,contour_count2):
            
            if (sortedvec_contour[i ,3] - sortedvec_contour2[j,3] == 0 and sortedvec_contour[i,4] - sortedvec_contour2[j ,4] == 0):
                twophotos[i, 0] = sortedvec_contour[i, 3]  # index to sort dots by x value
                twophotos[i, 1] = (sortedvec_contour[i, 0] - halflengthxpix)*pix_mm  # x value (centered) in mm for photo 1
                twophotos[i, 2] = (sortedvec_contour2[j, 0] - halflengthxpix)*pix_mm # x value (centered) in mm for photo 2
                twophotos[i, 3] = sortedvec_contour[i, 4] # index to sort dots by y value
                twophotos[i, 4] = (halflengthypix -  sortedvec_contour[i, 1])*pix_mm # y value (centered) in mm for photo 1
                twophotos[i, 5] = (halflengthypix -  sortedvec_contour2[j, 1])*pix_mm# y value (centered) in mm for photo 2
                twophotos[i, 6] = twophotos[i,2] - twophotos[i,1]
                twophotos[i, 7] = twophotos[i,5] - twophotos[i, 4]

    twophotos = [column for column in twophotos if( -0.1<column[0] <20) and  ( -0.1<column[3] <20) and (column[2] != 0) ]
    np.savetxt("twophotos.csv", twophotos, delimiter=",")
    print("twophotos length")
    print(len(twophotos))
    
    return len(twophotos)


def threeddots():
    #---------------------following is code using only photo1 to realign the target assuming camera is in corret position---------
    #                       later this code will be modified to find the camera coordinates and rotations
    #--get the minimization function

    #--finaldots.csv contains nominal x, y, z 3d positions (mm) (columns 0-2) as well as 2d image coordinates (3-4) in mm
    #   3d positions will be based on survey information later, then will use this to see where camera is actually found

    #--get the nominal dot locations from file (later will regnerate this from surveyor information and target geometry)
    #current columns 0-2 are camera coordinate system dots, 3-4 are index values for each dot, 5 is column of 0s (necessary for below),
    #6 and 7 are the MEG coordinate system dot locations, 3-4 are simply 6-7 rotated by 0.0819 rad
    #god_given2 = np.genfromtxt('god_given2.csv', delimiter=',')

    #threednominal = np.genfromtxt('newfinaldots.csv', delimiter=',')
    #threednominal = np.genfromtxt('final_dots428_1031143631.csv', delimiter=',')
    
    #threednominal = np.genfromtxt('5_23_avg_res.csv', delimiter=',') -final
    
    #threednominal = np.genfromtxt('5_23_avg_res_frame_pre_1029.csv', delimiter=',')

    #threednominal = np.genfromtxt('515_avg_res_1102.csv', delimiter=',')
    #threednominal = np.genfromtxt('522_avg_res1029.csv', delimiter=',')

    #threednominal = np.genfromtxt('519_avg_res11021.csv', delimiter=',')
    threednominal = np.genfromtxt('828_avg_res.csv', delimiter=',')                                                              

    twophotos = np.genfromtxt('twophotos.csv', delimiter=',')
    twophotoslength = len(twophotos)
    threednominallength = len(threednominal)
    rotthreednominal = np.zeros([threednominallength, 3])
    cameraangle = 0.0819
    xparam = 10
    yparam = 2.2
    zparam =  27
    '''
        for i in range (0, threednominallength):
        rotthreednominal[i, 0] = threednominal[i, 0]*np.cos(cameraangle) + threednominal[i, 2]*np.sin(cameraangle)
        rotthreednominal[i, 1] = threednominal[i, 1]
        rotthreednominal[i, 2]= threednominal[i, 2]*np.cos(cameraangle) -threednominal[i, 0]*np.sin(cameraangle)
        for i in range(0, threednominallength):
        threednominal[i, 0] = rotthreednominal[i, 0] + xparam
        threednominal[i, 1] = rotthreednominal[i, 1] + yparam
        threednominal[i, 2] = rotthreednominal[i, 2] + zparam
        '''
    #--here modify threednominal to include only dots found in both images
    threednominallength = len(threednominal)
    rot = [0, 0.02, 0.02] # three rotation angles

    #these values will be used to find the bowing
    for i in range(0, threednominallength):
        if threednominal[i,3] == 8 and threednominal[i,4] == 4:
            x0 = threednominal[i, 0]
            y0 = threednominal[i, 1]
            z0 = threednominal[i, 2]
        elif threednominal[i,3] == 16 and threednominal[i,4] == 4:
            xf = threednominal[i, 0]
            zf = threednominal[i, 2]
        elif threednominal[i,3] == 8 and threednominal[i,4] == 1:
            yf = threednominal[i, 1]
    megtargetangle = 1.3090

    cameratargetangle = 3.1415 - cameraangle - megtargetangle
    doubles_listj = []
    doubles_listi = []
    xf_x0 = xf - x0
    yf_y0 = yf - y0
    zf_z0 = zf - z0
    xf_x0 = (xf_x0**2 +zf_z0**2)**0.5
#print(len(god_given2))

    for i in range(0, twophotoslength):
        for j in range (0,threednominallength):
            if i ==0 and j ==0:
                oldtwophotosi = -1
                oldtwophotosj = -1
            if twophotos[i, 0] == threednominal[j, 3] and twophotos[i, 3] ==threednominal[j, 4]:
                threednominal[j, 5] = threednominal[j, 5] + 1
                twophotos[i, 8] = twophotos[i,8] + 1
                #god_given2[k, 9] = god_given2[k, 9] + 1
    
                if oldtwophotosi == twophotos[i, 0] and oldtwophotosj == twophotos[i, 3]:
                    #god_given2[k, 9] = god_given2[k, 9] + 5
                    threednominal[j, 5] = threednominal[j, 5] + 5
                    doubles_listi.append(twophotos[i, 0])
                    doubles_listj.append(twophotos[i, 3])
                oldtwophotosi = twophotos[i, 0]
                oldtwophotosj = twophotos[i, 3]
    #print(doubles_listi)
    #print(doubles_listj)
    for i in range(0, twophotoslength):
        for j in range(0, len(doubles_listi)):
            if doubles_listi[j] == twophotos[i, 0] and doubles_listj[j] == twophotos[i, 3]:
                twophotos[i, 8] = twophotos[i,8] + 5

    twophotos = [ column for column in twophotos if (4 > column[8] >0.5) ]
    np.savetxt("twophotos.csv", twophotos, delimiter=",")
    twophotos = np.genfromtxt('twophotos.csv', delimiter=',')

    threednominal = [ column for column in threednominal if (4 > column[5] >0.5) ]
    np.savetxt("this_3dnominal.csv", threednominal, delimiter=",")
    threednominal = np.genfromtxt("this_3dnominal.csv", delimiter=',')

    idg = np.lexsort((threednominal[:,3], threednominal[:,4]))
    threednominal = threednominal[idg]
    np.savetxt('this_3dnominal.csv', threednominal, delimiter=",")
    threednominal = np.genfromtxt("this_3dnominal.csv", delimiter=',')


    #print(len(threednominal),len(twophotos))
    return cameratargetangle, xf_x0, yf_y0, x0, y0

def angle_tests():

    threednominal = np.genfromtxt('3ddotsreal.csv', delimiter=',')
    a11 = np.cos(rot[0])*np.cos(rot[2])
    a12 = -np.cos(rot[1])*np.sin(rot[2]) + np.sin(rot[0])*np.sin(rot[1])*np.cos(rot[2])
    a13 = np.sin(rot[2])*np.sin(rot[1]) + np.cos(rot[2])*np.sin(rot[0])*np.cos(rot[1])
    a21 = np.cos(rot[0])*np.sin(rot[1])
    a22=  np.cos(rot[1])*np.cos(rot[2]) + np.sin(rot[0])*np.sin(rot[1])*np.sin(rot[2])
    a23 = -np.sin(rot[1])*np.cos(rot[2]) + np.cos(rot[1])*np.sin(rot[0])*np.sin(rot[2])
    a31 = -np.sin(rot[0])
    a32 = np.sin(rot[1])*np.cos(rot[0])
    a33 = np.cos(rot[1])*np.cos(rot[0])
    
    for i in range (0, threednominallength):
        threednominal[i, 0] = a11*threednominal[i, 0] + a12*threednominal[i, 1] + a13*threednominal[i, 2]
        threednominal[i, 1] = a21*threednominal[i, 0] + a22*threednominal[i, 1] + a23*threednominal[i, 2]
        threednominal[i, 2] = a31*threednominal[i, 0] + a32*threednominal[i, 1] + a33*threednominal[i, 2]
    
    
#produce bowing

    bow = 1
    #-----------fake a bowing-------------------------------------------
    for i in range(0, threednominallength):
        xbowing =  np.sin(cameratargetangle)*( bow*(threednominal[i, 0] - x0)**2 + ((xf_x0)*(threednominal[i, 1] - y0)*bow/(yf_y0))**2 + bow*(xf_x0**2))
        zbowing = np.cos(cameratargetangle)*( bow*(threednominal[i, 0] - x0)**2 + ((xf_x0)*(threednominal[i, 1] - y0)*bow/(yf_y0))**2 + bow*(xf_x0**2))
    
    for i in range(0, threednominallength):
        threednominal[i, 0] = threednominal[i, 0] + xbowing
        threednominal[i, 1] = threednominal[i, 1]
        threednominal[i, 2] = threednominal[i, 2] + zbowing



def intro_minimization(focal_length, xpic1, ypic1, nomx, nomy, nomz):
    #--p0 is initial value of param_vec, the array of the initial values of the fitting parameters
    p0 = np.array([50, 0, 0, 0], dtype = float)
    #------------------------here is the actual minimization -----------------------------------------------------------
    #  1: function minimized, 2:initial parameters, 3:arguments that aren't minimzed, 4:method
    #xnomtopix = lambda param_vec,nomx,nomz: focal_length*(nomx + param_vec[0])/( nomz + param_vec[2] - focal_length)
    #ynomtopix = lambda param_vec,nomy,nomz: focal_length*(nomy + param_vec[1])/( nomz + param_vec[2] - focal_length)
    xnomtopix = lambda param_vec,nomx,nomz: param_vec[0]*(nomx + param_vec[1])/( nomz + param_vec[3] - param_vec[0])
    ynomtopix = lambda param_vec,nomy,nomz: param_vec[0]*(nomy + param_vec[2])/( nomz + param_vec[3] - param_vec[0])
    
    twophotoslength = len(nomx)
    #print(len(nomx),len(xpic1))
    
    xchi = lambda param_vec:np.sum([ (xnomtopix(param_vec, nomx[i], nomz[i]) - xpic1[i])**2 for i in range(twophotoslength)])
    ychi = lambda param_vec:np.sum([ (ynomtopix(param_vec, nomy[i], nomz[i]) - ypic1[i])**2 for i in range(twophotoslength)])
    sigma = 0.000237 #mm at the image plane i.e. 0.4 pix
    N = twophotoslength
    sigma_squared = sigma*sigma
    totalchi = lambda param_vec:(xchi(param_vec) + ychi(param_vec))/sigma_squared
    
    #roughnom_pic1 = minimize(totalchi, p0, method='Nelder-Mead',options={'maxiter': 5000, 'fatol' : 1e-11})
    #print(roughnom_pic1.x)
    #print(totalchi(roughnom_pic1.x))
    #return np.array([-6.5252e-3,   2.7078e-3,  0.7784e-3, -2.0588098, .9774017,  -1.199684,  0.05], dtype = float) #initial parameters are the values of the first optimizer
    return np.array([0., 0., 0., 0., 0, 0, 0.], dtype = float) #initial parameters are the values of the first optimizer

    #return np.array([0,  0,  0,  5, 5, -40,  30], dtype = float) #initial parameters are the values of the first optimizer

def minimization(focal_length, xpic1, ypic1, nomx, nomy, nomz, p2, residuex, residuey, god_givenximgpln, god_givenyimgpln, cameratargetangle, xf_x0, yf_y0, x0, y0):
    threednominallength = len(nomx)
    #--verify that x and x1 are the same length   -- put an if here with a stop if it isn't right, with an error message  wm
    print("length going to min ", len(xpic1))
    #print(len(nomx))
    nomx = nomx - 0.152272
    nomy = nomy - 0.982569
    nomz = nomz - 1195.261017
    a11 =lambda param_vec :np.cos(param_vec[0])*np.cos(param_vec[2])
    a12 = lambda param_vec:-np.cos(param_vec[1])*np.sin(param_vec[2]) + np.sin(param_vec[0])*np.sin(param_vec[1])*np.cos(param_vec[2])
    a13 = lambda param_vec:np.sin(param_vec[2])*np.sin(param_vec[1]) + np.cos(param_vec[2])*np.sin(param_vec[0])*np.cos(param_vec[1])
    a21 = lambda param_vec:np.cos(param_vec[0])*np.sin(param_vec[2])
    a22 = lambda param_vec:np.cos(param_vec[1])*np.cos(param_vec[2]) + np.sin(param_vec[0])*np.sin(param_vec[1])*np.sin(param_vec[2])
    a23 = lambda param_vec:-np.sin(param_vec[1])*np.cos(param_vec[2]) + np.cos(param_vec[1])*np.sin(param_vec[0])*np.sin(param_vec[2])
    a31 = lambda param_vec:-np.sin(param_vec[0])
    a32 = lambda param_vec:np.sin(param_vec[1])*np.cos(param_vec[0])
    a33 = lambda param_vec:np.cos(param_vec[1])*np.cos(param_vec[0])
    bz = lambda param_vec, nomx, nomy, nomz:np.cos(cameratargetangle)*( param_vec[6]*(( (((nomx-x0)**2) +((nomz-z0)**2))**0.5)/(xf_x0))**2 + param_vec[6]*((nomy - y0)/(yf_y0))**2 - param_vec[6])
    bx = lambda param_vec, nomx, nomy, nomz:np.sin(cameratargetangle)*( param_vec[6]*(( (((nomx-x0)**2) +((nomz-z0)**2))**0.5)/(xf_x0))**2 + param_vec[6]*((nomy - y0)/(yf_y0))**2 - param_vec[6])
    #return a11,a12,a13,a21,a22,a23,a31,a32,a33,bz,bx
    #nomx_prime = lambda param_vec, nomx, nomy, nomz:nomx*a11(param_vec) + nomy*a12(param_vec) + nomz*a13(param_vec) + param_vec[3]*np.cos(1.225) + np.sin(1.225)*(0.0096)  + bx(param_vec, nomx, nomy, nomz) + 0.152272
    #nomy_prime = lambda param_vec, nomx, nomy, nomz:nomx*a21(param_vec) + nomy*a22(param_vec) + nomz*a23(param_vec) + param_vec[4] + 0.982569
    #nomz_prime = lambda param_vec, nomx, nomy, nomz:nomx*a31(param_vec) + nomy*a32(param_vec) + nomz*a33(param_vec) +  1.30369389e-02 + param_vec[3]*np.sin(1.225) - np.cos(1.225)*(0.0096) + bz(param_vec, nomx, nomy, nomz) +1195.261017
    nomx_prime = lambda param_vec, nomx, nomy, nomz:nomx*a11(param_vec) + nomy*a12(param_vec) + nomz*a13(param_vec) + param_vec[3] + bx(param_vec, nomx, nomy, nomz) + 0.152272
    nomy_prime = lambda param_vec, nomx, nomy, nomz:nomx*a21(param_vec) + nomy*a22(param_vec) + nomz*a23(param_vec) + param_vec[4] + 0.982569
    nomz_prime = lambda param_vec, nomx, nomy, nomz:nomx*a31(param_vec) + nomy*a32(param_vec) + nomz*a33(param_vec) +param_vec[5] + bz(param_vec, nomx, nomy, nomz) +1195.261017

    #xnomtopix2 = lambda param_vec, nomx, nomy, nomz: (param_vec[6]*nomx_prime(param_vec, nomx, nomy, nomz))/(nomz_prime(param_vec, nomx, nomy, nomz)-param_vec[6])
    #ynomtopix2 = lambda param_vec, nomx, nomy, nomz: (param_vec[6]*nomy_prime(param_vec, nomx, nomy, nomz))/(nomz_prime(param_vec, nomx, nomy, nomz)-param_vec[6])
    xnomtopix2 = lambda param_vec, nomx, nomy, nomz: (focal_length*nomx_prime(param_vec, nomx, nomy, nomz))/(nomz_prime(param_vec, nomx, nomy, nomz))
    ynomtopix2 = lambda param_vec, nomx, nomy, nomz: (focal_length*nomy_prime(param_vec, nomx, nomy, nomz))/(nomz_prime(param_vec, nomx, nomy, nomz))


    xchi2 = lambda param_vec: np.sum([ (xnomtopix2(param_vec, nomx[i], nomy[i], nomz[i]) - xpic1[i] - residuex[i])**2 for i in range(twophotoslength)])
    tchi = lambda param_vec: xchi(param_vec) + ychi(param_vec)
    ychi2 = lambda param_vec: np.sum([ (ynomtopix2(param_vec, nomx[i], nomy[i], nomz[i]) - ypic1[i] - residuey[i])**2 for i in range(twophotoslength)])
    sigma = 0.000167*1.2 #0.12 pix
    N = twophotoslength
    sigma_squared = sigma*sigma
    totalchi2 = lambda param_vec: (xchi2(param_vec) + ychi2(param_vec))/sigma_squared
    xchi = lambda param_vec: (xnomtopix2(param_vec, nomx, nomy, nomz) - xpic1 -residuex)**2/sigma_squared
    ychi = lambda param_vec: (ynomtopix2(param_vec, nomx, nomy, nomz) - ypic1 -residuey)**2/sigma_squared
    



    bounds = [(-0.02,-0.03,-0.1,-400, -400, -400,  51, 0), (0.03,0.03,0.1,400, 400,400,  53, 200)]
    bounds = np.array(bounds)
    bounds = bounds.T
    #------------------------here is the minimization -----------------------------------------------------------
    #  1: function minimized, 2:initial parameters, 3:arguments that aren't minimzed, 4:method
    #residueinfo2 = minimize(totalchi2, p2, method='L-BFGS-B',bounds =bounds,  options={'maxiter': 5000, 'ftol' : 1e-13})
    residueinfo2 = minimize(totalchi2, p2, method='Nelder-Mead',  options={'maxiter': 5000, 'ftol' : 1e-9})
    chi = totalchi2(residueinfo2.x)
    print(residueinfo2.x)
    print("chi %.4f and dof %.f"%( chi, N*2 - 7))
    import lmfit
    p = lmfit.Parameters()
    p.add_many( ('r1',residueinfo2.x[0]), ('r2', residueinfo2.x[1]), ('r3', residueinfo2.x[2]), ('x', residueinfo2.x[3]), ('y', residueinfo2.x[4]), ('z', residueinfo2.x[5]), ('b', residueinfo2.x[6]) )
    def test(p):
        return xchi([p['r1'],p['r2'],p['r3'],p['x'],p['y'], p['z'],p['b']]) ,ychi([p['r1'],p['r2'],p['r3'],p['x'],p['y'], p['z'],p['b']])
    mini = lmfit.Minimizer(test, p, nan_policy='omit')
    result = mini.minimize(method = 'Nelder')
    out2 = mini.minimize(method='leastsq', params=result.params)
    np.savetxt('cov.csv',1e6*out2.covar, delimiter=",")
    
    print(out2.covar)
    #lmfit.report_fit(out2.params, min_correl=.01)
    #cx, cy, grid = lmfit.conf_interval2d(mini, out2, 'x', 'z', 30, 30)
    #cx = cx*1000
    #cy = cy*1000
    #matplotlib.rcParams.update({'font.size': 14})

    #plt.contourf(cx, cy, grid, np.linspace(0, 1, 11))
    #plt.xlabel(r'$x^{C} [\mu m]$')
    #plt.colorbar()
    #plt.ylabel(r'$z^{C} [\mu m]$')
    #plt.show()
    
    

    #print(residueinfo2)
##    print('Nominal-Photo1- value of total chi squared')
##    print('Nominal-Photo1- value of parameters (three rotations in radians, three translations in mm')
##    print("%.4f,%.4f, %.4f,%.4f,%.4f ,  %.4f ,  %.4f " % (residueinfo2.x[0],residueinfo2.x[1], residueinfo2.x[2], residueinfo2.x[3], residueinfo2.x[4], residueinfo2.x[5], residueinfo2.x[6] ))
    #print(residueinfo2)
    '''
    print('Rotation Matrix - Nominal Rotated into Photo1')
    print("%.4f, %.4f, %.4f" % (a11(residueinfo2.x), a12(residueinfo2.x), a13(residueinfo2.x)))
    print("%.4f, %.4f, %.4f" % (a21(residueinfo2.x), a22(residueinfo2.x), a23(residueinfo2.x)))
    print("%.4f, %.4f, %.4f" % (a31(residueinfo2.x), a23(residueinfo2.x), a33(residueinfo2.x)))
    '''
    nomx_prime_array= np.zeros(twophotoslength)
    nomy_prime_array= np.zeros(twophotoslength)
    nomz_prime_array= np.zeros(twophotoslength)
    xnomtopix2_array = np.zeros(twophotoslength)
    ynomtopix2_array = np.zeros(twophotoslength)
    for i in range(0, twophotoslength):
        xnomtopix2_array[i] = xnomtopix2(residueinfo2.x, nomx[i], nomy[i], nomz[i])
        ynomtopix2_array[i] = ynomtopix2(residueinfo2.x, nomx[i], nomy[i], nomz[i])
    for i in range(0, twophotoslength):
        nomx_prime_array[i]= nomx_prime(residueinfo2.x, nomx[i], nomy[i], nomz[i]) - 0.152272
        nomy_prime_array[i]= nomy_prime(residueinfo2.x, nomx[i], nomy[i], nomz[i]) - 0.982569
        nomz_prime_array[i]= nomz_prime(residueinfo2.x, nomx[i], nomy[i], nomz[i]) - 1195.261017

    dx = np.zeros([twophotoslength, 1])
    dy = np.zeros([twophotoslength, 1])
    dxx = np.zeros([twophotoslength, 1])
    dyy = np.zeros([twophotoslength, 1])
    for i in range(0, twophotoslength):
        dx[i] =  (xnomtopix2_array[i] - xpic1[i] - residuex[i])
        dy[i] =  (ynomtopix2_array[i] - ypic1[i] - residuey[i])

    center_dot_index = 0
    for i in range(twophotoslength):
        if xindex[i] == 8 and yindex[i] ==4:
            center_dot_index = i
        elif xindex[i] == 9 and yindex[i] ==4:
            center_dot_index = i
        elif xindex[i] == 7 and yindex[i] ==4:
            center_dot_index = i
        elif xindex[i] == 8 and yindex[i] ==3:
            center_dot_index = i
        elif xindex[i] == 8 and yindex[i] ==5:
            center_dot_index = i

    
    #change in x y z from original image
    center_delta_x = nomx_prime_array[center_dot_index] - nomx[center_dot_index] #- bx(residueinfo2.x, nomx[center_dot_index], nomy[center_dot_index], nomz[center_dot_index]) + bx([0, 0, 0, 0, 0, 0,104.7/1000], nomx[center_dot_index], nomy[center_dot_index], nomz[center_dot_index])
    center_delta_y = nomy_prime_array[center_dot_index] - nomy[center_dot_index]
    center_delta_z = nomz_prime_array[center_dot_index] - nomz[center_dot_index] #- bz(residueinfo2.x, nomx[center_dot_index], nomy[center_dot_index], nomz[center_dot_index]) + bz([0, 0, 0, 0, 0, 0,104.7/1000], nomx[center_dot_index], nomy[center_dot_index], nomz[center_dot_index])
    sig = 0
    dof = 2*twophotoslength - 7
    #print(dof, 2*twophotoslength)
    sig = (chi - dof)/((2*dof)**0.5)
    #what is printed to megon
    fitting_parameters = '%.5f, %.4f, %.4f, %.4f, %.4f, %.4f, %.4f, %.4f, %.4f, %.4f, %.4f, %.4f, %.4f, %.4f, %.4f, %.4f, %s, %.4f, %.4f, %.0f\n'  % (chi,(residueinfo2.x[0] )*1000 , (residueinfo2.x[1])*1000, (residueinfo2.x[2])*1000 , (center_delta_x)*1000, (center_delta_y)*1000 ,(center_delta_z)*1000 ,(residueinfo2.x[6])*1000 , focal_length, 1000*(out2.covar[0, 0]**0.5), 1000*(out2.covar[1, 1]**0.5), 1000*(out2.covar[2, 2]**0.5), 1000*(out2.covar[3, 3]**0.5), 1000*(out2.covar[4, 4]**0.5), 1000*(out2.covar[5, 5]**0.5), 1000*(out2.covar[6, 6]**0.5), image1, dof, sig, threshold)
    megon = 'Total Chi:%.5f:theta:%.4f:phi:%.4f:psi:%.4f:x:%.4f:y:%.4f:z:%.4f:b:%.4f:\n'  % (chi,(residueinfo2.x[0] )*1000 , (residueinfo2.x[1])*1000, (residueinfo2.x[2])*1000 , (center_delta_x)*1000, (center_delta_y)*1000 ,(center_delta_z)*1000 ,(residueinfo2.x[6])*1000 )
    
    #print(fitting_parameters)
    print("del z %.1f"%(center_delta_z*1000))
    god_given = np.zeros([len(nomx), 10])
    for i in range(0, twophotoslength):
        god_given[i, 0] = nomx_prime_array[i]  # 3d x
        god_given[i, 1] = nomy_prime_array[i]  # 3d y
        god_given[i, 2] = nomz_prime_array[i] # 3d z
        god_given[i, 3] = xnomtopix2_array[i]  # image plane x
        god_given[i, 4] = ynomtopix2_array[i]  # image plane y
        god_given[i, 5] = xindex[i]
        god_given[i, 6] = yindex[i]
        god_given[i, 7] = xnomtopix2_array[i]  - xpic1[i] - residuex[i]
        god_given[i, 8] = ynomtopix2_array[i]  - ypic1[i] - residuey[i]
        god_given[i, 9] = 0
    
    np.savetxt("new_dots_god_given%s.csv"%(image1), god_given, delimiter=",")
    too_large_index = []
    for i in range(len(dx)):
        if (abs(god_given[i, 7]) > sigma*4) or (abs(god_given[i, 8]) > sigma*4):
            too_large_index.append(i)
#sigma*4
#twophotos = [column for column in twophotos if( -0.1<column[0] <20) and  ( -0.1<column[3] <20) and (column[2] != 0) ]
#np.savetxt("twophotos.csv", twophotos, delimiter=",")
    return dx,dy, dxx, dyy, too_large_index, fitting_parameters, megon
def arrow_plot(dx,dy,xindex,yindex, filename, arrow_type):
    zero = np.zeros(twophotoslength)
    #import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    
    #--optionally modify the third and fourth arguments to 'zero' to only look at change in x or change in y

    Q = plt.quiver(xindex, yindex, dx, dy) #--the actual line that plots the quiver plot
    ax.quiverkey(Q, X=0.3, Y=1.1, U= ((np.mean(abs(dx))**2 +np.mean(abs(dy))**2)**0.5) ,  label='~ %.0f microns at object'%(1000*24*((np.mean(abs(dx))**2 +np.mean(abs(dy))**2)**0.5)), labelpos='E', fontproperties={'size': 10})

    #--axis information   (needs better axis labels:   variable plotted [units] how is the length of the arrow known to viewer?
    #  probably need an arrow of fixed length somewhere, separately for x and y
    #  find a way to get the scale the same in x and y
    ax.set_ylabel("index ", fontsize=10) #axis infoj
    ax.set_xlabel("index", fontsize=10)

    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(10)
    for tick in ax.yaxis.get_major_ticks():
        tick.label.set_fontsize(10)
    plt.savefig('%s%s.png'%(arrow_type, filename) )


def scp_file(latest_file, scp_number):
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.set_missing_host_key_policy(paramiko.WarningPolicy)
    ssh.connect('megon01', port = 22, username = 'meg', password ='Mu2e+gamma!')
    #scp = SCPClient(ssh.get_transport())
    print (latest_file)
    #scp.put(latest_file)
    sftp = ssh.open_sftp()

    t = paramiko.Transport(('megon01', 22))
    t.connect(username='meg', password='Mu2e+gamma!')
    sftp = paramiko.SFTPClient.from_transport(t)

    print( ' connection to megon successful ')
    try:
        sftp.put(latest_file, '/home/meg/online/slowcontrol/tgtcam/'+latest_file, confirm=True)
        sftp.put(latest_file, '/home/meg/online/web/mhttpd/arrow_plot%i.png'%(scp_number), confirm=True)

        sftp.close()
        ssh.close()
    except:
        print( 'failed to SCP to mac')



if __name__ == '__main__':
    
    image1 = sys.argv[1]
    #image2 = max(glob.glob('*'), key=os.path.getctime)
    image2 = sys.argv[2]
    threshold =int(sys.argv[3])

    #print ('sortedvec_contour%s'%(image2))
    if 'sortedvec_contour%s.csv'%(image1) not in os.listdir():
        print('Searching for dots in',image1)
    length1 = dot_finder(image1,1, threshold)
    if 'sortedvec_contour%s.csv'%(image2) not in os.listdir():
        print('Searching for dots in',image2)
        dot_finder(image2,2, threshold)
    #scp_file('vec_contour1.csv')
    if length1 > 90:
    #print('Creating twophotos.csv')
        two_photos(image1,image2)
    
    #print('Creating 3Ddots.csv')
        cameratargetangle, xf_x0, yf_y0, x0, y0= threeddots()

        threednominal = np.genfromtxt('this_3dnominal.csv', delimiter=',')
    

        twophotos = np.genfromtxt('twophotos.csv', delimiter=',')
        twophotoslength = len(twophotos)
    else:
        twophotoslength = 0
    print(twophotoslength)
    if twophotoslength > 90:
        nomx = threednominal[:, [0]]
        nomy = threednominal[:, [1]]
        nomz = threednominal[:, [2]]

        residuex = threednominal[:, [6]]
        residuey = threednominal[:, [7]]
        god_givenximgpln = threednominal[:, [0]]
        god_givenyimgpln = threednominal[:, [0]]
        


        xindex = twophotos[:, [0]]
        yindex = twophotos[:, [3]]
        xpic1 = twophotos[:, [1]] #--pic1 image plane x dot coordinate in mm
        ypic1 = twophotos[:, [4]] #--pic1 image plane y dot coordinate in mm
        xpic2 = twophotos[:, [2]] #--pic2 image plane x dot coordinate in mm
        ypic2 = twophotos[:, [5]] #--pic2 image plane y dot coordinate in mm
        x2_x1 = twophotos[:, [6]] #difference
        y2_y1 = twophotos[:, [7]] #difference
        
        
        
        #print('Running intro_minimization')
        #p2 = intro_minimization(focal_length, xpic1, ypic1, nomx, nomy, nomz)
        #p2 =[ 1.47295706e-05, -5.18091648e-06, -2.61845472e-05, -2.26468513e-03, -1.00333352e-02,  1.89321401e-03]
        p2 = [0., 0., 0., 0., 0., 0. ,0. ]
        #print('Running minimization')
        dx,dy, dxx, dyy, too_large_index, fitting_parameters, megon= minimization(focal_length, xpic1, ypic1, nomx, nomy, nomz,p2, residuex, residuey, god_givenximgpln, god_givenyimgpln, cameratargetangle, xf_x0, yf_y0, x0, y0)

        if len(too_large_index) == 0:
            with open('522_w_res_vary_threshold.csv','a', newline='') as fd:
                fd.write(fitting_parameters)
            print(megon)
        
        
        else:
            print("too large index", len(too_large_index))
            xpic1 = np.delete(xpic1, too_large_index, axis = 0)
            ypic1 = np.delete(ypic1, too_large_index, axis = 0)
            nomx = np.delete(nomx, too_large_index, axis = 0)
            nomy = np.delete(nomy, too_large_index, axis = 0)
            nomz = np.delete(nomz, too_large_index, axis = 0)
            residuex = np.delete(residuex, too_large_index, axis = 0)
            residuey = np.delete(residuey, too_large_index, axis = 0)
            god_givenximgpln = np.delete(god_givenximgpln, too_large_index, axis = 0)
            god_givenyimgpln = np.delete(god_givenyimgpln, too_large_index, axis = 0)
            xindex = np.delete(xindex, too_large_index, axis = 0)
            yindex = np.delete(yindex, too_large_index, axis = 0)
            twophotoslength = len(nomx)
            dx,dy, dxx, dyy, too_large_index, fitting_parameters, megon = minimization(focal_length, xpic1, ypic1, nomx, nomy, nomz,p2, residuex, residuey, god_givenximgpln, god_givenyimgpln, cameratargetangle, xf_x0, yf_y0, x0, y0)
            with open('522_w_res_vary_threshold.csv','a', newline='') as fd:
                fd.write(fitting_parameters)
            print(megon)
        #from anamodules.frame_foil import frame_foil
        #normal_diff, theta_fr_f, r_value_foil, r_value_frame, theta_foil = frame_foil(image1)
        #fr_fo = "%.4f, %.4f, %.4f, %.4f, %.4f %s\n"%(normal_diff, theta_fr_f, r_value_foil, r_value_frame, theta_foil, image1)
        #with open('3_21_frame_foil.csv','a', newline='') as fd:
        #    fd.write(fr_fo)
        #print('Creating Arrow plot')
        chipic = 'chipic'
        arrow_plot(dx,dy,xindex,yindex, image1, chipic)
        latest_file = "chipic%s.png"%(image1)
        scp_file(latest_file, 1)
        print("end foil")
    else:
        print("Total Chi:0.:theta:0.:phi:0.:psi:0.:x:0.:y:0.:z:0.:b:0.:")



