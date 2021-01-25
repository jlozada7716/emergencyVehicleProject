import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

fig, ax = plt.subplots()
xdata, ydata = [], []
ln, = plt.plot([], [], 'ro', animated=True)

def init():
	ax.set_xlim(0, 2*np.pi)
	ax.set_ylim(-1, 1)
	return ln,

def update(frame):
	xdata = [frame]#xdata.append(frame)
	ydata = [np.sin(frame)]#ydata.append(np.sin(frame))
	ln.set_data(xdata, ydata)
	return ln,
	
def getFrames(frames):
	for frame in frames:
		yield frame 
		
frames = np.linspace(0, 2*np.pi, 128)
frameGenerator = getFrames(frames)


ani = FuncAnimation(fig, update, frameGenerator,
                    init_func=init, blit=True, interval = 100)
plt.show()