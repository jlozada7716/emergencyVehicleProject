import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np


fig = plt.figure()
ax = fig.add_subplot(111,projection='3d')


with open('vehicle_coordinates.txt', 'r') as inp: 
	lines = inp.read().splitlines()
	
vehicles = []
specialVehicle = []
unsafeZones = []

timeCounter = 0
for line in lines[1:]:
	if line == 'end':
		timeCounter = timeCounter + 1
		if timeCounter == 20:
			break
		else:
			continue
	tokens = line.split(',')
	t = ([float(x) for x in tokens])
	t.append(timeCounter)
	t = tuple(t)
	if t[0] == -1:
		specialVehicle.append(t)
	else:
		vehicles.append(t)
		for x in np.arange(t[1]-1.5,t[1]+1.5,0.5):
			unsafeZones.append((x,t[2],timeCounter))


vids,vps,vlanes,vtimes = zip(*vehicles)
vids = np.array(vids)
vps = np.array(vps)
vlanes = np.array(vlanes)
vtimes = np.array(vtimes)

sids,sps,slanes,stimes = zip(*specialVehicle)
sps = np.array(sps)
slanes = np.array(slanes)
stimes = np.array(stimes)

unsfps,unsflanes,unsftimes = zip(*unsafeZones)

ax.plot(vps[vids==1],vlanes[vids==1],vtimes[vids==1],'g')
ax.plot(vps[vids==1],vlanes[vids==1],vtimes[vids==1],'go')
ax.plot(vps[vids==2],vlanes[vids==2],vtimes[vids==2],'g')
ax.plot(vps[vids==2],vlanes[vids==2],vtimes[vids==2],'go')
ax.plot(vps[vids==3],vlanes[vids==3],vtimes[vids==3],'g')
ax.plot(vps[vids==3],vlanes[vids==3],vtimes[vids==3],'go')
ax.plot(sps,slanes,stimes,'b')
ax.plot(sps,slanes,stimes,'bo')

ax.plot(unsfps,unsflanes,unsftimes,marker='o',markeredgecolor='r',markerfacecolor='r',markersize=2,linestyle='')
#ax.view_init(elev=15,azim=-122)
#ax.view_init(elev=48,azim=15)
ax.view_init(elev=28,azim=-104)
ax.set_xlabel('position')
ax.set_ylabel('lane')
ax.set_zlabel('time')
plt.show()
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	