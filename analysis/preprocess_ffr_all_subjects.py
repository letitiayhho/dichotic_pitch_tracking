#!/usr/bin/env python3

import os
import sys
import subprocess
import argparse
from util.io.iter_BIDSPaths import *
from util.io.bids import DataSink


def main(force, subs, skips) -> None:
    BIDS_ROOT = '../data/bids'
    DERIV_ROOT = '../data/bids/derivatives/'
    layout = BIDSLayout(BIDS_ROOT, derivatives = False)
    fpaths = layout.get(extension = 'eeg',
                        return_type = 'filename')
    BADS = []
#     BADS = ['9', '25', '31', '34', '38'] # skipped because low trial counts

    for (fpath, sub, task, run) in iter_BIDSPaths(fpaths):

        # if subs were given but sub is not in subs, don't preprocess
        if bool(subs) and sub not in subs:
            continue

        # if sub in skips, don't preprocess
        if sub in skips:
            continue

        # if sub is bad, don't preprocess
        if sub in BADS:
            continue

        # skip if subject is already preprocessed
        sink = DataSink(DERIV_ROOT, 'preprocess_ffr')
        micro_fpath = sink.get_path(
            subject = sub,
            task = task,
            run = run,
            desc = 'forFFR',
            suffix = 'epo',
            extension = 'fif.gz'
        )

        if os.path.isfile(micro_fpath) and not force:
            print(f"Subject {sub} run {run} is already preprocessed")
            continue

        print("subprocess.check_call(\"sbatch ./preprocess.py %s %s\" % (sub,run), shell=True)")
        subprocess.check_call("sbatch ./preprocess_ffr.py %s %s" % (sub, run), shell=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run preprocess.py over given subjects')
    parser.add_argument('--force', 
                        type = bool, 
                        nargs = 1, 
                        help = 'run even if output files already exist', 
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
    force = args.force
    subs = args.subs
    skips = args.skips
    print(f"force: {force}, subs: {subs}, skips : {skips}")
    if bool(subs) & bool(skips):
        raise ValueError('Cannot specify both subs and skips')
    main(force, subs, skips)
