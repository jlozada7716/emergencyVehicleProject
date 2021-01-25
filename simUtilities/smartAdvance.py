import numpy as np
import os, sys
sys.path.append(os.path.join(os.sep, 'gitlab_repos', 'emergency_vehicle_cooperative_driving','pyscripts','simUtilities'))

from .vehicle import vehicle
from .simulation import simulation
import networkx as nx
import pdb


class smartAdvance():
	vehicleDict = None 
	sid = None #vehicle to advance
	nOfLanes = 3
	planAheadDistance = 600
	targetPosition = 0
	trajectory = []
	logDump = False
	logFile = 'log.txt'
	simulation = None
	
	
	
	def __init__(self,vehicleDict,vehicleIDToAdvance=-1,planAheadDistance=200,simulation=None):
		self.vehicleDict = vehicleDict
		self.planAheadDistance = planAheadDistance
		self.sid = vehicleIDToAdvance
		self.simulation = simulation
		if self.logDump:
			with open(self.logFile, 'w') as out: 
				out.write('in __init__ file:\n')
				out.write('this file contains the logs from the simulation\n')
				out.write('----------------\n')
			
		
		
	def step(self):
		#check if the interested vehicle is in scene 
		if not self.sid in self.vehicleDict: return
		sv =self.vehicleDict[self.sid]
		if sv.position >= self.targetPosition:#if target reached 
			self.targetPosition = self.targetPosition + self.planAheadDistance#update targetPosition
			self.trajectory = self.computeTrajectory()#calculate trajectory
		if len(self.trajectory)>0:
			vf,vl,l = self.trajectory[0]#pick the first lane change info
			#if the leading and following vehicle are still in the target lane and are contiguous
			if (vl == None or vl.lane ==l) and (vf == None or vf.lane == l) and self.areContiguous(vl,vf):
				if (vl != None) and vl.position < sv.position: #is leading vehicle behind the emergency vehicle? 
					sv.slowDownMode = True #slow down
				else:
					sv.slowDownMode = False 
					if (vf == None) or vf.position < sv.position: 
						if sv.changeLane(l-sv.lane):
							self.trajectory.pop(0)
			else:
				self.trajectory = self.computeTrajectory()
				
		
		
	def areContiguous(self,vl,vf):
		if (vl == None or vf == None ): return True #no need to check for contiguity
		for vid,v in self.vehicleDict.items():
			if (v.lane == vl.lane  and  (v.position > vf.position) and (v.position < vl.position)):
				#print('leader and follower not contiguous')
				return False 
		return True 
		
	def myround(self, x, base=5): #rounding to closest 0.5
		return int(base * round(float(10*x)/base))/10 	


	def getLeaderAndFollower(self,position,lane):
		vf = None
		vl = None
		for vid,v in self.vehicleDict.items():
			if (v.lane!=lane) or (vid == self.sid): continue
			if (v.position<position) and (vf==None or vf.position<v.position): vf = v 
			if (v.position>position) and (vl==None or vl.position>v.position): vl = v 
		return (vf,vl)
			 
		
	def computeTrajectory(self):
		#print('computing trajectory')
		#input('press any key and enter ....')
		#create an empty graph 
		G = nx.DiGraph()
		sv = self.vehicleDict[self.sid]
		#add all nodes to the graph 
		spaceResolution = 0.5
		plannedPosition = self.myround(sv.position+self.planAheadDistance+spaceResolution)
		predictionTime =  int(round(plannedPosition-sv.position)) #assuming speed = 1, in general it will be greater 
		
		#print('start,end,targetPosition: (%f,%f,%f)'%(sv.position,sv.position+self.planAheadDistance+spaceResolution,self.targetPosition))
		#print('predictionTime: %f'%predictionTime)
		for x in np.arange(self.myround(sv.position),plannedPosition+5*spaceResolution,spaceResolution):
			for t in range(predictionTime):
				for l in range(self.nOfLanes):
					G.add_node((x,t,l)) #(position,time,lane)
					
		#predict vehicle positions and label nodes
		nodeLabels = {}			
		for x in G: nodeLabels[x] = False #initialize all nodes as unoccupied
		
		#pdb.set_trace()
			
		for t in range(predictionTime):#predict vehicle positions and label nodes
			for vid,v in self.vehicleDict.items():
				if vid == self.sid: continue 
				vpt = v.position + t*v.speed 
				occRange = (self.myround(vpt-sv.maxSpeed*sv.tau-v.length),self.myround(vpt+v.maxSpeed*v.tau+sv.length))
				#label the occupied nodes 
				for x in np.arange(occRange[0],occRange[1],spaceResolution):
					nodeLabels[(x,t,v.lane)] = True
		#pdb.set_trace()
		
		# if self.logDump:
			# with open(self.logFile,'a') as out:
				# out.write('just done with labeling all the nodes in the compute trajectory method\n')
				# for x in G: out.write(str(x)+'\n')
				# out.write('----------------\n')
		
		# if self.logDump:
			# with open(self.logFile, 'a') as out:
				# for x,occ in nodeLabels.items():
					# if occ and x[1] == 0: out.write(str(x)+'\n')
		
		

		
		
		#add all edges to the graph 
		reachableNodes = set([(self.myround(sv.position),0,sv.lane)]) #(position,time,lane)
		
		
		targetReached = False
		targetNode = None
		legalLanes = set(range(self.nOfLanes))
		ss = sv.speed 
		sa = sv.acceleration
		path = []
		#print('speed,acceleration: %f,%f'%(ss,sa))
		laneChangeWeight = 0.0001
		for t in range(predictionTime):#from all the reachable nodes at time t, add edges corresponding all the reachable nodes to time t+1
			if targetReached: break
			lmax = self.myround(np.minimum(ss + sa,sv.maxSpeed)) #estimated maximum initial speed + acceleration 
			lmaxAdded = 0 #max length of edges which were actually added
			newReachable = set()
			for node in reachableNodes: #iterate through all current reachable nodes 
				adjacentLanes = set(range(sv.lane-1,sv.lane+2)) #can only move by one lane 
				for lane in adjacentLanes.intersection(legalLanes):
					for y in np.arange(node[0],node[0]+lmax+spaceResolution,spaceResolution): #for each node y
						reachableNode = (y,t+1,lane) #node in time t+1 under consideration
						if reachableNode in nodeLabels and not nodeLabels[reachableNode]:
							if y >= plannedPosition: 
								targetReached = True
								targetNode = reachableNode
							newReachable.add(reachableNode)
							if y-node[0] > lmaxAdded: lmaxAdded = y - node[0]
							G.add_edge(node,reachableNode)
							#add weights 
							if lane == node[2]: G[node][reachableNode]['weight'] = 1
							else: G[node][reachableNode]['weight'] = 1+laneChangeWeight
			ss = lmaxAdded#update speed 
			reachableNodes = newReachable
			#dump newly reachable nodes to the log file
			# if self.logDump:
				# with open(self.logFile, 'a') as out:
					# out.write('newly reachable noded from time %d to %d\n'%(t,t+1))
					# for x in reachableNodes: out.write(str(x)+'\n')
					# out.write('-----------------------\n')
						
		#compute the shortest path between the source and target node 
		sourceNode = (self.myround(sv.position),0,sv.lane)
		if not targetReached:
			print('target not reached\n')
			return []
		
		try:
			#print('source node:%s, target node:%s'%(sourceNode,targetNode))
			path = nx.shortest_path(G,source=sourceNode,target=targetNode,weight='weight')
		except nx.exception.NetworkXNoPath as e:
			print('cannot find a path. Reason: %s'%e)
			return []
			
		# print('shortest path is computed')
		# inp = input('do you want to print the path (y/n)?:')
		# if inp == 'y':
			# print(path)
			
		
		#dump the path to the log file
		if self.logDump:
			with open(self.logFile,'a') as out:
				out.write('just done computing the shortest path, printed below:\n')
				out.write(str(path)+'\n')
				out.write('--------------\n')
				
		#inp = input('do you want to continue y/n:')
		#if inp == 'n': quit()
		
			
		#compute the lane changes 
		previousLane = path[0][2]
		trajectory = []
		for node in path[1:]:
			lane = node[2]
			if lane != previousLane: #lane change detected 
				#get leader and follower in the target lane 
				#print('detected change in lane in the path at node: '+str(node))
				vf,vl = self.getLeaderAndFollower(node[0],node[2])
				#print('the follower and the leader are %s,%s'%(vf,vl))
				trajectory.append((vf,vl,node[2]))
			previousLane = lane 
			
		# if inp == 'y': #alreay printed the path
			# inp = input('do you want to print the trajectory (y/n)?:')
			# if inp == 'y':
				# lanceChanges = []
				# for x in trajectory: 
					# laneChange = []
					# if x[0]== None: laneChange.append(None)
					# else: laneChange.append(x[0].id)
					# if x[1] == None: laneChange.append(None)
					# else: laneChange.append(x[1].id)
					# laneChange.append(x[2])
					# lanceChanges.append(laneChange)
				# print(lanceChanges)
				# input('press any key and enter to continue')
		
		#print('trajectory:')
		# for x in trajectory:
			# vfid = None 
			# vlid = None 
			# targetLane = x[2]
			# if x[0] != None: vfid = x[0].id
			# if x[1] != None: vlid = x[1].id 
			# print('vf,vl,lane: %s,%s,%s'%(vfid,vlid,targetLane))
		# input('enter any key and press enter: ')
		
		return trajectory
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
#place holder 
		
		
		
		
		
		
		
		
		
		
		