'''
Created on 11 May 2016

@author: wnm24546
'''

import matplotlib.pyplot as plt
import numpy as np

def makePlot(a=1, b=4.8):
    fig = plt.figure()
    ax = fig.add_axes([0.12, 0.12, 0.76, 0.76], polar=True)
    r = np.arange(-8*np.pi, 8*np.pi, 0.01)
    theta = ((r+a)/b)**2
    ax.plot(theta, r, color='#00c000', lw=2)
    
    plt.show()
    
    fig.savefig(r"FermatSpiral.svg")

makePlot()