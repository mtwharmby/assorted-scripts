import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import optparse
import os

power = 5


def main():
    topas_files = False
    parser = optparse.OptionParser()
    parser.add_option('-p', '--plot', action='store', type='str')
    parser.add_option('-r', '--reflections', action='store', type='str')
    parser.add_option('-f', '--savefile', action='store', default=False, type='str')
    parser.add_option('-t', '--topas', action='store_true', default=False)
    parser.add_option('-s', '--save', action='store_true', default=False)
    opts, args = parser.parse_args()
    
    if opts.savefile and opts.save:
        print "Can't have two save options. Will display plot instead."
        opts.savefile = False
        opts.save = False
    if opts.save and not opts.topas:
        print "Can't save outside of topas mode and without a filename (use -f/--savefile). \nWill display plot instead."
        opts.save = False
    
    plt.rcParams['mathtext.fontset']='stixsans'
    
    if opts.topas:
        data_file_path = opts.plot+"_RietPlot.dat"
        reflns_file_path = opts.plot+"_Reflns.dat"
    else:
        data_file_path = opts.plot
        reflns_file_path = opts.reflections
    
    intens = readData(data_file_path)
    x_tth = intens[:,0]
    y_obs = intens[:,1]
    y_calc = intens[:,2]
    y_diff = intens[:,3]
    
    x_hkl = readData(reflns_file_path)
    
    fig = plt.figure(figsize=(11,8))
    mainAxes = fig.add_subplot(1,1,1)
    
    
    
    y_obs_max = findArrayMinMax(y_obs)[1]
    iDiffY, hklY = generatePlotDependentData(y_obs, y_calc, y_diff, x_hkl, y_obs_max)
    hklYPos = hklY[0]
    setupPlot(mainAxes, x_tth, y_obs, y_calc, hklYPos, y_obs_max, label=True)
    plotData(mainAxes, x_tth, y_obs, y_calc, iDiffY, x_hkl, hklY)
    
    insetPos = [0.31, 0.5, 0.59, 0.4]
    insetAxes = fig.add_axes(insetPos)
    
    insetMin = 18
    minIndex = np.where(x_tth >= insetMin)[0][0]
    tthI = x_tth[minIndex:]
    iObsI = y_obs[minIndex:]
    iCalcI = y_calc[minIndex:]
    iDiffI = y_diff[minIndex:]
    minHKLIndex = np.where(x_hkl >= insetMin)[0][0]
    hklXI = x_hkl[minHKLIndex:]
    
    iMaxI = findArrayMinMax(iObsI)[1]*1.1
    iDiffYI, hklYI = generatePlotDependentData(iObsI, iCalcI, iDiffI, hklXI, iMaxI)
    hklYIPos = hklYI[0]
    setupPlot(insetAxes, tthI, iObsI, iCalcI, hklYIPos, iMaxI, adjust_power=True)
    plotData(insetAxes, tthI, iObsI, iCalcI, iDiffYI, hklXI, hklYI)
    
    if opts.savefile:
        fileName = opts.savefile
        saveLocation = os.getcwd()
        outFile = os.path.join(saveLocation, fileName)
        plt.savefig(outFile, dpi=600)
    elif opts.save:
        fileName = opts.plot+"_RietveldPlot"
        saveLocation = os.getcwd()
        outFile = os.path.join(saveLocation, fileName)
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

def setupPlot(axesPlot, tthPlot, iObsPlot, iCalcPlot, hklYPosPlot, iMaxPlot, label=False, adjust_power=False):
    #Configure the main plot
    axesPlot.set_xlim(np.amin(tthPlot), np.amax(tthPlot))
    axesPlot.get_xaxis().set_major_locator(ticker.MultipleLocator(10))
    axesPlot.get_xaxis().set_minor_locator(ticker.MultipleLocator(2.5))
    yMin, yMax = findYMinMax(iObsPlot, iCalcPlot, hklYPosPlot, iMaxPlot, adjust_power)
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

def findYMinMax(iObsFind, iCalcFind, hklYPosFind, iMaxFind, adjust_power):
    if adjust_power:
        factor = power -1
    else:
        factor = power
    yMin = round((hklYPosFind-(iMaxFind*0.05))/10**(factor-1))*10**(factor-1)
    yMax = round((iMaxFind*1.05)/10**(factor-1))*10**(factor-1)
    
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
    