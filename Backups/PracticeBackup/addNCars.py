import numpy as np
import os, sys  #unsure if needed but just in case
sys.path.append(os.path.join(os.sep, 'gitlab_repos', 'emergency_vehicle_cooperative_driving','pyscripts','simUtilities'))

from simUtilities.Practice.myVehicle import myVehicle

lanePlacement = 0.5

class addNCars():
    vehicleDict = {}
    trafficDensity = 0
    aggression = 0
    timeStep = 0
    def __init__(self, vehicleDict, timeStep, carNum = 1, trafficDensity = 35, aggression = 3):
        self.vehicleDict = vehicleDict
        self.timeStep = timeStep
        self.carNum = carNum
        self.trafficDensity = trafficDensity
        self.aggression = aggression

    def step(self):
        # self.vehicleDict = Simulation.vehicleDict
        self.timeStep += 1
        if self.timeStep % self.trafficDensity == 0:		#Create vehicle every 15 timeSteps
            vin = len(self.vehicleDict) + 1
            if (vin > 0):
                vin -= 1
            if vin <= self.carNum - 1: #Limits it to carNum amount of cars
                speed = np.random.normal(loc=7, scale=self.aggression)
                speed = np.minimum(speed, 13)
                speed = np.maximum(speed, 4)
                lane = self.lanePlacer()
                v = myVehicle(self.vehicleDict, vin, lane, speed, 0)
                self.vehicleDict[vin] = v
        return True

    def lanePlacer(self): 	# takes the lane property and places the vehicle in the correct y position
        bounds = lanePlacement*10
        lane = np.random.randint(-bounds, bounds + 1)
        if (lane > 0.33*bounds):
            lane = lanePlacement
        elif (lane < -0.33*bounds):
            lane = -lanePlacement
        else:
            lane = 0
        return lane