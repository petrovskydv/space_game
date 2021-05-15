import curses
import random
from itertools import cycle

from animation import blink, fire, animate_spaceship
from utils import get_frame

TIC_TIMEOUT = 500
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

    frames = [
        (frame1, frame2),
        (frame2, frame1)
    ]
    frames_iterator = cycle(frames)

    spaceship_coroutine = animate_spaceship(canvas, frames_iterator, timeout=TIC_TIMEOUT)

    stars_coroutines = [blink(canvas, random.randint(1, before_border_row), random.randint(1, before_border_column),
                              symbol=random.choice(stars), timeout=TIC_TIMEOUT) for _ in range(1, STARS_NUMBER)]

    fire_coroutines = [fire(canvas, before_border_row, fire_row_number)]

    while True:

        for star_coroutine in stars_coroutines:
            star_coroutine.send(None)
            # canvas.refresh()

        spaceship_coroutine.send(None)
        # canvas.refresh()

        for fire_coroutine in fire_coroutines.copy():
            try:
                fire_coroutine.send(None)
                # canvas.refresh()
            except StopIteration:
                fire_coroutines.remove(fire_coroutine)
                canvas.border()
        canvas.refresh()

if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
