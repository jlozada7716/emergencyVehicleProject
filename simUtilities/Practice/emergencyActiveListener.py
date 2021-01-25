import numpy as np
import os, sys
sys.path.append(os.path.join(os.sep, 'gitlab_repos', 'emergency_vehicle_cooperative_driving','pyscripts','simUtilities'))

class emergencyActiveListener():
    vehicleDict = {}
    visibleDist = 0


    def __init__(self, vehicleDict, visibleDist):
        self.vehicleDict = vehicleDict
        self.visibleDist = visibleDist

    def step(self):
        if -1 in self.vehicleDict:
            for vid, v in self.vehicleDict.items():
                if (np.mod(v.x - self.vehicleDict[-1].x, 1000) <= self.visibleDist
                        or (np.mod(self.vehicleDict[-1].x - v.x, 1000) < 50)
                        and np.mod(self.vehicleDict[-1].x - v.x, 1000) > 0) and vid != -1:
                    v.emergencyResponse = True
                else:
                    v.emergencyResponse = False
        return True