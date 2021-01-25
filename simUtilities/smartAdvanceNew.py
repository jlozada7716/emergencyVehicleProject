import numpy as np
import os, sys
sys.path.append(os.path.join(os.sep, 'gitlab_repos', 'emergency_vehicle_cooperative_driving','pyscripts','simUtilities'))

from .vehicle import vehicle
from .simulation import simulation
import networkx as nx
import pdb


class smartAdvanceNew():
	vehicleDict = None 
	sid = None #vehicle to advance
	nOfLanes = 3
	logDump = False
	logFile = 'log.txt'
	simulation = None
	planningTime = 20
	waitTime = 1
	
	
	
	def __init__(self,vehicleDict,vehicleIDToAdvance=-1,planningTime=20,simulation=None):
		self.vehicleDict = vehicleDict
		self.planningTime = planningTime
		self.sid = vehicleIDToAdvance
		self.simulation = simulation
			
		
		
	def step(self):
		#check if the interested vehicle is in scene 
		if not self.sid in self.vehicleDict: return
		if self.waitTime:
			self.waitTime = self.waitTime - 1
			return 
		sv = self.vehicleDict[self.sid]
		if (len(sv.trajectory)==0):#if target reached 
			sv.trajectory = self.computeTrajectory()#calculate trajectory
		
				
		
		
	def myround(self, x, base=5): #rounding to closest 0.5
		return int(base * round(float(10*x)/base))/10 	


	# def getLeaderAndFollower(self,position,lane):
		# vf = None
		# vl = None
		# for vid,v in self.vehicleDict.items():
			# if (v.lane!=lane) or (vid == self.sid): continue
			# if (v.position<position) and (vf==None or vf.position<v.position): vf = v 
			# if (v.position>position) and (vl==None or vl.position>v.position): vl = v 
		# return (vf,vl)
			 
		
	def computeTrajectory(self):
		#create an empty graph 
		G = nx.DiGraph()
		sv = self.vehicleDict[self.sid]
		#add all nodes to the graph 
		spaceResolution = 0.5
		
		predictionTime =  self.planningTime #assuming speed = 1, in general it will be greater 
		plannedPosition = sv.position + sv.maxSpeed*predictionTime
		
		for x in np.arange(self.myround(sv.position),plannedPosition+5*spaceResolution,spaceResolution):
			for t in range(predictionTime+1):
				for l in range(self.nOfLanes):
					G.add_node((x,t,l)) #(position,time,lane)
					
		#predict vehicle positions and label nodes
		nodeLabels = {}			
		for x in G: nodeLabels[x] = False #initialize all nodes as unoccupied
		
		#pdb.set_trace()
			
		for t in range(predictionTime+1):#predict vehicle positions and label nodes
			for vid,v in self.vehicleDict.items():
				if vid == self.sid: continue 
				vpt = v.position + t*v.speed 
				occRange = (self.myround(vpt-sv.maxSpeed*sv.tau-v.length),self.myround(vpt+v.maxSpeed*v.tau+sv.length))
				#label the occupied nodes 
				for x in np.arange(occRange[0],occRange[1],spaceResolution):
					nodeLabels[(x,t,v.lane)] = True
		#pdb.set_trace()
		
		
		#add all edges to the graph 
		sourceNode = (self.myround(sv.position),0,sv.lane)
		reachableNodes = set([sourceNode]) #(position,time,lane)
		#targetReached = False
		#targetNode = None
		legalLanes = set(range(self.nOfLanes))
		ss = sv.speed 
		sa = sv.acceleration
		
		laneChangeWeight = 0.0001
		stoppingPenalty = 0.0001
		farthestReachableNode = None 
		farthestReachableNodes = set()
		farthestReachbleDistance = 0
		#pdb.set_trace()
		for t in range(predictionTime+1):#from all the reachable nodes at time t, add edges corresponding all the reachable nodes to time t+1
			#if targetReached: break
			#pdb.set_trace()
			lmax = sv.maxSpeed #assuming infinite acceleration
			#self.myround(np.minimum(ss + sa,sv.maxSpeed)) #estimated maximum initial speed + acceleration 
			#lmaxAdded = 0 #max length of edges which were actually added
			newReachable = set()
			for node in reachableNodes: #iterate through all current reachable nodes 
				adjacentLanes = set(range(node[2]-1,node[2]+2)) #can only move by one lane 
				for lane in adjacentLanes.intersection(legalLanes):
					for y in np.arange(node[0],node[0]+lmax+spaceResolution,spaceResolution): #for each node y
						reachableNode = (y,t+1,lane) #node in time t+1 under consideration
						if reachableNode in nodeLabels and not nodeLabels[reachableNode]:
							# if y >= plannedPosition: 
								# targetReached = True
								# targetNode = reachableNode
							newReachable.add(reachableNode)
							if reachableNode[1] == predictionTime:
								if reachableNode[0]==farthestReachbleDistance:
									farthestReachableNodes.add(reachableNode)
								if reachableNode[0]>farthestReachbleDistance: 
									farthestReachableNode = reachableNode
									farthestReachableNodes = set()
									farthestReachableNodes.add(farthestReachableNode)
									farthestReachbleDistance = reachableNode[0]
							
							#if y-node[0] > lmaxAdded: lmaxAdded = y - node[0]
							G.add_edge(node,reachableNode)
							#add weights 
							edgeWeight = 1
							if node[2] != reachableNode[2]: edgeWeight = edgeWeight + laneChangeWeight
							if node[0] == reachableNode[0]: edgeWeight = edgeWeight + stoppingPenalty
							G[node][reachableNode]['weight'] = edgeWeight
							# if lane == node[2]: G[node][reachableNode]['weight'] = 1
							# else: G[node][reachableNode]['weight'] = 1+laneChangeWeight
							
			#ss = lmaxAdded#update speed 
			reachableNodes = newReachable
		
		# pdb.set_trace()	
		#compute the shortest path between the source and the targetNode 
		trajectory = []
		trajectories = []
		
		
		if farthestReachableNode == None: 
			print('something went wrong while calculating the best trajectory')
			return []
		else:
			# try:
				# trajectory = nx.shortest_path(G,source=sourceNode,target=farthestReachableNode,weight='weight')
			# except nx.exception.NetworkXNoPath as e:
				# pass 
			try: 
				for targetNode in farthestReachableNodes:
					trajectories.append((nx.shortest_path(G,source=sourceNode,target=targetNode,weight='weight'), nx.shortest_path_length(G,source=sourceNode,target=targetNode,weight='weight')))
				trajectories.sort(key=lambda x: x[1])
				trajectory = trajectories[0][0]
			except nx.exception.NetworkXNoPath as e:
				pass 
		
		
		
		
			
		
		return trajectory[1:]
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
#place holder 
		
		
		
		
		
		
		
		
		
		
		