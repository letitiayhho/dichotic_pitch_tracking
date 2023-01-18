import numpy as np
import random
from scipy.io import wavfile

# Constants
FREQS = [130, 200, 280] #Hz
SIDES = ['right', 'left']
DURATION = 0.5
FS = 44100

def generate_stereo_tone(FS, DURATION, side, freq):
    # Generate Tones
    time = np.arange(0, DURATION, 1.0/float(FS))
    if side == 'right':
        tone_left = np.zeros(len(time))
        tone_right = np.cos(2.0 * np.pi * freq * time)
    elif side == 'left':
        tone_left = np.cos(2.0 * np.pi * freq * time)
        tone_right = np.zeros(len(time))

    # A 2D array where the left and right tones are contained in their respective rows
    stereo_tone = np.vstack((tone_left, tone_right))

    # Reshape 2D array so that the left and right tones are contained in their respective columns
    stereo_tone = stereo_tone.transpose()
    
    return(stereo_tone)

def get_fname(side, freq):
    fname = "tones/" + str(side) + "_" + str(freq) + ".wav"
    return(fname)

for side in SIDES:
    for freq in FREQS:

        # Generate stereo tone and save as .wav
        stereo_tone = generate_stereo_tone(FS, DURATION, side, freq)
        fname = get_fname(side, freq)
        wavfile.write(fname, FS, stereo_tone)
