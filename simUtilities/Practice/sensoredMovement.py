import numpy as np
import os, sys
import time
sys.path.append(os.path.join(os.sep, 'gitlab_repos', 'emergency_vehicle_cooperative_driving','pyscripts','simUtilities'))

# from .myVehicle import myVehicle
xSimDistance = 2000

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
        tic = time.time()
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
                                if (value <= 0.01): # Normal Vehicles
                                    direction = self.laneToDirection(self.vehicleDict[vid].lane, lane)
                                    self.vehicleDict[vid].changeLane(direction)
                                    self.acceleration = 0
                                    break
            # EmergencyVehicle is in Range
            elif self.vehicleDict[vid].vy == 0 and np.mod(self.vehicleDict[-1].x - self.vehicleDict[vid].x, xSimDistance) > 500:   # Emergency Vehicle is in range
                selfLane = self.vehicleDict[vid].lane # Used for simplicity (Current vehicle's lane)
                # Condition: Vehicle is in same lane as the emergency vehicle
                if self.vehicleDict[-1].lane == selfLane and np.random.rand() < 0.1:
                    for lane in self.emergencyLanes:
                        if np.abs(lane - selfLane) == self.lanePlacement and self.changeLaneAttempt(vid, lane - selfLane): # if lane is adjacent by 1 to selfLane
                            break
                            # lead = self.vehicleDict[vid].getLeadingVehicle(lane)
                            # follow = self.vehicleDict[vid].getFollowingVehicle(lane)
                            # if self.vehicleDict[vid].checkSafety(lead, follow):
                            #     direction = self.laneToDirection(selfLane, lane) # gets direction from the selfLane to lane
                            #     self.vehicleDict[vid].changeLane(direction)
                            #     break # to leave loop in this case
                # Condition 2: Vehicle is in lane above the Emergency Vehicle
                elif self.vehicleDict[-1].lane < selfLane and np.random.rand() < 0.1 and selfLane != 2*self.lanePlacement:
                    self.changeLaneAttempt(vid, self.lanePlacement)
                    # lead = self.vehicleDict[vid].getLeadingVehicle(selfLane+self.lanePlacement)
                    # follow = self.vehicleDict[vid].getFollowingVehicle(selfLane+self.lanePlacement)
                    # if self.vehicleDict[vid].checkSafety(lead, follow):
                    #     direction = self.laneToDirection(selfLane, selfLane+self.lanePlacement)
                    #     self.vehicleDict[vid].changeLane(direction)
                # Condition 3: Vehicle is in lane below the Emergency Vehicle
                elif self.vehicleDict[-1].lane > selfLane and np.random.rand() < 0.1 and selfLane != -2*self.lanePlacement:
                    self.changeLaneAttempt(vid, -self.lanePlacement)
                    # lead = self.vehicleDict[vid].getLeadingVehicle(selfLane-self.lanePlacement)
                    # follow = self.vehicleDict[vid].getFollowingVehicle(selfLane-self.lanePlacement)
                    # if self.vehicleDict[vid].checkSafety(lead, follow):
                    #     direction = self.laneToDirection(selfLane, selfLane-self.lanePlacement)
                    #     self.vehicleDict[vid].changeLane(direction)

            # Catches vehicle from flying past lane change by calling isClose function
            if self.vehicleDict[vid].vy != 0:
                self.vehicleDict[vid].isClose()

        toc = time.time()
        # if (toc - tic) > 0.00001:
        #     print('Sensored elapsed time: %f' % (toc - tic))
        return True


    def changeLaneAttempt(self, vid, displacement):
        selfLane = self.vehicleDict[vid].lane
        lead = self.vehicleDict[vid].getLeadingVehicle(selfLane + displacement)
        follow = self.vehicleDict[vid].getFollowingVehicle(selfLane + displacement)
        if self.vehicleDict[vid].checkSafety(lead, follow):
            direction = self.laneToDirection(selfLane, selfLane + displacement)
            self.vehicleDict[vid].changeLane(direction)
            return True
        return False

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

