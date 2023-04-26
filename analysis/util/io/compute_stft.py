import numpy as np
import mne
import pandas as pd
from scipy import signal
from scipy import signal
from util.io.bids import DataSink

def summarize_stft(f, Zxx, n_epochs, condition_freqs): # approximate power at the condition freqs
    Zxx_condensed = np.empty([n_epochs, len(condition_freqs), 19])
    
    for i in range(len(condition_freqs)):
        
        # find indexes of freqs surrounding the condition freq
        freq = condition_freqs[i]
        a = int(np.argwhere(f < freq)[-1])
        b = a+1
        
        # subset power for the condition freq
        condition_Zxx = Zxx[:,a:b+1, :]
        
        # take average to get approximate for power at condition freq
        condition_Zxx = np.mean(condition_Zxx, axis = 1)
        Zxx_condensed[:, i, :] = condition_Zxx
    
    return Zxx_condensed

def get_stft_for_one_channel(x, fs, n_epochs, condition_freqs): # where x is n_epochs, n_windows
    f, t, Zxx = signal.stft(x, fs) 

    # Take real values
    Zxx = np.abs(Zxx)
    
    # Summarize to frequencies of interest
    Zxx = summarize_stft(f, Zxx, n_epochs, condition_freqs)
    
    return (f, t, Zxx)

def compute_stft(fpath, sub, task, run):
    DERIV_ROOT = '../data/bids/derivatives'
    FS = 5000
    CONDITION_FREQS = [50, 100, 150, 200, 250]
    
    # Read data
    epochs = mne.read_epochs(fpath)
    print("events read")
    events = epochs.events
    epochs = epochs.get_data()
    
    # Get metadata
    n_freqs = len(CONDITION_FREQS)
    n_epochs = np.shape(epochs)[0]
    n_chans = np.shape(epochs)[1]
    
    # Compute stft across all channels
    Zxxs = np.empty([n_epochs, n_chans, n_freqs, 19]) # n_epochs, n_chans, n_freqs, n_windows
    for chan in range(n_chans):
        x = pd.DataFrame(epochs[:, chan, :])
        f, t, Zxx = get_stft_for_one_channel(x, FS, n_epochs, CONDITION_FREQS)
        Zxxs[:, chan, :, :] = Zxx
        
    # Reshape for decoder
    Zxxs = Zxxs.reshape((n_epochs, n_freqs*n_chans, 19)) # n_epochs, n_freqs*n_chans, n_windows

    # Save powers and events
    sink = DataSink(DERIV_ROOT, 'decoding')
    stft_fpath = sink.get_path(
        subject = sub,
        task = task,
        run = run,
        desc = 'stft',
        suffix = 'power',
        extension = 'npy',
    )
    print('Saving scores to: ' + stft_fpath)
    np.save(stft_fpath, Zxxs)
        
    return (Zxxs, events)
