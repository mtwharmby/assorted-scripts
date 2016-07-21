'''
Created on 4 Jul 2016

@author: wnm24546
'''

import glob, os, sys
import h5py
import numpy as np


############################################
## EDIT LINES BELOW HERE ###################
############################################
#Give the directory path the files are and... (all values between ' or ")
working_directory = '/scratch/tmp'

#...either the full name of the files...
#files_names = ['112004_KNJ-KA-218-01-PtNi-120s.hdf5', '112031_KNJ-KA-218-01-PtNi-120s.hdf5']

#...or the base name of the files and their numbers
file_name_template = '_Hf-Fum(10x2min)_aq-3s_2min.hdf5'
file_numbers = [222643, 222702, 222761, 222820, 222879,
                222938, 222997, 223056, 223115, 223174]


############################################
## NOTHING SHOULD NEED EDITING BELOW HERE ##
############################################

def main():
    #Get numpy datasets from each of the files and put them into a list
    dataSets = []
    for name in files:
        if template == -1:
            fName = os.path.join(wDir, name)
        else:
            fName = os.path.join(wDir, str(name)+template)
        dataSets.append(get_data_from_file(fName))
    
    #Merge dataSets into one big dataset with the same shape (0,2048,2048)
    sumDataSet = np.zeros(dataSets[0].shape)
    for dataSet in dataSets:
        sumDataSet = np.add(dataSet, sumDataSet)
    #Create an average dataset by dividing the sumdataset by the number of files
    avsDataSet = sumDataSet/len(files)
    
    #Output the summed data and the averaged data to two HDF files with different names
    outputFiles = {'Summed' : sumDataSet, 'Averaged' : avsDataSet}
    for key in outputFiles:
        if template != -1:
            foutName = key+template
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

def get_data_from_file(filename):
    print "FName="+filename
    with h5py.File(filename, 'r') as dataFile:
        return dataFile['/entry/instrument/detector/data'][()]

def usage_message():
    print ("\nmergeHDFs can be configured in the script, or will take either one or two \n
           "arguments. To configure in the script, set the working_directory,\n" 
           "file_name_template and file_numbers fields for your needs.\n"
           "The three arguments (separated by spaces) the script accepts are:\n"
           "\t1) working directory - full path\n"
           "\t2) the file name template - .hdf5 is automatically appended\n"
           "\t3) file numbers - comma separated list of numbers in the filenames\n"
           )
    return

#Set the working directory
if len(sys.argv) >= 1:
    wDir = sys.argv[1]
elif working_directory != None:
    wDir = working_directory
else:
    print "ERROR: No working directory given!"
    usage_message()
    exit(1)
#Check the working directory exists
if not os.path.isdir(wDir):
    print "ERROR: Given working directory does not exist/is not directory."
    exit(1))
    
#If we don't have a file_list already, try to make one
if not files_list || file_list == None: #Empty list or None
    #Set the template
    if len(sys.argv >= 2):
        template = sys.argv[2]
    elif file_name_template != None:
        template = file_name_template
    else:
        print "ERROR: file_name_template not given!"
        usage_message()
        exit(1)
    #Set the file numbers
    if len(sys.argv) == 3:
        numbers = sys.argv[3].split(",")
    elif not file_numbers || file_numbers != None:
        numbers = file_numbers
    else:
        os.chdir(wDir)
        file_numbers=[]
        for file in glob.glob(template):
            fileNumbers.append[re.findall('\d+',str1))[0]] #Assumes number we want is the first one in the filename
        
        if not file_numbers:
        print "ERROR: file_numbers not given & could not be found!"
        usage_message()
        exit(1)
    
    #Make a file_list from the template & numbers
    file_list = []
    for number in numbers:
        file_list.append(number+template+".hdf5")

if __name__=="__main__":
    main()