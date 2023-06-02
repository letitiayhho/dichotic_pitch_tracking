import pandas as pd

def remap_aux_labels(sub, raw, remapping_fpath):
    remapping = pd.read_csv(remapping_fpath)
    remap = remapping[(remapping['sub'] == int(sub)) & (remapping['tag'] == 12)]
    aux = list(remap['aux'])
    rename = list(remap['rename'])
    remap_dict = {}
    remap_dict[aux[0]] = rename[0]
    remap_dict[aux[1]] = rename[1]
    return raw, remap_dict
