import pandas as pd
import os.path
import random

from psychopy import prefs
prefs.hardware['audioLib'] = ['ptb']
from psychopy.sound.backend_ptb import SoundPTB as Sound
from psychopy import visual, core, event
from psychtoolbox import GetSecs, WaitSecs, hid
from psychopy.hardware.keyboard import Keyboard
from numpy import nan

def set_seed(SUB_NUM, BLOCK_NUM):
    SEED = int(SUB_NUM + "0" + BLOCK_NUM)
    print("Current seed: " + str(SEED))
    random.seed(SEED)
    
def get_window():
    WIN = visual.Window(size = (1920, 1080),
        screen = -1,
        units = "norm",
        fullscr = False,
        pos = (0, 0),
        allowGUI = False)
    return(WIN)

def get_keyboard(dev_name):
    devs = hid.get_keyboard_indices()
    idxs = devs[0]
    names = devs[1]
    try:
        idx = [idxs[i] for i, nm in enumerate(names) if nm == dev_name][0]
    except:
        raise Exception(
        'Cannot find %s! Available devices are %s.'%(dev_name, ', '.join(names))
        )
    return Keyboard(idx)

def open_log(SUB_NUM, BLOCK_NUM):
    log = "../data/logs/sub-" + SUB_NUM + "_blk-" + BLOCK_NUM + ".log"
    if not os.path.isfile(log): # create log file if it doesn't exist
        print(f"Creating {log}")
        d = {
                'seed': [],
                'sub_num': [],
                'block_num': [],
                'seq_num': [],
                'stream': [],
                'target': [],
                'tone_num' : [],
                'left_freq' : [],
                'right_freq' : [],
                'mark' : [],
                'is_target' : [],
                'rt' : [],
                'hit' : [],
                'false_alarm' : [],
                'reward' : [],
            }
        df = pd.DataFrame(data = d)
        df.to_csv(log, mode='w', index = False)
    return(log)

def get_seq_num(LOG):
    log = pd.read_csv(LOG)
    seq_nums = log['seq_num']
    if len(seq_nums) == 0:
        seq_num = 1
    else:
        seq_num = seq_nums.iloc[-1]
    seq_num = int(seq_num) + 1
    print(f"seq_num: {seq_num}")
    return(seq_num)

def get_n_seqs(BLOCK_NUM):
    if BLOCK_NUM == "0":
        n_seqs = 3
    else:
        n_seqs = 18
    return(n_seqs)

def start(BLOCK_NUM, WIN, TONE_LEN, FREQS):
    if BLOCK_NUM == "0":
        instructions(WIN)
    else:
        block_welcome(WIN, BLOCK_NUM)
        
def play_instruction_tone(stream, order, freq):
    s = Sound(f"tones/{stream}_{str(freq)}.wav")
    txt = visual.TextStim(WIN, text = f"Press 'enter' to hear the {order} tone in your {stream} ear")
    event.clearEvents(eventType = None)
    txt.draw()
    WIN.flip()
    event.waitKeys(keyList = ['return'])
    s.play()
    WaitSecs(1)
    
def display_instructions(WIN, text):
    instructions = visual.TextStim(WIN, text = text)
    instructions.draw()
    WIN.flip()
    event.waitKeys(keyList = ['return'])
    print(text)

def instructions(WIN):
    display_instructions(WIN, "Welcome to the experiment. Press 'enter' to begin.")
    display_instructions(WIN, "In each trial for this task you will hear different sequences of tones simultaneously in both ears. The sequences will consist of three different tones, and you will either be asked to pay attention to either the sequence in your left or your right ear. Press 'enter' to hear those tones…")
    
    play_instruction_tones('left', 'first', '130')
    play_instruction_tones('left', 'first', '200')
    play_instruction_tones('left', 'first', '280')
    play_instruction_tones('right', 'first', '130')
    play_instruction_tones('right', 'first', '200')
    play_instruction_tones('right', 'first', '280')
    
    display_instructions(WIN, text = "For each sequence of tones one of the three tones you just heard will be randomly selected as the ‘target’ tone. You will be allowed to listen to the target tone as many times as you like. Your task is to count and remember how many times you hear the target tone in the sequence. Press 'enter' for the remaining instructions…")
    display_instructions(WIN, text = "At the end of the sequence you will be asked to report how many times you heard the target sequence. If are correct or close enough you will receive an extra $0.10 at the end of the experiment. Press 'enter' for the remaining instructions…")
    display_instructions(WIN, text = "It is important for you not to move your body, move your your eyes or blink while the tones are playing. To help with this, a fixation cross '+' will be shown during the tone sequence. Keep your gaze on the fixation cross and hold as still as you can while the cross is on the screen. Press 'enter' for the remaining instructions…")
    display_instructions(WIN, text = "You will now complete three practice trials. Please let you experimenter know if you have any questions or are experiencing any difficulties with the display or audio. Press 'enter' to continue to the practice trials…")

def block_welcome(WIN, BLOCK_NUM):
    blk_welcome = visual.TextStim(WIN, text = f"Welcome to block number {BLOCK_NUM}/5. Press 'enter' to continue.")
    blk_welcome.draw()
    WIN.flip()
    event.waitKeys(keyList = ['return'])
    
def start(BLOCK_NUM, WIN, TONE_LEN, FREQS):
    if BLOCK_NUM == "0":
        instructions(WIN)
    else:
        block_welcome(WIN, BLOCK_NUM)

def get_stream():
    return(random.choice(['r', 'l']))

def get_target():
    return(random.choice([130, 200, 280]))

def get_seq_len():
    return(random.choice([24, 30, 36])

def _replaceitem(x, target, no_targets):
    if x == target:
        if no_targets:
            return(0)
        else:
            return(1)
    else:
        return(2)
    
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

def get_is_target(tones, stream, target):
    if stream == 'l':
        distractors = tones[:, 0]
    elif stream == 'r':
        distractors = tones[:, 1]
    is_target = [x == target for x in distractors]
    return(is_target)

def get_mark(tones):
    tones[tones == 130] = 1
    tones[tones == 200] = 2
    tones[tones == 280] = 3
    tones = tones.astype(str)
    markers = []
    for row in tones:
        markers.append(row[0] + row[1])
    return(markers)
    
def get_tone_weights(stream, target, tones, no_targets):
    if stream == 'l':
        distractors = tones[:, 0]
    elif stream == 'r':
        distractors = tones[:, 1]
    weights = list(map(_replaceitem, distractors, [target] * len(distractors), [no_targets] * len(distractors)))
    return(weights)

def play_target(WIN, target, stream):
    if stream == 'l':
        fname = f"tones/left_{str(target)}.wav"
    elif stream == 'r':
        fname = f"tones/right_{str(target)}.wav"

    t_snd = Sound(fname)

    target_text = visual.TextStim(WIN, text = "Press 'space' to hear the target tone. Remember to listen for the target only in the same ear as you currently hear it. Press 'enter' to begin the trial!")
    target_text.draw()
    WIN.flip()
    target_played = False
    n_target_plays = 0

    while True:
        keys = event.getKeys(keyList = ['space', 'return'])
        if 'space' in keys:
            t_snd.play()
            target_played = True
            n_target_plays += 1
            print('Target played')
        elif 'return' in keys and target_played:
            break

    return(n_target_plays)

def fixation(WIN):
    fixation = visual.TextStim(WIN, '+')
    fixation.draw()
    WIN.flip()
    return(fixation)

def get_tone(tones, tone_id, markers, weights, no_target_weights, cannot_be_target):
    if cannot_be_target:
        i = random.choices(range(len(tones)), no_target_weights)[0]
    else:
        i = random.choices(range(len(tones)), weights)[0]
    tone = tones[i]
    is_target = tone_id[i]
    marker = markers[i]
    print(tone)
    print(is_target)
    return(tone, is_target, marker)

def get_tone_fname(tone_array):
    left_freq = tone_array[0]
    right_freq = tone_array[1]
    fname = "tones/left_" + str(left_freq) + "_right_" + str(right_freq) + ".wav"
    return(fname)

def play_tone(MARKER, tone_fpath, is_target):
    t0 = boxSecs()
    snd = Sound(tone_fpath)
    snd.play(when = now + 0.1)
    WaitSecs(0.1)
    MARKER.send(mark)
    
    (secs, btns) = box.secs(0.6) # read response, 0.6 secs
    if len(secs) < 1:
        rt = nan
    else:
        rt = secs[0] - t0
    WaitSecs(0.6 - rt)
    return(rt)

def grade(rt, is_target):
    if is_target and rt is not nan:
        hit = 1
        false_alarm = 0
    elif not is_target and rt is not nan:
        hit = 0
        false_alarm = 1
    else:
        hit = 0
        false_alarm = 0
    return(hit, false_alarm)

def compute_reward(reward):
    earned = sum(reward) * 0.05
    deducted = -(sum(reward)) * 0.05
    reward = reward + earned + deducted
    return(reward)

def give_feedback(hits, false_alarms, reward):
    feedback = visual.TextStim(WIN, text = f"You had {hits} hits and {false_alarms}. You've earned ${reward} for this block.")
    feedback.draw()
    WIN.flip()
    event.waitKeys(keyList = ['return'])

def broadcast(n_tones, var):
    if not isinstance(var, list):
        broadcasted_array = [var]*n_tones
    return(broadcasted_array)

def write_log(LOG, SEQ_LEN, seed, sub_num, block_num, seq_num, stream, target, 
              tone_num, left_freq, right_freq, mark, is_target, rt, hit, false_alarm, reward):
    print("Writing to log file")
    d = {
        'seed': broadcast(SEQ_LEN, seed),
        'sub_num': broadcast(SEQ_LEN, sub_num),
        'block_num': broadcast(SEQ_LEN, block_num),
        'seq_num': broadcast(SEQ_LEN, seq_num),
        'stream': broadcast(SEQ_LEN, stream),
        'target': broadcast(SEQ_LEN, target),
        'tone_num' : tone_nums,
        'left_freq' : left_freq,
        'right_freq' : right_freq,
        'mark' : markers,
        'is_target' : is_target,
        'rt' : rt,
        'hit' : hit, 
        'false_alarm' : false_alarm,
        'reward': broadcast(SEQ_LEN, target),
    }
    df = pd.DataFrame(data = d)
    df.to_csv(LOG, mode='a', header = False, index = False)
