import pandas as pd
import os.path
import random
import git
#import time
from numpy import nan, array
from psychopy import prefs
prefs.hardware['audioLib'] = ['ptb']
from psychopy.sound.backend_ptb import SoundPTB as Sound
from psychopy import visual, core, event
from psychtoolbox import GetSecs, WaitSecs, hid
from psychopy.hardware.keyboard import Keyboard

def set_cwd(): # set working directory to git top level
    repo = git.Repo('.', search_parent_directories=True)
    os.chdir(repo.working_tree_dir)
    print(repo.working_tree_dir)

def set_seed(SUB_NUM, BLOCK_NUM, seq_num):
    seed = int(SUB_NUM + "0" + BLOCK_NUM + "0" + str(seq_num))
    print("Current seed: " + str(seed))
    random.seed(seed)
    return(seed)
    
def get_window():
    WIN = visual.Window(size = (1920, 1080),
        screen = -1,
        units = "norm",
        fullscr = False,
        pos = (0, 0),
        allowGUI = False)
    return(WIN)

#def init_RTBox(MARKER):
#    BOX = MARKER.box
#    BOX.buttonNames(['1', '1', '1', '1'])
#    return(BOX)

def init_Cedrus(serial):
   BOX = RBx20(serial)

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
    log = "data/logs/sub-" + SUB_NUM + "_blk-" + BLOCK_NUM + ".log"
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
                'miss' : [],
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
        seq_num = seq_nums.iloc[-1] + 1
    seq_num = int(seq_num)
    print(f"seq_num: {seq_num}")
    return(seq_num)

def get_reward(LOG):
    log = pd.read_csv(LOG)
    reward = log['reward']
    if len(reward) == 0:
        reward = 0
    else:
        reward = reward.iloc[-1]
    reward = float(reward)
    print(f"reward: {reward}")
    return(reward)

def get_n_seqs(BLOCK_NUM):
    if BLOCK_NUM == "0":
        n_seqs = 3
    else:
        n_seqs = 16
    return(n_seqs)

def start(WIN, BLOCK_NUM):
    if BLOCK_NUM == "0":
        instructions(WIN)
    else:
        block_welcome(WIN, BLOCK_NUM)
        
def play_instruction_tone(WIN, stream, order, freq):
    s = Sound(f"task/tones/{stream}_{str(freq)}.wav")
    txt = visual.TextStim(WIN, text = f"Press 'space' to hear the {order} tone in your {stream} ear.")
    event.clearEvents(eventType = None)
    txt.draw()
    WIN.flip()
    event.waitKeys(keyList = ['space'])
    s.play()
    WaitSecs(0.3)
    WIN.flip()
    
def display_instructions(WIN, text):
    instructions = visual.TextStim(WIN, text = text)
    instructions.draw()
    WIN.flip()
    event.waitKeys(keyList = ['return'])
    WIN.flip()
    print(text)

def instructions(WIN):
    display_instructions(WIN, "Welcome to the experiment. \n\n Press 'enter' to begin.")
    display_instructions(WIN, "In each trial for this task you will hear different sequences of tones simultaneously in both ears. The sequences will consist of three different tones, and you will be asked to pay attention to the sequence in either your left or your right ear. \n\n Press 'enter' to hear examples of those tones.")
    
    play_instruction_tone(WIN, 'left', 'first', '130')
    play_instruction_tone(WIN, 'left', 'second', '200')
    play_instruction_tone(WIN, 'left', 'third', '280')
    play_instruction_tone(WIN, 'right', 'first', '130')
    play_instruction_tone(WIN, 'right', 'second', '200')
    play_instruction_tone(WIN, 'right', 'third', '280')

    display_instructions(WIN, "For each sequence of tones, one of the three tones you just heard will be randomly selected as the ‘target’ tone. You will be allowed to listen to the target tone as many times as you like before the trial begins. Every time you hear a target tone, press any botton on the response box as quickly as you can. \n\n Press 'enter' for the remaining instructions.")
    display_instructions(WIN, "Pay close attention to whether the target tone plays on your left or right side, you will be listening only to the tones and targets on that side. \n\n Press 'enter' for the remaining instructions.")
    display_instructions(WIN, "You will receive an extra $0.10 for every tone you correctly identify as a target, and lose $0.05 for every target you miss or every tone you mistakenly identify as the target. \n\n Press 'enter' for the remaining instructions.")
    display_instructions(WIN, "It is important for you not to move your body, move your your eyes or blink while the tones are playing. To help with this, a fixation cross '+' will be shown during the each tone sequence. Keep your gaze on the fixation cross and stay relaxed while the cross is on the screen. \n\n Press 'enter' for the remaining instructions.")
    display_instructions(WIN, "You will now complete three practice trials. Please let you experimenter know if you have any questions or are experiencing any difficulties with the display or audio. \n\n Press 'enter' to continue to the practice trials.")

def block_welcome(WIN, BLOCK_NUM):
    display_instructions(WIN, f"Welcome to block number {BLOCK_NUM}/5. \n\n Press 'enter' to continue.")
    display_instructions(WIN, "Remember to keep your gaze on the fixation cross and stay relaxed while the fixation cross is on the screen. \n\n Press 'enter' to begin the block.")

def get_stream():
    return(random.choice(['r', 'l']))

def get_target():
    return(random.choice([130, 200, 280]))

def get_seq_len():
    return(random.choice([36, 42, 48]))

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
    tones = array(tones)
    return(tones)

def get_is_target(tones, stream, target):
    if stream == 'l':
        distractors = tones[:, 0]
    elif stream == 'r':
        distractors = tones[:, 1]
    tone_id = [x == target for x in distractors]
    return(tone_id)

def get_mark(tones):
    recoded_tones = tones.copy()
    recoded_tones[recoded_tones == 130] = 1
    recoded_tones[recoded_tones == 200] = 2
    recoded_tones[recoded_tones == 280] = 3
    recoded_tones = recoded_tones.astype(str)
    marks = []
    for row in recoded_tones:
        marks.append(row[0] + row[1]) # first number indicates left tone ID, second number right tone ID
    return(marks)
    
def get_tone_weights(stream, target, tones, no_targets):
    if stream == 'l':
        distractors = tones[:, 0]
    elif stream == 'r':
        distractors = tones[:, 1]
    weights = list(map(_replaceitem, distractors, [target] * len(distractors), [no_targets] * len(distractors)))
    return(weights)

def play_target(WIN, target, stream):
    if stream == 'l':
        fname = f"task/tones/left_{str(target)}.wav"
    elif stream == 'r':
        fname = f"task/tones/right_{str(target)}.wav"

    t_snd = Sound(fname)

    target_text = visual.TextStim(WIN, text = "Press 'space' to hear the target tone. Remember to listen for the target only in the same ear as you currently hear it. \n\n Press 'enter' to begin the trial.")
    target_text.draw()
    WIN.flip()
    target_played = False
    n_target_plays = 0

    while True:
        keys = event.getKeys(keyList = ['space', 'return'])
        if 'space' in keys:
            t_snd.play()
            n_target_plays += 1
            print('Target played')
        elif 'return' in keys and n_target_plays > 0:
            break

    WaitSecs(1)
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
    mark = int(markers[i])
    return(tone, is_target, mark)

def get_tone_fname(tone_array):
    left_freq = tone_array[0]
    right_freq = tone_array[1]
    fname = "task/tones/left_" + str(left_freq) + "_right_" + str(right_freq) + ".wav"
    return(fname)

def play_tone(BOX, MARKER, tone_fpath, mark):
    t0 = GetSecs()
    snd = Sound(tone_fpath)
    snd.play(when = t0 + 0.001)
    WaitSecs(0.001)
    MARKER.send(mark)
    
    timeout = 0.5
    key, rt = BOX.waitKeys(timeout = timeout)
    if rt != None:
        WaitSecs(timeout - rt)
    else:
        rt = nan

    return(rt)

def grade(rt, is_target):
    if is_target and rt is not nan:
        hit, miss, false_alarm = 1, 0, 0
    elif not is_target and rt is not nan:
        hit, miss, false_alarm = 0, 0, 1
    elif is_target and rt is nan:
        hit, miss, false_alarm = 0, 1, 0
    else:
        hit, miss, false_alarm = 0, 0, 0
    return(hit, miss, false_alarm)

def compute_reward(hits, misses, false_alarms, reward):
    earned = sum(hits) * 0.1
    deducted = -((sum(misses) + sum(false_alarms)) * 0.05)
    reward = round(reward + earned + deducted, 2)
    if reward < 0:
        reward = 0
    return(reward)

def give_feedback(WIN, hits, misses, false_alarms, reward):
    feedback = visual.TextStim(WIN, text = f"You had {sum(hits)} hits, {sum(misses)} misses and {sum(false_alarms)} false alarms. You have a total of ${reward} for this block. Press 'enter' to continue.")
    feedback.draw()
    WIN.flip()
    event.waitKeys(keyList = ['return'])
    print(f'hits: {sum(hits)}')
    print(f'misses: {sum(misses)}')
    print(f'false_alarms: {sum(false_alarms)}')
    print(f'reward: {reward}')

def broadcast(n_tones, var):
    if not isinstance(var, list):
        broadcasted_array = [var]*n_tones
    return(broadcasted_array)

def write_log(LOG, SEQ_LEN, seed, SUB_NUM, BLOCK_NUM, seq_num, stream, target, 
              tone_num, left_freq, right_freq, mark, is_target, rt, hit, miss, false_alarm, reward):
    print("Writing to log file")
    d = {
        'seed': broadcast(SEQ_LEN, seed),
        'sub_num': broadcast(SEQ_LEN, SUB_NUM),
        'block_num': broadcast(SEQ_LEN, BLOCK_NUM),
        'seq_num': broadcast(SEQ_LEN, seq_num),
        'stream': broadcast(SEQ_LEN, stream),
        'target': broadcast(SEQ_LEN, target),
        'tone_num' : tone_num,
        'left_freq' : left_freq,
        'right_freq' : right_freq,
        'mark' : mark,
        'is_target' : is_target,
        'rt' : rt,
        'hit' : hit, 
        'miss' : miss, 
        'false_alarm' : false_alarm,
        'reward': broadcast(SEQ_LEN, reward),
    }
    df = pd.DataFrame(data = d)
    df.to_csv(LOG, mode='a', header = False, index = False)

def end(WIN, BLOCK_NUM, reward):
    if BLOCK_NUM == "0":
        display_instructions(WIN, "Congratulations for finishing the practice block. Let your experimenter know if you have any questions or if you would like to repeat this practice block. If you are ready, you will now move on to the 5 experiment blocks, each of which will have 16 trials.")
    else:
        display_instructions(WIN, f"End of block! You earned a total of ${reward} for this block. Your experimenter will now come and check on you.")
