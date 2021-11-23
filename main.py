import curses
import random

from animation import blink, animate_spaceship, fill_orbit_with_garbage, check_game_over, timer
from common import coroutines
from curses_tools import show_gameover
from utils import get_frames, get_cycle_frames

TIC_TIMEOUT = 3000
STARS_NUMBER = 100


def draw(canvas):
    curses.curs_set(False)
    canvas.border()
    canvas.nodelay(True)

    height, width = canvas.getmaxyx()
    before_border_row = height - 2
    before_border_column = width - 2
    stars = '+*.:'
    garbage_folder_path = 'frames/garbage/'
    rocket_folder_path = 'frames/rocket/'

    garbage_frames = get_frames(garbage_folder_path)
    frames_cycle = get_cycle_frames(*get_frames(rocket_folder_path))

    spaceship_coroutine = animate_spaceship(canvas, frames_cycle, timeout=TIC_TIMEOUT)

    timer_coroutine = timer(canvas)

    stars_coroutines = [blink(canvas, random.randint(1, before_border_row), random.randint(1, before_border_column),
                              symbol=random.choice(stars), timeout=TIC_TIMEOUT) for _ in range(1, STARS_NUMBER)]

    garbage_coroutines = fill_orbit_with_garbage(
        canvas,
        garbage_frames,
        max_column=before_border_column,
        timeout=TIC_TIMEOUT
    )

    coroutines.append(spaceship_coroutine)
    coroutines.append(timer_coroutine)
    coroutines.append(garbage_coroutines)
    coroutines.extend(stars_coroutines)

    while True:
        if check_game_over():
            show_gameover(canvas)
            canvas.refresh()
        else:

            for star_coroutine in coroutines:
                try:
                    star_coroutine.send(None)
                except StopIteration:
                    coroutines.remove(star_coroutine)

            canvas.border()
            canvas.refresh()


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
