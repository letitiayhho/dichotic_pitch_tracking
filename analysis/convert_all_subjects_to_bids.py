#!/usr/bin/env python3

import os
import argparse
import subprocess
from util.io.iter_raw_paths import iter_raw_paths
from mne_bids import BIDSPath

def main(subs, skips) -> None:
    RAW_DIR = '../data/raw/' # where our data currently lives
    BIDS_DIR = '../data/bids/' # where we want it to live
    #BAD_SUBS = ['1', '2', '17']
    
    for (fpath, sub, task, run) in iter_raw_paths(RAW_DIR):

        # skip bad subjects
        #if sub in BAD_SUBS:
            #print(f'Bad subject {sub}, skipping')
            #continue

        # skip if subs were listed and this sub is not included
        if bool(subs) and sub not in subs:
            continue

        # skip sub in skips
        if sub in skips:
            continue

        # skips files that already exist
        bids_path = BIDSPath(
            run = run,
            subject = sub,
            task = task,
            datatype = 'eeg',
            root = BIDS_DIR
            )
        if os.path.isfile(bids_path) and force == False:
            print(f'File {bids_path} exists, skipping {fpath}')
            continue
        
        #print("subprocess.check_call(\"sbatch ./convert_to_bids.py %s %s %s %s\" % (fpath, sub, task, run), shell=True)")
        subprocess.check_call("sbatch ./convert_to_bids.py %s %s %s %s" % (fpath, sub, task, run), shell=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run convert_to_bids.py over given subjects')
    parser.add_argument('--force',
                        type = bool,
                        nargs = 1,
                        help = 'If true run script even if save_fpath exists.',
                        default = False)
    parser.add_argument('--subs',
                        type = str,
                        nargs = '*',
                        help = 'subjects to convert (e.g. 3 14 8), provide no argument to run over all subjects',
                        default = [])
    parser.add_argument('--skips',
                        type = str,
                        nargs = '*',
                        help = 'subjects NOT to convert (e.g. 1 9)',
                        default = [])
    args = parser.parse_args()
    force = args.force
    subs = args.subs
    skips = args.skips
    print(f"subs: {subs}, skips : {skips}")
    if bool(subs) & bool(skips):
        raise ValueError('Cannot specify both subs and skips')
    main(subs, skips)
