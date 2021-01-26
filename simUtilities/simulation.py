import numpy as np
import time
# np.random.seed(38)

class simulation():
	vehicleDict = {}
	stepListeners = []
	stopTime = 300
	timeStep = 0
	nOfLanes = 3
	emergencyVehicleTime = 0
	
	def __init__(self,stopTime=300,nOfLanes=3):
		self.stopTime = stopTime
		self.nOfLanes = nOfLanes
		self.vehicleDict = {}
		self.stepListeners = []
		self.timeStep = 0

	def step(self): #	will advance the simulation by one step
		# print(self.timeStep)
		# if self.timeStep == 482:
		# 	print('pause')
		self.timeStep = self.timeStep + 1
		# 	print('current time: %d, stop time: %d'%(self.timeStep,self.stopTime))
		if self.timeStep >= self.stopTime: 
			return False #end of simulation
		if not np.mod(self.timeStep,100):
			print('executing time step: %d'%self.timeStep)
		for listener in self.stepListeners:
			listener.step()
		#advance the special vehicle (if exists) first. This way, there is no uncertainty in the advancing of the special vehicle. 
		if -1 in self.vehicleDict: self.vehicleDict[-1].advance()
		tic = time.time()
		for vid,v in self.vehicleDict.items(): 
			if vid == -1: continue
			v.advance()
		toc = time.time()
		# if (toc - tic) > 0.00001:
			# print('Advanced elapsed time: %f' % (toc - tic))
		return True 
