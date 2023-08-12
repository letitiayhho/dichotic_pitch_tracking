#!/usr/bin/env python3

import glob
import pandas as pd

files = glob.glob('../../../figs/*tag-12*.png')

subs = []
auxs = []
for file in files:
    print(file)
    sub = int(file.split('_')[0].split('-')[1])
    aux = file.split('_')[2].split('-')[1].split('.')[0]
    subs.append(sub)
    auxs.append(aux)

d = {'sub': subs, 'aux': auxs}

print('Writing to ../../aux-label-remapping.csv')
df = pd.DataFrame(data = d)
df = df.sort_values(by = ['sub'])
df.to_csv('labels.csv')
