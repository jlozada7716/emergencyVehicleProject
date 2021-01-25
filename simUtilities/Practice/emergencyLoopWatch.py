import numpy as np
import os, sys
sys.path.append(os.path.join(os.sep, 'gitlab_repos', 'emergency_vehicle_cooperative_driving','pyscripts','simUtilities'))



class emergencyLoopWatch():
    Simulation = None
    emergencyV = None
    LoopComplete = False

    def __init__(self, Simulation):
        self.Simulation = Simulation

    def step(self):
        if -1 in self.Simulation.vehicleDict:
            self.emergencyV = self.Simulation.vehicleDict[-1]
        if (self.emergencyV != None):
            if self.emergencyV.x > 500: # To account for the modulos affecting where the loop ends
                self.emergencyV.emergencyVLoop = True
            if self.emergencyV.emergencyVLoop and (not self.LoopComplete) \
                and (self.emergencyV.x <= 6 or self.emergencyV.x >= 994):
                self.LoopComplete = True
                self.emergencyV.loopTime = self.Simulation.timeStep
                self.emergencyV.loopDone = True
                self.emergencyV.loopX = self.emergencyV.x
                self.Simulation.stopTime = self.Simulation.timeStep + 20
        return True
