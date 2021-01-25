import numpy as np
import pdb

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
	tau = 1
	leadingVehicle = None #will point to the vehicle object of the leading vehicle
	vehicleDict = {}
	maxLane = 3
	slowDownMode = False 
	trajectory = []
	followTrajectory = False 
	lcSpeedGain = True
	laneChangeCount = 0
	distanceToLeadingVehicle = 0
	
	
	#methods
	def __init__(self,vehicleDict,id=None,maxSpeed=3,lane=0,lcSpeedGain=True):
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
		self.lcSpeedGain = lcSpeedGain
		
		
	def advance(self):
		if self.followTrajectory and len(self.trajectory)>0:
			# pdb.set_trace()
			nextNode = self.trajectory.pop(0)#get the next node on the trajectory 
			#adjust the speed according to the next position in the trajectory 
			if (nextNode[2] != self.lane) and not self.changeLane(nextNode[2]-self.lane,nextNode[0]-self.position):
				# print('emergency vehicle not in the correct lane. Recalculating')
				self.trajectory = [] #rejecting the proposed trajectory  
			self.speed = np.minimum(nextNode[0]-self.position,self.maxSpeed+0.5) #0.5 is to compensate for the rounding effect in the trajectory computation algorithm
			#check if this speed is safe and adjust accordingly
			if self.leadingVehicle != None: 
				#predict leading vehicle's position 
				lvPosition = self.leadingVehicle.position + self.leadingVehicle.speed
				#set speed so as to no exceed safe position 
				safePosition = self.leadingVehicle.position - self.leadingVehicle.length - self.speed*self.tau
				if self.position + self.speed >= safePosition:
					self.speed = np.maximum(0,safePosition-self.position)
			#if projected trajectory is inconsistent with the current path, reject the trajectory. 
			if np.abs(self.speed + self.position - nextNode[0]) > 2*self.speed:
				# print('vehicle %d too far behind the proposed trajectory. Rejecting trajecotry'%self.id) 
				self.trajectory = []#rejecting the proposed trajectory
		
		else: #not following any trajectory 
			#randomly vary maxSpeed to avoid clutter 
			if (not self.followTrajectory) and  (np.random.rand() < 0.01):
					self.maxSpeed = self.maxSpeed + np.random.normal(loc=0,scale=0.05)
			#accelerate the vehicle to the maximum speed 
			self.speed = np.minimum(self.speed+self.acceleration,self.maxSpeed)		
			if self.leadingVehicle != None: #implementing safety conditions and lane change if possible
				#predict leading vehicle's position
				self.leadingVehicle = self.getLeadingVehicle(self, self.lane) #JUST ADDED
				lvPosition = self.leadingVehicle.position + self.leadingVehicle.speed
				#set speed so as to no exceed safe position 
				safePosition = self.leadingVehicle.position - self.leadingVehicle.length - self.speed*self.tau
				if self.position + self.speed >= safePosition:
					self.speed = np.maximum(0,safePosition-self.position)
					#change lane if possible 
					if not self.inFreezeMode() and self.lcSpeedGain: self.changeLanceToIncreaseSpeed()
						
			
		self.position = self.speed + self.position #advance 
		
		if self.leadingVehicle != None:
			self.distanceToLeadingVehicle = self.distanceToLeadingVehicle+ self.leadingVehicle.position - self.position
		
		
	
	def changeLanceToIncreaseSpeed(self):
		for direction in [1,-1]:
			if self.changeLane(direction,self.speed): break 
			#in case the vehicle changed lane, recalculate safety conditions 
			if self.leadingVehicle != None:
				lvPosition = self.leadingVehicle.position + self.leadingVehicle.speed
				#set speed so as to no exceed safe position 
				safePosition = self.leadingVehicle.position - self.leadingVehicle.length - self.speed*self.tau
				if self.position + self.speed >= safePosition: self.speed = np.maximum(0,safePosition-self.position)

	
	def inFreezeMode(self):
		sid = -1
		freezeRange = 20
		if (sid in self.vehicleDict) and (np.abs(self.position-self.vehicleDict[sid].position)<freezeRange) and (self.id != sid):
			return True
		else:
			return False 

	
	# def check_safety(self,targetLane):
		# '''
		# checks to see if the current position of the vehicle will be safe in the target lane 
		# '''
		# l = self.getLeadingVehicle(targetLane)
		# f = self.getFollowingVehicle(targetLane)
		# if (f == None or f.position + f.speed*f.tau <= self.position-self.length) and (l == None or self.position + self.speed*self.tau <= l.position - l.length): return True 
		# else: return False 
		
	def check_safety(self,targetLane,targetSpeed=None):
		'''
		checks to see if the current position of the vehicle will be safe in the target lane 
		'''
		if targetSpeed == None: targetSpeed = self.speed 
		targetPosition = self.position + targetSpeed
		for vid,v in self.vehicleDict.items():
			if v.lane != targetLane: continue 
			vEstPosition = v.position + v.speed*v.tau
			if (vEstPosition > targetPosition - self.length - v.speed*v.tau) and (vEstPosition-v.length < targetPosition+self.speed*self.tau): return False 
		return True
		
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

		
	def changeLane(self,direction,targetSpeed=None): #returns True if successfully changed lane
		'''
		Changes lane in the specified direction. 
		Parameters: 
			direction: the direction to change the lane 
		Returns:
			True if successful in the changing the lane safely, False otherwise
		'''
		if targetSpeed == None: targetSpeed = self.speed 
		if direction not in [-1,1]: return False
		if self.lane+direction not in range(self.maxLane): return False 
		if self.check_safety(targetLane=self.lane+direction,targetSpeed=targetSpeed): 
			#update the following vehicles' leading vehicle 
			vf = self.getFollowingVehicle(self.lane)
			self.lane = self.lane + direction
			if vf!= None: vf.leadingVehicle = vf.getLeadingVehicle(vf.lane)
		else: return False 
		#successfully changed lane. Find leaders according to the advanced position 
		self.position = self.position + targetSpeed
		self.leadingVehicle = self.getLeadingVehicle(self.lane)
		followingVehicle = self.getFollowingVehicle(self.lane)
		self.position = self.position - targetSpeed #resetting because the position will be advanced later within the advance method  
		if followingVehicle != None: followingVehicle.leadingVehicle = self
		#collecting metric for performance analysis
		self.laneChangeCount = self.laneChangeCount + 1
		
		
		return True 
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
