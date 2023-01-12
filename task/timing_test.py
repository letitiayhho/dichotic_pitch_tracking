from events import EventMarker
from functions import *
#import RTBox
import random

MARKER = EventMarker()
#MARKER = None
n_tones = 1000

stream = get_stream()
target = get_target()

tones = get_tone_array(target)
marks = get_mark(tones)
tone_id = get_is_target(tones, stream, target)
tone_array = tones[random.randint(0, 7)]
tone_fname = get_tone_fname(tone_array)
weights = get_tone_weights(stream, target, tones, False)
no_target_weights = get_tone_weights(stream, target, tones, True)
cannot_be_target = False

tone, is_target, mark = get_tone(tones, tone_id, marks, weights, no_target_weights, cannot_be_target)

for i in range(n_tones):
    print(i)
    rt = play_tone(MARKER, tone_fname, mark)
