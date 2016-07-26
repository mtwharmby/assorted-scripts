'''
Created on 26 Jul 2016

@author: wnm24546
'''

import os, sys
from __builtin__ import False

'''
The output file should have following structure:
c:\topas-5\tc .\template_inp "macro DATAFILE {.\relative_file_path\datafile.xy} macro GENERAL {local parameters}"
copy .\template_inp.out .\somewhere\new_name_related_to_datafile.out        #This should be optional, but is a good idea
copy .\template_inp.out .\template_inp.inp                                  #This should be optional
'''

inp_template="ZIF-4_Template"
data_path=""
batch_filename = None
given_prms = {}

copy_out = True
update_inp = False

output_path="out" #Relative to working directory
topas_path="c:\\topas-5\\tc"

def main():
    filenames = getDataFileNames()
    prms = makeLocalParams(given_prms)
    
    if batch_filename == None:
        writeBat(filenames, prms)
    else:
        writeBat(filenames, prms, batch_filename)

def getDataFileNames():
    assert os.path.exists(data_path)
    data_files = os.listdir(data_path)
    data_files.sort()
    
    return data_files

def makeLocalParams(defined_prms):
    return []


def writeBat(datafile_names, local_params, batfilename="sequence.bat"):
    with open(batfilename, "w") as batchFile:
        for i in range(0, len(datafile_names)):
            topas_line=topas_path+" .\\"+inp_template+" \"macro DATAFILE {"+os.path.join(".",data_path, datafile_names[i])+"} macro GENERAL {"+local_params[i]+"}\"\n"
            batchFile.write(topas_line)
        
            if copy_out:
                copy_out_line = "copy .\\"+inp_template+".out .\\"+output_path+"\\"+inp_template+"_i.out\n"
                batchFile.write(copy_out_line)
            
            if update_inp:
                update_line = "copy .\\"+inp_template+".out .\\"+inp_template+".inp\n"
                batchFile.write(update_line)


if __name__=="__main__":
    if len(sys.argv) >= 2:
        sys.argv[1] = batch_filename
        
        if len(sys.argv) >= 3:
            if sys.argv[2] == "0":
                copy_out = False
            elif sys.argv[2] == "1":
                copy_out = True
            
            if len(sys.argv) >= 4:
                if sys.argv[3] == "0":
                    update_inp = False
                elif sys.argv[3] == "0":
                    copy_out = True
                
                if len(sys.argv) > 4:
                    print "Too many arguments. Bye!"
                    exit(1)
    
    main()