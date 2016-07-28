'''
Created on 28 Jul 2016

@author: wnm24546
'''
import os, sys

header="Memb. Pres. / bar\tRwp / %\tchi^2\ta / A\tVolume / A^3\tB-M EOS Pressure / GPa\n"

def main(results_file):
    assert os.path.exists(results_file)
    file_name_parts = os.path.splitext(results_file)
    
    with open(results_file) as in_file, open(file_name_parts[0]+"_clean"+file_name_parts[1], "wb") as out_file:
        out_file.write(header)
        
        i = 0
        for line in in_file:
            if ((i % 2) == 0) & (i > 0):
                out_file.write(line)
            i += 1

if __name__=="__main__":
    if len(sys.argv) == 2:
        results_file_in = sys.argv[1]
    else :
        print "Please specify the results file to clean up"
        exit(1)
    main(results_file_in)