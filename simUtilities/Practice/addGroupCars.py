import numpy as np
import os, sys  #unsure if needed but just in case
sys.path.append(os.path.join(os.sep, 'gitlab_repos', 'emergency_vehicle_cooperative_driving','pyscripts','simUtilities'))

from simUtilities.Practice.myVehicle import myVehicle

lanePlacement = 0.5

class addGroupCars():
    vehicleDict = {}
    trafficDensity = 0
    aggression = 0
    timeStep = 0
    prevLane = 0
    safePlacement = True
    donePlacing = False


    def __init__(self, vehicleDict, timeStep, carNum = 1, trafficDensity = 35, aggression = 0.15):
        self.vehicleDict = vehicleDict
        self.timeStep = timeStep
        self.carNum = carNum
        self.trafficDensity = trafficDensity
        self.aggression = aggression

    def step(self):
        self.timeStep += 1
        if self.timeStep == 200 and not self.donePlacing:
            for i in range(0, 50): # In case the cars weren't all placed in time
                print("Didn't Finish")
        if self.safePlacement == True:
            self.safePlacement = self.safeToPlace()
        if self.timeStep % self.trafficDensity == 0 and self.safePlacement:		#Create vehicle every 15 timeSteps
            self.placeCar()
            self.placeCar()
            self.placeCar()
        return True

    def safeToPlace(self):
        if len(self.vehicleDict) > 10:
            for i in range(0, 5):
               if (self.vehicleDict[i].x >= 988):
                  return False
        return True

    def lanePlacer(self): 	# takes the lane property and places the vehicle in the correct y position
        bounds = lanePlacement*10 # Gets rid of the decimal
        if self.prevLane == -lanePlacement:
            lane = np.random.randint(0, bounds + 1)
        elif self.prevLane == lanePlacement:
            lane = np.random.randint(-bounds, 1)
        elif self.prevLane == 0:
            lane = np.random.randint(0, 2)
            if lane == 0:
                self.prevLane = -lanePlacement
                return -lanePlacement
            else:
                self.prevLane = lanePlacement
                return lanePlacement
        # lane = np.random.randint(-bounds, bounds + 1)
        if (lane >= 2.5):
            lane = lanePlacement
        elif (lane <= -2.5):
            lane = -lanePlacement
        else:
            lane = 0
        self.prevLane = lane
        return lane

    def threeLanePlacer(self):
        if self.prevLane == 0:
           lane = lanePlacement
        elif self.prevLane == lanePlacement:
            lane = -lanePlacement
        else:
            lane = 0
        self.prevLane = lane
        return lane

    def randomSpeed(self): # Outputs a random speed around a mean of 8.1 m/s
        speed = np.random.normal(loc=5.1, scale=self.aggression)
        speed = np.minimum(speed, 13)
        speed = np.maximum(speed, 4)
        return speed

    def placeCar(self): # Places a single car and checks if the cars are done being placed
        vin = len(self.vehicleDict) + 1
        if (vin > 0):
            vin -= 1
        if vin <= self.carNum - 1:  # Limits it to carNum amount of cars
            speed = self.randomSpeed()
            lane = self.threeLanePlacer()
            v = myVehicle(self.vehicleDict, vin, lane, speed, 0)
            self.vehicleDict[vin] = v
            print("Vehicles placed: ", vin)
        if vin == self.carNum - 1:
            print("Done Placing")
            self.donePlacing = True
