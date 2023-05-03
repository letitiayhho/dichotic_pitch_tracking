import mne
import os
import glob
import numpy as np
import pandas as pd

def add_stream_to_event_tags(events, sub):
    # Get marks and streams
    tags = get_tags(events)
    marks, streams = get_marks_and_streams_from_log_file(sub)

    # Find diff between marks and tags
    diffs = diff(marks, tags)
    indexes_to_drop_from_marks, indexes_to_drop_from_tags = get_drop_indexes(diffs)
    marks = apply_diff(marks, indexes_to_drop_from_marks)
    tags = apply_diff(tags, indexes_to_drop_from_tags)

    # Check
    if tags != marks:
        raise ValueError('Event tags do not match log file tags!')
    else:
        print('Successfully matched marks and tags :-)')

    # Now apply the diffs the list of stream sides
    streams = apply_diff(streams, indexes_to_drop_from_marks)

    # Now add streams to event tags
    hier_tags = make_tags_hierarchical(streams, tags)
    
    # Now make original events object match the new tags
    events = apply_diff(events.tolist(), indexes_to_drop_from_tags)
#     events = np.array(events)

    # Now add hierarchical tags to events object
    hier_events = add_hierarchical_tags_to_events(events, hier_tags)
    hier_events = np.array(hier_events)
    
    return hier_events

def get_drop_indexes(diffs):
    indexes_to_drop_from_tags = []
    indexes_to_drop_from_marks = []

    for i, diff in enumerate(diffs):
        change = diff[0]
        if change == 'addition': # tag is found in tags but not in marks
            indexes_to_drop_from_tags.append(i)
        elif change == 'removal':
            indexes_to_drop_from_marks.append(i)
    
    return indexes_to_drop_from_marks, indexes_to_drop_from_tags

def apply_diff(l, indexes):
    for index in sorted(indexes, reverse=True):
        del l[index]
    return l

def compute_lcs_len(text1, text2):
    """Computes a table of f(i, j) results."""
    n = len(text1)
    m = len(text2)

    # We store the results in a (n + 1) x (m + 1) matrix. The +1s are to
    # allocate space for the empty strings. Cell [i][j] will cache the
    # result of f(i, j).
    lcs = [[None for _ in range(m + 1)]
               for _ in range(n + 1)]

    # We then fill the matrix by going through all rows, using the fact
    # that each call only needs results from the previous (i - 1) or
    # same (i) row, and from the previous (j - 1) or same (j) column.
    for i in range(0, n + 1):
        for j in range(0, m + 1):
          # The remaining code is exactly the same recursion as before, but
          # we do not make recursive calls and instead use the results cached
          # in the matrix.
            if i == 0 or j == 0:
                lcs[i][j] = 0
            elif text1[i - 1] == text2[j - 1]:
                lcs[i][j] = 1 + lcs[i - 1][j - 1]
            else:
                lcs[i][j] = max(lcs[i - 1][j], lcs[i][j - 1])

    return lcs

def diff(text1, text2):
    """Computes the optimal diff of the two given inputs.

    The result is a list where all elements are Removals, Additions or
    Unchanged elements.
    """
    lcs = compute_lcs_len(text1, text2)
    results = []

    text1 = list(text1)
    text2 = list(text2)
    
    i = len(text1)
    j = len(text2)

  # We iterate until we reach the end of both texts.
    while i != 0 or j != 0:
        # If we reached the end of one of text1 (i == 0) or text2 (j == 0),
        # then we just need to print the remaining additions and removals.
        if i == 0:
            results.append(('addition', text2[j - 1]))
            j -= 1
        elif j == 0:
            results.append(('removal', text1[i - 1]))
            i -= 1
        # Otherwise there's still parts of text1 and text2 left. If the
        # currently considered parts are equal, then we found an unchanged
        # part which belongs to the longest common subsequence.
        elif text1[i - 1] == text2[j - 1]:
            results.append(('unchanged', text1[i - 1]))
            i -= 1
            j -= 1
        # In any other case, we go in the direction of the longest common
        # subsequence.
        elif lcs[i - 1][j] <= lcs[i][j - 1]:
            results.append(('addition', text2[j - 1]))
            j -= 1
        else:
            results.append(('removal', text1[i - 1]))
            i -= 1

    # Reverse results because we iterated over the texts from the end but
    # want the results to be in forward order.
    return list(reversed(results))

def get_tags(events):
    tags = []
    for i in range(1, len(events)):
        tags.append(events[i][2])
    return tags
    
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
    marks = list(logs.mark)
    streams = logs.stream

    return marks, streams

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

    return hier_tags

def add_hierarchical_tags_to_events(events, hier_tags):
    hier_events = []
    for i in range(0, len(events)):
        hier_event = list(events[i])
        hier_event[2] = hier_tags[i]
        hier_events.append(hier_event)
    return hier_events