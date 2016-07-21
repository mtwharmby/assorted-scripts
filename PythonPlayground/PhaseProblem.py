'''
Created on 2 Dec 2015

@author: wnm24546
'''

from scipy import fftpack
from PIL import Image

import matplotlib.pyplot as plt
import numpy as np
plt.close('all')


def makeFig(n, imageFile):
    img = Image.open(imageFile)
    dat = np.asarray(img)
    fft = fftpack.fft2(dat)
    
    fig=plt.figure(n)
    plt.subplot(121)
    plt.imshow(img)
    plt.subplot(122)
    plt.imshow(np.abs(fft))
    fig.show()

makeFig(1, "./WhiteOnBlack.png")
makeFig(2, "./BlackOnWhite.png")
plt.show()
