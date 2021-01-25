import numpy as np
import os, sys
sys.path.append(os.path.join(os.sep, 'gitlab_repos', 'emergency_vehicle_cooperative_driving','pyscripts','simUtilities'))

from .vehicle import vehicle
from .simulation import simulation
import pdb


#surrounding vehicles setup
class addVehiclesForExample():
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
		if self.Simulation.timeStep >=0 and self.Simulation.timeStep<= 20:
			vid = len(self.vehicleDict)+1
			v = vehicle(self.vehicleDict,id=vid,lane=1,maxSpeed=2,lcSpeedGain=False)
			self.vehicleDict[vid] = v
		if self.Simulation.timeStep == 14:
			vid = len(self.vehicleDict)+1
			v = vehicle(self.vehicleDict,id=vid,lane=2,maxSpeed=3,lcSpeedGain=False)
			self.vehicleDict[vid] = v
		if self.Simulation.timeStep == 17:
			vid = len(self.vehicleDict)+1
			v = vehicle(self.vehicleDict,id=vid,lane=0,maxSpeed=4,lcSpeedGain=False)
			self.vehicleDict[vid] = v
		if self.Simulation.timeStep == 24:
			vid = -1
			v = vehicle(self.vehicleDict,id=vid,lane=1,maxSpeed=10,lcSpeedGain=False)
			v.followTrajectory = True
			self.vehicleDict[vid] = v
			
		return True