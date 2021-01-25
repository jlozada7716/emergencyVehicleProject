import numpy as np
import os, sys
sys.path.append(os.path.join(os.sep, 'gitlab_repos', 'emergency_vehicle_cooperative_driving','pyscripts','simUtilities'))

class vehicleSpeedCollector():
    Simulation = None
    iterationSpeedList = []

    def __init__(self, Simulation, iterationSpeedList):
        self.Simulation = Simulation
        self.iterationSpeedList = iterationSpeedList

    def step(self):
        if self.Simulation.timeStep > 1000 and self.Simulation.timeStep <= 1200:
            for vid, v in self.Simulation.vehicleDict.items():
                self.iterationSpeedList.append(v.speed)
                # print('Vehicle %s Speed: %f' % (vid, v.speed))
        return True