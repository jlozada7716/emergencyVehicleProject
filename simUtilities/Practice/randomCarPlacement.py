import numpy as np
import os, sys  #unsure if needed but just in case
sys.path.append(os.path.join(os.sep, 'gitlab_repos', 'emergency_vehicle_cooperative_driving','pyscripts','simUtilities'))

from simUtilities.Practice.myVehicle import myVehicle

lanePlacement = 0.5


class randomCarPlacement():
    vehicleDict = {}
    carNum = None
    aggression = None
    laneSpace = []


    def __init__(self, vehicleDict = {}, carNum = 40, aggression=0.25):
        self.vehicleDict = vehicleDict
        self.carNum = carNum
        self.aggression = aggression
        lanePlacements = []
        for i in (0, 1001, 15): lanePlacements.add(i)
        for i in (0, 3): self.laneSpace = lanePlacements

    def step(self):

        return True

