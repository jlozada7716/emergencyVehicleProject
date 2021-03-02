import numpy as np
import os, sys
sys.path.append(os.path.join(os.sep, 'gitlab_repos', 'emergency_vehicle_cooperative_driving','pyscripts','simUtilities'))

xSimDistance = 2000


class emergencyActiveListener():
    vehicleDict = {}
    visibleDist = 50


    def __init__(self, vehicleDict, visibleDist):
        self.vehicleDict = vehicleDict
        self.visibleDist = visibleDist

    def step(self):
        if -1 in self.vehicleDict:
            for vid, v in self.vehicleDict.items():
                if (np.mod(v.x - self.vehicleDict[-1].x, xSimDistance) <= self.visibleDist or ((np.mod(self.vehicleDict[-1].x - v.x, xSimDistance) < 10)
                                                                                               and np.mod(self.vehicleDict[-1].x - v.x, xSimDistance) > 0)) and vid != -1:
                    v.emergencyResponse = True
                else:
                    if v.emergencyResponse: # GET RID OF LATER
                        pass # GET RID OF LATER
                    else:
                        v.emergencyResponse = False
        return True