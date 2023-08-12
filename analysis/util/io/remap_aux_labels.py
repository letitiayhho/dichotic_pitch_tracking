import pandas as pd

def remap_aux_labels(sub, raw, remapping_fpath):
    remapping = pd.read_csv(remapping_fpath)
    sub_remap = remapping[(remapping['sub'] == int(sub))]
    aux = list(sub_remap['aux'])
    remap = list(sub_remap['remap'])
    remap_dict = {}
    remap_dict[aux[0]] = remap[0]
    remap_dict[aux[1]] = remap[1]
    return raw, remap_dict
