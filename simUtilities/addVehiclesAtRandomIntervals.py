import numpy as np
import os, sys
sys.path.append(os.path.join(os.sep, 'gitlab_repos', 'emergency_vehicle_cooperative_driving','pyscripts','simUtilities'))

from .vehicle import vehicle

#surrounding vehicles setup
class addVehiclesAtRandomIntervals():
	nOfLanes = 3 #default
	trafficDensity = 0.1 #should be a value in the interval (0,1)
	vehicleDict = {}
	
	
	def __init__(self,vehicleDict,nOfLanes=3,trafficDensity=0.1):
		self.vehicleDict = vehicleDict
		self.nOfLanes = nOfLanes
		self.trafficDensity = trafficDensity
		
	
	def initialize(self):
		self.vehicleCount = 0
		gapCount = 0
	
	
	def step(self):
		if np.random.rand() <= self.trafficDensity:
			vid = len(self.vehicleDict)+1
			speed = np.random.normal(loc=3,scale=0.2)
			speed = np.maximum(speed,1)
			speed = np.minimum(speed,5)
			# traci.vehicle.setMaxSpeed(vid,speed)
			v = vehicle(self.vehicleDict,id=vid,lane=np.random.randint(low=0,high=self.nOfLanes),maxSpeed=speed)
			self.vehicleDict[vid] = v
			
		return True