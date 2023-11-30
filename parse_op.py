#!/bin/env python

################################################################################
## This script is used to process a pairwise ortholog file in tab-delimited   ##
## format. If a list of (non-redundant) pairs is given, only new ortholog     ##
## will be considered. The output will be a tab-delimited file containing     ##
## the ortholog pairs and the species they belong to.                         ##
## The result of this script can be used as input for fas.runMultiTaxa        ##
################################################################################

import sys
import os
from pathlib import Path
import json
import glob
import argparse
import multiprocessing as mp
from tqdm import tqdm


def read_json_file(json_file):
    """ Read annotation json file and return a dictionary
    where IDs are the protein IDs and values are their corresponding filename
    """
    taxa_dict = {}
    with open(json_file, 'r') as jf:
        anno_dict = json.load(jf)
        for id in anno_dict['feature']:
            taxa_dict[id] = json_file.split('/')[-1].replace('.json','')
    return(taxa_dict)


def read_json_dir(anno_dir, cpus):
    """ Run read_json_file() function paralelly for multiple files in
    annotation directory
    """
    taxa_dict = {}
    pool = mp.Pool(cpus)
    json_files = list(glob.glob(os.path.join(anno_dir, '*.json')))
    for _ in tqdm(pool.imap_unordered(read_json_file, json_files), total=len(json_files)):
        taxa_dict.update(_)
    pool.close()
    return(taxa_dict)


def map_ortho_pairs(in_file, taxa_dict, nr_pairs, cpus):
    """Mapping ortholog pairs to their taxa
    Input ortho_pairs is a list of pairwise ortholog IDs
    """
    missing_anno = {}

    with open(f'{in_file}.mapped', 'w') as out_file:
        diff_pairs = get_diff_pairs(in_file, nr_pairs, cpus)
        print(f'Total pairs: {len(diff_pairs)}')
        if len(diff_pairs) > 0:
            for (id1,id2) in diff_pairs:
                if id1 in taxa_dict and id2 in taxa_dict:
                    out_file.write('%s\t%s\t%s\t%s\n' % (id1, taxa_dict[id1], id2, taxa_dict[id2]))
                else:
                    if id1 not in taxa_dict:
                        missing_anno[id1] = ''
                    if id2 not in taxa_dict:
                        missing_anno[id2] = ''
    with open(f'{in_file}.missing', 'w') as mf:
        for m_id in missing_anno:
            mf.write('%s\n' % m_id)


def read_pairwise_ortholog(in_file):
    """Read pairwise ortholog file
    and return a list of all pairs
    """
    ortho_pairs = []
    if not os.path.exists(os.path.abspath(in_file)):
        sys.exit(f'ERROR: {in_file} not found!')
    with open (in_file, 'r') as f:
        for line in f:
            tmp = line.strip().split()
            ortho_pairs.append((tmp[0], tmp[1]))
    return(ortho_pairs)


def compare_pairs(opts):
    """Check if a given pair exists in a pre-defined list of pairs (nr_pairs)
    """
    (line, nr_pairs) = opts
    tmp = line.strip().split()
    diff_pair = ()
    if len(tmp) == 2:
        if not (tmp[0], tmp[1]) in nr_pairs and not (tmp[1], tmp[0]) in nr_pairs:
            diff_pair = (tmp[0], tmp[1])
    return(diff_pair)


def get_diff_pairs(in_file, nr_pairs, cpus):
    """Get ortholog pairs that are not in a pre-defined list (nr_pairs)
    If nr_pairs is empty, all of the pairs in in_file will be considered
    """
    diff_pairs = []
    if len(nr_pairs) > 0:
        jobs = []
        with open(in_file, 'r') as f:
            for line in f:
                jobs.append((line, nr_pairs))
        pool = mp.Pool(cpus)
        for _ in tqdm(pool.imap_unordered(compare_pairs, jobs), total=len(jobs)):
            diff_pairs.append(_)
        pool.close()
    else:
        diff_pairs = read_pairwise_ortholog(in_file)
    return(list(filter(None, diff_pairs)))


def main():
    parser = argparse.ArgumentParser()
    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional arguments')
    required.add_argument('-i', '--inputFile', help='Input pairwise ortholog prediction in tab-delimited format',
                        action='store', default='', required=True)
    required.add_argument('-a', '--annoDir', help='Folder contains annotation json files',
                        action='store', default='', required=True)
    optional.add_argument('--nrPairs', help='Pre-defined non-redundant ortholog pairs',
                          action='store', default='')
    optional.add_argument('--cpus', help='Number of CPUs used for parsing. Default = available cores - 1',
                          action='store', default=0, type=int)

    args = parser.parse_args()
    in_file = args.inputFile
    anno_dir = args.annoDir
    cpus = args.cpus
    if cpus == 0:
        cpus = mp.cpu_count()-1


    print('==> parsing json files...')
    taxa_dict = read_json_dir(anno_dir, cpus)
    if args.nrPairs:
        print('==> getting pre-defined nr-pairs...')
        nr_pairs = read_pairwise_ortholog(args.nrPairs)
    else:
        nr_pairs = []
    print('==> mapping proteins to taxa...')
    map_ortho_pairs(in_file, taxa_dict, nr_pairs, cpus)
    print(f'DONE! Check output file {in_file}.mapped')

if __name__ == '__main__':
    main()
