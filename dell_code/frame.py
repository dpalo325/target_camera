import cv2
import numpy as np
from numpy import genfromtxt
import math
import glob
import os
import sys
import matplotlib.pyplot as plt
from scipy.optimize import minimize
'''
    lowlimx    = 700;
    uplimx     = 3600;
    lowlimy    = 300;
    uplimy     = 2600;
    lowlimarea = 75;
    uplimarea  = 500;
    lower_aspect = 0.85
    upper_aspect = 1.2
    '''
lowlimx    = 680;
uplimx     = 3600;
lowlimy    =300;
uplimy     = 2600;
lowlimarea = 75;
uplimarea  = 120;
lower_aspect = 0.85
upper_aspect = 1.2

hotpixel_cnt = 0 #initializing hot pixel count
#halflengthxpix = 1928    #--half x size of the image
#halflengthypix = 1382    #--half y size of the image
#pix_mm = 1.67*(10**-3)  #conversion
cameraangle = 0.0819
sigma = 0.000237 #mm at the image plane i.e. 0.4 pix
image1 = sys.argv[1]
image2 = sys.argv[2]
threshold =int(sys.argv[3])
chipic = 'chipic'
changepic = 'changepic'
histx = 'histx'
histy = 'histy'
histl = 'histl'
too_large_index = []

ref = [0, 169, 325, 483, 631, 782, 922, 1065, 1199, 1463, 1594, 1716, 1839, 1955, 2074, 2189, 2296, 2415]
lowrefx = np.empty(len(ref))
highrefx = np.empty(len(ref))

for i in range (len(ref)):
    lowrefx[i] = ref[i] - 10
    highrefx[i] = ref[i] +10


hotpixel_cnt = 0
hotpixel_cnt1= 0
hotpixel_cnt2= hotpixel_cnt3= hotpixel_cnt4= hotpixel_cnt5= hotpixel_cnt6= 0 #initializing hot pixel count
halflengthxpix = 1928    #--half x size of the image
halflengthypix =  1382
pix_mm = 1.67*(10**-3) # 1.67*(10**-3)  #conversion
cameraangle = 0.0819
sigma = 0.000237 #mm at the image plane i.e. 0.4 pix
image1 = sys.argv[1]
image2 = sys.argv[2]
threshold =int(sys.argv[3])
focal_length =float(sys.argv[4])

xf_x0 = 0
yf_y0 = 0
x0 = 0
y0= 0


a = 1207
b = 1002
width = 80
center_x = 1930
center_y =  1356
inner_a = a - width
inner_b = b - width
outer_a = a + width
outer_b = b + width

frame_lowerlimx = 700
frame_lowerlimy = 300
frame_upperlimx =  3400
frame_upperlimy =  2500
lowlimarea = 20
uplimarea = 500


def dot_finder(image_name, image_number, threshold):
    #-------------------get first image------------------------------------------
    #latest_darkfield_image = max(glob.glob('*df.jpg'), key=os.path.getctime) # grabbing latest darkfield img
    #global hotpixel_cnt, hotpixel_cnt1, hotpixel_cnt2, hotpixel_cnt3, hotpixel_cnt4, hotpixel_cnt5, hotpixel_cnt6
    latest_darkfield_image ='UCI1026204715darkfield.jpg' # grabbing old darkfield as area is lit up
    #print(latest_darkfield_image)
    darkfield = cv2.imread(latest_darkfield_image, cv2.IMREAD_GRAYSCALE) # inserting darkfield into 2d array 'darkfield'
    print('frame dot finding')
    #---subtracting darkfield-------------------
    img = cv2.imread('%s'%(image1), cv2.IMREAD_GRAYSCALE)    #reading in true image
    backtorgb = cv2.cvtColor(img,cv2.COLOR_GRAY2RGB)
    
    for i in range(0, len(img)):
        for j in range(0, len(img[0])):
            #if 50 >= int(darkfield[i, j]) > 10: hotpixel_cnt1= hotpixel_cnt1 + 1
            #elif 100 >= int(darkfield[i, j]) > 50: hotpixel_cnt2= hotpixel_cnt2 + 1
            #elif 150 >= int(darkfield[i, j]) > 100: hotpixel_cnt3= hotpixel_cnt3 + 1
            #elif 200 >= int(darkfield[i, j]) > 150: hotpixel_cnt4= hotpixel_cnt4 + 1
            #elif 250 >=int(darkfield[i, j]) > 200: hotpixel_cnt5= hotpixel_cnt5 + 1
            #elif int(darkfield[i, j]) > 250: hotpixel_cnt6= hotpixel_cnt6 + 1
            
            
            if int(img[i, j]) - int(darkfield[i, j]) >0 :
                img[i, j] = int(img[i, j]) - int(darkfield[i, j])
            else:
                img[i, j] = 0
    cv2.imwrite('subtracted_%s.jpg'%(image_name), img)
    
    
    #src =  cv2.fastNlMeansDenoising(img,None,10,7,23)#---apply denoising filter
    #th,dst = cv2.threshold(src, 80,255,cv2.THRESH_BINARY)   #---set the black/white threshold if minimizer is used
    th,dst = cv2.threshold(img, threshold,255,cv2.THRESH_BINARY)   #---set the black/white threshold
    
    #----------------------find all contours------------------------------------------
    im2,contours,hierarchy = cv2.findContours(dst, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    #for i in range(len(contours)):
    #    if 50 < cv2.contourArea(contours[i]) < 300:
    #        cv2.drawContours(backtorgb,contours,i,(0,0,255)) #drawing contours but here resizing image and sent to screen
    #imS = cv2.resize(backtorgb, (1500, 1000))
    #cv2.imshow('draw contours',imS)
    #cv2.waitKey(0)
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
    vec_contour = [column for column in vec_contour if (frame_lowerlimx <= column[0] <= frame_upperlimx) and (frame_lowerlimy <= column[1] <= frame_upperlimy) and (lowlimarea <= column[2] <= uplimarea) and (lower_aspect <= column[3] <= upper_aspect)]#remove vec_contour rows if outside limits
    np.savetxt("vec_contour"+str(2)+".csv", vec_contour, delimiter=",")

#-------------------do some selection on good dots in pic--------------------
    vec_contour = [column for column in vec_contour if (frame_lowerlimx <= column[0] <= frame_upperlimx) and (frame_lowerlimy <= column[1] <= frame_upperlimy) and (lowlimarea <= column[2] <= uplimarea) and ((( column[0] - center_x)/inner_a)**2) + ((( column[1] - center_y)/inner_b)**2) > 1 and ((( column[0] - center_x)/outer_a)**2) + ((( column[1] - center_y)/outer_b)**2) < 1 and (lower_aspect <= column[3] <= upper_aspect)]#remove vec_contour rows if outside limits
    #print("length after cut %i", len(vec_contour))
    #--save the contour vector for later use
    np.savetxt("vec_contour"+str(image_number)+".csv", vec_contour, delimiter=",")
    #--read the positions back in from the file we just wrote, issue unless saved as file and then read back
    vec_contour = genfromtxt('vec_contour'+str(image_number)+'.csv', delimiter=',')
    if (len(vec_contour) ==0 ):
        vec_contour = np.zeros((4, 4))
    #sorting
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
    
    #actually producing the index values
    for j in range(0, contour_count):
        xreference = sortedvec_contour[0,0]
        xdata = sortedvec_contour[j,0]
        xdiff  = abs(xdata - xreference)
        sortedvec_contour[j,3] = -1
        for k in range(0,len(lowrefx)):
            if(lowrefx[k] < xdiff < highrefx[k]):
                sortedvec_contour[j,3] = k
                break
    sortedvec_contour[0, 4] = -1
    
    
    #--------ranges in y where we expect to find a dot------
    
    #actually calculating y index
    for j in range(0, len(sortedvec_contour)):
        yreference = sortedvec_contour[0, 1]
        ydata = sortedvec_contour[j, 1]
        if (ydata - yreference > -20):
            sortedvec_contour[j,4] = 0
        else:
            sortedvec_contour[j, 4] = 1
    for j in range(0, len(sortedvec_contour)):
        if sortedvec_contour[j,4] == 0 and sortedvec_contour[j,3] == 0:
            sortedvec_contour[j,4] == -1
    #sorting by column number and row number, sorting by x and then by y (first bunch have the same x)
    idm = np.lexsort((sortedvec_contour[:,3], sortedvec_contour[:,4]))
    sortedvec_contour = sortedvec_contour[idm]

    #--save the sorted data
    np.savetxt("sortedvec_contour_frame"+str(image_name)+".csv", sortedvec_contour, delimiter=",")
    return len(vec_contour), hotpixel_cnt1, hotpixel_cnt2, hotpixel_cnt3, hotpixel_cnt4, hotpixel_cnt5, hotpixel_cnt6,


def two_photos(image1,image2):
    sortedvec_contour = genfromtxt('sortedvec_contour_frame%s.csv'%(image1), delimiter=',') #get two sorted_veccontours aka the product of dot_finder
    sortedvec_contour2 = genfromtxt('sortedvec_contour_frame%s.csv'%(image2), delimiter=',')
    
    contour_count = len(sortedvec_contour) #get lengths
    contour_count2 = len(sortedvec_contour2)
    
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
                twophotos[i, 8] = 0

    twophotos = [column for column in twophotos if( -0.1<column[0] <20) and  ( -0.1<column[3] <20) and (column[2] != 0) ]
    np.savetxt("twophotos_frame.csv", twophotos, delimiter=",")
    return len(twophotos)

def threeddots():
    #---------------------following is code using only photo1 to realign the target assuming camera is in corret position---------
    #here making sure the god given truth, the three d dot position, and the two photos array produced abovew are all the same size
    #threednominal = np.genfromtxt('5_13_frame_test.csv', delimiter=',')
    #threednominal = np.genfromtxt('5_23_avg_res_frame.csv', delimiter=',')
    #threednominal = np.genfromtxt('new_dots_three_d_frame53.csv', delimiter=',')
    #threednominal = np.genfromtxt('frame_test_513_part3.csv', delimiter=',')
    #threednominal = np.genfromtxt('5_23_avg_res_frame_no2.csv', delimiter=',')
    #threednominal = np.genfromtxt('515_avg_res_frame_1102.csv', delimiter=',')
    #threednominal = np.genfromtxt('516_avg_res_frame_1102.csv', delimiter=',')
    #threednominal = np.genfromtxt('frame_reverse.csv', delimiter=',')
    
    #threednominal = np.genfromtxt('519_avg_res_frame_1102.csv', delimiter=',') # attempt to correct with the reverse dots
    threednominal = np.genfromtxt('519_avg_res_frame_1103.csv', delimiter=',') #attempt to correct with reverse dots and only using small residuals
    
    twophotos = np.genfromtxt('twophotos_frame.csv', delimiter=',')
    twophotoslength = len(twophotos)
    threednominallength = len(threednominal)
    #--here modify threednominal to include only dots found in both images
    threednominallength = len(threednominal)
    
    
    
    doubles_listj = [] #trap to kill i and j values which have more than one dot
    doubles_listi = [] #also used to kill something if another doesn't have the dot i.e. a dot 16, 0 exists which shouldnt
    
    
    for i in range(0, twophotoslength):
        for j in range (0,threednominallength):
            if i ==0 and j ==0:
                oldtwophotosi = -1
                oldtwophotosj = -1
            if twophotos[i, 0] == threednominal[j, 3] and twophotos[i, 3] ==threednominal[j, 4] :
                threednominal[j, 5] = threednominal[j, 5] + 1
                twophotos[i, 8] = twophotos[i,8] + 1
                
                if oldtwophotosi == twophotos[i, 0] and oldtwophotosj == twophotos[i, 3]:
                    threednominal[j, 5] = threednominal[j, 5] + 5
                    doubles_listi.append(twophotos[i, 0])
                    doubles_listj.append(twophotos[i, 3])
                oldtwophotosi = twophotos[i, 0]
                oldtwophotosj = twophotos[i, 3]

    for i in range(0, twophotoslength):
        for j in range(0, len(doubles_listi)):
            if doubles_listi[j] == twophotos[i, 0] and doubles_listj[j] == twophotos[i, 3]:
                twophotos[i, 8] = twophotos[i,8] + 5
        for i in range(0, twophotoslength):
            for j in range (0,threednominallength):
                if twophotos[i, 0]==0 and twophotos[i, 3]==0 and twophotos[i, 0] == threednominal[j, 3] and twophotos[i, 3] ==threednominal[j, 4] :
                    threednominal[j, 5] = threednominal[j, 5] + 5
                    twophotos[i, 8] = twophotos[i,8] + 5
    #entire sorting and saving of modified arrays
    twophotos = np.array([ column for column in twophotos if (4 > column[8] >0.5) ])
    idx = np.lexsort((twophotos[:,0], twophotos[:,3]))
    twophotos = twophotos[idx]
    np.savetxt("twophotos_frame.csv", twophotos, delimiter=",")

    threednominal = np.array([ column for column in threednominal if (4 > column[5] >0.5) ])
    print(len(threednominal))
    idd = np.lexsort((threednominal[:,3], threednominal[:,4]))
    threednominal = threednominal[idd]
    np.savetxt("this_3dnominal_frame.csv", threednominal, delimiter=",")

def intro_minimization(xpic1, ypic1, nomx, nomy, nomz):
    #--p0 is initial value of param_vec, the array of the initial values of the fitting parameters
    p0 = np.array([0, 0, 0], dtype = float)
    #------------------------here is the actual minimization -----------------------------------------------------------
    print(len(xpic1))
    
    #function projecting 3d onto img plane x and y
    xnomtopix = lambda param_vec,nomx,nomz: focal_length*(nomx + param_vec[0])/( nomz + param_vec[2] - focal_length)
    ynomtopix = lambda param_vec,nomy,nomz: focal_length*(nomy + param_vec[1])/( nomz + param_vec[2] - focal_length)
    twophotoslength = len(nomx)
    
    xchi = lambda param_vec:np.sum([ (xnomtopix(param_vec, nomx[i], nomz[i]) - xpic1[i] )**2 for i in range(twophotoslength)])
    ychi = lambda param_vec:np.sum([ (ynomtopix(param_vec, nomy[i], nomz[i]) - ypic1[i] )**2 for i in range(twophotoslength)])
    totalchi = lambda param_vec:(xchi(param_vec) + ychi(param_vec))
    roughnom_pic1 = minimize(totalchi, p0, method='nelder-mead')
    return np.array([0, 0, 0, roughnom_pic1.x[0], roughnom_pic1.x[1], roughnom_pic1.x[2]], dtype = float) #initial parameters are the values of the first optimizer
#return np.array([-0.0428, -0.006, -0.0276, 55.121, -30.7155, , 0.4015], dtype = float) #initial parameters are the values of the first optimizer
#at one point just returned values from one successful

def minimization(xpic1, ypic1, nomx, nomy, nomz, p2, residuex, residuey, god_givenximgpln, god_givenyimgpln, twophotoslength, xindex, yindex, god_given_x, god_given_y, god_given_z, nomx2, nomy2, nomz2, xpic12, ypic12, xindex2, yindex2):
    nomx = nomx #- 0.152272
    nomy = nomy #- 0.982569
    nomz = nomz #- 1195.261017
    nomx2 = np.array(nomx2)
    nomy2 = np.array(nomy2)
    nomz2 = np.array(nomz2)
    twophotoslength = len(nomx)
    #defining angle matrix functions
    a11 =lambda param_vec :np.cos(param_vec[0])*np.cos(param_vec[2])
    a12 = lambda param_vec:-np.cos(param_vec[1])*np.sin(param_vec[2]) + np.sin(param_vec[0])*np.sin(param_vec[1])*np.cos(param_vec[2])
    a13 = lambda param_vec:np.sin(param_vec[2])*np.sin(param_vec[1]) + np.cos(param_vec[2])*np.sin(param_vec[0])*np.cos(param_vec[1])
    a21 = lambda param_vec:np.cos(param_vec[0])*np.sin(param_vec[2])
    a22 = lambda param_vec:np.cos(param_vec[1])*np.cos(param_vec[2]) + np.sin(param_vec[0])*np.sin(param_vec[1])*np.sin(param_vec[2])
    a23 = lambda param_vec:-np.sin(param_vec[1])*np.cos(param_vec[2]) + np.cos(param_vec[1])*np.sin(param_vec[0])*np.sin(param_vec[2])
    a31 = lambda param_vec:-np.sin(param_vec[0])
    a32 = lambda param_vec:np.sin(param_vec[1])*np.cos(param_vec[0])
    a33 = lambda param_vec:np.cos(param_vec[1])*np.cos(param_vec[0])
    #defining bowing functions
    #bz = lambda param_vec, nomx, nomy, nomz:np.sin(cameratargetangle)*( param_vec[6]*((nomx - x0)/(xf_x0))**2 + param_vec[6]*((nomy - y0)/(yf_y0))**2 - param_vec[6])
    #bx = lambda param_vec, nomx, nomy, nomz:np.cos(cameratargetangle)*( param_vec[6]*((nomx - x0)/(xf_x0))**2 + param_vec[6]*((nomy - y0)/(yf_y0))**2 - param_vec[6])
    #definitn new 3d prime function
    nomx_prime = lambda param_vec, nomx, nomy, nomz:nomx*a11(param_vec) + nomy*a12(param_vec) + nomz*a13(param_vec) + param_vec[3] + 0.152272
    nomy_prime = lambda param_vec, nomx, nomy, nomz:nomx*a21(param_vec) + nomy*a22(param_vec) + nomz*a23(param_vec) + param_vec[4]+ 0.982569
    nomz_prime = lambda param_vec, nomx, nomy, nomz:nomx*a31(param_vec) + nomy*a32(param_vec) + nomz*a33(param_vec) + param_vec[5]+ 1195.261017
    
    #projecting new 3d onto img plane
    xnomtopix2 = lambda param_vec, nomx, nomy, nomz: (focal_length*nomx_prime(param_vec, nomx, nomy, nomz))/(nomz_prime(param_vec, nomx, nomy, nomz))
    ynomtopix2 = lambda param_vec, nomx, nomy, nomz: (focal_length*nomy_prime(param_vec, nomx, nomy, nomz))/(nomz_prime(param_vec, nomx, nomy, nomz))
    #non normalized chi squared for x and y with residue
    xchi2 = lambda param_vec: np.sum([ (xnomtopix2(param_vec, nomx[i], nomy[i], nomz[i]) - xpic1[i] -residuex[i])**2 for i in range(twophotoslength)])
    ychi2 = lambda param_vec: np.sum([ (ynomtopix2(param_vec, nomx[i], nomy[i], nomz[i]) - ypic1[i] -residuey[i])**2 for i in range(twophotoslength)])
    sigma = 0.000167*1.2 #0.12 pix
    N = twophotoslength
    sigma_squared = sigma*sigma
    totalchi2 = lambda param_vec: (xchi2(param_vec) + ychi2(param_vec))/sigma_squared
    #------------------------here is the minimization -----------------------------------------------------------
    #  1: function minimized, 2:initial parameters, 3:arguments that aren't minimzed, 4:method
    bounds = [(-0.02,-0.02,-0.1,-400, -400, -400), (0.04,0.04,0.1,400, 400,400)]
    bounds = np.array(bounds)
    bounds = bounds.T
    #residueinfo2 = minimize(totalchi2, p2, method='L-BFGS-B',bounds =bounds,  options={'maxiter': 5000, 'ftol' : 1e-12})
    residueinfo2 = minimize(totalchi2, p2, method='Nelder-Mead',  options={'maxiter': 5000, 'ftol' : 1e-9})
    
    #print("%.4f"%((totalchi2(residueinfo2.x)-(N*2 -6))/(2*(N*2 -6)**0.5)))
    chi =totalchi2(residueinfo2.x)
    print(chi, 2*N -6)
    dof = 2*N -7
    sig = (chi -dof)/((2*dof)**0.5)
    #print(residueinfo2)
    #print(residueinfo2.x)
    #could print rot matrix
    #print('Rotation Matrix - Nominal Rotated into Photo1')
    #print("%.4f, %.4f, %.4f" % (a11(residueinfo2.x), a12(residueinfo2.x), a13(residueinfo2.x)))
    #print("%.4f, %.4f, %.4f" % (a21(residueinfo2.x), a22(residueinfo2.x), a23(residueinfo2.x)))
    #print("%.4f, %.4f, %.4f" % (a31(residueinfo2.x), a23(residueinfo2.x), a33(residueinfo2.x)))
    
    fit_status =residueinfo2.status #fit status
    #make array to fill with new prime coordinates and arrahy of projected 2d coordinates of optimized nominal
    nomx_prime_array= np.empty(twophotoslength)
    nomy_prime_array= np.empty(twophotoslength)
    nomz_prime_array= np.empty(twophotoslength)
    xnomtopix2_array = np.empty(twophotoslength)
    ynomtopix2_array = np.empty(twophotoslength)
    nomx_prime_array2= np.zeros(len(xpic12))
    nomy_prime_array2= np.zeros(len(xpic12))
    nomz_prime_array2= np.zeros(len(xpic12))
    xnomtopix2_array2 = np.zeros(len(xpic12))
    ynomtopix2_array2 = np.zeros(len(xpic12))
    
    for i in range(0, len(xpic12)):
        xnomtopix2_array2[i] = xnomtopix2(residueinfo2.x, nomx2[i], nomy2[i], nomz2[i])
        ynomtopix2_array2[i] = ynomtopix2(residueinfo2.x, nomx2[i], nomy2[i], nomz2[i])
    
    for i in range(0, len(xpic12)):
        nomx_prime_array2[i]= nomx_prime(residueinfo2.x, nomx2[i], nomy2[i], nomz2[i]) - 0.152272
        nomy_prime_array2[i]= nomy_prime(residueinfo2.x, nomx2[i], nomy2[i], nomz2[i]) - 0.982569
        nomz_prime_array2[i]= nomz_prime(residueinfo2.x, nomx2[i], nomy2[i], nomz2[i]) - 1195.261017
    
    #filling
    for i in range(0, twophotoslength):
        xnomtopix2_array[i] = xnomtopix2(residueinfo2.x, nomx[i], nomy[i], nomz[i])
        ynomtopix2_array[i] = ynomtopix2(residueinfo2.x, nomx[i], nomy[i], nomz[i])
    for i in range(0, twophotoslength):
        nomx_prime_array[i]= nomx_prime(residueinfo2.x, nomx[i], nomy[i], nomz[i])- 0.152272
        nomy_prime_array[i]= nomy_prime(residueinfo2.x, nomx[i], nomy[i], nomz[i]) - 0.982569
        nomz_prime_array[i]= nomz_prime(residueinfo2.x, nomx[i], nomy[i], nomz[i])- 1195.261017
    if nomx2[0] ==0:
        god_given = np.zeros((len(nomx), 10))
        for i in range(len(nomx)):
            god_given[i, 0] = nomx_prime_array[i]  # 3d x
            god_given[i, 1] = nomy_prime_array[i]  # 3d y
            god_given[i, 2] = nomz_prime_array[i] # 3d z
            god_given[i, 3] = xnomtopix2_array[i]  # image plane x
            god_given[i, 4] = ynomtopix2_array[i]  # image plane y
            god_given[i, 5] = xindex[i]
            god_given[i, 6] = yindex[i]
            god_given[i, 7] = xnomtopix2_array[i]  - xpic1[i] -residuex[i]
            god_given[i, 8] = ynomtopix2_array[i]  - ypic1[i]-residuey[i]
            god_given[i, 9] = 0
    else:
        god_given = np.zeros((len(nomx2), 10))
        for i in range(len(nomx2)):
            god_given[i, 0] = nomx_prime_array2[i]  # 3d x
            god_given[i, 1] = nomy_prime_array2[i]  # 3d y
            god_given[i, 2] = nomz_prime_array2[i] # 3d z
            god_given[i, 3] = xnomtopix2_array2[i]  # image plane x
            god_given[i, 4] = ynomtopix2_array2[i]  # image plane y
            god_given[i, 5] = xindex2[i]
            god_given[i, 6] = yindex2[i]
            god_given[i, 7] = xnomtopix2_array2[i]  - xpic12[i]
            god_given[i, 8] = ynomtopix2_array2[i]  - ypic12[i]
            god_given[i, 9] = 0
    np.savetxt("new_dots_god_given_framewres5193%s.csv"%(image1), god_given, delimiter=",")
    #change names of these things
    dx = np.zeros([twophotoslength, 1])
    dy = np.zeros([twophotoslength, 1])
    dxx = np.zeros([twophotoslength, 1])
    dyy = np.zeros([twophotoslength, 1])
    arrow_x = np.zeros([twophotoslength, 1])
    arrow_y = np.zeros([twophotoslength, 1])
    for i in range(0, twophotoslength):
        dx[i] =  (xnomtopix2_array[i] - xpic1[i]) # residue contribution
        dy[i] =  (ynomtopix2_array[i] - ypic1[i] )# residue contribution
        arrow_x[i] =  xnomtopix2_array[i] - xpic1[i]
        arrow_y[i] =  ynomtopix2_array[i] - ypic1[i]
        dxx[i] = xnomtopix2_array[i] -  god_givenximgpln[i]
        dyy[i] = ynomtopix2_array[i] -  god_givenyimgpln[i]
    center_dot_index = 0
    for i in range(twophotoslength):
        if xindex[i] == 7 and yindex[i] ==0:
            center_dot_index = i
        elif xindex[i] ==8 and yindex[i] ==0:
            center_dot_index = i
        elif xindex[i] == 9 and yindex[i] ==0:
            center_dot_index = i
        elif xindex[i] == 10 and yindex[i] ==0:
            center_dot_index = i
        elif xindex[i] == 7 and yindex[i] ==1:
            center_dot_index = i
    #change in x y z from original image
    center_delta_x = nomx_prime_array[center_dot_index] - nomx[center_dot_index]
    center_delta_y = nomy_prime_array[center_dot_index] - nomy[center_dot_index]
    center_delta_z = nomz_prime_array[center_dot_index] - nomz[center_dot_index]
    too_large_index = []
    fitting_parameters = '%.5f, %.4f, %.4f, %.4f, %.4f, %.4f, %.4f, %s, %.4f, %.4f\n'  % (chi,(residueinfo2.x[0] )*1000 , (residueinfo2.x[1])*1000, (residueinfo2.x[2])*1000 , (center_delta_x)*1000, (center_delta_y)*1000 ,(center_delta_z)*1000 , image1, dof, sig)

    #if dots are too large then find this index
    for i in range(len(dx)):
        if (abs(god_given[i, 7]) >10*sigma) or (abs(god_given[i, 8]) >10*sigma):
            too_large_index.append(i)
    myCsvRow = "0"
    return dx,dy, dxx, dyy, too_large_index, arrow_x, arrow_y, fitting_parameters, myCsvRow, residueinfo2.status

def arrow_plot(arrow_x,arrow_y,xindex,yindex, filename, arrow_type):
    zero = np.zeros(len(arrow_x))
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    dl = np.zeros(len(arrow_x))
    for i in range(len(arrow_x)):
        dl[i] = np.sqrt(arrow_x[i]**2 + arrow_y[i]**2)
    #--optionally modify the third and fourth arguments to 'zero' to only look at change in x or change in y
    
    Q = plt.quiver(xindex, yindex, arrow_x, arrow_y) #--the actual line that plots the quiver plot
    if arrow_type == 'chipic':
        ax.quiverkey(Q, X=0.3, Y=1.1, U= np.mean(abs(dl)) ,  label='Residual Contributions ~ %.0f microns at object'%(1000*20*np.mean(abs(dl))), labelpos='E', fontproperties={'size': 10})
    if arrow_type == 'changepic':
        ax.quiverkey(Q, X=0.3, Y=1.1, U= np.mean(abs(arrow_y)) ,  label='3D Projected WRT 10-21 Image,~ %.0f microns at object'%(1000*20*np.mean(abs(arrow_y))), labelpos='E', fontproperties={'size': 10})
    
    #--axis information   (needs better axis labels:   variable plotted [units] how is the length of the arrow known to viewer?
    #  probably need an arrow of fixed length somewhere, separately for x and y
    #  find a way to get the scale the same in x and y
    plt.xlim(-1.5,17.5)
    plt.ylim(-1.5,9.5)
    ax.set_ylabel("index ", fontname="Arial", fontsize=20) #axis infoj
    ax.set_xlabel("index", fontname="Arial", fontsize=20)
    
    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(10)
    for tick in ax.yaxis.get_major_ticks():
        tick.label.set_fontsize(10)
    plt.savefig('%s%s_%s.png'%(filename,arrow_type, focal_length) )

def histogram(dx, dy, filename):
    dx = dx*1000*23.28
    dy = dy*1000*23.28
    min_dx =-50
    min_dy = -50
    max_dx =50
    max_dy = 50
    xbins = np.zeros(50)
    ybins = np.zeros(50)
    lbins = np.zeros(50)
    dl = np.zeros(len(dx))
    
    for i in range(50):
        xbins[i] = max(dx)*i/50
        ybins[i] = max(dy)*i/50
    for i in range(len(dx)):
        dl[i] = np.sqrt(dx[i]**2 + dy[i]**2)
    for i in range(50):
        lbins[i] = max(dl)*i/50
    np.savetxt('dl%s'%(filename), dl, delimiter=",")

    plt.figure(1,[3.7,4.5])
    nx, xbins, xpatches = plt.hist(dx, 50,[-50,50])
    plt.xlabel('dx[um]')
    plt.ylabel('')
    plt.title('X Residual Referenced to Object Plane')
    plt.savefig('%s%s_%s.png'%(filename,"histx", focal_length) )

    plt.figure(2,[3.7,4.5])
    ny, ybins, ypatches = plt.hist(dy, 50,[-50,50])
    plt.xlabel('dy[um]')
    plt.ylabel('')
    plt.title('Y Residual Referenced to Object Plane')
    plt.savefig('%s%s_%s.png'%(filename,"histy", focal_length) )

    plt.figure(3)
    nl, lbins, lpatches = plt.hist(dl, 200)
    plt.xlabel('Residual at Image Plane')
    plt.ylabel('')
    plt.title('Histogram of Total Residual Contributions')
    plt.savefig('%s%s_%s.png'%(filename,"histl", focal_length) )

if __name__ == '__main__':
    
    hotpixel_cnt = 0
    length_vec_contour= 0
    if 'sortedvec_contour_frame%s.csv'%(image1) not in os.listdir():
        print('Searching for dots in',image1)
        length_vec_contour, hotpixel_cnt1, hotpixel_cnt2, hotpixel_cnt3, hotpixel_cnt4, hotpixel_cnt5, hotpixel_cnt6,= dot_finder(image1,1, threshold)
    if 'sortedvec_contour_frame%s.csv'%(image2) not in os.listdir():
        print('Searching for dots in',image2)
        length_vec_contour, hotpixel_cnt1, hotpixel_cnt2, hotpixel_cnt3, hotpixel_cnt4, hotpixel_cnt5, hotpixel_cnt6, = dot_finder(image2,2, threshold)
    #print('Creating twophotos.csv')

    length_vec_contour = two_photos(image1,image2)


    #hotpixel= "hot1:%d:hot2:%d:hot3:%d:hot4:%d:hot5:%d:hot6:%d:"%(hotpixel_cnt1, hotpixel_cnt2, hotpixel_cnt3, hotpixel_cnt4, hotpixel_cnt5, hotpixel_cnt6)

    #print('Creating 3Ddots.csv')
    threeddots()
    threednominal = np.genfromtxt('this_3dnominal_frame.csv', delimiter=',')
    god_given2 = np.genfromtxt('this_god_given_truth.csv', delimiter=',')
    twophotos = np.genfromtxt('twophotos_frame.csv', delimiter=',')
    twophotoslength = len(twophotos)

    nomx = threednominal[:, [0]]
    nomy = threednominal[:, [1]]
    nomz = threednominal[:, [2]]

    residuex = threednominal[:, [6]]
    residuey = threednominal[:, [7]]
    god_givenximgpln = twophotos[:, [0]]
    god_givenyimgpln = god_given2[:, [4]]
    god_given_x = twophotos[:, [0]]
    god_given_y = twophotos[:, [0]]
    god_given_z = twophotos[:, [0]]
    twophotoslength = len(twophotos)
    xindex = twophotos[:, [0]]
    yindex = twophotos[:, [3]]
    xindex = np.array(xindex)
    yindex = np.array(yindex)
    xpic1 = twophotos[:, [1]] #--pic1 image plane x dot coordinate in mm
    ypic1 = twophotos[:, [4]] #--pic1 image plane y dot coordinate in mm
    xpic2 = twophotos[:, [2]] #--pic2 image plane x dot coordinate in mm
    ypic2 = twophotos[:, [5]] #--pic2 image plane y dot coordinate in mm
    x2_x1 = twophotos[:, [6]] #difference
    y2_y1 = twophotos[:, [7]] #difference


    #print('Running intro_minimization')
    p2 = intro_minimization(xpic1, ypic1, nomx, nomy, nomz)
    #print(p2)
    #print('Running minimization')
    dx,dy, dxx, dyy, too_large_index, arrow_x, arrow_y, fitting_parameters, myCsvRow, fit_status = minimization(xpic1, ypic1, nomx, nomy, nomz,p2, residuex, residuey, god_givenximgpln, god_givenyimgpln, twophotoslength, xindex, yindex, god_given_x, god_given_y, god_given_z, [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0])
    
    if len(too_large_index) == 0 and fit_status ==0:
        with open('5_19_frame_nores.csv','a', newline='') as fd:
            fd.write(fitting_parameters)

    else:
        #print("first minimization failed")
        #print("too large index")
        #print(too_large_index)
        xpic12 = np.delete(xpic1, too_large_index, axis = 0)
        ypic12 = np.delete(ypic1, too_large_index, axis = 0)
        nomx2 = np.delete(nomx, too_large_index, axis = 0)
        nomy2 = np.delete(nomy, too_large_index, axis = 0)
        nomz2 = np.delete(nomz, too_large_index, axis = 0)
        residuex2 = np.delete(residuex, too_large_index, axis = 0)
        residuey2 = np.delete(residuey, too_large_index, axis = 0)
        god_givenximgpln2 = np.delete(god_givenximgpln, too_large_index, axis = 0)
        god_givenyimgpln2 = np.delete(god_givenyimgpln, too_large_index, axis = 0)
        xindex2 = np.delete(xindex, too_large_index, axis = 0)
        yindex2 = np.delete(yindex, too_large_index, axis = 0)
        god_given_x2 = np.delete(god_given_x, too_large_index, axis = 0)
        god_given_y2 = np.delete(god_given_y, too_large_index, axis = 0)
        god_given_z2 = np.delete(god_given_z, too_large_index, axis = 0)
        twophotoslength = len(nomx)
        dx,dy, dxx, dyy, too_large_index, arrow_x, arrow_y, fitting_parameters, myCsvRow, fit_status = minimization(xpic12, ypic12, nomx2, nomy2, nomz2,p2, residuex2, residuey2, god_givenximgpln2, god_givenyimgpln2,twophotoslength, xindex2, yindex2, god_given_x2, god_given_y2, god_given_z2, nomx, nomy, nomz, xpic1, ypic1, xindex, yindex)
        with open('5_19_frame_nores.csv','a', newline='') as fd:
            fd.write(fitting_parameters)

        frame = "frame"
        #pltdot.histogram(arrow_x, arrow_y, image1)
        arrow_plot(arrow_x,arrow_y,xindex,yindex, image1, frame)
        #pltdot.arrow_plot(dxx,dyy,xindex,yindex, image1, changepic)

        if (length_vec_contour <10):
            print("not enough dots were found")
            #making a bunch of blank images to send as the histogams, arrow plots etc
            from PIL import Image
            image = Image.new('RGB', (500, 500))
            image.save('%s%s.png'%(image1, histx), "PNG")
            image.save('%s%s.png'%(image1, histy), "PNG")
            image.save('%s%s.png'%(image1, histl), "PNG")
            image.save('%s%s.png'%(image1, changepic), "PNG")
            image.save('%s%s.png'%(image1, chipic), "PNG")
            fitting_parameters = 'Total Chi:%.5f:Theta:%.4f:Phi:%.4f:Psi:%.4f:X:%.4f:Y:%.4f:Z:%.4f:Bowing:%.4f:'%(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
            print(fitting_parameters+hotpixel)
            with open('fitting_parameters.csv','a', newline='') as fd:
                fd.write(myCsvRow+indep_z_result)

