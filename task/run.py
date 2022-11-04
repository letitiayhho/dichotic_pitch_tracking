from psychopy import visual, core, event
from psychtoolbox import WaitSecs
from events import EventMarker
from functions import *
import RTBox

# ask for subject and block number
SUB_NUM = input("Input subject number: ")
BLOCK_NUM = input("Input block number: ")

# set seed
SEED = int(SUB_NUM + "0" + BLOCK_NUM + str(seq_num))
print("Current seed: " + str(SEED))
random.seed(SEED)

# set up keyboard, window and RTBox
WIN = visual.Window(size = (1920, 1080),
    screen = -1,
    units = "norm",
    fullscr = False,
    pos = (0, 0),
    allowGUI = False)
MARKER = EventMarker()
box = RTBox.RTBox()
box.buttonNames(['1', '1', '1', '1'])
LOG = open_log(SUB_NUM, BLOCK_NUM)

# have subj listen the tones and display instructions if training block
start(BLOCK_NUM, WIN, TONE_LEN, FREQS)

for seq_num in range(N_SEQS):

    # Randomize stream and target
    stream = get_stream()
    target = get_target()
    
    # Get weights for tones to select from
    tones = get_tone_array(target)
    tone_id = get_is_target(tones, stream, target)
    markers = get_markers(tones)
    weights = get_tone_weights(stream, target, tones, False)
    no_target_weights = get_tone_weights(stream, target, tones, True)
    
    tone_nums = []
    left_freq = []
    right_freq = []
    markers_ = []
    is_targets = []
    rts = []
    hits = []
    false_alarms = []

    cannot_be_target = True
    for tone_num in range(1, SEQ_LEN + 1):
        fixation(WIN)
        
        tone, is_target, marker = get_tone(tones, tone_id, markers, weights, no_target_weights, cannot_be_target)
        tone_fname = get_tone_fname(tone)
        rt = play_tone(MARKER, tone_fname)
        hit, false_alarm = grade(rt, target)
        cannot_be_target = is_target # Make sure targets can't play consecutively

        tone_nums.append(tone_num)
        left_freq.append(tone[0])
        right_freq.append(tone[1])
        markers_.append(marker)
        is_targets.append(is_target)
        rts.append(rt)
        hits.append(hit)
        false_alarms.append(false_alarm)
        
        WIN.flip()
        
    # Give feedback
    give_feedback(hits, false_alarms)
        
    write_log(LOG,
              SEQ_LEN,
              SEED, 
              SUB_NUM,
              BLOCK_NUM,
              seq_num,
              stream, 
              target, 
              tone_nums,
              left_freq, 
              right_freq, 
              markers_,
              is_targets,
              rts,
              hits,
              false_alarms)

print("Block over.")

core.quit()
