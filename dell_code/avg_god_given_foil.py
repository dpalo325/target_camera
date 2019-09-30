import numpy as np
a = np.genfromtxt('522_no_residue_fixedI.csv', delimiter=',')
max = 0
length = np.zeros(len(a))
for i in range(len(a)):
    try:
        result = np.genfromtxt('new_dots_god_given522UCI0%.0f.jpg.csv'%(a[i, 12]), delimiter=',')
        length[i] = int(len(result))
        if length[i] > max:
            max = length[i]
    except:
        b = 1
for i in range(len(a)):
    result = np.genfromtxt('new_dots_god_given522UCI0%.0f.jpg.csv'%(a[i, 12]), delimiter=',')
    print(result.shape)
    z = int(max - length[i])
    ze = np.zeros((z, 8))
    ze = ze -1
    result = np.vstack((result, ze))

    if i == 0:
        total = result
    if i > 0:
        total = np.dstack((total, result))

print(total.shape)

avg_resx = np.zeros((17, 9))
counter = np.zeros((17, 9))
sumsqx = np.zeros((17, 9))
sumsqy = np.zeros((17, 9))

avg_resy = np.zeros((17, 9))
avgx= np.zeros((17, 9))
avgy= np.zeros((17, 9))
avgz = np.zeros((17, 9))

for b in range(int(max)):
    for k in range(4):
        for i in range(17):
            for j in range(9):
                if total[b, 3, k] ==i and total[b, 4, k] ==j:
                    avg_resx[i, j] = avg_resx[i, j] + total[b, 6, k]
                    avg_resy[i, j] = avg_resy[i, j] + total[b, 7, k]
                    counter[i, j]  = counter[i, j]  + 1
                    avgx[i, j] = avgx[i, j] + total[b, 0, k]
                    avgy[i, j] = avgy[i, j] + total[b, 1, k]
                    avgz[i, j] = avgz[i, j] + total[b, 2, k]
avg_resx = avg_resx/counter
avgx =avgx/counter
avgy = avgy/counter
avgz = avgz/counter
avg_resy = avg_resy/counter
for b in range(int(max)):
    for k in range(4):
        for i in range(17):
            for j in range(9):
                if total[b, 3, k] ==i and total[b,4, k] ==j:
                    sumsqx[i, j] = sumsqx[i, j] + (avg_resx[i, j] - total[b, 6, k])**2
                    sumsqy[i, j] = sumsqy[i, j] + (avg_resy[i, j] - total[b, 7, k])**2

sumsqx = np.sqrt(sumsqx/ (counter -1) )
sumsqy = np.sqrt(sumsqy/ (counter -1) )

xindex = np.zeros((17, 9))
yindex = np.zeros((17, 9))
not_usedx = []
not_usedy = []

for i in range(17):
    for j in range(9):
        xindex[i, j] = i
        yindex[i, j] = j


sumsqx = sumsqx.reshape((17*9, 1))
sumsqy = sumsqy.reshape((17*9, 1))
xindex = xindex.reshape((17*9, 1))
yindex = yindex.reshape((17*9, 1))
avg_resx = avg_resx.reshape((17*9, 1))
avg_resy = avg_resy.reshape((17*9, 1))
counter = counter.reshape((17*9, 1))
avgx = avgx.reshape((17*9, 1))
avgy = avgy.reshape((17*9, 1))
avgz = avgz.reshape((17*9, 1))

for i in range(17*9):
    if sumsqx[i] == 0 and sumsqy[i] == 0:
        not_usedx.append(i)
sumsqx = np.delete(sumsqx, not_usedx, axis = 0)
sumsqy = np.delete(sumsqy, not_usedx, axis = 0)
xindex = np.delete(xindex, not_usedx, axis = 0)
yindex = np.delete(yindex, not_usedx, axis = 0)
avg_resx = np.delete(avg_resx, not_usedx, axis = 0)
avg_resy = np.delete(avg_resy, not_usedx, axis = 0)
counter = np.delete(counter, not_usedx, axis = 0)
avgx = np.delete(avgx, not_usedx, axis = 0)
avgy = np.delete(avgy, not_usedx, axis = 0)
avgz = np.delete(avgz, not_usedx, axis = 0)
print(avgz.shape)
zer = np.zeros((len(sumsqx), 1))
final_res = np.hstack(( avgx, avgy, avgz, xindex, yindex, zer, avg_resx, avg_resy, sumsqx, sumsqy, counter))
np.savetxt("828_avg_res.csv", final_res, delimiter=",")




