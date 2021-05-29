import curses
import random
from itertools import cycle

from animation import blink, fire, animate_spaceship, fly_garbage
from utils import get_frame

TIC_TIMEOUT = 5000
STARS_NUMBER = 100


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
    garbage_frame = get_frame('frames/duck.txt')

    frames = [
        (frame1, frame2),
        (frame2, frame1)
    ]
    frames_cycle = cycle(frames)

    spaceship_coroutine = animate_spaceship(canvas, frames_cycle, timeout=TIC_TIMEOUT)

    stars_coroutines = [blink(canvas, random.randint(1, before_border_row), random.randint(1, before_border_column),
                              symbol=random.choice(stars), timeout=TIC_TIMEOUT) for _ in range(1, STARS_NUMBER)]

    fire_coroutines = [fire(canvas, before_border_row, fire_row_number)]

    garbage_coroutines = [fly_garbage(canvas, column=10, garbage_frame=garbage_frame, timeout=TIC_TIMEOUT)]

    while True:

        for star_coroutine in stars_coroutines:
            star_coroutine.send(None)

        spaceship_coroutine.send(None)

        for fire_coroutine in fire_coroutines.copy():
            try:
                fire_coroutine.send(None)
            except StopIteration:
                fire_coroutines.remove(fire_coroutine)

        for garbage_coroutine in garbage_coroutines.copy():
            try:
                garbage_coroutine.send(None)
            except StopIteration:
                garbage_coroutines.remove(garbage_coroutine)

        canvas.border()
        canvas.refresh()


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
