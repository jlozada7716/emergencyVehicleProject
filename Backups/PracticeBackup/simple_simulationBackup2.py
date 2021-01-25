import numpy as np
import matplotlib.pyplot as plt 
from matplotlib.animation import FuncAnimation
import simUtilities  # load package
import os, sys 
# add package location to system path
sys.path.append(os.path.join(os.sep, 'gitlab_repos', 'emergency_vehicle_cooperative_driving', 'pyscripts'))

lanePlacement = .5 #Horizontal center of top and bottom lane

class myVehicle:
	vehicleDict = {}
	id = None
	x = 0
	y = 0
	speed = 0
	maxSpeed = None
	acceleration = 0.1
	decceleration = 0.1
	maxAcceleration = 3
	maxDecceleration = 3
	vy = None
	trajectory = []
	length = 1
	tau = 11
	followTrajectory = False
	lane = None
	leadingVehicle = None
	followingVehicle = None
	distanceToLeadingVehicle = 0
	
	def __init__(self, vehicleDict, id = None, lane = 0, speed=0.2, vy=0.05):
		if (id == None):
			self.id = len(vehicleDict) + 1
		else:
			self.id = id
		self.vehicleDict = vehicleDict
		self.lane = lane
		self.y = lane
		self.speed = speed
		self.maxSpeed = speed
		# self.decceleration = speed * 0.03
		self.vy = vy
		self.leadingVehicle = self.getLeadingVehicle(targetLane=self.lane)
		self.targetSpeed = speed
		
	def advance(self):
		slowingDown = False
		# self.x = self.x + self.speed
		# self.y = self.y + self.vy
		# if self.y > 2.5:
		# 	self.vy = -np.abs(self.vy)
		# if self.y < -2.5:
		# 	self.vy = np.abs(self.vy)
		if self.followTrajectory and len(self.trajectory) > 0:
			# pdb.set_trace()
			nextNode = self.trajectory.pop(0)  # get the next node on the trajectory
			# adjust the speed according to the next position in the trajectory
			print(nextNode[2] - self.lane)
			if (nextNode[2] != self.lane) and not self.changeLane(nextNode[2] - self.lane):
				# print('emergency vehicle not in the correct lane. Recalculating')
				self.trajectory = []  # rejecting the proposed trajectory
			self.speed = np.minimum(nextNode[0] - self.x,
									self.maxSpeed + 0.5)  # 0.5 is to compensate for the rounding effect in the trajectory computation algorithm
			# check if this speed is safe and adjust accordingly
			if self.leadingVehicle != None:
				# predict leading vehicle's position
				lvPosition = self.leadingVehicle.x + self.leadingVehicle.speed
				# set speed so as to no exceed safe position
				safePosition = self.leadingVehicle.x - self.leadingVehicle.length - self.speed * self.tau
				if self.x + self.speed >= safePosition:
					self.speed = np.maximum(0, safePosition - self.x)
			# if projected trajectory is inconsistent with the current path, reject the trajectory.
			if np.abs(self.speed + self.x - nextNode[0]) > 2 * self.speed:
				# print('vehicle %d too far behind the proposed trajectory. Rejecting trajectory'%self.id)
				self.trajectory = []  # rejecting the proposed trajectory

		else:  # not following any trajectory
			if self.leadingVehicle != None:  # implementing safety conditions and lane change if possible
				# predict leading vehicle's position
				lvPosition = self.leadingVehicle.x + self.leadingVehicle.speed
				# set speed so as to no exceed safe position
				safePosition = self.leadingVehicle.x - self.leadingVehicle.length - self.speed * self.tau
				if self.x + self.speed >= safePosition and self.leadingVehicle.y == self.y:
					self.matchLeadingSpeed(safePosition)
					slowingDown = True
					# self.speed = np.maximum(0, safePosition - self.x)
					# change lane if possible
					# if not self.inFreezeMode() and self.lcSpeedGain: self.changeLanceToIncreaseSpeed()

			# randomly vary maxSpeed to avoid clutter
			if (not self.followTrajectory) and (np.random.rand() < 0.01):
				self.maxSpeed = self.maxSpeed + np.random.normal(loc=0, scale=.05)
			# accelerate the vehicle to the maximum speed
			if (not slowingDown):
				self.speed = np.minimum(self.speed + self.acceleration, self.maxSpeed)
		self.x = self.speed + self.x  # advance
		self.y = self.vy + self.y

		if self.leadingVehicle != None:
			self.distanceToLeadingVehicle = self.distanceToLeadingVehicle + self.leadingVehicle.x - self.x

	def changeLane(self, direction): 	# shifts the vehicle across a lane
		if (direction == 1):
			shift = self.speed * 0.01
		if (direction == 0):
			shift = -self.speed * 0.01
		shift = np.minimum(shift, 0.08)
		shift = np.maximum(shift, -0.08)

		if (self.lane == lanePlacement and shift > 0):
			shift = -shift
		if (self.lane == -lanePlacement and shift < 0):
			shift = -shift
		self.vy = shift
		self.leadingVehicle = self.getLeadingVehicle(self.lane)
		return True

	def isClose(self, lane):
		if (np.abs(self.y - lane) < (lanePlacement/10) and (np.abs(self.lane - self.y) > (lanePlacement/10))):
			self.lane = lane
			self.y = lane
			self.vy = 0
			self.leadingVehicle = self.getLeadingVehicle(lane)

	def getLeadingVehicle(self, targetLane):
		leadingVehicle = None
		# Set Leading Vehicle
		for vid, v in self.vehicleDict.items():
			if v.lane == targetLane and v.x > self.x and (leadingVehicle==None or v.x < leadingVehicle.x):
				leadingVehicle = v
		return leadingVehicle

	def getFollowingVehicle(self, targetLane):
		followingVehicle = None
		for vid, v in self.vehicleDict.items():
			if v.lane == targetLane and v.x < self.x and (followingVehicle == None or v.x > followingVehicle.x):
				followingVehicle = v
		return followingVehicle

	def inFreezeMode(self):
		sid = -1
		freezeRange = 20
		if (sid in self.vehicleDict) and (np.abs(self.x-self.vehicleDict[sid].x)<freezeRange) and (self.id != sid):
			return True
		else:
			return False

	def matchLeadingSpeed(self, safePosition):
		if self.x >= safePosition:
			safeOverboardFactor = (self.x - safePosition) * 0.3
			self.speed = np.maximum(self.speed - self.decceleration*safeOverboardFactor, 0)
		elif (self.leadingVehicle.x - self.x <=10):
			self.speed = self.leadingVehicle.speed

class addNCars:
	vehicleDict = {}
	trafficDensity = 0
	aggression = 0

	def __init__(self, vehicleDict, carNum = 1, trafficDensity = 35, aggression = 3):
		self.vehicleDict = vehicleDict
		self.carNum = carNum
		self.trafficDensity = trafficDensity
		self.aggression = aggression

	def step(self):
		self.vehicleDict = Simulation.vehicleDict
		if Simulation.timeStep % self.trafficDensity == 0:		#Create vehicle every 15 timeSteps
			vin = len(self.vehicleDict) + 1
			if (vin > 0):
				vin -= 1
			if vin <= self.carNum - 1: #Limits it to carNum amount of cars
				speed = np.random.normal(loc=7, scale=self.aggression)
				speed = np.minimum(speed, 13)
				speed = np.maximum(speed, 4)
				lane = self.lanePlacer()
				v = myVehicle(Simulation.vehicleDict, vin, lane, speed, 0)
				self.vehicleDict[vin] = v
		return True

	def lanePlacer(self): 	# takes the lane property and places the vehicle in the correct y position
		bounds = lanePlacement*10
		lane = np.random.randint(-bounds, bounds + 1)
		if (lane > 0.33*bounds):
			lane = lanePlacement
		elif (lane < -0.33*bounds):
			lane = -lanePlacement
		else:
			lane = 0
		return lane

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

# class seeAndAvoidCOPY:
# 	vehicleDict = None
# 	sid = None 	# Advancing vehicle
# 	visibleDist = 0 	# How far ahead the vehicle is concerned about
# 	lanes = {-lanePlacement, 0, lanePlacement}
#
# 	def __init__(self, vehicleDict, sid, visibleDist = 5):
# 		self.vehicleDict = vehicleDict
# 		self.sid = sid
# 		self.visibleDist = visibleDist
#
# 	def step(self):
# 		if not self.sid in self.vehicleDict: return	# does not execute if desired vehicle isn't in program
#
# 		for vid in self.vehicleDict:
# 			if ((self.vehicleDict[self.sid].y == self.vehicleDict[vid].y)
# 					and (self.vehicleDict[vid].x - self.vehicleDict[self.sid].x < self.visibleDist)
# 					and vid != self.sid):	# Only shift if same lanes and within visibleDist
# 				self.vehicleDict[self.sid].shift() #Calls the shift function in vehicle
# 			elif (self.vehicleDict[vid].vy != 0 and self.vehicleDict[vid].y != self.vehicleDict[vid].lane):
# 				for lane in self.lanes:
# 					self.vehicleDict[vid].isClose(lane)
# 					# if self.vehicleDict[vid].y == lane:
# 					# 	self.vehicleDict[vid].lane = lane
# 					# 	self.vehicleDict[vid].vy = 0
# 		return True

stopTime = 700  # stop after 700 steps
Simulation = simUtilities.simulation(stopTime=stopTime)  # create a simulation

vehicleAdder = addNCars(Simulation.vehicleDict, 40, 20, 5) # create a listener to add vehicles
Simulation.stepListeners.append(vehicleAdder)

algLister = seeAndAvoid(Simulation.vehicleDict, 70)	# dodge algorithm
Simulation.stepListeners.append(algLister)	# add listener to your simulation

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
	ax.set_xlim(-10, 700)
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











