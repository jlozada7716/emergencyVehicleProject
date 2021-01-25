import pandas as pd 
import matplotlib.pyplot as plt
import numpy as np


data = pd.DataFrame.from_csv('simulation_results.csv')


def getHistogram(a):
	n,bins = np.histogram(a)
	centers = [(bins[i]+bins[i+1])/2 for i in range(len(bins)-1)]
	return (n,centers)
	

n1,centers1 = getHistogram(data['greedy_distance'])
n2,centers2 = getHistogram(data['smart_distance'])
n3,centers3 = getHistogram(data['smart_distance']-data['greedy_distance'])
	
plt.plot(centers1,n1,label='Greedy Algorithm')
plt.plot(centers2,n2,label='CANSAVE')
# plt.hist(data['greedy_distance'],label='Greedy Algorithm')
# plt.hist(data['smart_distance'],label='Smart Algorithm')
plt.legend()
plt.xlabel('distance travelled')
plt.ylabel('frequency')


plt.figure()
#plt.plot(centers3,n3,label='Smart-Greedy')
plt.hist(data['smart_distance']-data['greedy_distance'])
plt.xlabel('difference of distance travelled')
plt.ylabel('frequency')
plt.show()
