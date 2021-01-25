import numpy as np
import os, sys
sys.path.append(os.path.join(os.sep, 'gitlab_repos', 'emergency_vehicle_cooperative_driving','pyscripts','simUtilities'))

from simUtilities.Practice.myVehicle import myVehicle
from simUtilities.simulation import simulation

class addSpecialVehicle():
	Simulation = None 
	insertTime = 0
	lanePlacement = 0
	lane = 0
	lanes = {}
	
	def __init__(self,Simulation, insertTime, lanePlacement = 1):
		self.Simulation = Simulation 
		self.insertTime = insertTime
		self.lanePlacement = lanePlacement
		self.lanes = {-lanePlacement, 0, lanePlacement}
		lane = np.random.randint(0, 3)
		lane = self.intToLane(lane)
		
	def step(self):
		if self.Simulation.timeStep == self.insertTime and (-1 not in self.Simulation.vehicleDict):
			vehicleToReplace = len(self.Simulation.vehicleDict) - 1
			v = self.Simulation.vehicleDict[vehicleToReplace]
			v.id = -1
			v.insertTime = self.Simulation.timeStep
			v.insertX = v.x # Data Collector needs to be updated as vehicle doesn't spawn at 0
			v.m = 0.1
			v.l = 0.7
			self.Simulation.vehicleDict[-1] = v
			del self.Simulation.vehicleDict[vehicleToReplace]
			print("Emergency Vehicle Spawned")
		return True

	def intToLane(self, lane): #Converts integer into lane value
		if lane == 0:
			lane = -self.lanePlacement
		elif lane == 1:
			lane = 0
		else:
			lane = self.lanePlacement
		return lane