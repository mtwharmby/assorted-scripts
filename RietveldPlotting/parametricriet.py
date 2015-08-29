import matplotlib as mpl
import matplotlib.ticker as ticker
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import matplotlib.pyplot as plt
import os
import string

scale_pow = 5

def main():
	#Get data from all sets using this list:
	#temps = [80,120,150,180,210,240,270,298]
	temps = [298,270,240,210,180,150,120,80]
	#temps=[298,80]
	
	allTDataSet={}
	rawTDataSet={}
	
	for t in temps:
		tempDataFileName = os.getcwd()+'\\RietPlots\\RietPlot_{:04d}'.format(t)+'.dat'
		rawTDataSet[t] = readData2(tempDataFileName)
		
	mpl.rcParams.update({'font.size':18})

	#### Assuming we've got the data sorted:
	fig = plt.figure(figsize=(12,8))
	ax = fig.add_subplot(111, projection='3d')
	
	for t in temps:
		axisX = rawTDataSet[t][:,0] #0th column of temp t
		axisY = np.empty(axisX.shape)
		axisY.fill(t)
		
		axisZ_diff = rawTDataSet[t][:,3]
		axisZ_obs = rawTDataSet[t][:,1]
		axisZ_calc = rawTDataSet[t][:,2]
		
		print str(t)+' obs max: '+str(np.amax(axisZ_obs))
		print str(t)+' calc max: '+str(np.amax(axisZ_calc))
		print str(t)+' diff min: '+str(np.amin(axisZ_diff))+'\n'
		
		#now make plots
		ax.plot(axisX, axisY, axisZ_diff, c='b', zorder=1)		
		ax.scatter(axisX, axisY, axisZ_obs, marker='x', s=8, c='k', zorder=5) #?
		ax.plot(axisX, axisY, axisZ_calc, c='r', zorder=10)
	
	ax.zaxis.set_major_formatter(ticker.FuncFormatter(myFormatter))
	
	#Ranges
	ax.set_xlim([3,40])
	ax.set_ylim([78,300])
	ax.set_zlim([-95000,602000])
		
	#Labels
	ax.set_xlabel(r'2$\theta$ / '+u'\u00B0')
	ax.set_ylabel('Temperature / K')
	ax.set_zlabel(r'Intensity / $\times$'+'$10^{{{0:d}}}$'.format(scale_pow)+' a.u.')
	
	#View direction
	ax.view_init(elev=15., azim=-40.)
	
	plt.show()


def readData(dataFileName):
	try:
		dataFile = open(dataFileName, 'rb')
	except:
		print 'Problems opening data file '+dataFileName
		exit(1)
	
	allLines = dataFile.readlines()
	dataFile.close()
	
	#Remove all white space and break up into values.
	allLines = map(string.split, allLines)
	
	#Cast strings as floats and return
	
	
	
	return [[float(x[0]), float(x[1]), float(x[2]), float(x[3])] for x in allLines]
	
def readData2(dataFileName):
	try:
		return np.loadtxt(dataFileName)
	except:
		print 'Problems opening data file '+dataFileName
		exit(1)

#from stackoverflow.com/questions/14775040
def myFormatter(x, p):
	return "%.2f" % (x / (10 ** scale_pow))


if __name__ == "__main__":
    main()
