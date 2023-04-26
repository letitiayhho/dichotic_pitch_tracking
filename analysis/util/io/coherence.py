import mne
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mne_bids import BIDSPath, read_raw_bids
from bids import BIDSLayout
from mne_connectivity import seed_target_indices, spectral_connectivity_time, spectral_connectivity_epochs

def get_stim_sub(SUB, RUN): # Use a different sub for generating stim channels if sub has bad Aux channel
    # Constants
    N_SUBS = 45
    SUBS_WITH_BAD_AUX = ['13', '28']
    OTHER_BAD_SUBS = ['1', '2', '41', '45']

    # If sub has bad aux
    if SUB in SUBS_WITH_BAD_AUX:
        print("Using Aux data from a different sub to generate stim")

        # Identify sub to choose from
        bad_subs = SUBS_WITH_BAD_AUX + OTHER_BAD_SUBS
        all_subs = [str(x) for x in range(1, N_SUBS + 1)]
        possible_subs = set(bad_subs) ^ set(all_subs)

        # Randomly pick a sub
        np.random.seed(0)
        STIM_SUB = np.random.choice(list(possible_subs))
        STIM_RUN = 1
    else:
        STIM_SUB = SUB
        STIM_RUN = RUN
    return(STIM_SUB, STIM_RUN)

def get_raw_epochs(BIDS_ROOT, sub, task, run):
    sub = str(sub)
    run = str(run)
    bids_path = BIDSPath(root = BIDS_ROOT,
                     subject = sub,
                     task = task,
                     run = run,
                     datatype = 'eeg')
    raw = read_raw_bids(bids_path, verbose = False)
    raw_events, raw_event_id = mne.events_from_annotations(raw)
    raw_epochs = mne.Epochs(raw, 
                    events = raw_events, 
                    baseline = None,
                    event_id = raw_event_id)
    return(raw_epochs)

def create_stim_epochs_array(raw_epochs, n_epochs, CONDS):
    n_conds = len(CONDS)
    n_samps = 3501
    stim_epochs_array = np.empty((n_epochs, n_conds, n_samps))
    for i in range(n_conds):
        cond = CONDS[i]
        stim = raw_epochs[cond].get_data(['stim'])
        stim = stim.mean(0).flatten()
        cond_stim_epochs = [stim]*n_epochs
        stim_epochs_array[:, i , :] = cond_stim_epochs
    return(stim_epochs_array)

def plot_stim_chans(FIGS_ROOT, SUB, RUN, RAW_TMIN, RAW_TMAX, stim_epochs_array):
    n_samples = np.shape(stim_epochs_array)[2]
    t = np.linspace(RAW_TMIN, RAW_TMAX, n_samples, endpoint = False)

    fig, axs = plt.subplots(5)
    axs[0].plot(t, stim_epochs_array[0, 0, :])
    axs[1].plot(t, stim_epochs_array[0, 1, :])
    axs[2].plot(t, stim_epochs_array[0, 2, :])
    axs[3].plot(t, stim_epochs_array[0, 3, :])
    axs[4].plot(t, stim_epochs_array[0, 4, :])
    fname = f"{FIGS_ROOT}/subj-{SUB}_run-{RUN}_averaged_aux.png"
    print(f"Saving averaged aux channel plot to {fname}")
    plt.savefig(fname)

def create_stim_epochs_object(stim_epochs_array, events, CONDS, FS, RAW_TMIN):
    info = mne.create_info(ch_names = CONDS,
                           ch_types = ['stim'] * 5,
                           sfreq = FS)

    # Manually add channel info to match original data to stop mne from shouting at us, very hacky
    info['custom_ref_applied'] = True
    info['description'] = 'Anonymized using a time shift to preserve age at acquisition'
    info['experimenter'] = 'mne_anonymize'
    info['highpass'] = 30.0
    info['line_freq'] = 60.0
    info['lowpass'] = 270.0
    event_id = {'100': 10001, '150': 10002, '200': 10003, '250': 10004, '50': 10005}

    # Manually add info that is passed in through mne.EpochsArray instead of in the info dict, also very hacky
    baseline = (-0.20000000298023224, 0.0)

    # Create Epochs object
    simulated_epochs = mne.EpochsArray(stim_epochs_array, 
                                       info, 
                                       events = events, 
                                       tmin = RAW_TMIN, 
                                       event_id = event_id, 
                                       baseline = baseline)
    return(simulated_epochs)
    
def get_coh_indices(N_CHANS):
    # Set indices of channel pairs to compute coherence across
    stim_indices = np.array([63, 64, 65, 66, 67]*N_CHANS)
    chan_indices = np.repeat(np.arange(1, 63, 1), 5)
    indices = (stim_indices, chan_indices)
    return(indices)

def get_fmin_and_fmax(CONDS):
    freqs = np.array(list(map(int, CONDS)))
    fmin = freqs - 5
    fmax = freqs + 5
    return(fmin, fmax)

def get_coh(cond, epochs, indices, fmin, fmax, CONDS, FS, METHOD):
    print(f"METHOD: {METHOD}")
    coh = spectral_connectivity_epochs(
        epochs[cond], 
        method = METHOD, 
        mode = 'fourier', 
        indices = indices,
        sfreq = FS, 
        fmin = fmin, 
        fmax = fmax, 
        faverage = True, 
        n_jobs = 1)
    return(coh)

def clean_coh(coh, CONDS, N_CHANS):
    N_CONDS = len(CONDS)
    df = np.zeros((N_CHANS, N_CONDS))
    coh_vals = coh.get_data()
    for i in range(N_CHANS * N_CONDS):
        a = i
        b = a%5
        chan = int(i/N_CONDS)
        val = coh_vals[a, b]
        df[chan, b] = val
    return(df)

def create_coh_df(coh, cond, CONDS, N_CHANS, SUB):
    coh_df = pd.DataFrame(data = coh, 
                          columns = CONDS)
    coh_df.insert(0, 'chan', list(range(1, N_CHANS+1)))
    coh_df.insert(0, 'cond', np.array([cond]*N_CHANS))
    coh_df.insert(0, 'sub', np.array([SUB]*N_CHANS))
    return(coh_df)

