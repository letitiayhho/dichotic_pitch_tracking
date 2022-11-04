from psychopy import visual, core, event
from psychtoolbox import WaitSecs
from events import EventMarker
from functions import *
import RTBox

# constants
TONE_DIR = 'tones'

# ask for subject and block number
SUB_NUM = input("Input subject number: ")
BLOCK_NUM = input("Input block number: ")

# set subject number, block and seq_num as seed
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
KB = get_keyboard('Dell Dell USB Entry Keyboard')
MARKER = EventMarker()
box = RTBox.RTBox()
box.buttonNames(['1', '1', '1', '1'])
LOG = open_log(SUB_NUM, BLOCK_NUM)

# # have subj listen the tones and display instructions if training block
# start(BLOCK_NUM, WIN, TONE_LEN, FREQS)

SEED = int(SUB_NUM + "0" + BLOCK_NUM)
random.seed(SEED)

for seq_num in range(N_SEQS):
    # Randomize stream and target
    stream = get_stream()
    target = get_target()
    
    # Get weights for tones to select from
    tones = get_tone_array(target)
    weights = get_tone_weights(stream, target, tones, False)
    no_target_weights = get_tone_weights(stream, target, tones, True)
    tone_id = get_is_target(tones, stream, target)
    
    tone_nums = []
    left_freq = []
    right_freq = []
    is_targets = []
    rts = []

    cannot_be_target = True
    for tone_num in range(1, SEQ_LEN + 1):
        fixation(WIN)
        
        tone, is_target = get_tone(tones, tone_id, weights, no_target_weights, cannot_be_target)
        tone_fname = get_tone_fname(tone)
        rt = play_tone(ISI, tone_fname)
        cannot_be_target = is_target

        tone_nums.append(tone_num)
        left_freq.append(tone[0])
        right_freq.append(tone[1])
        is_targets.append(is_target)
        rts.append(rt)
        
        WIN.flip()
        
        # Give feedback
        
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
              is_targets,
              rts)

print("Block over.")

core.quit()
