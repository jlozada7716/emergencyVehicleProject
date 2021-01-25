import numpy as np
import matplotlib.pyplot as plt
import csv
import os.path
fig = plt.figure()
# ax = fig.add_axes([0.5, 0.5, 0.5, 0.5])
def graphMaker():
    with open(r"C:\Users\jloza\Documents\HarishProject\simple_simulation\AverageVehicleSpeedDataTrial7_100Iterations.csv", 'r') as inp:
        read_data = csv.reader(inp, delimiter=',')
        iterations = []
        times = []
        for row in read_data:
            iteration = float(row[0])
            time = float(row[1])
            iterations.append(iteration)
            times.append(time)

    # x_pos = [i for i, _ in enumerate(iteration)]
    plt.bar(iterations, times, color='blue')
    plt.xlabel("Vehicle Amount")
    plt.ylabel("Average Speed of Vehicles")
    plt.title("Speed Analysis Simulation")
    # plt.ylim(80, 105)
    plt.ylim(8, 12)
    plt.xticks(np.arange(min(iterations), max(iterations)+1, 5.0))
    plt.show()

graphMaker()