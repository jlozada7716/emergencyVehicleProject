import numpy as np

#define the vehicle class 
class vehicle: 
	#attributes
	id = None
	speed = 0
	position = 0
	lane = 0
	maxSpeed = 3
	acceleration = 1
	decceleration = 1
	maxAcceleration = 3
	maxDecceleration = 3
	length = 1
	tau = 2
	leadingVehicle = None #will point to the vehicle object of the leading vehicle
	vehicleDict = {}
	maxLane = 3
	slowDownMode = False 
	
	
	#methods
	def __init__(self,vehicleDict,id=None,maxSpeed=3,lane=0):
		if id == None:
			self.id = len(vehicleDict)+1
		else:
			self.id = id
		self.maxSpeed = maxSpeed
		self.lane = lane
		#identify leading vehicle
		self.vehicleDict = vehicleDict 
		#set the leading vehicle
		self.leadingVehicle = self.getLeadingVehicle(targetLane=self.lane)
		
		
	def advance(self):
		if self.slowDownMode: 
			self.speed = np.maximum(0,self.speed-self.decceleration)
		else:
			if self.id != -1: #vary speed with a small probability 
				if np.random.rand() < 0.01:
					self.maxSpeed = self.maxSpeed + np.random.normal(loc=0.1,scale=0.05)
			self.speed = np.minimum(self.speed+self.acceleration,self.maxSpeed)		
			if self.leadingVehicle != None: #implementing safety conditions and lane change if possible
				#predict leading vehicle's position 
				lvPosition = self.leadingVehicle.position + self.leadingVehicle.speed
				#set speed so as to no exceed safe position 
				safePosition = self.leadingVehicle.position - self.leadingVehicle.length - self.speed*self.tau
				if self.position + self.speed >= safePosition:
					self.speed = np.maximum(0,safePosition-self.position)
					#if the vehicle can change lane, it will at this point, unless the special vehicle is in proximity
					sid = -1
					# if (sid not in self.vehicleDict) or (np.abs(self.position-self.vehicleDict[sid].position)>20) or self.id == sid:
						# for direction in [1,-1]:
							# if self.changeLane(direction): break 
			
			self.position = self.speed + self.position
		
		
	def check_safety(self,targetLane):
		'''
		checks to see if the current position of the vehicle will be safe in the target lane 
		'''
		l = self.getLeadingVehicle(targetLane)
		f = self.getFollowingVehicle(targetLane)
		if (f == None or f.position + f.speed*f.tau <= self.position-self.length) and (l == None or self.position + self.speed*self.tau <= l.position - l.length): return True 
		else: return False 
		
		
	def getLeadingVehicle(self,targetLane): #get leading vehicle according to current position on target lane
		leadingVehicle = None
		#set the leading vehicle 
		for vid,v in self.vehicleDict.items():
			if v.lane == targetLane and v.position > self.position and (leadingVehicle==None or v.position < leadingVehicle.position): leadingVehicle = v
		return leadingVehicle
		
		
	def getFollowingVehicle(self,targetLane):
		followingVehicle = None
		for vid,v in self.vehicleDict.items():
			if v.lane == targetLane and v.position < self.position and (followingVehicle==None or v.position > followingVehicle.position): followingVehicle = v
		return followingVehicle
		
		
	def changeLane(self,direction): #returns True if successfully changed lane
		'''
		Changes lane in the specified direction. 
		Parameters: 
			direction: the direction to change the lane 
		Returns:
			True if successful in the changing the lane safely, False otherwise
		'''
		if direction not in [-1,1]: return False
		if self.lane+direction not in range(self.maxLane): return False 
		if self.check_safety(targetLane=self.lane+direction): 
			#update the following vehicles' leading vehicle 
			vf = self.getFollowingVehicle(self.lane)
			self.lane = self.lane + direction
			if vf!= None: vf.leadingVehicle = vf.getLeadingVehicle(vf.lane)
		else: return False 
		self.leadingVehicle = self.getLeadingVehicle(self.lane)
		followingVehicle = self.getFollowingVehicle(self.lane)
		if followingVehicle != None: followingVehicle.leadingVehicle = self
		return True 
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
