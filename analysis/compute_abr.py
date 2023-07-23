#!/usr/bin/env python3

#SBATCH --time=00:10:00
#SBATCH --partition=broadwl
#SBATCH --ntasks=1
#SBATCH --mem-per-cpu=16G
#SBATCH --mail-type=all
#SBATCH --mail-user=letitiayhho@uchicago.edu
#SBATCH --output=logs/compute_abr_%j.log

import mne
import sys
import numpy as np
import pandas as pd
from mne_bids import BIDSPath, read_raw_bids
from bids import BIDSLayout
from util.io.iter_BIDSPaths import *

def main(SUB, TASK, RUN) -> None:
    # Load data
    FPATH = f'/project2/hcn1/dichotic_pitch_tracking/data/bids/derivatives/preprocessing/sub-{SUB}/sub-{SUB}_task-dichotic_run-{RUN}_desc-clean_epo.fif.gz'
    epochs = mne.read_epochs(FPATH, preload = True)
    
    # Change to (tone number 1/2/3, left/right l/r, attended/unattended True/False)
    # tone 1, left, attended: 21*
    # tone 2, left, attended: 22*
    # tone 3, left, attended: 23*
    # tone 1, right, attended: 1*1
    # tone 2, right, attended: 1*2
    # tone 3, right, attended: 1*3
    # tone 1, left, unattended: 11*
    # tone 2, left, unattended: 12*
    # tone 3, left, unattended: 13*
    # tone 1, right, unattended: 2*1
    # tone 2, right, unattended: 2*2
    # tone 3, right, unattended: 2*3

    cond_dict = {
        (1, 'l', True): ['211', '212', '213'],
        (2, 'l', True): ['221', '222', '223'],
        (3, 'l', True): ['231', '232', '233'],
        (1, 'r', True): ['111', '121', '131'],
        (2, 'r', True): ['112', '122', '132'],
        (3, 'r', True): ['113', '123', '133'],
        (1, 'l', False): ['111', '112', '113'],
        (2, 'l', False): ['121', '122', '123'],
        (3, 'l', False): ['131', '132', '133'],
        (1, 'r', False): ['211', '221', '231'],
        (2, 'r', False): ['212', '222', '232'],
        (3, 'r', False): ['213', '223', '233']
    }
    
    # Separate channels by hemisphere
    all_channels = epochs.ch_names
    midline_channels = ['AFz', 'Fz', 'FCz', 'Cz', 'CPz', 'Pz', 'POz', 'Oz']
    left_channels = ['AF3', 'C1','C3','C5','T7','CP1','CP3','CP5','F1','F3','F5','F7','FC1','FC3','FC5','FT7','FT9','Fp1','O1','P1','P3','P5','P7','PO3','PO7','TP7','TP9']
    right_channels = ['AF4','C2','C4','C6','T8','CP2','CP4','CP6','F2','F4','F6','F8','FC2','FC4','FC6','FT10','FT8','Fp2','O2','P2','P4','P6','P8','PO4','PO8','TP10','TP8']

    # Checks
    print('Checks:')
    all_channels_set = set(epochs.ch_names)
    midline_channels_set = set(midline_channels)
    left_channels_set = set(left_channels)
    right_channels_set = set(right_channels)
    print(all_channels_set - midline_channels_set - left_channels_set - right_channels_set)

    intersection = all_channels_set & right_channels_set # channels that are in both sets
    right_missing = list(right_channels_set - intersection)
    print(f'Channels missing from right hemisphere: {right_missing}')
    for missing_item in right_missing:
        print(f'Removing {missing_item} from both hemispheres')
        index = right_channels.index(missing_item)
        right_channels.pop(index)
        left_channels.pop(index)

    intersection = all_channels_set & left_channels_set # channels that are in both sets
    left_missing = list(left_channels_set - intersection)
    print(f'Channels missing from left hemisphere: {left_missing}')
    for missing_item in left_missing:
        print(f'Removing {missing_item} from both hemispheres')
        index = left_channels.index(missing_item)
        right_channels.pop(index)
        left_chanenls.pop(index)

    print(f'Number of channels in manually created lists: {len(midline_channels) + len(left_channels) + len(right_channels)}')
    print(f'Number of channels in epochs object: {len(all_channels)}')
    
    # Average across each condition
    #     Event tags have 3 numbers (stream, tone in left ear, tone in right ear)
    #         stream {1: right, 2: left}
    #         tone in left ear {1: 130, 2: 200, 3: 280}
    #         tone in right ear {1: 130, 2: 200, 3: 280}
    #
    #     Average across each tone in the time domain
    #         tone duration: 400 msec
    #         baseline: 400 msec
    #         buffer: 50 msec

    evokeds = pd.DataFrame()

    # For each condition
    for key in cond_dict.keys():

        # Get the correct epochs
        cond_epochs = epochs[cond_dict[key]]

        # Average across the time domain
        cond_evoked = cond_epochs.average()

        # Compute psd for epoch and baseline TAKE BY HEMISPHERE
        P_left = cond_evoked.compute_psd(tmin = 0, tmax = 0.4, fmin = 100, fmax = 300, picks = left_channels)
        P0_left = cond_evoked.compute_psd(tmin = -0.4, tmax = 0, fmin = 100, fmax = 300, picks = left_channels)
        P_right = cond_evoked.compute_psd(tmin = 0, tmax = 0.4, fmin = 100, fmax = 300, picks = right_channels)
        P0_right = cond_evoked.compute_psd(tmin = -0.4, tmax = 0, fmin = 100, fmax = 300, picks = right_channels)

        # Extract the data only
        P_left = P_left.get_data()
        P0_left = P0_left.get_data()
        P_right = P_right.get_data()
        P0_right = P0_right.get_data()

        # Take log
        dB_left = 10*np.log10(P_left/P0_left)
        dB_right = 10*np.log10(P_right/P0_right)

        # Take difference between hemispheres
        dB_diff = dB_right - dB_left

        # Create row for data frame
        row = {
            'sub': SUB,
            'task': TASK,
            'run': RUN,
            'tone_num': key[0],
            'stream': key[1],
            'attended': key[2],
            'dB_diff': dB_diff}

        # Add to dataframe
        evokeds = evokeds.append(row, ignore_index = True)
    
    save_fp = f'../data/bids/derivatives/abr/sub-{SUB}_task-{TASK}_run-{RUN}_abr.csv'
    print(f'Saving to {save_fp}')
    evokeds.to_csv(save_fp, index = False)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(1)
    sub = sys.argv[1]
    task = sys.argv[2]
    run = sys.argv[3]
    main(sub, task, run)
