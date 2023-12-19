#!/bin/env python

################################################################################
## This script is used to get FAS scores for a list of pairwise orthologs     ##
################################################################################

import sys
import os
from pathlib import Path
import json
import argparse
import statistics
import numpy as np

def read_json_file(json_file):
    """ Read annotation json file into dictionary
    """
    with open(json_file, 'r') as f:
        return(json.load(f))


def get_fas(fas_dict, in_file):
    """ Get pairwise FAS scores for a input pairwise orthologs
    Return a dictionary with keys are ortholog pair IDs and values are their
    pairwise FAS scores
    """
    fas_out = {}
    with open(in_file, 'r') as f:
        for line in f:
            tmp = line.strip().split()
            if len(tmp) >= 2:
                if f'{tmp[0]}_{tmp[1]}' in fas_dict:
                    fas_out.update({f'{tmp[0]}_{tmp[1]}': fas_dict[f'{tmp[0]}_{tmp[1]}']})
                elif f'{tmp[1]}_{tmp[0]}' in fas_dict:
                    fas_out.update({f'{tmp[1]}_{tmp[0]}': fas_dict[f'{tmp[1]}_{tmp[0]}']})
    return(fas_out)


def get_mean(fas_dict):
    """ Calculate mean score for a fas_dict (output from get_fas())
    """
    fas_list = []
    for pair in fas_dict:
        if not 'NA' in fas_dict[pair]:
            fas_list.append(statistics.mean(np.array(fas_dict[pair], dtype = float)))
    if len(fas_list) > 0:
        return((round(statistics.mean(fas_list), 3),len(fas_list)))
    else:
        return('NA')


def write_output(fas_dict, out_file, out_format):
    """ Save output from get_fas() to txt or json file
    """
    if out_format == 'json':
        jsonOut = json.dumps(fas_dict, ensure_ascii=False)
        f = open(outDir+'/'+outName+'.json', 'w')
        f.write(jsonOut)
        f.close()
    else:
        with open(f'{out_file}.txt', 'w') as f:
            for pair in fas_dict:
                ids = '\t'.join(pair.split('_'))
                f.write('%s\t%s\n' % (ids, statistics.mean(np.array(fas_dict[pair], dtype = float))))


def main():
    parser = argparse.ArgumentParser()
    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional arguments')
    required.add_argument('-i', '--inputFile', help='Input pairwise ortholog prediction in tab-delimited format',
                        action='store', default='', required=True)
    required.add_argument('-f', '--fasFile', help='Json file contains calculated FAS scores',
                        action='store', default='', required=True)
    optional.add_argument('-o', '--outputFile', help='Name of output file containing all FAS scores',
                        action='store', default='')
    optional.add_argument('--outputFormat', help='Format of output file',
                        action='store', default='txt', choices = ['txt', 'json'])

    args = parser.parse_args()
    in_file = args.inputFile
    fas_file = args.fasFile
    out_file = args.outputFile
    out_format = args.outputFormat

    print('==> parsing json files...')
    all_fas_dict = read_json_file(fas_file)
    print('==> getting fas scores...')
    sel_fas_dict = get_fas(all_fas_dict, in_file)
    if out_file:
        print(f'==> writing to {out_file}/{out_format}...')
        write_output(sel_fas_dict, out_file, out_format)
    (mean,pairs) = get_mean(sel_fas_dict)
    print(f'MEAN FAS SCORE: {mean} (calculated with {pairs}/{len(sel_fas_dict)} pairs)')
    print(f'DONE!')

if __name__ == '__main__':
    main()
