from psychopy import visual, core, event
from psychtoolbox import WaitSecs
from events import EventMarker
from functions import *

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

# open log file
LOG = open_log(SUB_NUM, BLOCK_NUM)
seq_num = get_seq_num(LOG)
score = get_score(LOG)
score_needed = get_score_needed(BLOCK_NUM)

# have subj listen the tones and display instructions if training block
start(BLOCK_NUM, WIN, TONE_LEN, FREQS)

# play sequences until SCORE_NEEDED is reached
while score < score_needed:
    target = get_target(FREQS)
    n_tones = get_n_tones(SEQ_LENS)

    # Play target
    n_target_plays = play_target(WIN, TONE_LEN, target)
    ready(WIN)
    WaitSecs(1)

    # Play tones
    fixation(WIN)
    WaitSecs(1)
    tone_nums, freqs, marks, is_targets, n_targets = play_sequence(MARKER, FREQS, TONE_LEN, target, n_tones)
    WIN.flip()
    WaitSecs(0.5)

    # Get response
    response = get_response(WIN)
    correct, score = update_score(WIN, n_targets, response, score, score_needed)

    # Write log file
    write_log(LOG, n_tones, SEED, SUB_NUM, BLOCK_NUM, seq_num, target, n_target_plays, tone_nums,
              freqs, marks, is_targets, n_targets, response, correct, score)
    
    seq_num += 1
    print(f'seq_num: {seq_num}')
    WaitSecs(1)

print("Block over.")

core.quit()
