#!/usr/bin/env python3

import pandas as pd

def get_map_from_csv(maps_dir, fp):
    mapping_table = pd.read_csv(maps_dir + fp)
    mapping = {mapping_table.number[i]: mapping_table.name[i] for i in range(len(mapping_table))}
    return mapping

def get_chan_mapping(maps_dir, sub):
    special_mappings = {
               '2': 'pitch_tracking_64_at_IZ.csv',
               '3': 'pitch_tracking_64_at_IZ.csv',
               '4': 'pitch_tracking_no_IZ.csv',
               '5': 'pitch_tracking_64_at_IZ.csv',
               '6': 'pitch_tracking_64_at_IZ.csv',
               }

    if sub in special_mappings.keys():
        fp = special_mappings[sub]
    else:
        fp = 'pitch_tracking_64_at_FCZ.csv'
    mapping = get_map_from_csv(maps_dir, fp)
    return mapping

__all__ = ['get_chan_mapping']
