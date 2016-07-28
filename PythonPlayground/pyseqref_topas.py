'''
Created on 26 Jul 2016

@author: wnm24546
'''

import os, sys
import shutil
import subprocess

import traceback
from subprocess import CalledProcessError

'''
The output file should have following structure:
c:\topas-5\tc .\template_inp "macro DATAFILE {.\relative_file_path\datafile.xy} macro GENERAL {local parameters}"
copy .\template_inp.out .\somewhere\new_name_related_to_datafile.out        #This should be optional, but is a good idea
copy .\template_inp.out .\template_inp.inp                                  #This should be optional
'''

inp_template="ZIF4Zn_NaCl_SequentialRietTmpl_21"
data_path="up_spots_new"
prm_label = "mp_000"
given_prms = {"mp_000" : [0, 69]}

copy_out = True
update_inp = False
recycle = True
edit_next_inp = True
initial_values = {"REPLACE_WITH_LPA" : 5.643366, "REPLACE_MP" : given_prms["mp_000"][0], "REPLACE_WITH_XOPOS" : 12.0753893 }

output_path="out21_up" #Relative to working directory
topas_path="c:\\topas-5\\tc"

def main():
    filenames = getDataFileNames()
    prms = makeLocalParams(given_prms, (len(filenames)))
    
    sequential_refinement(filenames, prms, prm_label)

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
    for key in given_prms:
        prm_vals = _calculate_prm_vals(key, nfiles)
        
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

def _calculate_prm_vals(prm_name, nfiles):
    values = given_prms[prm_name]
    if len(values) == nfiles:
        prm_vals = values
    elif len(values) == 2:
        prm_vals = range(values[0], values[1]+1)
    elif len(values) == 3:
        prm_vals = range(values[0], values[1]+1, values[3])
    else:
        print "ERROR: Unknown description of prm values."
        exit(1)
    return prm_vals

def get_prm_val(prm_name, nfiles, index):
    return _calculate_prm_vals(prm_name, nfiles)[index]


def run_topas(inp_templt, topas_args, do_errors=False):
    inp_path = check_file(inp_templt, "inp")
    try:
        if do_errors:
            with open(inp_path+".inp", "ab") as inp_file:
                inp_file.write("do_errors")
            print "INFO: Errors will be calculated"
        
        #TODO Consider piping stdout to a log file
        print "INFO: Starting TOPAS run..."
        top_proc = subprocess.Popen([topas_path, inp_path, topas_args])
        top_proc.wait()
    except CalledProcessError as ex:
        print "ERROR: Running TOPAS on "+inp_templt+".inp failed!"
        raise ex
        exit(1)

'''
Check the file with a given extension exists & return the full path without 
the extension
'''
def check_file(inp_templt, ext=None):
    try:
        file_path = os.path.join(".", inp_templt)
        if ext == None:
            assert os.path.exists(file_path)
        else:
            assert os.path.exists(file_path+"."+ext)
        return file_path
    except AssertionError:
        print "ERROR: File "+file_path+"."+ext+" not found!"
        exit(1)

def sequential_refinement(datafile_names, local_params, prm_label=None):
    #Local method for checking & making (if needed) output directory
    def check_make_output_dir():
        output_dir_path = os.path.join(".", output_path)
        if not os.path.exists(output_dir_path):
            print "INFO: Making output directory..."
            os.mkdir(output_dir_path)
        return output_dir_path
    
    def check_out_file(inp_templt):
        out_file_stem = check_file(inp_templt, "out")
        return out_file_stem+".out"
    
    #Generate the suffix to prevent this file from being overwritten
    def make_out_file_suffix(datafile_nr, prm_label):
        if (prm_label == None) | (not prm_label in given_prms):
            #Use the number of the file to make the suffix, with zero padding 
            #from maximum number of files
            if (not prm_label in given_prms):
                print "WARNING: Couldn't find requested prm name for output files"
            suffix = str(datafile_nr)
            suffix_width = len(str(len(datafile_names)))
        else:
            #Use the prm to generate the suffix, with zero padding from the 
            #maximum value of the prm
            suffix_set = given_prms[prm_label]
            if (len(suffix_set) != len(datafile_names)):
                if len(suffix_set) == 2:
                    suffix_set = range(suffix_set[0], suffix_set[1]+1)
                else:
                    suffix_set = range(suffix_set[0], suffix_set[1]+1, suffix_set[3])
            suffix = str(suffix_set[datafile_nr])
            suffix_width = len(str(max(suffix_set)))
        
        return suffix.zfill(suffix_width)
    
    def inject_initial_values(inp_template):
        print "INFO: Injecting intial values:\n"+str(initial_values)+"\n"
        with open(check_file(inp_template+"_Tmpl", "inp")+".inp") as template_inp_file, open(os.path.join(".", inp_template+".inp"), "wb") as real_inp_file:
            for line in template_inp_file:
                for key, new_val in initial_values.iteritems():
                    line = line.replace(key, str(new_val))
                real_inp_file.write(line)
    
    #Check the inp template exists and the number of datafiles equals the number of parameter entries
    assert len(datafile_names) == len(local_params)
    
    #If we're editing using a template, we need to set up the first file
    if edit_next_inp:
        inject_initial_values(inp_template)
        
    for i in range(0, len(datafile_names)):
        #Do the first TOPAS run using the standard args
        datafile = check_file(os.path.join(data_path, datafile_names[i]))
        args = "macro DATAFILE {"+datafile+"} macro GENERAL {"+local_params[i]+"}"
        run_topas(inp_template, args)
        
        #Generate this file's suffix
        suffix = make_out_file_suffix(i, prm_label)
        
        #If requested, copy the out file to the out directory
        if copy_out:
            out_dir = check_make_output_dir()
            dest_out_file = os.path.join(out_dir, inp_template+"_"+suffix+".out")
            shutil.copy(check_out_file(inp_template), dest_out_file)

        #If requested, re-run the refinement of the current file using old input
        if recycle:
            out_dir = check_make_output_dir()
            recycle_inp_name = inp_template+"_"+suffix
            recycle_inp_name_path = os.path.join(".", recycle_inp_name)
            shutil.copy(check_out_file(inp_template), recycle_inp_name+".inp")
            run_topas(recycle_inp_name, args, do_errors=True)
            shutil.move(recycle_inp_name+".inp", os.path.join(out_dir, recycle_inp_name+".inp"))
            shutil.move(check_out_file(recycle_inp_name), os.path.join(out_dir, recycle_inp_name+".out"))
            
        if update_inp:
            shutil.copy(check_out_file(inp_template), os.path.join(".", inp_template+"inp"))
        
        if edit_next_inp:
            #If we're at the end of the list skip this step
            if i+1 == len(datafile_names):
                continue
            edit_values = {}
            
            #Get new LPA value
            with open(check_file("lpa", "txt")+".txt") as lpa_file:
                lpa = lpa_file.readline()
                edit_values["REPLACE_WITH_LPA"] = lpa.lstrip(" ")
            #Get new Xo position
            next_mp_val = get_prm_val("mp_000", len(datafile_names), i+1) #This is specific for a membrane pressure cell experiment
            if next_mp_val >= 46:
                if next_mp_val == 46:
                    edit_values["REPLACE_WITH_XOPOS"] = str(initial_values["REPLACE_WITH_XOPOS"])
                else:
                    with open(check_file("xo_pos", "txt")+".txt") as xopos_file:
                        xopos = xopos_file.readline()
                        edit_values["REPLACE_WITH_XOPOS"] = xopos.lstrip(" ")
            #Get the mp value to allow TOPAS inp to decide if we need the Xo_Is phase
            edit_values["REPLACE_MP"] = str(next_mp_val)
            
            print "\nINFO: Inserting following values:\n"+str(edit_values)+"\n"
            
            with open(check_file(inp_template+"_Tmpl", "inp")+".inp") as template_inp_file, open(check_file(inp_template, "inp")+".inp", "wb") as real_inp_file:
                for line in template_inp_file:
                    for key, new_val in edit_values.iteritems():
                        line = line.replace(key, new_val)
                    real_inp_file.write(line)
                    
        

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