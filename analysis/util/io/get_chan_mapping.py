#!/usr/bin/env python3

import pandas as pd

def get_map_from_csv(maps_dir, fp):
    mapping_table = pd.read_csv(maps_dir + fp)
    mapping = {mapping_table.number[i]: mapping_table.name[i] for i in range(len(mapping_table))}
    return mapping

def get_chan_mapping(maps_dir, sub):
    fp = 'pitch_tracking_64_at_FCZ.csv'
    mapping = get_map_from_csv(maps_dir, fp)
    return mapping

__all__ = ['get_chan_mapping']
