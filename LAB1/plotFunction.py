import matplotlib.pyplot as plt
import numpy as np

def function(points):
	fig, ax = plt.subplots()
	x = np.linspace(0,250,250)
	ax.plot(x,points)
	plt.show()
