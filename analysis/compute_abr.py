#!/usr/bin/env python3

#SBATCH --time=00:02:00
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

def extract_power_at_condition_freq(freq, freqs, power):
    power_at_condition_frequencies = []
    lower_index = int(np.argwhere(freq < freqs)[-2])
    upper_index = lower_index+5 # last index is not inclusive
    power_at_slice = power[:,lower_index:upper_index]
    power_at_condition_freq = np.mean(power_at_slice, axis = 1)
    power_at_condition_freq = np.squeeze(power_at_condition_freq)
    return power_at_condition_freq

def get_channel_coords(coords, channel_names):
    x_coords = []
    y_coords = []
    for channel in channel_names:
        x_coord = coords['x'][coords['ch_name'] == channel]
        x_coord = x_coord.tolist()[0]
        x_coords.append(x_coord)
        y_coord = coords['y'][coords['ch_name'] == channel]
        y_coord = y_coord.tolist()[0]
        y_coords.append(y_coord)

    return(x_coords, y_coords)

def get_channels(recorded_channels):
    recorded_channels_set = set(recorded_channels)
    midline_channels = ['AFz', 'Fz', 'FCz', 'Cz', 'CPz', 'Pz', 'POz', 'Oz']
    left_channels = ['AF3', 'C1','C3','C5','T7','CP1','CP3','CP5','F1','F3','F5','F7','FC1','FC3','FC5','FT7','FT9','Fp1','O1','P1','P3','P5','P7','PO3','PO7','TP7','TP9']
    right_channels = ['AF4','C2','C4','C6','T8','CP2','CP4','CP6','F2','F4','F6','F8','FC2','FC4','FC6','FT10','FT8','Fp2','O2','P2','P4','P6','P8','PO4','PO8','TP10','TP8']
    
    print('Checks:')
    midline_channels_set = set(midline_channels)
    left_channels_set = set(left_channels)
    right_channels_set = set(right_channels)
    print(recorded_channels_set - midline_channels_set - left_channels_set - right_channels_set)

    intersection = recorded_channels_set & right_channels_set # channels that are in both sets
    right_missing = list(right_channels_set - intersection)
    print(f'Channels missing from right hemisphere: {right_missing}')
    for missing_item in right_missing:
        print(f'Removing {missing_item} from both hemispheres')
        index = right_channels.index(missing_item)
        right_channels.pop(index)
        left_channels.pop(index)

    intersection = recorded_channels_set & left_channels_set # channels that are in both sets
    left_missing = list(left_channels_set - intersection)
    print(f'Channels missing from left hemisphere: {left_missing}')
    for missing_item in left_missing:
        print(f'Removing {missing_item} from both hemispheres')
        index = left_channels.index(missing_item)
        right_channels.pop(index)
        left_channels.pop(index)

    print(f'Number of channels in manually created lists: {len(midline_channels) + len(left_channels) + len(right_channels)}')
    print(f'Number of channels in epochs object: {len(recorded_channels)}')
    return right_channels, left_channels

def main(SUB, TASK, RUN) -> None:
    # Load data
    FPATH = f'/project2/hcn1/dichotic_pitch_tracking/data/bids/derivatives/preprocessing/sub-{SUB}/sub-{SUB}_task-dichotic_run-{RUN}_desc-clean_epo.fif.gz'
    epochs = mne.read_epochs(FPATH, preload = True)
    coords = pd.read_csv('../data/captrak/2dcoords.csv')
    
    # Change tags
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
    
    # Get names of channels used, drop channels excluded
    recorded_channels = epochs.ch_names
    left_channels, right_channels = get_channels(recorded_channels)
    print(f'Left channels: {left_channels}')
    print(f'Right channels: {right_channels}')
    
    # Compute FFR
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
        P_left, freqs = P_left.get_data(return_freqs = True)
        P0_left = P0_left.get_data()
        P_right = P_right.get_data()
        P0_right = P0_right.get_data()

        # Take log
        dB_left = 10*np.log10(P_left/P0_left)
        dB_right = 10*np.log10(P_right/P0_right)

        # Take difference between hemispheres
        dB_diff = dB_right - dB_left

        # Take dB only at condition freqs
        freq = key[0]
        dB_diff_at_condition_freq = extract_power_at_condition_freq(freq, freqs, dB_diff)

        # Get channel coordinates
        x, y = get_channel_coords(coords, right_channels)

        # Create row for data frame
        row = {
            'sub': [SUB]*len(right_channels),
            'task': [TASK]*len(right_channels),
            'run': [RUN]*len(right_channels),
            'tone_num': [key[0]]*len(right_channels),
            'stream': [key[1]]*len(right_channels),
            'attended': [key[2]]*len(right_channels),
            'right_channels': right_channels,
            'x': x,
            'y': y,
            'dB_diff': dB_diff_at_condition_freq}

        # Add to dataframe
        row_df = pd.DataFrame(row)
        evokeds = evokeds.append(row_df, ignore_index = True)
    
    save_fp = f'../data/bids/derivatives/abr/sub-{SUB}_task-{TASK}_run-{RUN}_abr.pkl'
    print(f'Saving to {save_fp}')
    evokeds.to_pickle(save_fp)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(1)
    sub = sys.argv[1]
    task = sys.argv[2]
    run = sys.argv[3]
    main(sub, task, run)
