#!/usr/bin/env python
# name            :parse_counts_deseq.py
# description     :This script can help in merging the readcounts table and pre-filter them based on counts per condition.
# author          :siva.selvanayagam@wur.nl
# date            :2022/04/22
# version         :0.1
# usage           :parse_counts_deseq.py [-h] --out-file <FILENAME> --rep-file <FILENAME> --count-file <FILENAME> [<FILENAME> ...] --cut-off
# notes           : 
# perl_version    :3.9.12
# ==============================================================================

__author__ = "Sivasubramani S"
__email__ = "siva.selvanayagam@wur.nl"
__version__ = "0.1"

import argparse
from collections import defaultdict 

# function to count number of elements having value more than the cut-off
def count_above(in_list, cutoff):
    count = 0
    for elm in in_list:
        if elm >= cutoff:
            count += 1
    return count
    
# command-line aurgument parsing options
parser = argparse.ArgumentParser(description="merge and pre-filter readcount tables")
parser.add_argument("--out-file", dest="outfile", 
                    metavar="<FILENAME>", help="output filename", required=True)
parser.add_argument("--rep-file", dest="rep_file", 
                    metavar="<FILENAME>", help="file containing sample_name<tab>rep_name informations.", required=True)
parser.add_argument("--count-file", nargs='+',
                    metavar="<FILENAME>", dest="count_files", help="readcount files", required=True)
parser.add_argument("--cut-off", dest="cutoff",
                    metavar="<int>", help="minimum value of readcount/TPM to pass the gene for 50 percent of total samples", required=True)
options = parser.parse_args()

# reading input files and hash the readcounts/TPMs
sample_names = []
count_dict = defaultdict()
length_dict = defaultdict()
for in_file in options.count_files:
    print(f"reading input file {in_file}...")
    line_no = 0
    with open(in_file) as fh:
        for line in fh:
            line = line.strip()
            line_no += 1
            line_entries = line.split(',')
            if line_no == 1:
                for col_no in range(1, len(line_entries)):
                    if line_entries[col_no] in sample_names:
                        print("sample name is repeated in files. Please check. Quiting.")
                        SystemExit(1)
                    sample_names.append(line_entries[col_no])
                col_names = line_entries
                continue
            if line_entries[0] not in count_dict:
                count_dict[line_entries[0]] = defaultdict()
            for col_no in range(1, len(line_entries)):
                count_dict[line_entries[0]][col_names[col_no]] = line_entries[col_no]
    fh.close()

# reading the replicats file
replicates_dict = defaultdict()
line_no = 0
with open(options.rep_file, 'r') as fh:
    for line in fh:
        line = line.strip()
        line_no += 1
        if line_no == 1:
            continue
        line_entries = line.split()
        if not line_entries[1] in sample_names:
            continue
        if not line_entries[0] in replicates_dict:
            replicates_dict[line_entries[0]] = []
        replicates_dict[line_entries[0]].append(line_entries[1])


# Writing the merged data in output file
fw = open(options.outfile, 'w')
fw.write(f"gene_name")
for sample in sample_names:
    fw.write(f"\t{sample}")
fw.write(f"\n")
for gene_name in count_dict:
    fw.write(f"{gene_name}")
    for sample in sample_names:
        if sample not in count_dict[gene_name]:
            fw.write(f"\t0")
        else:
            fw.write(f"\t{count_dict[gene_name][sample]}")
    fw.write(f"\n")
fw.close()


# Filter the data and write to output file
sample_names = []
fw = open(options.outfile + '_filtered.txt', 'w')
fw.write(f"gene_name")
for sample in replicates_dict:
    reps = replicates_dict[sample]
    for rep in reps:
        sample_names.append(rep)
        fw.write(f"\t{rep}")
fw.write(f"\n")

for gene in count_dict:
    gene_counts = []
    for sample in replicates_dict:
        sample_sum = 0
        rep_no = 0
        reps = replicates_dict[sample]
        for rep in reps:
            rep_no += 1
            sample_sum += float(count_dict[gene][rep])
        gene_counts.append(sample_sum/rep_no)
    if count_above(gene_counts, float(options.cutoff)) >= len(gene_counts)*0.5:
        fw.write(f"{gene}")
        for sample in sample_names:
            if sample not in count_dict[gene]:
                fw.write(f"\t0")
            else:
                fw.write(f"\t{count_dict[gene][sample]}")
        fw.write(f"\n")
