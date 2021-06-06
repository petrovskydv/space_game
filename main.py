import curses
import random

from animation import blink, animate_spaceship, fill_orbit_with_garbage
from utils import get_garbage_frames, ger_rocket_frames, get_cycle_frames

TIC_TIMEOUT = 1000
STARS_NUMBER = 100
ORBIT_GARBAGE_COROUTINES = []
FIRE_COROUTINES = []
OBSTACLES_COROUTINES = []


def draw(canvas):
    curses.curs_set(False)
    canvas.border()
    canvas.nodelay(True)

    height, width = canvas.getmaxyx()
    before_border_row = height - 2
    before_border_column = width - 2
    stars = '+*.:'

    garbage_frames = get_garbage_frames()
    frames_cycle = get_cycle_frames(*ger_rocket_frames())

    global FIRE_COROUTINES
    spaceship_coroutine = animate_spaceship(canvas, frames_cycle, fire_coroutines=FIRE_COROUTINES, timeout=TIC_TIMEOUT)

    stars_coroutines = [blink(canvas, random.randint(1, before_border_row), random.randint(1, before_border_column),
                              symbol=random.choice(stars), timeout=TIC_TIMEOUT) for _ in range(1, STARS_NUMBER)]

    global ORBIT_GARBAGE_COROUTINES
    garbage_coroutines = fill_orbit_with_garbage(ORBIT_GARBAGE_COROUTINES, OBSTACLES_COROUTINES, canvas, garbage_frames,
                                                 max_column=before_border_column, timeout=TIC_TIMEOUT)

    while True:

        for star_coroutine in stars_coroutines:
            star_coroutine.send(None)

        spaceship_coroutine.send(None)
        garbage_coroutines.send(None)

        for fire_coroutine in FIRE_COROUTINES.copy():
            try:
                fire_coroutine.send(None)
            except StopIteration:
                FIRE_COROUTINES.remove(fire_coroutine)

        for garbage_coroutine in ORBIT_GARBAGE_COROUTINES.copy():
            try:
                garbage_coroutine.send(None)
            except StopIteration:
                ORBIT_GARBAGE_COROUTINES.remove(garbage_coroutine)

        for obstacle_coroutine in OBSTACLES_COROUTINES.copy():
            try:
                obstacle_coroutine.send(None)
            except StopIteration:
                OBSTACLES_COROUTINES.remove(obstacle_coroutine)

        canvas.border()
        canvas.refresh()


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
