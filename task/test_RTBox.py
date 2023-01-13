from events import EventMarker
from psychtoolbox import GetSecs, WaitSecs
from functions import *

WIN = get_window()
MARKER = EventMarker()
BOX1 = init_RTBox(MARKER)
BOX2 = init_RTBox(MARKER)
BOX2.buttonNames(['2', '2', '2', '2'])

BOX1.clear()
BOX2.clear()

text = visual.TextStim(WIN, text = "+")
text.draw()
WIN.flip()

t0 = GetSecs()
while not timeout:
    (secs, btns) = BOX2.secs(5)
rt = secs[0] - t0
print(rt, btns)

WIN.flip()

WaitSecs(2)

text = visual.TextStim(WIN, text = "+")
text.draw()
WIN.flip()

t0 = GetSecs()
(secs, btns) = BOX2.secs(5)
rt = secs[0] - t0
print(rt, btns)

WIN.flip()

BOX1.close()
BOX2.close()
