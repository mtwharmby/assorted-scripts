import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import optparse
import os

power = 5


def main():
    parser = optparse.OptionParser()
    parser.add_option('-p', '--plot', action='store', type='str')
    parser.add_option('-r', '--reflections', action='store', type='str')
    parser.add_option('-s', '--savefile', action='store', default=False, type='str')
    opts, args = parser.parse_args()
    
    plt.rcParams['mathtext.fontset']='stixsans'
    
    intens = readData(opts.plot)
    tth = intens[:,0]
    iObs = intens[:,1]
    iCalc = intens[:,2]
    iDiff = intens[:,3]
    
    hklX = readData(opts.reflections)
    
    fig = plt.figure(figsize=(11,8))
    mainAxes = fig.add_subplot(1,1,1)
    
    iMax = findArrayMinMax(iObs)[1]
    iDiffY, hklY = generatePlotDependentData(iObs, iCalc, iDiff, hklX, iMax)
    hklYPos = hklY[0]
    setupPlot(mainAxes, tth, iObs, iCalc, hklYPos, iMax, label=True)
    plotData(mainAxes, tth, iObs, iCalc, iDiffY, hklX, hklY)
    
    insetPos = [0.31, 0.5, 0.59, 0.4]
    insetAxes = fig.add_axes(insetPos)
    
    insetMin = 5
    minIndex = np.where(tth >= insetMin)[0][0]
    tthI = tth[minIndex:]
    iObsI = iObs[minIndex:]
    iCalcI = iCalc[minIndex:]
    iDiffI = iDiff[minIndex:]
    minHKLIndex = np.where(hklX >= insetMin)[0][0]
    hklXI = hklX[minHKLIndex:]
    
    iMaxI = findArrayMinMax(iObsI)[1]*1.1
    iDiffYI, hklYI = generatePlotDependentData(iObsI, iCalcI, iDiffI, hklXI, iMaxI)
    hklYIPos = hklYI[0]
    setupPlot(insetAxes, tthI, iObsI, iCalcI, hklYIPos, iMaxI)
    plotData(insetAxes, tthI, iObsI, iCalcI, iDiffYI, hklXI, hklYI)
    
    if opts.savefile:
        fileName = opts.savefile
        saveLocation = os.getcwd()
        outFile = os.path.join(saveLocation, "RietveldPlots", fileName)
        plt.savefig(outFile, dpi=600)
        
    else:
        plt.show()

def readData(dataFileName):
    try:
        return np.loadtxt(dataFileName)
    except:
        print 'Problems opening data file '+str(dataFileName)
        exit(1)

def myFormatter(x, p):
    return "%.2f" % (x / (10 ** power))

def setupPlot(axesPlot, tthPlot, iObsPlot, iCalcPlot, hklYPosPlot, iMaxPlot, label=False):
    #Configure the main plot
    axesPlot.set_xlim(np.amin(tthPlot), np.amax(tthPlot))
    axesPlot.get_xaxis().set_major_locator(ticker.MultipleLocator(10))
    axesPlot.get_xaxis().set_minor_locator(ticker.MultipleLocator(2.5))
    yMin, yMax = findYMinMax(iObsPlot, iCalcPlot, hklYPosPlot, iMaxPlot)
    axesPlot.set_ylim(yMin, yMax)
    axesPlot.get_yaxis().set_major_formatter(ticker.FuncFormatter(myFormatter))
    axesPlot.get_yaxis().set_major_locator(ticker.MultipleLocator(10**power))
    axesPlot.get_yaxis().set_minor_locator(ticker.MultipleLocator(5*10**(power-1)))
    
    if label:
        axesPlot.set_xlabel(r'2$\theta$ / '+u'\u00B0', fontsize=16)
        axesPlot.set_ylabel(r'Intensity / $\times$'+'$10^{{{0:d}}}$'.format(power)+' a.u.', fontsize=16)

def plotData(axesPlot, tthPlot, iObsPlot, iCalcPlot, iDiffPlot, hklXPlot, hklYPlot):
    axesPlot.scatter(tthPlot, iObsPlot, color='k', marker='+')
    axesPlot.plot(tthPlot, iCalcPlot, color='r', linestyle='-')
    axesPlot.plot(tthPlot, iDiffPlot, color='b', linestyle='-')
    axesPlot.scatter(hklXPlot, hklYPlot, color='k', marker='|', s=56)

def generatePlotDependentData(iObsGen, iCalcGen, iDiffGen, hklXGen, iMaxGen):
    iDiffMaxMinGen = findArrayMinMax(iDiffGen)
    iDiffYGen = shiftIDiff(iDiffGen, iDiffMaxMinGen, findArrayMinMax(iObsGen)[0])
    iDiffYMaxMinGen = findArrayMinMax(iDiffYGen)
    hklYGen = np.array(hklXGen, dtype=float)
    hklYGen.fill(iDiffYMaxMinGen[0]-(iMaxGen*0.05))
    
    return iDiffYGen, hklYGen

def shiftIDiff(iDiffShift, iDiffMinMaxShift, iMinShift):
    if iDiffMinMaxShift[1] > iMinShift:
        shift = iMinShift-iDiffMinMaxShift[1]
        iDiffShift = iDiffShift+shift
    
    return iDiffShift

def findYMinMax(iObsFind, iCalcFind, hklYPosFind, iMaxFind):
    yMin = round((hklYPosFind-(iMaxFind*0.05))/10**(power-1))*10**(power-1)
    yMax = round((iMaxFind*1.05)/10**(power-1))*10**(power-1)
    
    return yMin, yMax

def findArrayMinMax(array):
    return np.array([np.amin(array), np.amax(array)])

def findTwoArrayMinMax(arrayOne, arrayTwo):
    maxMins = np.array([findArrayMinMax(arrayOne), findArrayMinMax(arrayTwo)])
    
    iMin = np.amin(maxMins[:,0])
    iMax = np.amax(maxMins[:,1])
    
    return [iMin, iMax]


if __name__ == "__main__":
    main()
    