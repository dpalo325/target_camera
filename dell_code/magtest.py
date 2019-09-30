import numpy as np
from numpy import genfromtxt
import sys
image = sys.argv[1]
image2 = sys.argv[2]

def foil():
    a = genfromtxt('sortedvec_contour'+str(image)+'.csv', delimiter=',')
    b = genfromtxt('sortedvec_contour'+str(image2)+'.csv', delimiter=',')
    ax = []
    bx = []
    ay= []
    by=[]
    x = []
    y = []
    for i in range(len(a)):
        for j in range(len(b)):
            if a[i, 3] == b[j, 3] and a[i, 4] == b[j, 4]:
                ax.append(1.67*(a[i, 0]-1928)*10**-3)
                bx.append(1.67*(b[j, 0]-1928)*10**-3)
                ay.append(1.67*(1382- a[i, 1])*10**-3)
                by.append(1.67*(1382 -b[j, 1])*10**-3)
                x.append(a[i, 3])
                y.append(a[i, 4])

    ax = np.array(ax)
    bx = np.array(bx)
    ay = np.array(ay)
    by = np.array(by)
    x = np.array(x)
    y = np.array(y)

    max = np.zeros(17)
    min = np.zeros(17)
    for i in range(17):
        min[i] +=10
    minax= np.zeros(17)
    minbx= np.zeros(17)
    maxax=  np.zeros(17)
    maxbx= np.zeros(17)
    minay= np.zeros(17)
    minby= np.zeros(17)
    maxay=  np.zeros(17)
    maxby= np.zeros(17)
    for i in range(len(ax)):
        for j in range(17):
            if j == x[i]:
                if y[i] < min[j] and y[i] >= 0:
                    min[j] = y[i]
                if y[i] > max[j]:
                    max[j] = y[i]
    for i in range(len(ax)):
        for j in range(17):
            if j == x[i]:
                if y[i] == min[j]:
                    minay[j] = ay[i]
                    minby[j] = by[i]
                    minax[j] = ax[i]
                    minbx[j] = bx[i]
                if y[i] == max[j]:
                    maxay[j] = ay[i]
                    maxby[j] = by[i]
                    maxax[j] = ax[i]
                    maxbx[j] = bx[i]
    hia = np.zeros(17)
    hib = np.zeros(17)
    za = np.zeros(17)
    zb = np.zeros(17)
    xa = np.zeros(17)
    xb = np.zeros(17)
    bad = []
    for j in range(17):
        if minax[j] !=0  and  minbx[j] !=0  and  minay[j] !=0  and  minby[j] !=0 and min[j] < 5 and max[j] >4:
            hia[j] = ( (minay[j] -maxay[j])**2 + (minax[j] -maxax[j])**2)**0.5
            hib[j] = ( (minby[j] -maxby[j])**2 + (minbx[j] -maxbx[j])**2)**0.5
            za[j] = 51.611*7*0.997*(max[j] - min[j])/hia[j]
            zb[j] = 51.611*7*0.997*(max[j] - min[j])/hib[j]
            xa[j] = minax[j]*za[j]/51.611
            xb[j] = minbx[j]*zb[j]/51.611
            xa[j] = xa[j] - xb[j]
            za[j] = za[j] - zb[j]
        else:
            bad.append(j)

    for j in range(17):
        if abs(xa[j]) > 2*np.mean(abs(xa)) or abs(za[j]) > 2*np.mean(abs(za)):
            bad.append(j)
    print(bad)
    xa = np.delete(xa, bad)
    xb = np.delete(xb, bad)
    za = np.delete(za, bad)
    zb = np.delete(zb, bad)
    del_x = np.mean(xa)
    del_z = np.mean(za)
    print(za)
    return del_x, del_z, len(xa)
del_x, del_z, length = foil()
#import magtest_frame
#del_x_fr, del_z_fr = magtest_frame.frame()
#test = "%.3f, %.3f, %.3f, %.3f, %.3f, %s \n"%(del_x*1000, del_z*1000, del_x_fr*1000, del_z_fr*1000, length, image)
#print('sucess')
#print(test)
min = genfromtxt('new_dots_god_given'+str(image)+'.csv', delimiter=',')
min2 = genfromtxt('new_dots_god_given'+str(image2)+'.csv', delimiter=',')
min_list = []
min2_list = []
minx = np.zeros(3)
min2x = np.zeros(3)
print(image)
for i in range(len(min)):
    if min[i, 5] == 8 and min[i, 6] == 1:
        a =1
        min_list.append(i)
    if min[i, 5] == 8 and min[i, 6] == 7:
        min_list.append(i)
        a =1
    if min[i, 5] == 2 and min[i, 6] == 4:
        #min_list.append(i)
        a =1

    if min[i, 5] == 14 and min[i, 6] == 4:
        #min_list.append(i)
        a =1


for i in range(len(min2)):
    if min2[i, 5] == 8 and min2[i, 6] == 1:
        a =1
        min2_list.append(i)
    if min2[i, 5] == 8 and min2[i, 6] == 7:
        min2_list.append(i)
        a =1
    if min2[i, 5] == 2 and min2[i, 6] == 4:
        #min2_list.append(i)
        a =1

    if min2[i, 5] == 14 and min2[i, 6] == 4:
        #min2_list.append(i)
        a =1


print(len(min2_list), len(min_list))
def average(a, b, c, d):
    return (a+b+c+d)/4
def average2(a, b):
    return (a+b)/2

minx[0] = average2(min[min_list[0], 0], min[min_list[1], 0]) +0.152272
minx[2]= average2(min[min_list[0], 2], min[min_list[1], 2])+1195.261017
minx[1]= average2(min[min_list[0], 1], min[min_list[1], 1])+ 0.982569

min2x[0] = average2(min2[min2_list[0], 0], min2[min2_list[1], 0]) +0.152272
min2x[2]= average2(min2[min2_list[0], 2], min2[min2_list[1], 2])+1195.261017
min2x[1]= average2(min2[min2_list[0], 1], min2[min2_list[1], 1])+ 0.982569
#min2x[0] = average(min2[min2_list[0], 0], min2[min2_list[1], 0], min2[min2_list[2], 0], min2[min2_list[3], 0])+ 0.152272
#min2x[2] =average(min2[min2_list[0], 2], min2[min2_list[1], 2], min2[min2_list[2], 2], min2[min2_list[3], 2])+1195.261017


min_frame = genfromtxt('new_dots_god_given_framewres5192'+str(image)+'.csv', delimiter=',')
min2_frame  = genfromtxt('new_dots_god_given_framewres5192'+str(image2)+'.csv', delimiter=',')
min_list_frame  = []
min2_list_frame  = []
minx_frame  = np.zeros(3)
min2x_frame  = np.zeros(3)

for i in range(len(min_frame )):
    if min_frame[i, 5] == 7 and min_frame[i, 6] == 0:
        min_list_frame.append(i)
    if min_frame[i, 5] == 10 and min_frame[i, 6] == 0:
        min_list_frame.append(i)
    if min_frame[i, 5] == 7 and min_frame[i, 6] == 1:
        min_list_frame.append(i)
    if min_frame[i, 5] == 10 and min_frame[i, 6] == 1:
        min_list_frame.append(i)

for i in range(len(min2_frame)):
    if min2_frame[i, 5] == 7 and min2_frame[i, 6] == 0:
        min2_list_frame.append(i)
    if min2_frame[i, 5] == 10 and min2_frame[i, 6] == 0:
        min2_list_frame.append(i)
    if min2_frame[i, 5] == 7 and min2_frame[i, 6] == 1:
        min2_list_frame.append(i)
    if min2_frame[i, 5] == 10 and min2_frame[i, 6] == 1:
        min2_list_frame.append(i)


print("length of frame", len(min2_list_frame), len(min_list_frame))
def average_frame(a, b, c, d):
    return (a+b+c+d)/4
if len(min2_list_frame) ==4 and len(min_list_frame) ==4:
    minx_frame[0] = average(min_frame[min_list_frame[0], 0], min_frame[min_list_frame[1], 0], min_frame[min_list_frame[2], 0], min_frame[min_list_frame[3], 0])+ 0.152272
    minx_frame[2]= average(min_frame[min_list_frame[0], 2], min_frame[min_list_frame[1], 2], min_frame[min_list_frame[2], 2], min_frame[min_list_frame[3], 2])+1195.261017
    min2x_frame[0] = average(min2_frame[min2_list_frame[0], 0], min2_frame[min2_list_frame[1], 0], min2_frame[min2_list_frame[2], 0], min2_frame[min2_list_frame[3], 0]) + 0.152272
    min2x_frame[2] =average(min2_frame[min2_list_frame[0], 2], min2_frame[min2_list_frame[1], 2], min2_frame[min2_list_frame[2], 2], min2_frame[min2_list_frame[3], 2])+1195.261017

    test = "%.3f, %.3f, %.3f, %.3f, %.6f, %s, %.3f, %.3f \n"%(minx_frame[0], minx_frame[2], minx[0], minx[2], del_z, image, (minx_frame[0]- minx[0])*np.cos(0.345) -(minx_frame[2]- minx[2])*np.sin(0.345), (minx_frame[0]- minx[0])*np.sin(0.345) +(minx_frame[2]- minx[2])*np.cos(0.345) )
    #test = "%.6f, %.6f, %.6f, %s\n"%(minx[0], minx[1], minx[2], image)

    print(test)
    with open('mag524.csv','a', newline='') as fd:
        fd.write(test)

