'''
Created on 26 Jul 2016

@author: wnm24546
'''

import os, sys

'''
The output file should have following structure:
c:\topas-5\tc .\template_inp "macro DATAFILE {.\relative_file_path\datafile.xy} macro GENERAL {local parameters}"
copy .\template_inp.out .\somewhere\new_name_related_to_datafile.out        #This should be optional, but is a good idea
copy .\template_inp.out .\template_inp.inp                                  #This should be optional
'''

inp_template="ZIF4Zn_NaCl_SequentialRietTmpl_10"
data_path="up_spots_new"
batch_filename = None
prm_label = "p_000"
given_prms = {"p_000" : [45, 69]}

copy_out = True
update_inp = False
recycle = True

output_path="out_up" #Relative to working directory
topas_path="c:\\topas-5\\tc"

def main():
    filenames = getDataFileNames()
    prms = makeLocalParams(given_prms, (len(filenames)))
    
    writeBat(filenames, prms, batch_filename, prm_label)

def getDataFileNames():
    assert os.path.exists(data_path)
    data_files = os.listdir(data_path)
    data_files.sort()
    
    return data_files

'''
Structure of local params:
[prm pres = 1 prm temp = 295, prm pres = 2 prm temp = 295, ...]
'''
def makeLocalParams(defined_prms, nfiles):
    prm_list = []
    #Create an array which will be nfiles x nPrms
    prm_tmpls = []
    prm_array = []
    for key, values in given_prms.iteritems():
        if len(values) == nfiles:
            prm_vals = values
        elif len(values) == 2:
            prm_vals = range(values[0], values[1]+1)
        elif len(values) == 3:
            prm_vals = range(values[0], values[1]+1, values[3])
        else:
            print "ERROR: Unknown description of prm values."
            exit(1)
        
        #Make sure we have the same number of prm_vals as files
        assert len(prm_vals) == nfiles
        
        #Add the set of prm values into the array
        prm_array.append(prm_vals)
        prm_tmpls.append("prm "+key+" = ")
    
    #Check there are as many prm_templs values as number of prms
    assert len(prm_tmpls) == len(defined_prms)
        
    for j in range(nfiles):
        prm_entry = ""
        for i in range(len(defined_prms)):
            prm_entry = prm_entry+prm_tmpls[i]+str(prm_array[i][j])+"; "
        prm_list.append(prm_entry.rstrip(' '))
    
    #Check there are as many prm sets as the number of entries we're going to populate
    assert len(prm_list) == nfiles
    return prm_list


def writeBat(datafile_names, local_params, batfilename=None, prm_label=None):
    #Local method for checking & making (if needed) output directory
    def check_make_output_dir():
        if not os.path.exists(os.path.join(".", output_path)):
            print "INFO: Making output directory..."
            os.mkdir(os.path.join(".", output_path))
    
    #Check the inp template exists and the number of datafiles equals the number of parameter entries
    assert os.path.exists(os.path.join(".", inp_template+".inp"))
    assert len(datafile_names) == len(local_params)
    
    if batfilename == None:
        batfilename = "sequence.bat"
    
    #Determine maximum width of the string form of the number of files
    if (prm_label == None) | (not prm_label in given_prms):
        if (not prm_label in given_prms):
            print "WARNING: Couldn't find requested prm name for output files"
        suffix_width = len(str(len(datafile_names)))
    else:
        suffix_set = given_prms[prm_label]
        if (len(suffix_set) != len(datafile_names)):
            if len(suffix_set) == 2:
                suffix_set = range(suffix_set[0], suffix_set[1]+1)
            else:
                suffix_set = range(suffix_set[0], suffix_set[1]+1, suffix_set[3])
        suffix_width = len(str(max(suffix_set)))
    
    with open(batfilename, "w") as batchFile:
        for i in range(0, len(datafile_names)):
            topas_line=topas_path+" "+os.path.join(".", inp_template)+" \"macro DATAFILE {"+os.path.join(".",data_path, datafile_names[i])+"} macro GENERAL {"+local_params[i]+"}\"\n"
            batchFile.write(topas_line)
            
            if (prm_label == None) | (not prm_label in given_prms):
                suffix = str(i)
            else:
                suffix = str(suffix_set[i])
            
            if recycle:
                recycle_inp_name = inp_template+"_"+suffix.zfill(suffix_width)
                recycle_copy_inp_line = "copy "+os.path.join(".", inp_template+".out")+" "+os.path.join(".", recycle_inp_name+".inp\n")
                batchFile.write(recycle_copy_inp_line)
                recycle_topas_line=topas_path+" "+os.path.join(".", inp_template+"_"+suffix.zfill(suffix_width))+" \"macro DATAFILE {"+os.path.join(".",data_path, datafile_names[i])+"} macro GENERAL {"+local_params[i]+"}\"\n"
                batchFile.write(recycle_topas_line)
                if copy_out:
                    #Create output directory if it doesn't exist already
                    check_make_output_dir()
                    recycle_move_inp_line = "move /y "+recycle_inp_name+".inp "+os.path.join(".", output_path, recycle_inp_name+".inp\n")
                    recycle_move_out_line = "move /y "+recycle_inp_name+".out "+os.path.join(".", output_path, recycle_inp_name+".out\n")
                    batchFile.write(recycle_move_inp_line)
                    batchFile.write(recycle_move_out_line)
        
            if copy_out:
#                 if prm_label == None:
#                     suffix = str(i)
#                 else:
#                     suffix = str(suffix_set[i])
                
                #Create output directory if it doesn't exist already
                check_make_output_dir()
                
                copy_out_line = "copy "+os.path.join(".", inp_template+".out")+" "+os.path.join(".", output_path, inp_template+"_"+suffix.zfill(suffix_width)+".out")+"\n"
                batchFile.write(copy_out_line)
            
            if update_inp:
                update_line = "copy .\\"+inp_template+".out .\\"+inp_template+".inp\n"
                batchFile.write(update_line)


if __name__=="__main__":
    if len(sys.argv) >= 2:
        batch_filename = sys.argv[1]
        
        if len(sys.argv) >= 3:
            if sys.argv[2] == "0":
                copy_out = False
            elif sys.argv[2] == "1":
                copy_out = True
            
            if len(sys.argv) >= 4:
                if sys.argv[3] == "0":
                    update_inp = False
                elif sys.argv[3] == "1":
                    update_inp = True
                
                if len(sys.argv) > 4:
                    print "Too many arguments. Bye!"
                    exit(1)
    
    main()