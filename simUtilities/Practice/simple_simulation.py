import numpy as np
import matplotlib.pyplot as plt 
from matplotlib.animation import FuncAnimation
import simUtilities  # load package
import os, sys
import time
# add package location to system path
sys.path.append(os.path.join(os.sep, 'gitlab_repos', 'emergency_vehicle_cooperative_driving', 'pyscripts'))

np.random.seed(7)
lanePlacement = .5 #Horizontal center of top and bottom lane
from simUtilities.Practice.myVehicle import myVehicle

class myBoomListener: 
	vehicleDict = {}
	
	def __init__(self,vehicleDict):
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
			if v.speed > 15:
				for i in range(0, 100000):
					print("CRASH ")
			if follow != None and follow.id != v.id:
				if v.x == follow.x and v.y == follow.y:
					for i in range(0, 100000):
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
                speed = np.random.normal(loc=8.2, scale=0.5)
                speed = np.minimum(speed, 13)
                speed = np.maximum(speed, 4)
                print("Vehicle #", vin, " Speed: ", speed)
                # if (vin == 0):
                #     speed = 8
                #     print(vin, " speed: ", speed)
                # else:
                #     speed = 11
                #     print(vin, " speed: ", speed)
                v = myVehicle(self.vehicleDict, vin, 0, speed, 0)
                self.vehicleDict[vin] = v
                # if vin == self.carNum - 1:
                #     print("Done Placing")
        return True


def analyzeAverageVehicleSpeed():
	tic = time.time()
	iterationSpeedList = []	# To collect average speed within a single iteration
	iterationSpeedAverageList = []	# To collect average speed among many iterations
	with open('AverageVehicleSpeedDataTrial7_100Iterations.csv', 'w') as out: #open file
		for vehicles in range(30, 156, 5): #increment by 5
			itShift = (vehicles - 20) * 100 # For seed
			print('vehicleAmount #%d' % vehicles)
			for iteration in range(0, 100):
				print('iteration #%d' % iteration)
				#perform Simulation
				np.random.seed(seed=(iteration + itShift + 50000))
				stopTime = 1250 # Data is only recorded from 1000 to 1200
				Simulation = simUtilities.simulation(stopTime=stopTime)  # starts the simulation

				vehicleAdder = simUtilities.addGroupCars(Simulation.vehicleDict, Simulation.timeStep, vehicles, 2, 0.4)   # create a listener to add vehicles
				Simulation.stepListeners.append(vehicleAdder)

				visionLister = simUtilities.sensoredMovement(Simulation.vehicleDict, 50, lanePlacement, Simulation)  # new Dodge algorithm
				Simulation.stepListeners.append(visionLister)  # add listener to your simulation

				speedCollector = simUtilities.vehicleSpeedCollector(Simulation, iterationSpeedList)
				Simulation.stepListeners.append(speedCollector)

				crashListen = crashListener(Simulation.vehicleDict)
				Simulation.stepListeners.append(crashListen)

				for i in range(Simulation.stopTime):
					Simulation.step()

				sum = 0
				for i in iterationSpeedList:
					sum += i
				averageSpeed = sum / len(iterationSpeedList) # Average Speed of single iteration
				print("Iteration ", iteration, "'s Average Speed: ", averageSpeed)
				iterationSpeedAverageList.append(averageSpeed)
				iterationSpeedList.clear()
				sum = 0

			averagesSum = 0
			for i in iterationSpeedAverageList:
				averagesSum += i
			finalAverageSpeed = averagesSum / len(iterationSpeedAverageList)  # Average speed of all the iteration for a number of vehicles
			print("Iterations Recorded: ", len(iterationSpeedAverageList))
			print("Final Average Time", finalAverageSpeed)
			out.write('%d,%f\n' % (vehicles, finalAverageSpeed))
			iterationSpeedAverageList.clear()
			averagesSum = 0
	toc = time.time()
	print('elapsed time: %f' % (toc - tic))

def analyzeEmergencyResults():
	tic = time.time()
	iterationTimeList = []
	sum = 0
	with open('VehicleSimulatorDataTrial5.csv', 'w') as out:
		for vehicles in range(20, 61, 2):
			itShift = (vehicles - 20) * 500
			print('vehicleAmount #%d' % vehicles)
			# out.write('EmergencyEfficiencyData\n')
			for iteration in range(100, 600):
				print('iteration #%d' % iteration)
				# perform Simulation
				# print('EmergencyAlgo:')
				np.random.seed(seed=(iteration+itShift+10000))
				stopTime = 2000
				insertTime = 500
				Simulation = simUtilities.simulation(stopTime=stopTime)  # starts the simulation

				vehicleAdder = simUtilities.addNCars(Simulation.vehicleDict, Simulation.timeStep, vehicles, 2, 0.3)  # create a listener to add vehicles
				Simulation.stepListeners.append(vehicleAdder)

				specialVehicleAdder = simUtilities.addSpecialVehicle(Simulation, insertTime, 0)
				Simulation.stepListeners.append(specialVehicleAdder)

				visionLister = simUtilities.sensoredMovement(Simulation.vehicleDict, 50, lanePlacement, Simulation)  # new Dodge algorithm
				Simulation.stepListeners.append(visionLister)  # add listener to your simulation

				emergencyListener = simUtilities.emergencyActiveListener(Simulation.vehicleDict, 200)
				Simulation.stepListeners.append(emergencyListener)

				dataCollector = simUtilities.emergencyLoopWatch(Simulation)
				Simulation.stepListeners.append(dataCollector)

				crashListen = crashListener(Simulation.vehicleDict)
				Simulation.stepListeners.append(crashListen)
				loopX = -3000 	# Default in case vehicle never spawns
				for i in range(Simulation.stopTime):
					Simulation.step()

				if -1 in Simulation.vehicleDict:
					eV = Simulation.vehicleDict[-1]
					if eV.loopDone:
						loopX = eV.loopX
				if eV.loopX < 100 and loopX != -3000:
					loopX = eV.loopX + 1000
				# Each timeStep is one half second
				# timeLoop = (loopX - eV.insertX) / ((eV.loopTime - eV.insertTime) * 2)
				if (loopX != -3000):
					timeLoop = (eV.loopTime - eV.insertTime) * 1000 / loopX
					iterationTimeList.append(timeLoop)
				# out.write('%d,%f\n' % (iteration, timeLoop))
			for i in iterationTimeList:
				sum += i
			average = sum / len(iterationTimeList)
			print("Iterations Recorded: ", len(iterationTimeList))
			print("Average Time", average)
			out.write('%d,%f\n' % (vehicles, average))
			iterationTimeList.clear()
			sum = 0
	toc = time.time()
	print('elapsed time: %f' % (toc - tic))



# analyzeEmergencyResults()
# analyzeAverageVehicleSpeed()

stopTime = 1400  # stop after 700 steps
Simulation = simUtilities.simulation(stopTime=stopTime)  # create a simulation

vehicleAdder = simUtilities.addGroupCars(Simulation.vehicleDict, Simulation.timeStep, 115, 2, 0.15) # create a listener to add vehicles
Simulation.stepListeners.append(vehicleAdder)

# vehicleAdder = simUtilities.addGroupCar(Simulation.vehicleDict, Simulation.timeStep, 20, 2, 0.4)
# Simulation.stepListeners.append(vehicleAdder)

# specialVehicleAdder = simUtilities.addSpecialVehicle(Simulation, 200, 0)
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
