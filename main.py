import curses
import random
from itertools import cycle

from animation import blink, fire, animate_spaceship, fill_orbit_with_garbage
from utils import get_frame

TIC_TIMEOUT = 5000
STARS_NUMBER = 100
ORBIT_GARBAGE_COROUTINES = []


def draw(canvas):
    curses.curs_set(False)
    canvas.border()
    canvas.nodelay(True)

    height, width = canvas.getmaxyx()
    before_border_row = height - 2
    before_border_column = width - 2
    stars = '+*.:'
    fire_row_number = 10

    frame1 = get_frame('frames/rocket_frame_1.txt')
    frame2 = get_frame('frames/rocket_frame_2.txt')
    garbage_frames = [
        get_frame('frames/duck.txt'),
        get_frame('frames/hubble.txt'),
        get_frame('frames/lamp.txt'),
        get_frame('frames/trash_large.txt'),
        get_frame('frames/trash_small.txt'),
        get_frame('frames/trash_xl.txt'),
    ]

    frames = [
        (frame1, frame2),
        (frame2, frame1)
    ]
    frames_cycle = cycle(frames)

    spaceship_coroutine = animate_spaceship(canvas, frames_cycle, timeout=TIC_TIMEOUT)

    stars_coroutines = [blink(canvas, random.randint(1, before_border_row), random.randint(1, before_border_column),
                              symbol=random.choice(stars), timeout=TIC_TIMEOUT) for _ in range(1, STARS_NUMBER)]

    fire_coroutines = [fire(canvas, before_border_row, fire_row_number)]

    global ORBIT_GARBAGE_COROUTINES
    garbage_coroutines = fill_orbit_with_garbage(ORBIT_GARBAGE_COROUTINES, canvas, garbage_frames,
                                                 max_column=before_border_column, timeout=TIC_TIMEOUT)

    while True:

        for star_coroutine in stars_coroutines:
            star_coroutine.send(None)

        spaceship_coroutine.send(None)
        garbage_coroutines.send(None)

        for fire_coroutine in fire_coroutines.copy():
            try:
                fire_coroutine.send(None)
            except StopIteration:
                fire_coroutines.remove(fire_coroutine)

        for garbage_coroutine in ORBIT_GARBAGE_COROUTINES.copy():
            try:
                garbage_coroutine.send(None)
            except StopIteration:
                ORBIT_GARBAGE_COROUTINES.remove(garbage_coroutine)

        canvas.border()
        canvas.refresh()


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
