import numpy as np
import os, sys  #unsure if needed but just in case
sys.path.append(os.path.join(os.sep, 'gitlab_repos', 'emergency_vehicle_cooperative_driving','pyscripts','simUtilities'))

from simUtilities.Practice.myVehicle import myVehicle

lanePlacement = 0.5
xSimDistance = 2000


class addGroupCars():
    vehicleDict = {}
    trafficDensity = 0
    aggression = 0
    timeStep = 0
    prevLane = 0
    carNum = None
    safePlacement = True
    donePlacing = False
    start = False
    lane1 = None
    lane2 = None
    lane3 = None


    def __init__(self, vehicleDict, timeStep, carNum = 1, trafficDensity = 35, aggression = 0.15):
        self.vehicleDict = vehicleDict
        self.timeStep = timeStep
        self.carNum = carNum
        self.trafficDensity = trafficDensity
        self.aggression = aggression
        self.lane1 = []
        self.lane2 = []
        self.lane3 = []
        for x in range(0, xSimDistance, 20):
            self.lane1.append(x)
            self.lane2.append(x)
            self.lane3.append(x)

    def step(self):
        self.randomPlace()
        return True

    def randomPlace(self):
        if not self.start:
            for i in range(0, self.carNum):
                lane = np.random.randint(1, 4)
                if lane == 1 and len(self.lane1) > 0:
                    position = np.random.randint(0, len(self.lane1))
                    position = self.lane1.pop(position)
                    self.specificCarPlace(position, lanePlacement)
                elif lane == 2 and len(self.lane2) > 0:
                    position = np.random.randint(0, len(self.lane2))
                    position = self.lane2.pop(position)
                    self.specificCarPlace(position, 0)
                elif len(self.lane3) > 0:
                    position = np.random.randint(0, len(self.lane3))
                    position = self.lane3.pop(position)
                    if i == 4 or i == 7:
                        print(position)
                    self.specificCarPlace(position, -lanePlacement)
                else:
                    i = i - 1
                    print("Didn't Finish")
            self.start = True


    def safeToPlace(self):
        if len(self.vehicleDict) > 10:
            for i in range(0, 5):
               if (self.vehicleDict[i].x >= xSimDistance * 0.95):
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
        speed = np.random.normal(loc=3.3, scale=self.aggression)
        speed = np.minimum(speed, 6)
        speed = np.maximum(speed, 3)
        return speed


    def specificCarPlace(self, x, lane): # Places a single car and checks if the cars are done being placed
        vin = len(self.vehicleDict) + 1
        if (vin > 0):
            vin -= 1
        if vin <= self.carNum - 1:  # Limits it to carNum amount of cars
            speed = self.randomSpeed()
            v = myVehicle(self.vehicleDict, vin, lane, speed, 0, x)
            self.vehicleDict[vin] = v
            # print("Vehicles placed: ", vin)
        if vin == self.carNum - 1:
            print("Done Placing")
            self.donePlacing = True

    def placeCar(self): # Places a single car and checks if the cars are done being placed
        vin = len(self.vehicleDict) + 1
        if (vin > 0):
            vin -= 1
        if vin <= self.carNum - 1:  # Limits it to carNum amount of cars
            speed = self.randomSpeed()
            lane = self.threeLanePlacer()
            v = myVehicle(self.vehicleDict, vin, lane, speed, 0, 0)
            self.vehicleDict[vin] = v
            print("Vehicles placed: ", vin)
        if vin == self.carNum - 1:
            print("Done Placing")
            self.donePlacing = True
