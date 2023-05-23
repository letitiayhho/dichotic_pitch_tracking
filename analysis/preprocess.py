#!/usr/bin/env python3

#SBATCH --time=03:00:00
#SBATCH --partition=bigmem2
#SBATCH --ntasks=1
#SBATCH --mem-per-cpu=160G
#SBATCH --mail-type=all
#SBATCH --mail-user=letitiayhho@uchicago.edu
#SBATCH --output=logs/preprocess_%j.log

import sys
import gc
from util.io.preprocessing import *

def main(sub, task, run) -> None:
    # Constants
    BIDS_ROOT = '../data/bids'
    DERIV_ROOT = '../data/bids/derivatives'
    LOWPASS = 300
    FS = 5000

    # Import data
    print("---------- Import data ----------")
    print(sub, task, run)
    raw = import_bids_data(BIDS_ROOT, sub, task, run)
    events, event_ids = read_events(raw)

    # Create virtual EOGs
    raw.load_data()
    raw = create_eogs(raw)

    # Resampling and PREP
    print("---------- Resampling and PREP ----------")
    raw, bads = run_PREP(raw, sub, run, LOWPASS)

    # Run ICA on one copy of the data
    print("---------- Run ICA on one copy of the data ----------")
    raw_for_ica = bandpass(raw, None, 1)
    raw = bandpass(raw, 300, 100)

    epochs_for_ica = epoch(raw_for_ica, events, event_ids)
    epochs = epoch(raw, events, event_ids)
    del raw_for_ica
    del raw
    gc.collect()

    ica = compute_ICA(epochs_for_ica) # run ICA on less aggressively filtered data
    epochs, ica = apply_ICA(epochs_for_ica, epochs, ica) # apply ICA on more aggressively filtered data

    # Baseline correct and reject trials
    print("---------- Baseline correct and reject trials ----------")
    epochs = baseline_correct(epochs)
    epochs, thres = reject_trials(epochs)

    # Save results and generate report
    print("---------- Save results and generate report ----------")
    fpath, sink = get_save_path(DERIV_ROOT, sub, task, run)
    save_and_generate_report(fpath, epochs, sink, sub, task, run, ica, bads, thres)
    print("Saving results and report to: " + str(fpath))

__doc__ = "Usage: ./preprocess.py <sub> <task> <run>"

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(1)
    sub = sys.argv[1]
    task = sys.argv[2]
    run = sys.argv[3]
    main(sub, task, run)
