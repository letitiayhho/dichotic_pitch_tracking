import mne
import os
import glob
import pandas as pd

def add_stream_to_event_tags(events, sub):

    # Extract event tags
    tags = []
    for i in range(1, len(events)):
        tags.append(events[i][2])
        
    # Get marks from log files
    marks, streams = get_marks_and_streams_from_log_file(sub)

    # Find the indexes that match event and log tags up
    window = 20
    tags_i, marks_i = get_index_of_match(tags, marks, window)

    # Trim marks to match event tags
    start_i = marks_i
    end_i = marks_i + len(tags)
    marks = marks[start_i:end_i]
    streams = streams[start_i:end_i]

    # Add stream to tag
    hier_tags = make_tags_hierarchical(streams, tags)

    # Add hierarchical tags to events object
    hier_events = add_hierarchical_tags_to_events(events, hier_tags)

    return(hier_events)
        
def get_marks_and_streams_from_log_file(sub):
    # Get events from log files
    log_dir = '../data/logs'
    logs = pd.DataFrame()

    for fpath in list(glob.glob(f'{log_dir}/sub-{sub}_*.log')):
        print(fpath)

        # checking if it is a file
        if os.path.isfile(fpath):
            log = pd.read_csv(fpath)
            logs = pd.concat([logs, log])

    logs = logs.sort_values(by = ['block_num', 'seq_num', 'tone_num'])
    logs = logs.reset_index()
    marks = logs.mark
    streams = logs.stream

    return(marks, streams)

def check(tags, marks, tags_i, marks_i, score):
    if tags[tags_i] == marks[marks_i]:
        score += 1
        tags_i += 1
        marks_i += 1
    else:
        tags_i = tags_i - score
        marks_i += 1
        score = 0
    return(tags_i, marks_i, score)

def get_index_of_match(tags, marks, window):
    for tags_i in range(len(tags) - window):
        for marks_i in range(len(marks) - window):
            tags_set = tuple(tags[tags_i:tags_i+window])
            marks_set = tuple(marks[marks_i:marks_i+window])
            if tags_set == marks_set:
                print(f'Match found! tags_i: {tags_i}; marks_i: {marks_i}')
                print(f'tags_set: {tags_set}')
                print(f'marks_set: {marks_set}')
                found = True
                break
        if found:
            break

    if not found:
        raise ValueError('No match found!')
    if tuple(tags[tags_i:len(tags)]) != tuple(marks[marks_i:marks_i + len(tags)]): # length of marks will always >= length of tags
        raise ValueError('Event tags do not match log file tags!')
    return(tags_i, marks_i)

def make_tags_hierarchical(streams, tags):

    # Change stream string value from 'r' and 'l' into 1 and 2
    stream_tag = streams.replace(['r', 'l'], [1, 2])
    stream_tag = list(stream_tag)

    # Concat stream tags with event tags
    hier_tags = []
    hier_tags.insert(0, 99999)
    for stream, tag in zip(stream_tag, tags):
        hier_tag = int(str(stream) + str(tag))
        hier_tags.append(hier_tag)

    return(hier_tags)

def add_hierarchical_tags_to_events(events, hier_tags):
    hier_events = []
    for i in range(0, len(events)):
        hier_event = list(events[i])
        hier_event[2] = hier_tags[i]
        hier_events.append(hier_event)
    return(hier_events)