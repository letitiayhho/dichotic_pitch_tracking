#!/usr/bin/env python

import re
import os
import itertools
from typing import Tuple, Iterator

KeyType = Tuple[str, str, str, str]

def iter_raw_paths(data_dir) -> Iterator[KeyType]:
    fnames = os.listdir(data_dir)
#    fnames = [f for f in fnames if '.vhdr' in f] # filter for .vhdr files
#
#    # Get subject list
#    filt = re.compile('(([0-9]|[1-9][0-9]){1,2})')
#    subs = list(map(lambda x: (re.search(filt, x)).group(0), fnames))
#
#    # Get a task list
#    tasks = ['pitch']*len(subs) # broadcast
#
#    # Get a run list
#    filt = re.compile('\w+[0-9]_([0-9]).*')
#    runs = list(map(filt.findall, fnames))
#    runs = ['1' if x == [] else x for x in runs]
#    runs = list(itertools.chain(*runs))
#
#
    for fname in fnames:
        if '.vhdr' not in fname:
            continue

        # Get subject number
        filt = re.compile('(([0-9]|[1-9][0-9]){1,2})')
        sub = re.search(filt, fname).group(0)

        # Get task name
        task = 'pitch'

        # Get run number
        print(fname)
        filt = re.compile('\w+[0-9]_([0-9]).*')
        run = re.findall(filt, fname)
        run = '1' if run == [] else run[0]

        key = (fname, sub, task, run)
        yield key

__all__ = ['iter_raw_paths']
