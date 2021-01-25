import numpy as np
import matplotlib.pyplot as plt 
from matplotlib.animation import FuncAnimation
import matplotlib.animation as animation
import time

import os, sys 
sys.path.append(os.path.join(os.sep, 'gitlab_repos', 'emergency_vehicle_cooperative_driving','pyscripts'))
import simUtilities
import pdb


#pdb.set_trace = lambda: None 

# np.random.seed(seed=10)
stopTime = 700 #stop after 700 steps 
Simulation = simUtilities.simulation(stopTime=stopTime) #create a simulation 

#setting up the figure for animation 
fig, ax = plt.subplots()
xdata, ydata = [], []
ln, = plt.plot([], [], 'ro', animated=True)
ln1, = plt.plot([],[], 'bo', animated=True)



		
		
def getNextPositions(): #will advance the simulation by one step and yeilds the vehiclelist 
	while(Simulation.step()): yield Simulation.vehicleDict
	

	
def init():
	ax.set_xlim(0, 500)
	ax.set_ylim(-0.2, 2.2)
	return ln,

	
def update(frame):
	xdata = []
	ydata = []
	sXdata = []
	sYdata = []
	lowerLimit = 0
	vehiclesInScene = []
	plotLength = 100
	for vid,v in frame.items():
		if vid == -1:
			sXdata.append(v.position)
			sYdata.append(v.lane)
			lowerLimit = np.maximum(0,v.position-plotLength)
			#ax.set_title('emergency vehicle speed: %f'%v.speed)
		else:
			xdata.append(v.position)
			ydata.append(v.lane)
		# if (-1 in frame) and (np.abs(frame[-1].position-v.position)<=plotLength): 
			# vehiclesInScene.append(v)
	
	#collect vehicles in different lanes 
	# laneStrings = ['0: ','1: ','2: ']
	# for v in vehiclesInScene:
		# laneStrings[v.lane] = laneStrings[v.lane]+str(v.id)+','
	
	upperLimit = lowerLimit + 2*plotLength
	ax.set_xlim(lowerLimit,upperLimit)
	# for s in laneStrings:
		# print(s)
	ln.set_data(xdata, ydata)
	ln1.set_data(sXdata,sYdata)
	#pdb.set_trace()
	return ln,ln1
	
	
	
def compare_greedy_and_smart():
	tic = time.time()
	with open('simulation_results1.csv', 'w') as out: 
		out.write('iteration,greedy_distance,smart_distance\n')
		for iteration in range(100,400):
			print('iteration #%d'%iteration)
			#perform greedy algo first 
			print('greedy algo:')
			np.random.seed(seed=iteration)
			stopTime = 1000
			insertTime=500
			Simulation = simUtilities.simulation(stopTime=stopTime) #starts the simulation 
			
			vehicleDumper = simUtilities.addVehiclesAtRandomIntervals(Simulation.vehicleDict,trafficDensity=0.15)
			Simulation.stepListeners.append(vehicleDumper)
					
			emergencyVdumper = simUtilities.addSpecialVehicle(Simulation,insertTime=insertTime)
			Simulation.stepListeners.append(emergencyVdumper)
			
			greedyAlgo = simUtilities.greedyAdvance(Simulation.vehicleDict,vehicleIDToAdvance=-1)
			Simulation.stepListeners.append(greedyAlgo)
			
			for i in range(stopTime):
				Simulation.step()
			
			greedy_distance = Simulation.vehicleDict[-1].position
			
			
			#perform smart algo next  
			print('smart algo:')
			np.random.seed(seed=iteration)
			stopTime = 1000
			insertTime=500
			Simulation = simUtilities.simulation(stopTime=stopTime) #starts the simulation 
			
			vehicleDumper = simUtilities.addVehiclesAtRandomIntervals(Simulation.vehicleDict,trafficDensity=0.15)
			Simulation.stepListeners.append(vehicleDumper)
					
			emergencyVdumper = simUtilities.addSpecialVehicle(Simulation,insertTime=insertTime)
			Simulation.stepListeners.append(emergencyVdumper)
			
			
			smartAlgo = simUtilities.smartAdvanceNew(Simulation.vehicleDict,vehicleIDToAdvance=-1)
			Simulation.stepListeners.append(smartAlgo)
			
			
			
			for i in range(stopTime):
				Simulation.step()
			
			smart_distance = Simulation.vehicleDict[-1].position
			
			out.write('%d,%f,%f,\n'%(iteration,greedy_distance,smart_distance))

	toc = time.time()
	print('elapsed time: %f'%(toc-tic))



def main():
	#compare_greedy_and_smart()
	np.random.seed(seed=11)
	
	insertTime=500
	 #starts the simulation 


	vehicleDumper = simUtilities.addVehiclesAtRandomIntervals(Simulation.vehicleDict,trafficDensity=0.1)
	Simulation.stepListeners.append(vehicleDumper)
	
	
	emergencyVdumper = simUtilities.addSpecialVehicle(Simulation,insertTime=insertTime)
	Simulation.stepListeners.append(emergencyVdumper)
	
	# vehicleDumper = simUtilities.addVehiclesForExample1(Simulation.vehicleDict,Simulation=Simulation)
	# Simulation.stepListeners.append(vehicleDumper)
	# insertTime = 0

	# print('greedy algo:')
	greedyAlgo = simUtilities.greedyAdvance(Simulation.vehicleDict,vehicleIDToAdvance=-1)
	Simulation.stepListeners.append(greedyAlgo)
	
	# print('smart algo:')
	# smartAlgo = simUtilities.smartAdvanceNew(Simulation.vehicleDict,vehicleIDToAdvance=-1)
	# Simulation.stepListeners.append(smartAlgo)
	
	# outputDumper = simUtilities.dumpVehicleCoords(Simulation.vehicleDict)
	# Simulation.stepListeners.append(outputDumper)
	
	for i in range(insertTime):
		Simulation.step()
	
	
	frameGenerator = getNextPositions()
	# Writer = animation.writers['ffmpeg']
	# writer = Writer(fps=5, metadata=dict(artist='Me'), bitrate=1800)
	ani = FuncAnimation(fig, update, frameGenerator,init_func=init, blit=True, interval = 100,save_count=stopTime-insertTime)
	# ani.save('sceneSimulation.mp4', writer=writer)
	#WAS ADDED BELOW TWO LINES UNCOMMENT THE TOP THREE
	# writervideo = animation.FFMpegWriter(fps = 5)
	# ani.save('sceneSimulation.mp4', writer = writervideo)
	plt.show()
	
	# print('number of lane changes: %d'%Simulation.vehicleDict[-1].laneChangeCount)
	# print('average distance to leading vehicle: %f'%(Simulation.vehicleDict[-1].distanceToLeadingVehicle/(Simulation.timeStep-insertTime)))
	# print('distance travelled:%f'%Simulation.vehicleDict[-1].position)
	
		
	
	
	
if __name__ == '__main__':
	main()
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
