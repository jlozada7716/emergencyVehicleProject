import numpy as np
import os, sys
sys.path.append(os.path.join(os.sep, 'gitlab_repos', 'emergency_vehicle_cooperative_driving','pyscripts','simUtilities'))

from .myVehicle import myVehicle

class sensoredMovement():
    vehicleDict = {}
    visibleDist = 0
    lanePlacement = 1
    lanes = {}

    def __init__(self, vehicleDict, visibleDist = 100, lanePlacement = 1):
        self.vehicleDict = vehicleDict
        self.visibleDist = visibleDist
        self.lanePlacement = lanePlacement
        self.lanes = {-lanePlacement, 0, lanePlacement}

    def step(self):
        for vid in self.vehicleDict: #Iterates through each vehicle in the dictionary
            if (vid == 9):
               print("yay")
            if self.vehicleDict[vid].slowingDown \
                    and self.vehicleDict[vid].vy == 0 \
                    and self.vehicleDict[vid].leadingVehicle != None: #only executes when the vehicle is slowing down
                for lane in self.lanes:
                    if np.abs(lane - self.vehicleDict[vid].lane) == self.lanePlacement: #Makes sure that it doesn't observe two lanes away
                        lead = self.vehicleDict[vid].getLeadingVehicle(lane)
                        if lead == None:
                            direction = self.laneToDirection(self.vehicleDict[vid].lane, lane)
                            self.vehicleDict[vid].changeLane(direction)
                            break;
                        elif (lead != None):
                            safePosition = lead.x - lead.length - self.vehicleDict[vid].speed * self.vehicleDict[vid].tau
                            if (lead.x - self.vehicleDict[vid].x >= safePosition):
                                if (np.random.rand() <= 1):
                                    direction = self.laneToDirection(self.vehicleDict[vid].lane, lead.lane)
                                    if vid == 3:
                                        print("Nice")
                                    self.vehicleDict[vid].changeLane(direction)
                                    break;

                #
                # if (direction == 0):
                #     lane = self.vehicleDict[vid].lane - self.lanePlacement
                # else:
                #     lane = self.vehicleDict[vid].lane + self.lanePlacement
                # lead = self.vehicleDict[vid].getLeadingVehicle(lane)
                # if (lead != None):
                #     safePosition = lead.x - lead.length - self.vehicleDict[vid].speed * self.vehicleDict[vid].tau
                #     if (lead.x - self.vehicleDict[vid].x > safePosition):
                #        if (np.random.rand() <= 1):
                #             self.vehicleDict[vid].changeLane(direction)
            elif (self.vehicleDict[vid].vy != 0 and self.vehicleDict[vid].y != self.vehicleDict[vid].lane):
                for lane in self.lanes:
                    self.vehicleDict[vid].isClose(lane)
        return True


    def directionBound(self, lane, direction):
        if (lane == self.lanePlacement and direction == 1):
            direction = 0
        elif (lane == -self.lanePlacement and direction == 0):
            direction = 1

        return direction

    def laneToDirection(self, selfLane, leadLane): #0 is down 1 is up
        if selfLane > leadLane:
            direction = 0
        else:
            direction = 1
        return direction