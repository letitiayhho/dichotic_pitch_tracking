import pandas as pd
import os.path
import random

from psychopy import prefs
prefs.hardware['audioLib'] = ['ptb']
from psychopy.sound.backend_ptb import SoundPTB as Sound
from psychopy import visual, core, event
from psychtoolbox import GetSecs, WaitSecs, hid
from psychopy.hardware.keyboard import Keyboard

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
            'target': [],
            'tone_num': [],
            'n_target_plays': [],
            'freq': [],
            'mark': [],
            'is_target': [],
            'n_targets': [],
            'response': [],
            'correct': [],
            'score': [],
            }
        print(d)
        df = pd.DataFrame(data = d)
        df.to_csv(log, mode='w', index = False)
    return(log)

def get_seq_num(LOG):
    log = pd.read_csv(LOG)
    seq_nums = log['seq_num']
    if len(seq_nums) == 0:
        seq_num = 0
    else:
        seq_num = seq_nums.iloc[-1]
    seq_num = int(seq_num)
    print(f"seq_num: {seq_num}")
    return(seq_num)

def get_score(LOG):
    log = pd.read_csv(LOG)
    scores = log['score']
    if len(scores) == 0:
        score = 0
    else:
        score = scores.iloc[-1]
    score = int(score)
    print(f"score: {score}")
    return(score)

def get_score_needed(BLOCK_NUM):
    if BLOCK_NUM == "0":
        score_needed = 3
    else:
        score_needed = 18
    return(score_needed)

def get_target(FREQS):
    target = random.choice(FREQS)
    print(f"target: {target}")
    return(target)

def get_n_tones(SEQ_LENS):
    n_tones = random.choice(SEQ_LENS)
    return(n_tones)

def fixation(WIN):
    fixation = visual.TextStim(WIN, '+')
    fixation.draw()
    WIN.flip()
    return(fixation)

def hear_pitches(WIN, TONE_LEN, FREQS):
    p1 = Sound(FREQS[0], secs = TONE_LEN)
    p2 = Sound(FREQS[1], secs = TONE_LEN)
    p3 = Sound(FREQS[2], secs = TONE_LEN)

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

def instructions(WIN):
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
    
def start(BLOCK_NUM, WIN, TONE_LEN, FREQS):
    if BLOCK_NUM == "0":
        hear_pitches(WIN, TONE_LEN, FREQS)
        instructions(WIN)
    else:
        welcome(WIN, BLOCK_NUM)

def welcome(WIN, BLOCK_NUM):
    blk_welcome = visual.TextStim(WIN,
                                  text = f"Welcome to block number {BLOCK_NUM}. Press 'enter' to continue.",
                                  pos=(0.0, 0.0),
                                  color=(1, 1, 1),
                                  colorSpace='rgb' )
    blk_welcome.draw()
    WIN.flip()
    event.waitKeys(keyList = ['return'])

def play_target(WIN, TONE_LEN, target):
    t_snd = Sound(target, secs = TONE_LEN)

    target_text = visual.TextStim(WIN,
                                  text = "Press 'space' to hear the target tone. Press 'enter' to continue",
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

def ready(WIN):
    block_begin = visual.TextStim(WIN,
                                  text = "Please count how many times you hear the target tone. Press 'enter' to begin!",
                                  pos=(0.0, 0.0),
                                  color=(1, 1, 1),
                                  colorSpace='rgb')
    block_begin.draw()
    WIN.flip()
    event.waitKeys(keyList = ['return'])
    WIN.flip()

def play_sequence(MARKER, FREQS, TONE_LEN, target, n_tones):
    n_targets = 0
    force = False
    one_back = 0
    two_back = 0

    # play first tone
    tone_nums, freqs, marks, is_targets = play_first_tone(MARKER, TONE_LEN, FREQS, target)

    for tone_num in range(2, n_tones + 1):
        print(tone_num, end = ', ', flush = True)

        # select tone
        if not force:
            i = random.randint(0, len(FREQS)-1)
        freq = FREQS[i]
        mark = get_mark(FREQS, i, target)
        snd = Sound(freq, secs = TONE_LEN)

        # increment
        is_target, n_targets = check_target(freq, target, n_targets)

        # schedule sound
        now = GetSecs()
        snd.play(when = now + 0.1)
        WaitSecs(0.1)
        MARKER.send(mark)
        WaitSecs(TONE_LEN - 0.1)

        # add jitter between tones
        WaitSecs(TONE_LEN + random.uniform(-0.1, 0))

        # save tone info
        tone_nums.append(tone_num)
        freqs.append(freq)
        marks.append(mark)
        is_targets.append(is_target)

        # check for repeats
        force, i, one_back, two_back = check_repeats(FREQS, freq, one_back, two_back)

    print('')
    print(f"n_targets: {n_targets}")
    return(tone_nums, freqs, marks, is_targets, n_targets)

def get_mark(FREQS, i, target):
    tone_mark = i + 1
    target_mark = FREQS.index(target) + 1
    mark = int(str(target_mark) + str(tone_mark))
    return(mark)

def play_first_tone(MARKER, TONE_LEN, FREQS, target):
    print('1', end = ', ', flush = True)

    drop = FREQS.index(target)
    indexes = [0, 1, 2]
    indexes.pop(drop)
    i = random.choice(indexes)
    freq = FREQS[i]
    mark = get_mark(FREQS, i, target)

    # schedule sound
    now = GetSecs()
    snd = Sound(freq, secs = TONE_LEN)
    snd.play(when = now + 0.1)
    WaitSecs(0.1)
    MARKER.send(mark)
    WaitSecs(TONE_LEN - 0.1)

    # Add jitter between tones
    WaitSecs(TONE_LEN + random.uniform(-0.1, 0))

    tone_nums = [1]
    freqs = [freq]
    marks = [mark]
    is_targets = [0]

    return(tone_nums, freqs, marks, is_targets)

def check_target(freq, target, n_targets):
    if freq == target:
        is_target = 1
        n_targets += 1
    else:
        is_target = 0
    return(is_target, n_targets)

def check_repeats(FREQS, freq, one_back, two_back):
    if freq == one_back == two_back:
        force = True
        drop = FREQS.index(freq)
        indexes = [0, 1, 2]
        indexes.pop(drop)
        i = random.choice(indexes)
    else:
        force = False
        i = None
    two_back = one_back
    one_back = freq
    return(force, i, one_back, two_back)

def broadcast(n_tones, var):
    if not isinstance(var, list):
        broadcasted_array = [var]*n_tones
    return(broadcasted_array)

def write_log(LOG, n_tones, SEED, SUB_NUM, BLOCK_NUM, seq_num, target, n_target_plays, tone_nums,
              freqs, marks, is_targets, n_targets, response, correct, score):
    print("Writing to log file")
    d = {
        'seed': broadcast(n_tones, SEED),
        'sub_num': broadcast(n_tones, SUB_NUM),
        'block_num': broadcast(n_tones, BLOCK_NUM),
        'seq_num': broadcast(n_tones, seq_num),
        'target': broadcast(n_tones, target),
        'n_target_plays': broadcast(n_tones, n_target_plays),
        'tone_num' : tone_nums,
        'freq': freqs,
        'mark': marks,
        'is_target': is_targets,
        'n_targets': broadcast(n_tones, n_targets),
        'response': broadcast(n_tones, response),
        'correct': broadcast(n_tones, correct),
        'score': broadcast(n_tones, score),
        }
    df = pd.DataFrame(data = d)
    df.to_csv(LOG, mode='a', header = False, index = False)

def get_response(WIN):
    # Prompt response
    ask_response = visual.TextStim(WIN,
                      text = "How many times did you hear the target tone?",
                      pos=(0.0, 0.0),
                      color=(1, 1, 1),
                      colorSpace='rgb')
    ask_response.draw()
    WIN.flip()

    # Fetch response
    keylist = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'return', 'backspace']
    response = []
    response_text = ''

    while True:
        keys = event.getKeys(keyList = keylist)
        if response_text and 'return' in keys: # empty response not accepted
            break
        elif keys:
            if 'return' in keys:
                None
            elif 'backspace' in keys:
                response = response[:-1]
            else:
                response.append(keys)
            response_text = ''.join([item for sublist in response for item in sublist])
            WIN.flip()
            show_response = visual.TextStim(WIN,
                                           text = response_text,
                                           pos=(0.0, 0.0),
                                           color=(1, 1, 1),
                                           colorSpace='rgb')
            show_response.draw()
            WIN.flip()

    response = int(response_text)
    print(f"response: {response}")
    return(response)

def update_score(WIN, n_targets, response, score, SCORE_NEEDED):
    if abs(n_targets - response) == 0:
        correct = 2
        score += 1
        update = visual.TextStim(WIN,
                  text = f"You are correct! There were {n_targets} targets. Your score is now {score}/{SCORE_NEEDED}. Press 'enter' to continue.",
                  pos=(0.0, 0.0),
                  color=(1, 1, 1),
                  colorSpace='rgb'
                 )
    elif abs(n_targets - response) <= 2:
        correct = 1
        score += 1
        update = visual.TextStim(WIN,
                  text = f"Close enough! There were {n_targets} targets. Your score is now {score}/{SCORE_NEEDED}. Press 'enter' to continue.",
                  pos=(0.0, 0.0),
                  color=(1, 1, 1),
                  colorSpace='rgb'
                 )
    else:
        correct = 0
        update = visual.TextStim(WIN,
                  text = f"There were {n_targets} targets. \
                  \
                  Your score remains {score}/{SCORE_NEEDED}. \
                  \
                  Press 'enter' to continue.",
                  pos=(0.0, 0.0),
                  color=(1, 1, 1),
                  colorSpace='rgb'
                 )

    update.draw()
    WIN.flip()

    event.waitKeys(keyList = ['return'])
    WIN.flip()

    print(f'score: {score}')
    return(correct, score)
