'''
Created on 4 Jul 2016

@author: wnm24546
'''

import os
import h5py
import numpy as np

baseName = -1 #This is important.

def getDataFromFile(filename):
    print "FName="+filename
    with h5py.File(filename, 'r') as dataFile:
        return dataFile['/entry/instrument/detector/data'][()]

############################################
## EDIT LINES BELOW HERE ###################
############################################
#Give the directory path the files are and... (all values between ' or ")
wDir = '/dls/i15/data/2016/ee14091-1'

#...either the full name of the files...
#files = ['112004_KNJ-KA-218-01-PtNi-120s.hdf5', '112031_KNJ-KA-218-01-PtNi-120s.hdf5']

#...or the base name of the files and their numbers
baseName = '_Hf-Fum(10x2min)_aq-3s_2min.hdf5'
files = [222643, 222702, 222761, 222820, 222879,
         222938, 222997, 223056, 223115, 223174]


############################################
## NOTHING SHOULD NEED EDITING BELOW HERE ##
############################################
#Get numpy datasets from each of the files and put them into a list
dataSets = []
for name in files:
    if baseName == -1:
        fName = os.path.join(wDir, name)
    else:
        fName = os.path.join(wDir, str(name)+baseName)
    dataSets.append(getDataFromFile(fName))

#Merge dataSets into one big dataset with the same shape (0,2048,2048)
sumDataSet = np.zeros(dataSets[0].shape)
for dataSet in dataSets:
    sumDataSet = np.add(dataSet, sumDataSet)
#Create an average dataset by dividing the sumdataset by the number of files
avsDataSet = sumDataSet/len(files)

#Output the summed data and the averaged data to two HDF files with different names
outputFiles = {'Summed' : sumDataSet, 'Averaged' : avsDataSet}
for key in outputFiles:
    if baseName != -1:
        foutName = key+baseName
    else:
        foutName = key
    
    outputPath = os.path.join(wDir, 'processing')
    if not os.path.exists(outputPath):
        os.makedirs(outputPath)
        
    with h5py.File(os.path.join(outputPath, foutName), 'w') as outHDF:
        outHDF.attrs['creator']="mergeHDFs.py"
        outHDF.attrs['author']="Diamond Light Source Ltd."
        entry = outHDF.create_group('entry')
        instrument = entry.create_group('instrument')
        detector = instrument.create_group('detector')
        data = detector.create_dataset('data', data=outputFiles[key])
        data.attrs['dim0']="frame number n"
        data.attrs['dim1']="NDArray dim1"
        data.attrs['dim2']="NDArray dim0"
        data.attrs['interpretation']="image"
        data.attrs['signal']=1
        
        outHDF.close()
