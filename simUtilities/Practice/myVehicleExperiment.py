import numpy as np

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
    decceleration = 0.1
    vy = None
    leadingVehicle = None   # Calculates the vehicle in front in a desired lane
    followingVehicle = None # Calculates the vehicle behind in a desired lane
    distanceToLeadingVehicle = 0 # Leading Vehicle headway
    slowingDown = False # Keeps vehicle from accelerating while decelerating
    emergencyResponse = False # Puts vehicle in emergency mode if emerg vehicle is near
    #For Emergency Vehicle Analysis
    emergencyVLoop = False
    insertTime = 0
    insertX = 0
    loopTime = 0
    loopX = 0
    loopDone = False

    prevSpeed = 0
    prevX = 0
    l = 1
    m = 0
    alpha = 13
    deltaT = 1

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
        self.maxSpeed = speed
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
            if self.vy == 0:
                self.getLeadingVehicle(self.lane)
            self.decceleration = 0.35
            if self.leadingVehicle != None:
                # Find safe position to start braking in
                headway = np.mod(self.leadingVehicle.x - self.x, xSimDistance)
                if (self.leadingVehicle.speed >= 1):
                    speedRatio = self.speed / self.leadingVehicle.speed
                else:
                    speedRatio = 1
                # Determine whether the vehicle is within that safePosition
                if headway <= np.maximum(speedRatio * 50, 50) and self.leadingVehicle.y == self.y:
                    self.matchLeadingSpeed()
            if np.abs(self.y) >= 1.5*lanePlacement:
                self.speed = np.maximum(self.speed - self.decceleration, 0)
            elif self.lane != self.vehicleDict[-1]:
                self.speed = np.maximum(self.speed - self.decceleration, 2)
        else:  # not following any trajectory
            self.slowingDown = False
            if (self.leadingVehicle == None): #Used for acceleration
                self.distanceToLeadingVehicle = 0
            else:
                self.distanceToLeadingVehicle = np.mod(self.leadingVehicle.x - self.x, xSimDistance)
            if (self.vy == 0):
                self.leadingVehicle = self.getLeadingVehicle(self.lane) #IMPORTANT
            if self.leadingVehicle != None and np.mod(self.leadingVehicle.x - self.x, xSimDistance) < 100:  # implementing safety conditions and lane change if possible
                # Find safe position to start braking in
                self.prevX = self.x
                self.prevSpeed = self.speed
                self.acceleration = ((self.alpha * np.power(self.prevSpeed, self.m)) / np.power(np.mod(self.leadingVehicle.prevX - self.prevX, xSimDistance), self.l)) * (self.leadingVehicle.prevSpeed - self.prevSpeed)
                if self.acceleration < 0:
                    self.slowingDown = True
                else:
                    self.slowingDown = False
                self.speed = self.speed + self.acceleration
                self.x = np.mod(self.x + self.speed + 0.5 * self.acceleration, xSimDistance)
                # print("Vehicle #", self.id, " Acceleration: ", self.acceleration)
            else:
                self.prevX = self.x
                self.prevSpeed = self.speed
                # if np.random.rand() < 0.7 and self.id != -1:
                #     self.maxSpeed = np.minimum(self.maxSpeed + np.random.normal(loc=.3, scale=.05), 11)
                # if (self.distanceToLeadingVehicle > 15 or self.leadingVehicle == None):
                #     self.speed = np.minimum(self.speed, self.maxSpeed)
                self.x = np.mod(self.speed + self.x, xSimDistance)  # advance

                # headway = np.mod(self.leadingVehicle.x - self.x, xSimDistance)
                # speedRatio = 1.0
                # if (self.leadingVehicle.speed != 0):
                #     speedRatio = self.speed / self.leadingVehicle.speed
                # # Determine whether the vehicle is within that safePosition
                # if headway <= np.maximum(speedRatio * 50, 50) and self.speed >= self.leadingVehicle.speed: #  Changed from y to lane
                #     self.matchLeadingSpeed()
                #     self.slowingDown = True
                #     print("Slowing Down")
            # randomly vary maxSpeed to avoid clutter
            # if np.random.rand() < 0.05 and self.id != -1:
            #     self.maxSpeed = np.minimum(self.maxSpeed + np.random.normal(loc=.02, scale=.005), 11)
                # if (self.maxSpeed >= 11 and self.id != -1):
                #     print("Pause")
            # accelerate the vehicle to the maximum speed
            # if (not self.slowingDown and (self.distanceToLeadingVehicle > 15 or self.leadingVehicle == None)):
            #     self.speed = np.minimum(self.speed + self.acceleration, self.maxSpeed)
            #     self.decceleration = 0.1
        # self.x = np.mod(self.speed + self.x, xSimDistance)  # advance
        self.y = self.vy + self.y

        # self.prevX = self.x
        # self.prevSpeed = self.speed
        # self.speed = self.speed + self.acceleration
        # self.x = np.mod(self.x + self.speed + 0.5*self.acceleration, xSimDistance)
        # self.acceleration = alpha / np.power(self.leadingVehicle.x - self.prevX, self.l) * (self.leadingVehicle.prevSpeed - self.prevSpeed)









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
            else: # Emergency Situation
                # speedRatioLead = 1.5
                return self.checkSafetyEmergencyLane(lead, follow)

        if follow != None:
            headwayFollow = np.mod(self.x - follow.x, xSimDistance)
            if np.abs(follow.lane) != 2*lanePlacement and self.speed != 0 and np.abs(self.y) != 2*lanePlacement:
                speedRatioFollow = follow.speed / self.speed
            else:
                # speedRatioFollow = 1.5
                return self.checkSafetyEmergencyLane(lead, follow)
        if headwayLead > np.maximum(speedRatioLead * 20, 15) and headwayFollow > np.maximum(speedRatioFollow * 20, 15):
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

    def matchLeadingSpeed(self):  #Match the speed of vehicle in front when close enough
        #Create factor to exponentially deccelerate as vehicle gets closer to LeadingVehicle
        self.decceleration = self.decceleration * 1.4
        if (self.leadingVehicle.x - self.x < 40):
            self.decceleration = self.decceleration * 1.8
        self.speed = np.maximum(self.speed - self.decceleration, self.leadingVehicle.speed)
        if (self.leadingVehicle.x - self.x <= 15 and self.leadingVehicle.x - self.x > 0):
            #Set vehicle speed to LeadingVehicle's speed if close enough
            self.decceleration = self.decceleration * 2
        if self.leadingVehicle.x - self.x <= 5 and self.leadingVehicle.x - self.x >= 0 \
                and np.abs(self.y - self.leadingVehicle.y) <= lanePlacement/2:
            print("Moved")
            self.x = self.leadingVehicle.x - 10