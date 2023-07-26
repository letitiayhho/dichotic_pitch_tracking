#!/usr/bin/env python3

import os
import sys
import subprocess
import argparse
from util.io.iter_BIDSPaths import *

def main(subs, skips, force) -> None:
    BIDS_ROOT = '../data/bids'
    DERIV_ROOT = '../data/bids/derivatives'
    layout = BIDSLayout(BIDS_ROOT, derivatives = False)
    fpaths = layout.get(extension = 'eeg',
                        return_type = 'filename')

    for (fpath, sub, task, run) in iter_BIDSPaths(fpaths):

        # if subs were given but sub is not in subs, don't preprocess
        if bool(subs) and sub not in subs:
            continue

        # if sub in skips, don't preprocess
        if sub in skips:
            continue

        # skip if subject is already preprocessed
        save_fp = f'../data/bids/derivatives/abr/sub-{sub}_task-{task}_run-{run}_abr.pkl'
        if os.path.isfile(save_fp) and not force:
            print(f"Subject {sub} run {run} is already preprocessed")
            continue

        print(f"subprocess.check_call(\"sbatch ./compute_abr.py %s %s %s\" % ({sub}, {task}, {run}), shell=True)")
        subprocess.check_call("sbatch ./compute_abr.py %s %s %s" % (sub, task, run), shell=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run preprocess.py over given subjects')
    parser.add_argument('--force',
                        type = bool,
                        nargs = 1,
                        help = 'whether to preprocess even if output preprocessed file exists',
                        default = False)
    parser.add_argument('--subs', 
                        type = str, 
                        nargs = '*', 
                        help = 'subjects to preprocess (e.g. 3 14 8), provide no argument to run over all subjects', 
                        default = [])
    parser.add_argument('--skips', 
                        type = str, 
                        nargs = '*', 
                        help = 'subjects NOT to preprocess (e.g. 1 9)', 
                        default = [])
    args = parser.parse_args()
    force = args.force[0]
    subs = args.subs
    skips = args.skips
    print(f"subs: {subs}, skips : {skips}, force : {force}")
    if subs and skips:
        raise ValueError('Cannot specify both subs and skips')
    main(subs, skips, force)
