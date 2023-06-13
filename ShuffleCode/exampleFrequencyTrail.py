import numpy as np
import matplotlib.pyplot as plt

pi = np.pi
t=np.linspace(-2*pi, 2*pi, 1000)


fig, ax = plt.subplots(1,1)
for i in np.arange(1, pi, 0.05)[::-1]:
    left = np.exp(-(t + (i - 1) * 2*pi)**2) * np.cos(t * i)**2 - 1
    right = np.exp(-(t - (i - 1) * 2*pi)**2) * np.cos(t * i)**2 - 1 
    vertical_offset = i*2
    ax.fill_between(t, vertical_offset + left + right, facecolor='white',
        edgecolor='black')


plt.show()
