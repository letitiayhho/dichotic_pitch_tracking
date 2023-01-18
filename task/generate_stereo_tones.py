import numpy as np
import random
from scipy.io import wavfile

# Constants
LEFT_FREQS = [130, 130, 130, 200, 200, 200, 280, 280, 280] #Hz
RIGHT_FREQS = [130, 200, 280, 130, 200, 280, 130, 200, 280] #Hz
DURATION = 0.5
FS = 44100

def generate_stereo_tone(FS, DURATION, left_freq, right_freq):
    # Generate Tones
    time = np.arange(0, DURATION, 1.0/float(FS))
    tone_left = np.cos(2.0 * np.pi * left_freq * time)
    tone_right = np.cos(2.0 * np.pi * right_freq * time)

    # Add with 100 msecs of 0s at the beginning
    zeros = np.zeros(int(FS * 0.05))
    tone_left = np.append(zeros, tone_left)
    tone_right = np.append(zeros, tone_right)

    # A 2D array where the left and right tones are contained in their respective rows
    stereo_tone = np.vstack((tone_left, tone_right))

    # Reshape 2D array so that the left and right tones are contained in their respective columns
    stereo_tone = stereo_tone.transpose()
    
    return(stereo_tone)

def get_fname(left_freq, right_freq):
    fname = "tones/left_" + str(left_freq) + "_right_" + str(right_freq) + ".wav"
    return(fname)

for left_freq in LEFT_FREQS:
    for right_freq in RIGHT_FREQS:

        # Generate stereo tone and save as .wav
        stereo_tone = generate_stereo_tone(FS, DURATION, left_freq, right_freq)
        fname = get_fname(left_freq, right_freq)
        wavfile.write(fname, FS, stereo_tone)
