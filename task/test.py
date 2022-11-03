from psychopy.sound.backend_ptb import SoundPTB as Sound
from psychtoolbox import GetSecs, WaitSecs, hid
from psychopy import prefs
import numpy as np

prefs.hardware['audioLib'] = ['PTB', 'sounddevice', 'pyo','pygame']
print(prefs.hardware['audioLib'])

ISI = 0.3
target = 130
seq_len = 100
n_targets_min = 15
n_targets_max = 25

if target == 130:
    play_tones = tones
    del play_tones[(target, target)]
    
print(play_tones)

def play_tone(ISI, tone_fpath):
    now = GetSecs()
    snd = Sound(tone_fpath)
    snd.play(when = now + 0.1)
    WaitSecs(ISI - 0.1)

# Get list of tone files to play
def get_tone_array(target):
tones = [[130, 130],
         [130, 200],
         [130, 280],
         [200, 130],
         [200, 200],
         [200, 280],
         [280, 130],
         [280, 200],
         [280, 280]]
    tones.remove([target, target])
    tones = np.array(tones)
    return(tones)
    
def get_n_targets(n_targets_min, n_targets_max):
    n_targets = random.randint(n_targets_min, n_targets_max)
    return(n_targets)

def get_stream():
    stream = random.choice(['r', 'l'])
    return(stream)

def get_tone_fname(left_freq, right_freq):
    fname = "tones/left_" + str(left_freq) + "_right_" + str(right_freq) + ".wav"
    return(fname)
    
tones = get_tone_array(target)
stream = get_stream()
weights = get_tone_weights(stream, target, tones)
    randomList = random.choices(
  sampleList, weights=(10, 20, 30, 40, 50), k=5)
Get

def _replaceitem(x, target):
    if x == target:
        return(1)
    else:
        return(2)

def get_tone_weights(stream, target, tones):
    if stream == 'l':
        distractors = tones[:, 0]
    elif stream == 'r'
        distractors = tones[:, 1]
    weights = list(map(_replaceitem, distractors, [target] * len(distractors)))
    return(weights)
    
# stream, target, left tone, right tone, is_target, tone_num, seq_num
# now = GetSecs()
# snd = Sound('tones/left_130_right_280.wav')
# snd.play(when = now + 0.1)
# WaitSecs(2)