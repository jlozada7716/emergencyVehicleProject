class dumpVehicleCoords():
	fileName = None 
	fileObject = None
	vehicleDict = {}
	
	def __init__(self,vehicleDict,fileName='vehicle_coordinates.txt'):
		self.fileName = fileName
		self.fileObject = open(self.fileName,'w')
		self.fileObject.write('(vid,position,lane)\n')
		self.vehicleDict = vehicleDict
		
	def step(self):
		for vid,v in self.vehicleDict.items():
			self.fileObject.write('%d,%f,%d\n'%(v.id,v.position,v.lane))
		self.fileObject.write('end\n')
			
	def __del__(self):
		self.fileObject.close()
		