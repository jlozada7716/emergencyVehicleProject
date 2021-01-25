import numpy as np
import os, sys
sys.path.append(os.path.join(os.sep, 'gitlab_repos', 'emergency_vehicle_cooperative_driving','pyscripts','simUtilities'))

# from .myVehicle import myVehicle

class sensoredMovement():
    vehicleDict = {}
    Simulation = None
    visibleDist = 0
    lanePlacement = 1
    lanes = {}
    emergencyLanes = {}


    def __init__(self, vehicleDict, visibleDist = 100, lanePlacement = 1, Simulation=None):
        self.vehicleDict = vehicleDict
        self.visibleDist = visibleDist
        self.Simulation = Simulation
        self.lanePlacement = lanePlacement
        self.lanes = {-lanePlacement, 0, lanePlacement}
        self.emergencyLanes = {-2*lanePlacement, -lanePlacement, 0, lanePlacement, 2*lanePlacement}

    def step(self):
        for vid in self.vehicleDict: #Iterates through each vehicle in the dictionary
            if (not self.vehicleDict[vid].emergencyResponse): # EmergencyVehicle not in Range
                if self.vehicleDict[vid].slowingDown \
                        and self.vehicleDict[vid].vy == 0 \
                        and self.vehicleDict[vid].leadingVehicle != None: #only executes when the vehicle is slowing down
                    for lane in self.lanes:
                        if np.abs(lane - self.vehicleDict[vid].lane) == self.lanePlacement: #Makes sure that it doesn't observe two lanes away
                            lead = self.vehicleDict[vid].getLeadingVehicle(lane)
                            follow = self.vehicleDict[vid].getFollowingVehicle(lane)
                            if self.vehicleDict[vid].checkSafety(lead, follow) and self.IncreaseSpeedLaneChange(self.vehicleDict[vid], lead):
                                value = np.random.rand()
                                if (vid == -1): # Emergency Vehicle
                                    direction = self.laneToDirection(self.vehicleDict[vid].lane, lane)
                                    self.vehicleDict[vid].changeLane(direction)
                                    break
                                if (value <= 0.03): # Normal Vehicles
                                    direction = self.laneToDirection(self.vehicleDict[vid].lane, lane)
                                    self.vehicleDict[vid].changeLane(direction)
                                    break

            elif self.vehicleDict[vid].vy == 0:   # Emergency Vehicle is in range
                selfLane = self.vehicleDict[vid].lane
                if self.vehicleDict[-1].lane == selfLane and np.random.rand() < 0.2:   # Vehicle is in same lane as Emergency Vehicle
                    for lane in self.emergencyLanes:
                        if np.abs(lane - selfLane) == self.lanePlacement:
                            lead = self.vehicleDict[vid].getLeadingVehicle(lane)
                            follow = self.vehicleDict[vid].getFollowingVehicle(lane)
                            if self.vehicleDict[vid].checkSafety(lead, follow):
                                direction = self.laneToDirection(selfLane, lane)
                                self.vehicleDict[vid].changeLane(direction)
                                break # to leave loop in this case
                elif self.vehicleDict[-1].lane < selfLane and np.random.rand() < 0.2:  # Vehicle is in lane above Emergency Vehicle
                    lead = self.vehicleDict[vid].getLeadingVehicle(selfLane+self.lanePlacement)
                    follow = self.vehicleDict[vid].getFollowingVehicle(selfLane+self.lanePlacement)
                    if selfLane != 2*self.lanePlacement and self.vehicleDict[vid].checkSafety(lead, follow):
                        direction = self.laneToDirection(selfLane, selfLane+self.lanePlacement)
                        self.vehicleDict[vid].changeLane(direction)
                elif np.random.rand() < 0.2 and self.vehicleDict[-1].lane > selfLane:  # Vehicle is in lane below Emergency Vehicle
                    lead = self.vehicleDict[vid].getLeadingVehicle(selfLane-self.lanePlacement)
                    follow = self.vehicleDict[vid].getFollowingVehicle(selfLane-self.lanePlacement)
                    if selfLane != -2*self.lanePlacement and self.vehicleDict[vid].checkSafety(lead, follow):
                        direction = self.laneToDirection(selfLane, selfLane-self.lanePlacement)
                        self.vehicleDict[vid].changeLane(direction)
            # Catches vehicle from flying past lane change by calling isClose function
            if (self.vehicleDict[vid].vy != 0):
                lane = self.vehicleDict[vid].lane
                self.vehicleDict[vid].isClose(lane)
        return True


    # def directionBound(self, lane, direction):
    #     if (lane == self.lanePlacement and direction == 1):
    #         direction = 0
    #     elif (lane == -self.lanePlacement and direction == 0):
    #         direction = 1
    #
    #     return direction

    def laneToDirection(self, selfLane, leadLane): #0 is down 1 is up
        if selfLane > leadLane:
            direction = 0
        else:
            direction = 1
        return direction

    def IncreaseSpeedLaneChange(self, selfV, leadV): #Takes in vehicle and leadingVehicle in desired lane to check if lane change is worth it
        if (leadV != None):
            if np.mod(leadV.x - selfV.x, 1000) > 50 or leadV.speed >= selfV.leadingVehicle.speed:
                return True
            return False
        else:
            return True

