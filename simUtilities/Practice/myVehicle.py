import numpy as np
import os, sys
import time
lanePlacement = 0.5
xSimDistance = 1000

class myVehicle:
    vehicleDict = {}
    id = None
    x = 0
    y = 0
    lane = None
    speed = 0
    maxSpeed = None
    acceleration = 0
    decceleration = 0.1 # DELETE?
    vy = None
    leadingVehicle = None   # Calculates the vehicle in front in a desired lane
    followingVehicle = None # Calculates the vehicle behind in a desired lane
    distanceToLeadingVehicle = 0 # Leading Vehicle headway DELETE?
    slowingDown = False # Keeps vehicle from accelerating while decelerating
    emergencyResponse = False # Puts vehicle in emergency mode if emerg vehicle is near
    #For Emergency Vehicle Analysis
    emergencyVLoop = False
    insertTime = 0
    insertX = 0
    loopTime = 0
    loopX = 0
    loopDone = False

    prevAccel = 0
    prevSpeed = 0
    prevX = 0
    l = 1.3
    m = 0.5
    alpha = 13
    deltaT = 1
    flip = False

    a = 0.73 # Desired Acceleration
    b = 1.67 # Desired Deceleration
    delta = 4 #
    vo = 45
    length = 5
    s0 = 2
    s1 = 0
    t = 1.6 # Safe Time Headway
    firstSwitch = True






    def __init__(self, vehicleDict, id=None, lane=0, speed=0.2, vy=0):
        if (id == None):
            self.id = len(vehicleDict) + 1
        else:
            self.id = id
        self.vehicleDict = vehicleDict
        self.lane = lane
        self.y = lane
        self.speed = speed
        self.prevSpeed = speed
        self.maxSpeed = speed + 3.5
        self.vy = vy
        self.leadingVehicle = self.getLeadingVehicle(targetLane=lane)
        self.targetSpeed = speed

    def advance(self):

        if self.emergencyResponse == False and np.abs(self.lane) == 2*lanePlacement\
                and self.vy == 0 and np.random.rand() < 0.3: #For vehicles to get back in lane after emegResponse turns false
            if self.checkSafety(self.getLeadingVehicle(self.lane+lanePlacement), self.getFollowingVehicle(self.lane+lanePlacement))\
                    and self.lane == -2*lanePlacement:
                self.changeLane(1)
            elif self.checkSafety(self.getLeadingVehicle(self.lane-lanePlacement), self.getFollowingVehicle(self.lane-lanePlacement))\
                    and self.lane == 2*lanePlacement:
                self.changeLane(0)
        if self.emergencyResponse: # Emergency Vehicle has entered the simulation
            self.slowingDown = True
            self.updateLeadingVehicle()
            self.decceleration = 0.35
            if self.leadingVehicle != None:
                self.updatePrevAttributes()
                # Find safe position to start braking in
                self.slowSpeedFollowingBehavior()
            if np.abs(self.y) >= 1.5*lanePlacement:
                self.speed = np.maximum(self.speed - self.decceleration, 0)
            elif self.lane != self.vehicleDict[-1]:
                self.speed = np.maximum(self.speed - self.decceleration, 2)
            self.x = np.mod(np.maximum(self.x + self.prevSpeed + 0.5 * self.prevAccel, self.x), xSimDistance)
        else:  # not in emergencyMode or return from Emergency Mode
            self.slowingDown = False
            self.updateLeadingVehicle() # Checks for lead vehicle change
            if self.leadingVehicle != None and np.mod(self.leadingVehicle.x - self.x, xSimDistance) < 60:  # implementing safety conditions and lane change if possible
                self.updatePrevAttributes()
                self.decceleration = 0.35
                if self.id == 43:
                    print("43")
                approachingRate = self.speed - self.leadingVehicle.speed
                bumper2bumper = np.mod(self.leadingVehicle.x - self.x, xSimDistance) - self.l
                if bumper2bumper < 0.5:
                    print("LESS THAN 0.5 HEADWAY: ", bumper2bumper, " " , self.id)
                if bumper2bumper < 0:
                    print("LESS THAN 0 HEADWAY: ", bumper2bumper)
                # print("Vehicle id:", self.id, "headway: ", bumper2bumper)
                if self.speed == 0:
                    print("Stopped")
                desiredMinimumGap = self.s0 + self.s1 * np.sqrt(self.speed / self.vo) + self.t * self.speed + (self.speed * approachingRate / (2 * np.sqrt(self.a * self.b)))
                self.acceleration = self.a * (1 - np.power(approachingRate / self.vo, self.delta) - np.power(desiredMinimumGap / bumper2bumper, 2))

                self.acceleration = np.minimum(self.acceleration, self.a)
                # self.acceleration = ((self.alpha * np.power(self.prevSpeed, self.m)) / np.power(
                #     np.mod(self.leadingVehicle.prevX - 7 - self.prevX, xSimDistance), self.l)) * (
                #                                 self.leadingVehicle.prevSpeed - self.prevSpeed)



                # print("Vehicle ", self.id, " Acceleration: ", self.acceleration)
                # print("Vehicle ", self.id, " Speed: ", self.speed)
                # self.acceleration = np.minimum(self.acceleration, 1.5)
                # self.acceleration = np.maximum(self.acceleration, -2.5)
                if self.acceleration < 0: # DOUBLE CHECK FOR ERRORS
                    self.slowingDown = True
                else:
                    self.slowingDown = False
                # Changed self.accel to prevAccel and 2nd self.speed to prevSpeed (FIX IF NECESSARY)
                self.speed = np.maximum(self.speed + self.prevAccel, 0)
                self.speed = np.minimum(self.speed, self.maxSpeed)
                self.x = np.mod(np.maximum(self.x + self.prevSpeed + 0.5 * self.prevAccel, self.x), xSimDistance)
            else:
                self.updatePrevAttributes()
                self.acceleration = np.minimum(self.acceleration + 0.005, 0.75)
                # print("Vehicle ", self.id, " Speed: ", self.speed)
                # if not self.flip and self.id == 0:
                #     self.acceleration = self.acceleration + 0.2
                # elif self.id == 0:
                #     self.acceleration = self.acceleration - 0.1
                # else:
                #     self.acceleration = self.acceleration + 0.1
                self.speed = np.minimum(self.speed + self.acceleration, self.maxSpeed)
                # if self.speed == self.maxSpeed:

                # if self.speed == self.maxSpeed:
                #     self.flip = True
                self.speed = np.maximum(self.speed, 0)
                # if self.speed == 0:
                #     self.flip = False
                self.x = np.mod(self.speed + self.x, xSimDistance)  # advance
                self.maxSpeed += np.random.normal(loc = 0, scale = 0.0005)
        self.y = self.vy + self.y

    def changeLane(self, direction):  # shifts the vehicle across a lane
        if (direction == 1):
            shift = self.speed * 0.007
            shift = np.maximum(shift, 0.06)
            shift = np.minimum(shift, 0.05)
        if (direction == 0):
            shift = -self.speed * 0.007
            shift = np.maximum(shift, -0.06)
            shift = np.minimum(shift, -0.05)
        self.vy = shift
        if (shift > 0): #to get new leading vehicle without changing lane of vehicle
            lane = self.lane + lanePlacement
        else:
            lane = self.lane - lanePlacement
        self.leadingVehicle = self.getLeadingVehicle(lane)
        self.lane = lane
        return True

    def isClose(self, lane):    # Locks vehicle to lane when close (Unless leaving a lane)
        # (np.abs(self.y - lane) < (lanePlacement / 10) and (np.abs(self.lane - self.y) > (lanePlacement / 10))):


        if np.abs(self.y - lane) < (lanePlacement / 9):
            self.lane = lane
            self.y = lane
            self.vy = 0 # Stop shifting lanes
            self.leadingVehicle = self.getLeadingVehicle(lane)

    def getLeadingVehicle(self, targetLane):    #Determine vehicle in front
        leadingVehicle = None
        vehicleInFront = False # True if there is a vehicle in front
        leadingVehicleLoop = None # Used if no vehicle in front but there is one behind
        loopLead = 0 # Used to search for the first vehicle in the lane
        # Set Leading Vehicle
        for vid, v in self.vehicleDict.items():
            if v.lane == targetLane and v.x > self.x and (leadingVehicle == None or v.x < leadingVehicle.x):
                leadingVehicle = v
                vehicleInFront = True
            elif (not vehicleInFront) and v.lane == targetLane\
                    and (leadingVehicleLoop == None or v.x < loopLead) and v != self:
                loopLead = v.x
                leadingVehicleLoop = v
        if not vehicleInFront:
            leadingVehicle = leadingVehicleLoop
        return leadingVehicle

    def getFollowingVehicle(self, targetLane):  #Determine vehicle behind
        followingVehicle = None
        vehicleBehind = False # True if there is a vehicle behind
        followVehicleLoop = None # Used if no vehicle behind but there is one ahead
        loopFollow = None # Used to search for the last vehicle in the lane
        # Set Following Vehicle
        for vid, v in self.vehicleDict.items():
            if v.lane == targetLane and v.x <= self.x and (followingVehicle == None or v.x > followingVehicle.x):
                followingVehicle = v
                vehicleBehind = True
            elif (not vehicleBehind) and v.lane == targetLane\
                and (followVehicleLoop == None or v.x > loopFollow) and v != self:
                loopFollow = v.x
                followVehicleLoop = v
        if not vehicleBehind:
            followingVehicle = followVehicleLoop
        return followingVehicle

    def checkSafety(self, lead, follow):
        headwayLead = 51
        speedRatioLead = 1
        headwayFollow = 41
        speedRatioFollow = 1
        if lead != None:
            headwayLead = np.mod(lead.x - self.x, xSimDistance)
            if np.abs(lead.lane) != 2*lanePlacement and lead.speed != 0 and np.abs(self.y) != 2*lanePlacement:
                speedRatioLead = self.speed / lead.speed
            else:
                # speedRatioLead = 1.5
                return self.checkSafetyEmergencyLane(lead, follow)

        if follow != None:
            headwayFollow = np.mod(self.x - follow.x, xSimDistance)
            if np.abs(follow.lane) != 2*lanePlacement and self.speed != 0 and np.abs(self.y) != 2*lanePlacement:
                speedRatioFollow = follow.speed / self.speed
            else:
                # speedRatioFollow = 1.5
                return self.checkSafetyEmergencyLane(lead, follow)
        if headwayLead > np.maximum(speedRatioLead * 15, 15) and headwayFollow > np.maximum(speedRatioFollow * 20, 20):
            return True
        return False

    def checkSafetyEmergencyLane(self, lead, follow):
        headwayLead = np.mod(lead.x - self.x+2*self.speed, xSimDistance)
        headwayFollow = np.mod((self.x+self.speed) - follow.x, xSimDistance)
        if np.abs(self.y) == 2*lanePlacement:
            if headwayLead > 5 and headwayFollow > 8:
                return True
        if headwayLead > 45 and headwayFollow > 8 and self.speed < 6:
            return True
        return False

    def slowSpeedFollowingBehavior(self): # Behavior takes over for slow speeds
        self.acceleration = 0 # To reset when the vehicle reenters normal mode
        headway = np.mod(self.leadingVehicle.x - self.x, xSimDistance)
        if (self.leadingVehicle.speed >= 1):
            speedRatio = self.speed / self.leadingVehicle.speed
        else: # Ensures that if leading vehicle speed is very low, the ratio doesn't approach infinity
            speedRatio = 1
        # Determine whether the vehicle is within that safePosition
        if headway <= np.maximum(speedRatio * 80, 20) and self.leadingVehicle.y == self.y:
            self.matchLeadingSpeed()

    def matchLeadingSpeed(self):  #Match the speed of vehicle in front when close enough
        #Create factor to exponentially deccelerate as vehicle gets closer to LeadingVehicle
        self.decceleration += 0.2
        self.decceleration = np.minimum(self.decceleration, 2)
        if (self.leadingVehicle.x - self.x <= 30 and self.leadingVehicle.x - self.x > 0):
            #Set vehicle speed to LeadingVehicle's speed if close enough
            self.decceleration += 0.3
            self.decceleration = np.minimum(self.decceleration, 2.5)
        if np.abs(self.y) > lanePlacement:
            self.speed = np.maximum(self.speed - 2 * self.decceleration, 0)
        else:
            self.speed = np.maximum(self.speed - self.decceleration, 2)
        if self.leadingVehicle.x - self.x <= 3 and self.leadingVehicle.x - self.x >= 0 \
                and np.abs(self.y - self.leadingVehicle.y) <= lanePlacement/2:
            print("Moved")
            self.x = self.leadingVehicle.x - 10

    def updateLeadingVehicle(self): # Updates if leading vehicle changes when currentVehicle isn't changing lanes
        if (self.vy == 0):
            self.leadingVehicle = self.getLeadingVehicle(self.lane)

    def updatePrevAttributes(self): # Updates the previous x, speed, and acceleration of the vehicle
        self.prevX = self.x
        self.prevSpeed = self.speed
        self.prevAccel = self.acceleration