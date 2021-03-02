import numpy as np
import os, sys
import time
lanePlacement = 0.5
xSimDistance = 2000

class myVehicle:
    # State
    vehicleDict = {}
    id = None
    x = 0
    y = 0
    lane = None
    speed = 0
    maxSpeed = None
    acceleration = 0
    deceleration = 0 # DELETE?
    vy = None
    # Future Values
    futureY = None
    futureAX = None
    futureAY = None
    # Data Collection
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
    # Previous values
    prevAccel = 0
    prevSpeed = 0
    prevX = 0

    # Car following model
    a = 0.73 # Desired Acceleration
    b = 1.67 # Desired Deceleration
    delta = 4 # Acceleration Exponent
    vo = 45  # Desired Velocity
    length = 6  # Length of our vehicle
    s0 = 2      # Jam distance meters
    s1 = 0      #Jam Distance meters
    t = 3 # Safe Time Headway
    firstSwitch = True
    dt = 1 / 5  # Scan Interval


    def __init__(self, vehicleDict, id=None, lane=0, speed=0.2, vy=0, x=0):
        if (id == None):
            self.id = len(vehicleDict) + 1
        else:
            self.id = id
        self.vehicleDict = vehicleDict
        self.lane = lane
        self.y = lane
        self.x = x
        self.speed = speed
        self.prevSpeed = speed
        self.futureAX = 0
        self.maxSpeed = speed + 1
        self.vy = vy
        self.leadingVehicle = self.getLeadingVehicle(targetLane=lane)
        self.targetSpeed = speed

    def advance(self):  # Calculates the acceleration values and makes necessary lane changes
        if self.emergencyResponse == False and np.abs(self.lane) == 2*lanePlacement\
                and self.vy == 0 and np.random.rand() < 0.3: #For vehicles to get back in lane after emegResponse turns false
            # if self.checkSafety(self.getLeadingVehicle(self.lane+lanePlacement), self.getFollowingVehicle(self.lane+lanePlacement))\
            #         and self.lane == -2*lanePlacement:
            #     self.changeLane(1)
            # elif self.checkSafety(self.getLeadingVehicle(self.lane-lanePlacement), self.getFollowingVehicle(self.lane-lanePlacement))\
            #         and self.lane == 2*lanePlacement:
            #     self.changeLane(0)
            pass
        if self.emergencyResponse: # Emergency Vehicle has entered the simulation
            self.slowingDown = True
            self.updateLeadingVehicle()
            if self.leadingVehicle != None:
                self.futureAX = self.carFollowingModel(self.leadingVehicle, self, False)
                if self.futureAX > 0:
                    self.futureAX = 0
            else:
                self.futureAX = np.maximum(self.futureAX-0.03, self.b)

            if self.speed != 1:
                self.deceleration = np.maximum(self.deceleration - 0.2, -1*self.b)

            self.emergencyUpdate()
            # self.slowingDown = True
            # self.updateLeadingVehicle()
            # self.deceleration = 0.35
            # if self.leadingVehicle != None:
            #     self.updatePrevAttributes()
            #     # Find safe position to start braking in
            #     self.slowSpeedFollowingBehavior()
            # if np.abs(self.y) >= 1.5*lanePlacement:
            #     self.speed = np.maximum(self.speed - self.deceleration, 0)
            # elif self.lane != self.vehicleDict[-1]:
            #     self.speed = np.maximum(self.speed - self.deceleration, 2)
            # self.x = np.mod(np.maximum(self.x + self.prevSpeed + 0.5 * self.prevAccel, self.x), xSimDistance)
        else:  # not in emergencyMode or return from Emergency Mode
            self.slowingDown = False
            self.deceleration = 0
            self.updateLeadingVehicle() # Checks for lead vehicle change
            if self.leadingVehicle != None and np.mod(self.leadingVehicle.x - self.x, xSimDistance) < 80: # Car Following Model Activated
                # Calculate Acceleration of Following Vehicle
                self.futureAX = self.carFollowingModel(self.leadingVehicle, self, False)
                # Ensure acceleration bounds
                self.futureAX = np.minimum(self.futureAX, self.a)
                # Determine whether vehicle is slowing down or not
                self.slowingDownTest()
            else: # No leading vehicle (Accelerate to max speed)
                if self.speed == 0:
                    self.futureAX = 0
                self.futureAX = np.minimum(self.futureAX + 0.02, self.a/5)
                self.maxSpeed += np.random.normal(loc = 0, scale = 0.005)
        self.futureY = self.vy + self.y # Update the y value

    def update(self): # Updates the current state of the vehicle to the calculated future state
        self.updatePrevAttributes()
        self.speed = np.maximum(self.speed + self.prevAccel * self.dt, 0)
        self.speed = np.minimum(self.speed, self.maxSpeed)
        self.x = np.mod(np.maximum(self.prevX + self.prevSpeed + 0.5 * self.prevAccel * np.power(self.dt, 2), self.x), xSimDistance)
        self.acceleration = self.futureAX
        # Y values (TO BE UPDATED FOR FUTURE)
        self.y = self.futureY

    def emergencyUpdate(self):
        self.updatePrevAttributes()
        if np.abs(self.y) >= 1.5 * lanePlacement:
            self.speed = np.maximum(self.speed + self.prevAccel*self.dt + self.deceleration, 0)
        else:
            self.speed = np.maximum(self.speed + self.prevAccel*self.dt + self.deceleration, 2)
        self.speed = np.minimum(self.speed, self.maxSpeed)
        self.x = np.mod(np.maximum(self.prevX + self.prevSpeed + 0.5 * self.prevAccel * np.power(self.dt, 2), self.x), xSimDistance)
        self.acceleration = self.futureAX
        #Y values (TO BE UPDATED FOR FUTURE)
        self.y = self.futureY

    # def carFollowingModel(self):
    #     approachingRate = self.speed - self.leadingVehicle.speed # Approaching rate of the following vehicle to the leading Vehicle
    #     bumper2bumper = np.mod(self.leadingVehicle.x - self.x, xSimDistance) - self.length   # The headway between vehicles
    #
    #     self.headwayChecker(bumper2bumper, self.id)                                                   # Outputs warning if the headway is too small
    #     desiredMinimumGap = self.s0 + (self.s1 * np.sqrt(self.speed / self.vo)) + (self.t * self.speed) + (self.speed * approachingRate / (2 * np.sqrt(self.a * self.b)))
    #     if desiredMinimumGap < 3:
    #         desiredMinimumGap = np.maximum(desiredMinimumGap, 4)
    #     futureAX = self.a * (1 - np.power(approachingRate / self.vo, self.delta) - np.power(desiredMinimumGap / bumper2bumper, 2)) # Future Acceleration
    #     return futureAX

    def carFollowingModel(self, lead, follow, changingLane):
        approachingRate = follow.speed - lead.speed # Approaching rate of the following vehicle to the leading Vehicle
        bumper2bumper = np.mod(lead.x - follow.x, xSimDistance) - follow.length   # The headway between vehicles
        if not changingLane:
            self.headwayChecker(bumper2bumper, follow.id)
        desiredMinimumGap = follow.s0 + (follow.s1 * np.sqrt(follow.speed / follow.vo)) + (follow.t * follow.speed) + (follow.speed * approachingRate / (2 * np.sqrt(follow.a * follow.b)))
        if desiredMinimumGap < 3:
            desiredMinimumGap = np.maximum(desiredMinimumGap, 4)
        futureAX = follow.a * (1 - np.power(approachingRate / follow.vo, follow.delta) - np.power(desiredMinimumGap / bumper2bumper, 2)) # Future Acceleration
        return futureAX

    def changeLane(self, direction):  # shifts the vehicle across a lane
        if (direction == 1):
            shift = self.speed * 0.02
            shift = np.maximum(shift, 0.05)
            shift = np.minimum(shift, 0.1)
        if (direction == 0):
            shift = -self.speed * 0.02
            shift = np.maximum(shift, -0.1)
            shift = np.minimum(shift, -0.05)
        self.vy = shift
        if (shift > 0): #to get new leading vehicle without changing lane of vehicle
            lane = self.lane + lanePlacement
        else:
            lane = self.lane - lanePlacement
        self.leadingVehicle = self.getLeadingVehicle(lane)
        self.lane = lane
        return True

    def isClose(self):    # Locks vehicle to lane when close (Unless leaving a lane)
        if self.vy > 0 and self.y >= self.lane - lanePlacement / 6:
            self.vy = 0
            self.y = self.lane
            self.leadingVehicle = self.getLeadingVehicle(self.lane)
        if self.vy < 0 and self.y <= self.lane + lanePlacement / 6 :
            self.vy = 0
            self.y = self.lane
            self.leadingVehicle = self.getLeadingVehicle(self.lane)

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

    def getHeadway(self, lead, follow):
        return np.mod(lead.x - follow.x, xSimDistance) - self.length

    def checkSafety(self, lead, follow):
        # if self.id == 93:
        #     print()
        #     w1 = self.carFollowingModelSafety(lead, self)
        #     w2 = self.carFollowingModelSafety(self, follow)
        #     w3 = lead.speed
        #     w4 = self.getHeadway(lead, self)
        #     w6 = self.getHeadway(self, follow)
        if (self.carFollowingModel(lead, self, True) <= 0 or self.carFollowingModel(self, follow, True) < 0)\
                or (lead.speed <= 0.5 and self.getHeadway(lead, self) <= 15) or self.getHeadway(self, follow) <= 15 or self.getHeadway(lead, self) <= 15:
            return False
        else:
            return True

    def checkSafetyEmergencyLane(self, lead, follow): #Unused for now
        headwayLead = np.mod(lead.x - self.x+2*self.speed, xSimDistance)
        headwayFollow = np.mod((self.x+self.speed) - follow.x, xSimDistance)
        if np.abs(self.y) == 2*lanePlacement:
            if headwayLead > 5 and headwayFollow > 8:
                return True
        if headwayLead > 45 and headwayFollow > 8 and self.speed < 6:
            return True
        return False

    def slowSpeedFollowingBehavior(self): # Behavior takes over for slow speeds UNUSED FOR NOW
        self.acceleration = 0 # To reset when the vehicle reenters normal mode
        headway = np.mod(self.leadingVehicle.x - self.x, xSimDistance)
        if (self.leadingVehicle.speed >= 1):
            speedRatio = self.speed / self.leadingVehicle.speed
        else: # Ensures that if leading vehicle speed is very low, the ratio doesn't approach infinity
            speedRatio = 1
        # Determine whether the vehicle is within that safePosition
        if headway <= np.maximum(speedRatio * 80, 20) and self.leadingVehicle.y == self.y:
            self.matchLeadingSpeed()

    def updateLeadingVehicle(self): # Updates if leading vehicle changes when currentVehicle isn't changing lanes
        if (self.vy == 0):
            self.leadingVehicle = self.getLeadingVehicle(self.lane)

    def updatePrevAttributes(self): # Updates the previous x, speed, and acceleration of the vehicle
        self.prevX = self.x
        self.prevSpeed = self.speed
        self.prevAccel = self.acceleration

    def slowingDownTest(self): # For Sensored-Movement
        if self.futureAX < 0:
            self.slowingDown = True
        else:
            self.slowingDown = False

    def headwayChecker(self, bumper2bumper, followID): # DELETE LATER Meant for debugging
        if bumper2bumper + 3 < 0 and self.y == self.leadingVehicle.y:
            print("HEADWAY WARNING: ", bumper2bumper, " ", followID)