import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import optparse
import os
        
def make_plot(figure, riet_data, reflns_data=None, tth_start=0, tth_end=None, inset=False, font_sizes=None):
    def slice_on_tth(in_array, tth_start, tth_end):
        start_index = np.where(in_array[0] >= tth_start)[0][0]
        if tth_end is None:
            end_index = -1
        else:
            end_index =  np.where(in_array[0] >= tth_end)[0][0]
        return in_array[:,start_index:end_index]
    
    def myFormatter(x, pos):
        return "%.2f" % (x / (10**(scale_factor-1)))
    
    def get_axis_tick_pos(axis_min, axis_max):
        axis_range = axis_max - axis_min
        axis_scale = 10**(int(np.floor(np.log10(axis_range))))
        if (axis_range/axis_scale) <= 3:
            axis_tick_pos = axis_scale/2.0
        elif (axis_range/axis_scale) > 8:
            axis_tick_pos = axis_scale * 2.0
        else:
            axis_tick_pos = axis_scale
        print "axis_scale: "+str(axis_scale)
        print "axis_range: "+str(axis_range)
        print "axis_tick_pos: "+str(axis_tick_pos)
        return axis_tick_pos

 #  if font_sizes == None:
 #          font_sizes = {'tic_numbers':18, 'labels':24}
    
    #Slice our arrays & determine the overall maximum & minimum values...
    riet_plot_data = slice_on_tth(riet_data, tth_start, tth_end)
    maxima = np.amax(riet_plot_data, axis=1) #0 = tth, 1 = obs, 2 = calc, 3 = diff(, 4 = reflns) 
    minima = np.amin(riet_plot_data, axis=1)
    
    #If we're going to plot diff data on top of obs data, move the whole diff set down
    if maxima[3] > minima[1]:
        #Move down by the amount the two datasets overlap & recalculate minima + a bit
        riet_plot_data[3] -= (maxima[3] - minima[1]) + (max(maxima[1:]) * 0.01)
    else:
        riet_plot_data[3] += (max(maxima[1:]) * 0.01) - maxima[3]
    minima = np.amin(riet_plot_data, axis=1)
        
    #If we have reflection positions to plot too slice & set their position
    if reflns_data is not None:
        reflns_plot_data = np.stack((reflns_data, reflns_data))
        reflns_plot_data = slice_on_tth(reflns_plot_data, tth_start, tth_end)
        #Position is 2% of the maximum y value in the plot below the diff set
        refln_pos = minima[3] - (0.09 * 1 / np.log10(max(maxima[1:])) * max(maxima[1:]))
        reflns_plot_data[1].fill(refln_pos)
        
        maxima = np.append(maxima, refln_pos)
        minima = np.append(minima, refln_pos)
    
    #Set up the plot
    if inset:
        insetPos = [0.374, 0.57, 0.59, 0.4] #[0.31, 0.5, 0.59, 0.4]
        axes = figure.add_axes(insetPos)
    else:
        axes = figure.add_subplot(1,1,1)
    #...x-axis maxima & minima...
    axes.set_xlim(minima[0], maxima[0])
    x_tick_pos = get_axis_tick_pos(minima[0], maxima[0])
    axes.get_xaxis().set_major_locator(ticker.MultipleLocator(x_tick_pos))
    axes.get_xaxis().set_minor_locator(ticker.MultipleLocator(x_tick_pos / 4.0)) #To keep it as a float
    
    #...y-axis maxima & minima...
    if inset:
        scale_factor = main_scale_factor
        fudge_factor = 0.5
        axes.set_ylim(min(minima[1:]) - (max(maxima[1:]) * 0.05), max(maxima[1:]) * 1.05)
    else:
        scale_factor = int(round(np.log10(max(maxima[1:]))))
        fudge_factor = 1
        axes.set_ylim(min(minima[1:]) - (max(maxima[1:]) * 0.05), max(maxima[1:]) * 1.05)
    
    axes.get_yaxis().set_major_formatter(ticker.FuncFormatter(myFormatter))
    if int(round(np.log10(max(maxima[1:])))) <= (scale_factor - 1) :
        #When we have an inset with much smaller y-scale
        y_tick_pos = 10**(scale_factor-2)
    else:
        y_tick_pos = 10**(scale_factor-1)
    axes.get_yaxis().set_major_locator(ticker.MultipleLocator(y_tick_pos/fudge_factor))
    axes.get_yaxis().set_minor_locator(ticker.MultipleLocator(y_tick_pos / 4/fudge_factor))
    
    #Uncomment this line to not have any tick marks on the y-axis
 #   axes.get_yaxis().set_ticks([])
    axes.tick_params(labelsize=font_sizes['tic_numbers'])#16 #24
    
    #...and axis labels
    if not inset:
        axes.set_xlabel(r'2$\theta$ / '+u'\u00B0', fontsize=font_sizes['labels'])#20 #28
 #       axes.set_ylabel(r'Intensity / a.u.', fontsize=20)
        axes.set_ylabel(r'Intensity / $\times$'+'$10^{{{0:d}}}$'.format(scale_factor-1)+' a.u.', fontsize=font_sizes['labels'])
    
    #Finally plot the data
    axes.scatter(riet_plot_data[0], riet_plot_data[1], color='k', marker='+')
    axes.plot(riet_plot_data[0], riet_plot_data[2], color='r', linestyle='-')
    axes.plot(riet_plot_data[0], riet_plot_data[3], color='b', linestyle='-')
    if reflns_data is not None:
        axes.scatter(reflns_plot_data[0], reflns_plot_data[1], color='k', marker='|', s=56)
    
    #After everything is laid out, make sure we don't have any clipped text
    if not inset:
        plt.tight_layout()
    
    return scale_factor
        

def readData(dataFileName):
    try:
        return np.loadtxt(dataFileName, unpack=True)
    except:
        print 'Problems opening data file '+str(dataFileName)
        exit(1)

if __name__ == "__main__":
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
    
    rietveld_data = readData(data_file_path) #0 = tth, 1 = obs, 2 = calc, 3 = diff
    
    reflections_data = readData(reflns_file_path)
    
    fig_width=9 #Min is 6.6
    fig = plt.figure(figsize=(fig_width,fig_width*8/11))
#    fig = plt.figure(figsize=(11,8))

    #For a small final figure
    font_sizes = {'tic_numbers':18, 'labels':22}
    #For a large final figure
#    font_sizes = {'tic_numbers':14, 'labels':18}

#     Make the main plot and store the scale_factor
    main_scale_factor = make_plot(fig, rietveld_data, reflections_data, font_sizes=font_sizes)
#    main_scale_factor = make_plot(fig, rietveld_data, reflections_data, tth_start=8.4, font_sizes=font_sizes) 
    make_plot(fig, rietveld_data, reflections_data, tth_start=8.4, tth_end=39.99, inset=True, font_sizes=font_sizes)
#    main_scale_factor = make_plot(fig, rietveld_data, reflections_data, tth_start=14.19, tth_end=15.31)
    
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
    