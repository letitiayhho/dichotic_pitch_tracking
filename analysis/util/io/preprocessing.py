import numpy as np
import os.path as op
import os
from pprint import pformat
from typing import Tuple, Iterator
import time

# EEG utilities
import mne
from mne.preprocessing import ICA, create_eog_epochs
from pyprep.prep_pipeline import PrepPipeline
from autoreject import get_rejection_threshold, validation_curve

# BIDS utilities
from mne_bids import BIDSPath, read_raw_bids
from util.io.bids import DataSink
from bids import BIDSLayout

# Create Iterator object to loop over all files
KeyType = Tuple[str, str, str]

def fpaths() -> Iterator[KeyType]:
    for sub in subjects:
        for task in tasks:
            for run in runs:
                run = str(run) # layout.get_runs() doesn't return strings for some reason
                key = (sub, task, run)
                yield key

#def get_bids_path(bids_root, sub, task, run):
#    bids_path = BIDSPath(root = bids_root,
#                        subject = sub,
#                        task = task,
#                        run = run,
#                        datatype = 'eeg',
#                        )
#    return bids_path

def import_bids_data(bids_root, sub, task, run):
    bids_path = BIDSPath(root = bids_root,
                        subject = sub,
                        task = task,
                        run = run,
                        datatype = 'eeg',
                        )
    print(bids_path)
    raw = read_raw_bids(bids_path, verbose = False)
    raw = raw.pick_types(eeg = True)
    return raw

def read_events(raw):
    events, events_ids = mne.events_from_annotations(raw)
    return events, events_ids

def create_eogs(raw):
    raw = mne.set_bipolar_reference(raw, anode = 'Fp1', cathode = 'leog', ch_name = 'eog1', drop_refs = False)
    raw = mne.set_bipolar_reference(raw, anode = 'Fp2', cathode = 'reog', ch_name = 'eog2', drop_refs = False)
    raw = raw.drop_channels(['reog', 'leog'])
    raw = raw.set_channel_types({'eog1': 'eog', 'eog2': 'eog'})
    return raw


def resample(raw, fs, events): # Resample to a more manageable speed
    raw, events = raw.resample(fs, events = events)
    return raw, events

def run_PREP(raw, sub, run, LOWPASS): # Run PREP pipeline (notch, exclude bad channels, and re-reference)
    raw.load_data()
    seed = int(str(sub) + str(run))
    np.random.seed(seed)

    lf = raw.info['line_freq']
    prep_params = {
        'ref_chs': 'eeg',
        'reref_chs': 'eeg',
        'line_freqs': np.arange(lf, LOWPASS, lf) if np.arange(lf, LOWPASS, lf).size > 0 else [lf]
    }
    prep = PrepPipeline(raw, prep_params, raw.get_montage(), ransac = False, random_state = seed)
    prep = prep.fit()

    raw = prep.raw_eeg # replace raw with cleaned version
    raw_non_eeg = prep.raw_non_eeg # return the eog
    raw = raw.add_channels([raw_non_eeg], force_update_info=True) # combine eeg and non eeg
    bads = prep.noisy_channels_original
    return raw, bads

def bandpass(raw, h_freq, l_freq):
    raw = raw.filter(l_freq = l_freq, h_freq = h_freq)
    return raw

def epoch(raw, events, event_ids):
    epochs = mne.Epochs(
        raw,
        events,
        tmin = -0.2,
        tmax = 0.250,
        baseline = None, # do NOT baseline correct the trials yet; we do that after ICA
        event_id = event_ids, # remember which epochs are associated with which condition
        preload = True # keep data in memory
    )
    return epochs

def compute_ICA(epochs):
    ica = ICA(n_components = 15, random_state = 0)
    ica = ica.fit(epochs, picks = ['eeg', 'eog'])
    return ica

def apply_ICA(epochs_for_ica, epochs, ica):
    eog_indices, eog_scores = ica.find_bads_eog(epochs_for_ica, threshold = 1.96)
    ica.exclude = eog_indices
    epochs = ica.apply(epochs) # apply to aggressively filtered version of data
    return epochs, ica

def baseline_correct(epochs):
    epochs = epochs.pick_types(eeg = True) # change syntax?
    epochs = epochs.apply_baseline((-0.2, 0.))
    return epochs

def reject_trials(epochs):
    thres = get_rejection_threshold(epochs)
    epochs = epochs.drop_bad(reject = thres)
    return epochs, thres

def get_save_path(deriv_root, sub, task, run):
    sink = DataSink(deriv_root, 'preprocessing')

    # save cleaned data
    fpath = sink.get_path(
                    subject = sub,
                    task = task,
                    run = run,
                    desc = 'clean',
                    suffix = 'epo', # this suffix is following MNE, not BIDS, naming conventions
                    extension = 'fif.gz',
                    )
    fpath_split = fpath.split('_')
    fpath_split.insert(3, 'res-hi')
    fpath = '_'.join(fpath_split)
    return fpath, sink

def save_and_generate_report(fpath, epochs, sink, sub, task, run, ica, bads, thres):
    # Save
    epochs.save(fpath, overwrite = True)

    # Initialize report
    report = mne.Report(title = 'MNE Report for sub-%s run-%s'%(sub, run), verbose = True)
    report.parse_folder(op.dirname(fpath), pattern = '*run-%s*epo.fif.gz'%run, render_bem = False)

    # Plot the ERP
    fig_erp = epochs['50'].average().plot(spatial_colors = True)
    report.add_figure(
        fig_erp,
        caption = 'Average Evoked Response',
        title = 'evoked'
    )

    # Plot the excluded ICAs
    if ica.exclude: # if we found any bad components
        fig_ica_removed = ica.plot_components(ica.exclude)
        report.add_figure(
            fig_ica_removed,
            caption = 'Removed ICA Components',
            title = 'ICA'
        )

    # Format output
    html_lines = []
    for line in pformat(bads).splitlines():
        html_lines.append('<br/>%s' % line)
    html = '\n'.join(html_lines)
    report.add_html(html, title = 'Interpolated Channels')
    report.add_html('<br/>threshold: {:0.2f} microvolts</br>'.format(thres['eeg'] * 1e6),
                                title = 'Trial Rejection Criteria')
    report.add_html(epochs.info._repr_html_(), title = 'Info')
    report.save(op.join(sink.deriv_root, 'sub-%s_task-%s_run-%s_res-hi.html'%(sub, task, run)), open_browser = False, overwrite = True)
