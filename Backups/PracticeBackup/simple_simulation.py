import numpy as np
import matplotlib.pyplot as plt 
from matplotlib.animation import FuncAnimation
import simUtilities  # load package
import os, sys 
# add package location to system path
sys.path.append(os.path.join(os.sep, 'gitlab_repos', 'emergency_vehicle_cooperative_driving', 'pyscripts'))

lanePlacement = .5 #Horizontal center of top and bottom lane

class myBoomListener: 
	vehicleDict = {}
	
	def __init__(self,vehicleDict):
		self.vehicleDict = vehicleDict
		 
		
	def step(self):
		for vid in self.vehicleDict:
			if self.vehicleDict[vid].y > 2.5 or self.vehicleDict[vid].y < -2.5:
				print('boom') 

class seeAndAvoid:
	vehicleDict = {}
	# sid = None 	# Advancing vehicle
	visibleDist = 0 	# How far ahead the vehicle is concerned about
	lanes = {-lanePlacement, 0, lanePlacement}

	def __init__(self, vehicleDict, visibleDist = 5):
		self.vehicleDict = vehicleDict
		# self.sid = sid
		self.visibleDist = visibleDist
	def step(self):
		# if not self.sid in self.vehicleDict: return	# does not execute if desired vehicle isn't in program
		for sid in self.vehicleDict:
			for vid in self.vehicleDict:
				if ((self.vehicleDict[sid].y == self.vehicleDict[vid].y) and (self.vehicleDict[vid].x - self.vehicleDict[sid].x < self.visibleDist)
					and self.vehicleDict[vid].x - self.vehicleDict[sid].x > 0 and vid != sid
					and self.vehicleDict[sid].speed > self.vehicleDict[vid].speed):	# Only shift if same lanes and within visibleDist
						if (np.random.rand() <= 0.08):
							direction = np.random.randint(0, 2) #Picks random direction between 0 and 1
							direction = self.directionBound(self.vehicleDict[sid].lane, direction) #Makes sure the direction isn't out of bounds
							self.vehicleDict[sid].changeLane(direction) #Calls the shift function in vehicle

				elif (self.vehicleDict[sid].vy != 0 and self.vehicleDict[sid].y != self.vehicleDict[sid].lane):
					for lane in self.lanes:
						self.vehicleDict[sid].isClose(lane)
		return True

	def directionBound(self, lane, direction):
		if (lane == lanePlacement and direction == 1):
			direction = 0
		elif (lane == -lanePlacement and direction == 0):
			direction = 1

		return direction

stopTime = 700  # stop after 700 steps
Simulation = simUtilities.simulation(stopTime=stopTime)  # create a simulation

vehicleAdder = simUtilities.addNCars(Simulation.vehicleDict, Simulation.timeStep, 10, 10, 4) # create a listener to add vehicles
Simulation.stepListeners.append(vehicleAdder)

#	algLister = seeAndAvoid(Simulation.vehicleDict, 70)	# dodge algorithm
#	Simulation.stepListeners.append(algLister)	# add listener to your simulation

visionLister = simUtilities.sensoredMovement(Simulation.vehicleDict, 50, lanePlacement) # new Dodge algorithm
Simulation.stepListeners.append(visionLister)	#add listener to your simulation

boomLister = myBoomListener(Simulation.vehicleDict)  # create a listener
Simulation.stepListeners.append(boomLister)  # add listener to your simulation

# setting up the figure for animation
fig, ax = plt.subplots()
ln, = plt.plot([], [], 'ro', animated=True)

plt.axhline(y=lanePlacement/2, color='y', linestyle='dashed')
plt.axhline(y=-lanePlacement/2, color='y', linestyle='dashed')
plt.axhline(y=lanePlacement*1.5, color='black', linestyle='solid')
plt.axhline(y=-lanePlacement*1.5, color='black', linestyle='solid')


def getModifiedVehicle():  # will advance the simulation by one step and yields the vehiclelist
		while(Simulation.step()):
			yield Simulation.vehicleDict

def init():
	ax.set_xlim(0, 1000)
	ax.set_ylim(-2, 2)
	return ln,

def update(frame):
	xdata, ydata = [], []
	for vid, v in frame.items(): #ITERATES THROUGH EACH VEHICLE IN THE DICT
		xdata.append(v.x)
		ydata.append(v.y)
	# xdata = [frame.x] # FOR USE WITH SINGLE VEHICLE
	# ydata = [frame.y]
	ln.set_data(xdata, ydata)
	return ln,

frameGenerator = getModifiedVehicle()
ani = FuncAnimation(fig, update, frameGenerator, init_func=init, blit=True, interval = 50)
plt.show()











