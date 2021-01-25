import numpy as np

lanePlacement = 0.5

class myVehicle:
    vehicleDict = {}
    id = None
    x = 0
    y = 0
    speed = 0
    maxSpeed = None
    acceleration = 0.1
    decceleration = 0.2
    maxAcceleration = 3
    maxDecceleration = 3
    minimumHeadway = 200
    vy = None
    trajectory = []     # Comes into play when emergencyVehicle is spawned
    length = 5
    tau = 5    # Used to brake by a factor a multiple factor of speed
    followTrajectory = False    # Comes into play when emergencyVehicle is spawned
    lane = None
    leadingVehicle = None   # Calculates the vehicle in front in a desired lane
    followingVehicle = None # Calculates the vehicle behind in a desired lane
    distanceToLeadingVehicle = 0
    slowingDown = False

    def __init__(self, vehicleDict, id=None, lane=0.5, speed=0.2, vy=0.05):
        if (id == None):
            self.id = len(vehicleDict) + 1
        else:
            self.id = id
        self.vehicleDict = vehicleDict
        self.lane = lane
        self.y = lane
        self.speed = speed
        self.maxSpeed = speed
        self.vy = vy
        self.leadingVehicle = self.getLeadingVehicle(targetLane=self.lane)
        self.targetSpeed = speed

    def advance(self):
        if self.followTrajectory and len(self.trajectory) > 0:
            # pdb.set_trace()
            nextNode = self.trajectory.pop(0)  # get the next node on the trajectory
            # adjust the speed according to the next position in the trajectory
            print(nextNode[2] - self.lane)
            if (nextNode[2] != self.lane) and not self.changeLane(nextNode[2] - self.lane):
                # print('emergency vehicle not in the correct lane. Recalculating')
                self.trajectory = []  # rejecting the proposed trajectory
            self.speed = np.minimum(nextNode[0] - self.x,
                                    self.maxSpeed + 0.5)  # 0.5 is to compensate for the rounding effect in the trajectory computation algorithm
            # check if this speed is safe and adjust accordingly
            if self.leadingVehicle != None:
                # predict leading vehicle's position
                lvPosition = self.leadingVehicle.x + self.leadingVehicle.speed
                # set speed so as to no exceed safe position
                safePosition = self.leadingVehicle.x - self.leadingVehicle.length - self.speed * self.tau
                if self.x + self.speed >= safePosition:
                    self.speed = np.maximum(0, safePosition - self.x)
            # if projected trajectory is inconsistent with the current path, reject the trajectory.
            if np.abs(self.speed + self.x - nextNode[0]) > 2 * self.speed:
                # print('vehicle %d too far behind the proposed trajectory. Rejecting trajectory'%self.id)
                self.trajectory = []  # rejecting the proposed trajectory

        else:  # not following any trajectory
            self.leadingVehicle = self.getLeadingVehicle(self.lane)
            if self.leadingVehicle != None:  # Hazard Headway
                # predict leading vehicle's position: lvPosition = self.leadingVehicle.x + self.leadingVehicle.speed
                # Find safe position to start braking in
                # Determine whether the vehicle is within that safePosition
                relativeSpeed = self.speed - self.leadingVehicle.speed
                #  (self.speed * self.tau + self.x) >= self.leadingVehicle.x
                if self.leadingVehicle.x - self.x <= self.minimumHeadway and self.leadingVehicle.y == self.y and relativeSpeed > 0:
                    self.matchLeadingSpeed()
                    self.slowingDown = True
                if (self.leadingVehicle.x - self.x > 30):
                    self.slowingDown = False
                # self.speed = np.maximum(0, safePosition - self.x)
                # change lane if possible
                # if not self.inFreezeMode() and self.lcSpeedGain: self.changeLanceToIncreaseSpeed()

            # randomly vary maxSpeed to avoid clutter
            if (not self.followTrajectory) and (np.random.rand() < 0.01):
                self.maxSpeed = self.maxSpeed + np.random.normal(loc=0, scale=.05)
            # accelerate the vehicle to the maximum speed
            if (not self.slowingDown):
                self.speed = np.minimum(self.speed + self.acceleration, self.maxSpeed)
        self.x = self.speed + self.x  # advance
        self.y = self.vy + self.y

        if self.leadingVehicle != None: # Calculate distanceToLeadingVehicle
            self.distanceToLeadingVehicle = self.distanceToLeadingVehicle + self.leadingVehicle.x - self.x

    def changeLane(self, direction):  # shifts the vehicle across a lane
        if (direction == 1):
            shift = self.speed * 0.01
        if (direction == 0):
            shift = -self.speed * 0.01
        shift = np.minimum(shift, 0.08)
        shift = np.maximum(shift, -0.08)

        if (self.lane == lanePlacement and shift > 0):
            shift = -shift
        elif (self.lane == -lanePlacement and shift < 0):
            shift = -shift
        self.vy = shift
        if (shift > 0):
            self.lane = self.lane + lanePlacement
        else:
            self.lane = self.lane - lanePlacement
        self.leadingVehicle = self.getLeadingVehicle(self.lane)
        return True

    def isClose(self, lane):    # Locks vehicle to lane when close (Unless leaving a lane)
        if (np.abs(self.y - lane) < (lanePlacement / 10) and (np.abs(self.lane - self.y) > (lanePlacement / 10))):
            self.lane = lane
            self.y = lane
            self.vy = 0 # Stop shifting lanes
            self.leadingVehicle = self.getLeadingVehicle(lane)

    def getLeadingVehicle(self, targetLane):    #Determine vehicle in front
        leadingVehicle = None
        # Set Leading Vehicle
        for vid, v in self.vehicleDict.items():
            if v.lane == targetLane and self.x < v.x and (leadingVehicle == None or (v.x < leadingVehicle.x)):
                leadingVehicle = v
        return leadingVehicle

    def getFollowingVehicle(self, targetLane):  #Determine vehicle behind
        followingVehicle = None
        for vid, v in self.vehicleDict.items():
            if v.lane == targetLane and v.x < self.x and (followingVehicle == None or v.x > followingVehicle.x):
                followingVehicle = v
        return followingVehicle

    def inFreezeMode(self): #NOT SURE YET
        sid = -1
        freezeRange = 20
        if (sid in self.vehicleDict) and (np.abs(self.x - self.vehicleDict[sid].x) < freezeRange) and (self.id != sid):
            return True
        else:
            return False

    def matchLeadingSpeed(self):  #Match the speed of vehicle in front when close enough
        # Create factor to exponentially decelerate as vehicle gets closer to LeadingVehicle
        comfortOverboardFactor = 1 / (self.leadingVehicle.x - self.x - self.length) * 550
        self.speed = np.maximum(self.speed - self.decceleration * comfortOverboardFactor, self.leadingVehicle.speed)
        if ((self.leadingVehicle.x - self.x) <= 40 and self.slowingDown):
            #Set vehicle speed to LeadingVehicle's speed if close enough
            self.speed = self.leadingVehicle.speed

    def getHeadway(self, vehicle): #UNUSED SO FAR
        return vehicle.x - self.x
