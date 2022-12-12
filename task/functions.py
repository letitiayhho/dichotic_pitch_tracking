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

def fixation(WIN):
    fixation = visual.TextStim(WIN, '+')
    fixation.draw()
    WIN.flip()
    return(fixation)

def instructions(WIN, TONE_LEN, FREQS):
    p1 = Sound(FREQS[0], secs = TONE_LEN)
    p2 = Sound(FREQS[1], secs = TONE_LEN)
    p3 = Sound(FREQS[2], secs = TONE_LEN)
    
    welcome = visual.TextStim(WIN,
                            text = "Welcome to the experiment. Press 'enter' to begin.",
                            pos=(0.0, 0.0),
                            color=(1, 1, 1),
                            colorSpace='rgb')
    welcome.draw()
    WIN.flip()
    event.waitKeys(keyList = ['return'])
    core.wait(1)


    p1_txt = visual.TextStim(WIN,
                            text = "In this task you will be presented with random sequences of three tones. You will now hear the three tones. Press 'enter' to hear the first tone.",
                            pos=(0.0, 0.0),
                            color=(1, 1, 1),
                            colorSpace='rgb')
    p1_txt.draw()
    WIN.flip()
    event.waitKeys(keyList = ['return'])
    p1.play()
    core.wait(1)

    p2_txt = visual.TextStim(WIN,
                                text = "Press 'enter' to hear the second tone.",
                                pos=(0.0, 0.0),
                                color=(1, 1, 1),
                                colorSpace='rgb')

    event.clearEvents(eventType = None)
    p2_txt.draw()
    WIN.flip()
    event.waitKeys(keyList = ['return'])
    p2.play()
    core.wait(1)

    p3_txt = visual.TextStim(WIN,
                                text = "Press 'enter' to hear the third tone.",
                                pos=(0.0, 0.0),
                                color=(1, 1, 1),
                                colorSpace='rgb')

    event.clearEvents(eventType = None)
    p3_txt.draw()
    WIN.flip()
    event.waitKeys(keyList = ['return'])
    p3.play()
    core.wait(1)

    instruction_text = visual.TextStim(WIN,
                                      text = "In each trial of this experiment, one of the three tones you just heard will be randomly selected as the ‘target’ tone. You will be allowed to listen to the target tone as many times as you like. This target tone will then be played amidst a sequence of the other two tones. Your task is to count and remember how many times you hear the target tone in the sequence. Press 'enter' for the remaining instructions…",
                                      pos=(0.0, 0.0),
                                      color=(1, 1, 1),
                                      colorSpace='rgb')
    instruction2_text = visual.TextStim(WIN,
                                        text = "You will be asked how many times you heard the target tone at the end of a sequence and if you accurately report the number of target tones–or come close to the actual number of target tones–your 'score' will increase by 1. To finish each block, you will have to reach a score of 18. Please ask your experimenter any questions you may have about the task. Press 'enter' to continue…",
                                        pos=(0.0, 0.0),
                                        color=(1, 1, 1),
                                        colorSpace='rgb')
    instruction3_text = visual.TextStim(WIN,
                                        text = "It is important for you not to move your eyes or blink while the tones are playing. We also ask that you hold the rest of your body as still as possible. To help with this, a fixation cross '+' will be shown during the tone sequence. Keep your gaze on the fixation cross and hold as still as you can while the cross is on the screen. Press 'enter' to continue...",
                                        pos=(0.0, 0.0),
                                        color=(1, 1, 1),
                                        colorSpace='rgb')
    instruction4_text = visual.TextStim(WIN,
                                        text = "You will now complete a series of practice trials where you will try to reach a score of 3. Press 'enter' to continue to the first training trials...",
                                        pos=(0.0, 0.0),
                                        color=(1, 1, 1),
                                        colorSpace='rgb')
    instruction_text.draw()
    WIN.flip()
    event.waitKeys(keyList = ['return'])
    print('instruction1')

    event.clearEvents(eventType = None)
    instruction2_text.draw()
    WIN.flip()
    event.waitKeys(keyList = ['return'])
    WIN.flip()
    print('instruction2')

    event.clearEvents(eventType = None)
    instruction3_text.draw()
    WIN.flip()
    event.waitKeys(keyList = ['return'])
    WIN.flip()
    print('instruction3')

    event.clearEvents(eventType = None)
    instruction4_text.draw()
    WIN.flip()
    event.waitKeys(keyList = ['return'])
    WIN.flip()
    print('instruction4')

def block_welcome(WIN, BLOCK_NUM):
    blk_welcome = visual.TextStim(WIN,
                                  text = f"Welcome to block number {BLOCK_NUM}. Press 'enter' to continue.",
                                  pos=(0.0, 0.0),
                                  color=(1, 1, 1),
                                  colorSpace='rgb' )
    blk_welcome.draw()
    WIN.flip()
    event.waitKeys(keyList = ['return'])
    
def start(BLOCK_NUM, WIN, TONE_LEN, FREQS):
    if BLOCK_NUM == "0":
        instructions(WIN)
    else:
        block_welcome(WIN, BLOCK_NUM)

# def get_n_targets(n_targets_min, n_targets_max):
#     n_targets = random.randint(n_targets_min, n_targets_max)
#     return(n_targets)

def get_stream():
    stream = random.choice(['r', 'l'])
    return(stream)

def get_target():
    target = random.choice([130, 200, 280])
    return(target)

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

    target_text = visual.TextStim(WIN,
                                  text = "Press 'space' to hear the target tone. Remember to listen for the target only in the same ear as you currently hear it. Press 'enter' to begin the trial!",
                                  pos=(0.0, 0.0),
                                  color=(1, 1, 1),
                                  colorSpace='rgb')
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
    feedback = visual.TextStim(WIN,
                              text = f"You had {hits} hits and {false_alarms}. You've earned ${reward} for this block.",
                              pos=(0.0, 0.0),
                              color=(1, 1, 1),
                              colorSpace='rgb' )
    feedback.draw()
    WIN.flip()
    event.waitKeys(keyList = ['return'])

def broadcast(n_tones, var):
    if not isinstance(var, list):
        broadcasted_array = [var]*n_tones
    return(broadcasted_array)

def write_log(LOG, SEQ_LEN, seed, sub_num, block_num, seq_num, stream, target, 
              tone_num, left_freq, right_freq, marker, is_target, rt, hit, false_alarm, reward):
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
        'marker' : markers,
        'is_target' : is_target,
        'rt' : rt,
        'hits' : hit, 
        'false_alarm' : false_alarm,
        'reward': broadcast(SEQ_LEN, target),
    }
    df = pd.DataFrame(data = d)
    df.to_csv(LOG, mode='a', header = False, index = False)
