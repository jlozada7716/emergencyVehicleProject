import numpy as np
import os, sys
sys.path.append(os.path.join(os.sep, 'gitlab_repos', 'emergency_vehicle_cooperative_driving','pyscripts','simUtilities'))

from .vehicle import vehicle
from .simulation import simulation

import pdb


class greedyAdvance():
	vehicleDict = None 
	sid = None #vehicle to advance
	nOfLanes = 3
	waitTime = 1
	
	def __init__(self,vehicleDict,vehicleIDToAdvance):
		self.vehicleDict = vehicleDict
		self.sid = vehicleIDToAdvance
		
		
	def step(self):
		#check if the interested vehicle is in scene 
		if not self.sid in self.vehicleDict: return 
		if self.waitTime:
			self.waitTime = self.waitTime - 1
			return
		sv = self.vehicleDict[self.sid]
		#make a list of all available lanes 
		availableLanes = list(set(range(self.nOfLanes)).intersection([sv.lane-1,sv.lane,sv.lane+1]))
		#compute the distance to leading vehicle in all these lanes
		laneDistancePairs = []
		for availableLane in availableLanes:
			lv = sv.getLeadingVehicle(targetLane=availableLane)
			if lv == None: laneDistancePairs.append((availableLane,np.inf))
			else: laneDistancePairs.append((availableLane,lv.position-sv.position)) 
		#arrange them in descending order 
		laneDistancePairs.sort(key = lambda x: x[1],reverse=True)
		#if the current leader is farthest, don't do anything 
		#print(laneDistancePairs)
		#go through the list and change lane when you can 
		for pair in laneDistancePairs:
			if pair[0] == sv.lane: return 
			if sv.changeLane(pair[0]-sv.lane): return 
		
		
		
		
		
		
		
		
		
		
		
		
		
		