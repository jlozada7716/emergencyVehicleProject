import numpy as np
import matplotlib.pyplot as plt
import csv
import os.path
# fig = plt.figure()
# ax = fig.add_axes([0.5, 0.5, 0.5, 0.5])
def graphMaker(delta):
    with open(r"C:\Dev\emergencyVehicleProject\simUtilities\Practice\AverageSpeed_100Iterations2.csv", 'r') as inp:
        read_data = csv.reader(inp, delimiter=',')
        iterations = []
        times = []
        for row in read_data:
            iteration = float(row[0])
            speed = float(row[1]) * (1/delta)*2.23694
            iterations.append(iteration)
            times.append(speed)

    # x_pos = [i for i, _ in enumerate(iteration)]
    plt.figure()
    plt.plot(iterations, times)
    # plt.bar(iterations, times, color='blue')
    plt.xlabel("Vehicle Amount")
    plt.ylabel("Average Speed of Vehicles MPH")
    plt.title("Speed Analysis Simulation")
    # plt.ylim(80, 105)
    plt.ylim(30, 50)
    plt.xticks(np.arange(min(iterations), max(iterations)+1, 10.0))
    plt.show()

graphMaker(1/5)