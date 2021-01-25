import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import simUtilities  # load package
import os, sys
import time


np.random.seed(10)
from simUtilities.Practice.myVehicleExperiment import myVehicle

# add package location to system path
sys.path.append(os.path.join(os.sep, 'gitlab_repos', 'emergency_vehicle_cooperative_driving', 'pyscripts'))

lanePlacement = .5  # Horizontal center of top and bottom lane




class myBoomListener:
    vehicleDict = {}

    def __init__(self, vehicleDict):
        self.vehicleDict = vehicleDict

    def step(self):
        for vid in self.vehicleDict:
            if self.vehicleDict[vid].y > 2.5 or self.vehicleDict[vid].y < -2.5:
                print('boom')


class crashListener:
    vehicleDict = {}

    def __init__(self, vehicleDict):
        self.vehicleDict = vehicleDict

    def step(self):
        for vid in self.vehicleDict:
            v = self.vehicleDict[vid]
            follow = v.getFollowingVehicle(v.y)
            if follow != None and follow.id != v.id:
                if v.x == follow.x and v.y == follow.y:
                    for i in range(0, 1000000):
                        print("CRASH ")
        return True

class addCarsExp:
    vehicleDict = {}
    trafficDensity = 0
    carNum = 0
    timeStep = 0
    def __init__(self, vehicleDict, timeStep, carNum, trafficDensity):
        self.vehicleDict = vehicleDict
        self.timeStep = timeStep
        self.carNum = carNum
        self.trafficDensity = trafficDensity

    def step(self):
        self.timeStep += 1
        if self.timeStep % self.trafficDensity == 0:  # Create vehicle every 15 timeSteps
            vin = len(self.vehicleDict) + 1
            if (vin > 0):
                vin -= 1
            if vin <= self.carNum - 1:  # Limits it to carNum amount of cars
                speed = np.random.normal(loc=8.2, scale=0.3)
                speed = np.minimum(speed, 13)
                speed = np.maximum(speed, 4)
                # print("Vehicle #", vin, " Speed: ", speed)
                # if (vin == 0):
                #     speed = 8
                #     print(vin, " speed: ", speed)
                # else:
                #     speed = 9
                #     print(vin, " speed: ", speed)
                v = myVehicle(self.vehicleDict, vin, 0, speed, 0)
                self.vehicleDict[vin] = v
                # if vin == self.carNum - 1:
                #     print("Done Placing")
        return True


stopTime = 1200  # stop after 700 steps
Simulation = simUtilities.simulation(stopTime=stopTime)  # create a simulation

# vehicleAdder = addCarsExp(Simulation.vehicleDict, Simulation.timeStep, 50, 2) # create a listener to add vehicles
# Simulation.stepListeners.append(vehicleAdder)

vehicleAdder = simUtilities.addNCars(Simulation.vehicleDict, Simulation.timeStep, 110, 1, 0.5) # create a listener to add vehicles
Simulation.stepListeners.append(vehicleAdder)
#
# specialVehicleAdder = simUtilities.addSpecialVehicle(Simulation, 500, 0)
# Simulation.stepListeners.append(specialVehicleAdder)

visionLister = simUtilities.sensoredMovement(Simulation.vehicleDict, 50, lanePlacement, Simulation) # new Dodge algorithm
Simulation.stepListeners.append(visionLister)	#add listener to your simulation

# emergencyListener = simUtilities.emergencyActiveListener(Simulation.vehicleDict, 200)
# Simulation.stepListeners.append(emergencyListener)

boomLister = myBoomListener(Simulation.vehicleDict)  # create a listener
Simulation.stepListeners.append(boomLister)  # add listener to your simulation

# setting up the figure for animation
fig, ax = plt.subplots()
xdata, ydata = [], []
ln, = plt.plot([], [], 'ro', animated=True)
ln1, = plt.plot([],[], 'bo', animated=True)

plt.axhline(y=lanePlacement/2, color='w', linestyle='dashed')
plt.axhline(y=-lanePlacement/2, color='w', linestyle='dashed')
plt.axhline(y=lanePlacement*1.5, color='black', linestyle='solid')
plt.axhline(y=-lanePlacement*1.5, color='black', linestyle='solid')
rectangle = plt.Rectangle((0, -0.75), width=1000, height=1.5, fill=True, color='#333333')
rectangleBackround = plt.Rectangle((0, -2), width = 1000, height=4, fill = True, color='#CCCCCC')
rectangleBackround = plt.Rectangle((-15, -13), width = 30, height=26, fill = True, color='#CCCCCC')
# circle1 = plt.Circle((0,0), 9.75, color='w', linestyle='dashed', fill=False)
# circle2 = plt.Circle((0,0), 8.25, color='w', linestyle='dashed', fill=False)
# circle3 = plt.Circle((0,0), 11.25, color='black', linestyle='solid', fill=False)
# circle4 = plt.Circle((0,0), 6.75, color='black', linestyle='solid', fill=False)
# circleBackround = plt.Circle((0,0), 11.25, color='#333333', fill = True)
# circleBackround2 = plt.Circle((0,0), 6.75, color='#7EC850', fill = True)



def getModifiedVehicle():  # will advance the simulation by one step and yields the vehiclelist
		while(Simulation.step()):
			yield Simulation.vehicleDict

def init():
	# ax.set_xlim(-15, 15)
	# ax.set_ylim(-13, 13)
	ax.set_xlim(0, 1000)
	ax.set_ylim(-2, 2)
	ax.add_artist(rectangleBackround)
	ax.add_artist(rectangle)
	# ax.add_artist(circleBackround)
	# ax.add_artist(circle1)
	# ax.add_artist(circle2)
	# ax.add_artist(circle3)
	# ax.add_artist(circle4)
	# ax.add_artist(circleBackround2)
	return ln,

def update(frame):
	xdata, ydata = [], []
	sXdata, sYdata = [], []

	for vid, v in frame.items(): #ITERATES THROUGH EACH VEHICLE IN THE DICT
		r = v.y * 3 + 9
		theta = np.radians(-v.x * 360 / 1000)
		if vid == -1:
			# sXdata.append(r*np.cos(theta))
			# sYdata.append(r*np.sin(theta))
			sXdata.append(v.x)
			sYdata.append(v.y)
			ln1.set_data(sXdata, sYdata)
		# xdata.append(r*np.cos(theta))
		# ydata.append(r*np.sin(theta))
		xdata.append(v.x)
		ydata.append(v.y)
	ln.set_data(xdata, ydata)
	return ln, ln1

frameGenerator = getModifiedVehicle()
ani = FuncAnimation(fig, update, frameGenerator, init_func=init, blit=True, interval = 50)
plt.show()