#!/usr/bin/env python3

#SBATCH --time=00:30:00
#SBATCH --partition=broadwl
#SBATCH --ntasks=1
#SBATCH --mem-per-cpu=32G
#SBATCH --mail-type=all
#SBATCH --mail-user=letitiayhho@uchicago.edu
#SBATCH --output=logs/plot-aux-psd_%j.log

from mne_bids import BIDSPath, write_raw_bids, get_anonymization_daysback
import random
import pandas as pd
import numpy as np
import itertools
import mne
import os
import sys
import re
from util.io.iter_raw_paths import iter_raw_paths

def load_raw(sub, raw_dir, fpath):
    fpath = raw_dir + fpath
    print(fpath)
    raw = mne.io.read_raw_brainvision(fpath)
    raw.load_data()
    if int(sub) < 29:
        aux_names = ['Left', 'Right']
        raw.set_channel_types({'Left': 'eeg', 'Right': 'eeg'})
        raw.pick_channels(aux_names)
    elif 29 <= int(sub) < 41:
        aux_names = ['Audio', 'Audio2']
        raw.set_channel_types({'Audio': 'eeg', 'Audio2': 'eeg'})
        raw.pick_channels(aux_names)
    elif int(sub) >= 41:
        aux_names = ['left', 'right']
        raw.set_channel_types({'left': 'eeg', 'right': 'eeg'})
        raw.pick_channels(aux_names)
    return raw, aux_names

def get_events(raw):
    events, event_ids = mne.events_from_annotations(raw)
    return(events)

def epoch(raw, events):
    epochs = mne.Epochs(raw, events, tmin = -0.4, tmax = .4, baseline = (-0.4, 0))
    return(epochs)

def plot_aux(tag, sub, FIGS_DIR, epochs, aux_names):
    aux = aux_names[0]
    print(f"---------- Tag {tag}: Audio: {aux} ----------")
    plt = epochs[tag].plot_psd(picks = aux, fmin = 100, fmax = 400) # thought this was right
    figname = f'{FIGS_DIR}/sub-{sub}_tag-{tag}_aux-{aux}.png'
    print(f"saving to {figname}")
    plt.savefig(figname)
    
    aux = aux_names[1]
    print(f"---------- Tag {tag}: Audio: {aux} ----------")
    plt = epochs[tag].plot_psd(picks = aux, fmin = 100, fmax = 300) # thought this was left
    figname = f'{FIGS_DIR}/sub-{sub}_tag-{tag}_aux-{aux}.png'
    print(f"saving to {figname}")
    plt.savefig(figname)

def main() -> None:
    # Constants
    RAW_DIR = '../data/raw/'
    FIGS_DIR = '../figs'

    for (fpath, sub, task, run) in iter_raw_paths(RAW_DIR):
        raw, aux_names = load_raw(sub, RAW_DIR, fpath)
        events = get_events(raw)
        epochs = epoch(raw, events)
        plot_aux('12', sub, FIGS_DIR, epochs, aux_names)
        plot_aux('31', sub, FIGS_DIR, epochs, aux_names)
        
if __name__ == "__main__":
    main()
