#!/usr/bin/env python
import re
import itertools
from typing import Tuple, Iterator
from mne_bids import BIDSPath, read_raw_bids, print_dir_tree
from bids import BIDSLayout

KeyType = Tuple[str, str, str, str]

def iter_BIDSPaths(fpaths) -> Iterator[KeyType]:
#     # Get filepaths
#     if derivatives:
#         layout = BIDSLayout(bids_root, derivatives = derivatives)
#         fpaths = layout.get(scope = 'preprocessing',
#                             extension = 'fif.gz',
#                             return_type = 'filename')
#     else:
#         layout = BIDSLayout(bids_root)
#         fpaths = layout.get(extension = 'eeg',
#                             return_type = 'filename')

    # Get corresponding subject number
    filter_subs = re.compile('sub-(\d{1,2})_')
    subs = list(map(filter_subs.findall, fpaths))
    subs = list(itertools.chain(*subs))

    # Get corresponding run number
    filter_runs = re.compile('run-(\d)')
    runs = list(map(filter_runs.findall, fpaths))
    runs = list(itertools.chain(*runs))

    for i in range(len(fpaths)):
        key = (fpaths[i], subs[i], 'pitch', runs[i])
        print(key)
        yield key
