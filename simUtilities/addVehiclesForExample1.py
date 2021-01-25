import numpy as np
import os, sys
sys.path.append(os.path.join(os.sep, 'gitlab_repos', 'emergency_vehicle_cooperative_driving','pyscripts','simUtilities'))

from .vehicle import vehicle
from .simulation import simulation
import pdb


#surrounding vehicles setup
class addVehiclesForExample1():
	nOfLanes = 3 #default
	vehicleDict = {}
	Simulation = None
	
	
	def __init__(self,vehicleDict,nOfLanes=3,Simulation=None):
		self.vehicleDict = vehicleDict
		self.nOfLanes = nOfLanes
		self.Simulation = Simulation
		
		
	
	def initialize(self):
		self.vehicleCount = 0
		gapCount = 0
	
	
	def step(self):
		if self.Simulation.timeStep ==1:
			vid = 1
			v = vehicle(self.vehicleDict,id=vid,lane=0,maxSpeed=0.5,lcSpeedGain=False)
			self.vehicleDict[vid] = v
			vid = 2
			v = vehicle(self.vehicleDict,id=vid,lane=1,maxSpeed=0.5,lcSpeedGain=False)
			self.vehicleDict[vid] = v
		if self.Simulation.timeStep ==6:
			vid = 3
			v = vehicle(self.vehicleDict,id=vid,lane=1,maxSpeed=0.5,lcSpeedGain=False)
			self.vehicleDict[vid] = v
			vid = -1
			v = vehicle(self.vehicleDict,id=vid,lane=0,maxSpeed=1,lcSpeedGain=False)
			v.followTrajectory = True
			self.vehicleDict[vid] = v
		
			
		return True