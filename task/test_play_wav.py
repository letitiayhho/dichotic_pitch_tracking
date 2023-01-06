from psychopy import prefs
prefs.hardware['audioLib'] = ['ptb']
from psychopy.sound.backend_ptb import SoundPTB as Sound
from psychtoolbox import GetSecs, WaitSecs
from functions import *

MARKER = None
# tone_fname = 'task/tones/test_music.wav'
tone_fname = "task/tones/left_280.wav"

# n_tones = 20
# for i = range(n_tones):
rt = play_tone(MARKER, tone_fname)

# snd = Sound(200, secs = 10)
# snd.play()


WaitSecs(10)
