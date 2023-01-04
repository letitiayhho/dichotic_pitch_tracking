from events import EventMarker
from functions import *
import RTBox
import random

# MARKER = EventMarker()
MARKER = None
n_tones = 20

tones = get_tone_array(target)
tone_array = tones[random.randint(0, 9)]
tone_fname = get_tone_fname(tone_array)

for i = range(n_tones):
    rt = play_tone(MARKER, tone_fname)
