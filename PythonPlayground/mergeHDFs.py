'''
Created on 4 Jul 2016

@author: wnm24546
'''

import glob, os, re, sys
import h5py
import numpy as np


############################################
## EDIT LINES BELOW HERE ###################
############################################
#Give the directory path the files are and... (all values between ' or ")
working_directory = '/scratch/tmp/pdf_data'

#...either the full name of the files...
filenames_list=[]
#filenames_list = ['112004_KNJ-KA-218-01-PtNi-120s.hdf5', '112031_KNJ-KA-218-01-PtNi-120s.hdf5']

#...or the base name of the files and their numbers
file_name_template = 'Ce-BDC(250C-1hr)_aq-6s_2min'
file_numbers = []#222643, 222702, 222761, 222820, 222879,
                #222938, 222997, 223056, 223115, 223174]


############################################
## NOTHING SHOULD NEED EDITING BELOW HERE ##
############################################

def main(files, template=None):
    #Get numpy datasets from each of the files and put them into a list
    dataSets = []
    for name in files:
#         if template == -1:
        fName = os.path.join(wDir, name)
#         else:
#             fName = os.path.join(wDir, str(name)+template)
        dataSets.append(get_data_from_file(fName))
    
    #Merge dataSets into one big dataset with the same shape (0,2048,2048)
    sumDataSet = np.zeros(dataSets[0].shape, dtype=np.int32)
    for dataSet in dataSets:
        sumDataSet = np.add(dataSet, sumDataSet)
    #Create an average dataset by dividing the sumdataset by the number of files
    avsDataSet = sumDataSet/len(files)
    
    #Output the summed data and the averaged data to two HDF files with different names
    outputFiles = {'summed' : sumDataSet, 'averaged' : avsDataSet}
    for key in outputFiles:
        if template == None:
            output_file_name = key+".hdf5"
        else:
            output_file_name = key+"_"+template+".hdf5"
        
        output_path = os.path.join(wDir, 'processing')
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        
        print "Writing "+key.title()+" dataset file..."
        with h5py.File(os.path.join(output_path, output_file_name), 'w') as out_hdf:
            out_hdf.attrs['creator']="mergeHDFs.py"
            out_hdf.attrs['author']="Diamond Light Source Ltd."
            out_hdf.attrs['comment']=key.title()+" dataset from "+str(len(files))+" HDF files (full names given in input_files attribute)."
            out_hdf.attrs['input_files']=", ".join(files)
            entry = out_hdf.create_group('entry')
            instrument = entry.create_group('instrument')
            detector = instrument.create_group('detector')
            data = detector.create_dataset('data', data=outputFiles[key])
            data.attrs['dim0']="frame number n"
            data.attrs['dim1']="NDArray dim1"
            data.attrs['dim2']="NDArray dim0"
            data.attrs['interpretation']="image"
            data.attrs['signal']=1
            
            out_hdf.close()

def get_data_from_file(filename):
    print "Reading "+filename+"..."
    with h5py.File(filename, 'r') as dataFile:
        return dataFile['/entry/instrument/detector/data'][()]

def usage_message():
    print ("\nmergeHDFs can be configured in the script, or will take either one or two \n"
           "arguments. To configure in the script, set the working_directory,\n" 
           "file_name_template and file_numbers fields for your needs.\n"
           "The three arguments (separated by spaces) the script accepts are:\n"
           "\t1) working directory - full path\n"
           "\t2) the filename_str name template - .hdf5 is automatically appended\n"
           "\t3) filename_str numbers - comma separated list of numbers in the filenames\n"
           )
    return

#Set the working directory
if len(sys.argv) >= 2:
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
    exit(1)
    
#If we don't have a file_list already, try to make one
if (not filenames_list) | (filenames_list == None): #Empty list or None
    #Set the template
    if len(sys.argv) >= 3:
        template = sys.argv[2]
    elif file_name_template != None:
        template = file_name_template
    else:
        print "ERROR: file_name_template not given!"
        usage_message()
        exit(1)
    #Set the filename_str numbers
    if len(sys.argv) == 4:
        numbers = sys.argv[3].split(",")
    elif not (not file_numbers) | (file_numbers != None):#If there are file numbers
        numbers = file_numbers
    else:
        os.chdir(wDir)
        numbers=[]
        for filename_str in glob.glob("*"+str(template)+"*"):
            if ("dark" not in filename_str) & ("pristine" not in filename_str):
                numbers.append(re.findall('\d+',filename_str)[0]) #Assumes number we want is the first one in the filename
        
    if not numbers:
        print "ERROR: file_numbers not given & could not be found!"
        usage_message()
        exit(1)
    
    #Make a file_list from the template & numbers
    file_list = []
    numbers.sort()
    for number in numbers:
        file_list.append(str(number)+"_"+str(template)+".hdf5")
else:
    #We've got a list of all filenames already
    file_list = filenames_list

#Check 
for filename in file_list:
    try:
        assert os.path.exists(os.path.join(wDir, filename))
    except:
        print "ERROR: The file "+str(filename)+" does not exist in "+str(wDir)
        exit(1)

if (template == "") | (template == None):
    output_template = None
else:
    output_template = template.replace("(", "_")
    output_template = output_template.replace(")", "_")
    output_template = output_template.replace(".", "p")
    output_template = str(min(numbers))+"-"+str(max(numbers))+"_"+output_template


if __name__=="__main__":
    main(file_list, output_template)
    print "\n"