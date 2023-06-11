import numpy as np
import matplotlib.pyplot as plt

Npts = 1001
Ps = np.linspace(0, 1, Npts)


p1mesh, p2mesh  = np.meshgrid(Ps, Ps, indexing ='ij')

S = np.zeros_like(p1mesh)
for i in range(Npts):
    for j in range(Npts):
        p1 = p1mesh[i,j]
        p2 = p2mesh[i,j]
        if p1 + p2 <= 1.:
            p3 = 1 -(p1 + p2)
            if p1 == 0:
                s = 0
            elif p2 == 0:
                s = 0
            elif p3 == 0:
                s = 0
            else:
                s = -1/np.log(3)*(p1*np.log(p1)+p2*np.log(p2)+p3*np.log(p3))
            
            S[i,j] = s

#cp = plt.contour(Ps, Ps, S, 20)
#plt.clabel(cp, inline=True, fontsize=10)
h = plt.contourf(Ps, Ps, S, 50)
#plt.axis('scaled')

plt.plot([0,1/3],[1/3,1/3], 'k--')
plt.plot([1/3,1/3],[0,1/3], 'k--')
plt.scatter([1/3], [1/3], color = 'black')
plt.colorbar()

plt.xlabel('$p_1$')
plt.ylabel('$p_2$')

plt.savefig('../Images/trinomialEntropy.svg')
#plt.show()
