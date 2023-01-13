from cedrus.cedrus import RBx20
from events import EventMarker
from psychtoolbox import GetSecs, WaitSecs
from functions import *

serial = 'FTCGRG4Q'
BOX = RBx20(serial)

WIN = get_window()

text = visual.TextStim(WIN, text = "+")
text.draw()
WIN.flip()

key, rt = BOX.waitKeys(timeout = 2)
print(key, rt)
if rt != None:
	WaitSecs(2 - rt)

text = visual.TextStim(WIN, text = "wait")
text.draw()
WIN.flip()

WaitSecs(4)

text = visual.TextStim(WIN, text = "+")
text.draw()
WIN.flip()

key, rt = BOX.waitKeys(timeout = 2)
print(key, rt)
if rt != None:
	WaitSecs(2 - rt)

WIN.flip()

