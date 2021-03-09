import numpy as np
import os, sys
sys.path.append(os.path.join(os.sep, 'gitlab_repos', 'emergency_vehicle_cooperative_driving','pyscripts','simUtilities'))

from simUtilities.Practice.myVehicle import myVehicle
from simUtilities.simulation import simulation

class addSpecialVehicle():
	Simulation = None 
	insertTime = 0
	
	def __init__(self,Simulation, insertTime):
		self.Simulation = Simulation 
		self.insertTime = insertTime
		
	def step(self):
		if self.Simulation.timeStep == self.insertTime and (-1 not in self.Simulation.vehicleDict):
			vehicleToReplace = len(self.Simulation.vehicleDict) - 1
			v = self.Simulation.vehicleDict[vehicleToReplace]
			v.id = -1
			v.insertTime = self.Simulation.timeStep
			v.maxSpeed = v.maxSpeed + 1
			v.insertX = v.x # Data Collector needs to be updated as vehicle doesn't spawn at 0
			self.Simulation.vehicleDict[-1] = v
			del self.Simulation.vehicleDict[vehicleToReplace]
			print("Emergency Vehicle Spawned")
		return True
