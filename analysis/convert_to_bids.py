#!/usr/bin/env python3

#SBATCH --time=00:05:00
#SBATCH --partition=broadwl
#SBATCH --ntasks=1
#SBATCH --mem-per-cpu=64G # 64 enough for most subs
#SBATCH --mail-type=all
#SBATCH --mail-user=letitiayhho@uchicago.edu
#SBATCH --output=logs/convert-to-bids_%j.log

from mne_bids import BIDSPath, write_raw_bids, get_anonymization_daysback
import random
import pandas as pd
import numpy as np
import itertools
import mne
import os
import sys
import re
from util.io.add_stream_to_event_tags import *
from util.io.remap_aux_labels import *

def main(fpath, sub, task, run) -> None:
    print(fpath, sub, task, run)

    RAW_DIR = '../data/raw/'
    BIDS_DIR = '../data/bids/'
    MAPS_DIR = '../data/captrak/'

    # load data with MNE function for your file format
    full_fpath = os.path.join(RAW_DIR, fpath)
    print(full_fpath)
    raw = mne.io.read_raw_brainvision(full_fpath)
    raw.load_data()
    
    # Rename channels according to aux-label-remapping.csv
    print("Renaming aux channels")
    raw, remap_dict = remap_aux_labels(sub, raw, 'aux-label-remapping.csv')
    raw.rename_channels(remap_dict)
    raw.set_channel_types({'Left': 'stim', 'Right': 'stim'})

    # add some info BIDS will want
    print("Add line_freq to raw.info")
    raw.info['line_freq'] = 60 # the power line frequency in the building we collected in

    # map channel numbers to channel names
    print("Map channel numbers to channel names")
    print(f"Original channel names: {raw.ch_names}")
    if int(sub) < 29:
        map_fp = '../data/captrak/pitch_tracking_64_at_FCZ.csv'
        mapping_table = pd.read_csv(map_fp)
        mapping = {mapping_table.number[i]: mapping_table.name[i] for i in range(len(mapping_table))}
        raw.rename_channels(mapping)
    raw.add_reference_channels(ref_channels = ['Cz'])
    print(f"Channel names: {raw.ch_names}")

    # Checks
    n_channels = len(raw.ch_names)
    print(f"Number of channels: {n_channels}")
    if n_channels != 66:
        sys.exit(f"Incorrect number of channels, there should be 66 (2 aux incl) channels, instead there are {n_chans} channels")

    # Map channels to their coordinates
    print("Map channels to their captrak coordinates")
    captrak_found = False
    captrak_sub = sub

    while not captrak_found:
        print("Looking for captrak file")
        captrak_path = MAPS_DIR + 'sub-' + str(captrak_sub) + '.bvct'
        print(captrak_path)
        if os.path.isfile(captrak_path):
            print(f"Using captrak file from {captrak_sub}")
            dig = mne.channels.read_dig_captrak(captrak_path)
            raw.set_montage(dig, on_missing = 'warn')
            captrak_found = True
        else:
            captrak_sub = random.randint(3, 30)

    # Extract events from raw file
    print("Set annotations")
    events, event_ids = mne.events_from_annotations(raw)

    # Add stream to event tags
    events = add_stream_to_event_tags(events, sub)

    # Drop meaningless event name
    events = np.array(events)
    events = events[events[:,2] != event_ids['New Segment/'], :]

    # Rename events to their stimulus pitch
    annot = mne.annotations_from_events(events, sfreq = raw.info['sfreq'])
    raw.set_annotations(annot)

    # Get range of dates the BIDS specification will accept
    daysback_min, daysback_max = get_anonymization_daysback(raw)

    # Write data into BIDS directory, while anonymizing
    print("Write data into BIDS directory")
    bids_path = BIDSPath(
            run = run,
            subject = sub,
            task = task,
            datatype = 'eeg',
            root = BIDS_DIR
    )

    write_raw_bids(
        raw,
        bids_path = bids_path,
        allow_preload = True, # whether to load full dataset into memory when copying
        format = 'BrainVision', # format to save to
        anonymize = dict(daysback = daysback_min), # shift dates by daysback
        overwrite = True,
    )

    # Check if conversion was successful and .vhdr file was written
    vhdr_path = str(bids_path)
    print(f".vhdr file written? {os.path.exists(vhdr_path)}")
    print("Done :-)")

__doc__ = "Usage: ./convert-to-bids.py <fpath> <sub> <task> <run> <bids_path>"

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print(__doc__)
        sys.exit(1)
    fpath = sys.argv[1]
    sub = sys.argv[2]
    task = sys.argv[3]
    run = sys.argv[4]
    main(fpath, sub, task, run)

