import asyncio
import curses
import random
import uuid

from curses_tools import draw_frame, get_frame_size, read_controls
from explosion import explode
from game_scenario import get_garbage_delay_tics
from obstacles import Obstacle
from physics import update_speed
from utils import sleep

ROW = 15
COLUMN = 40
OBSTACLES = []
OBSTACLES_IN_LAST_COLLISIONS = []
GAME_OVER = False
CURRENT_YEAR = 1956


async def blink(canvas, row, column, symbol='*', timeout=1):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await sleep(timeout * random.randint(1, 2))

        canvas.addstr(row, column, symbol)
        await sleep(int(timeout * 0.3))

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await sleep(int(timeout * 0.5))

        canvas.addstr(row, column, symbol)
        await sleep(int(timeout * 0.3))


async def timer(canvas):
    global CURRENT_YEAR
    while True:
        CURRENT_YEAR += 1
        draw_frame(canvas, 1, 1, str(CURRENT_YEAR))
        await sleep(10000)


async def fire(canvas, start_row, start_column, rows_speed=-0.1, columns_speed=0):
    """Display animation of gun shot, direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await sleep(20)
        canvas.addstr(round(row), round(column), ' ')
        for obstacle in OBSTACLES:
            if obstacle.has_collision(round(row), round(column)):
                global OBSTACLES_IN_LAST_COLLISIONS
                OBSTACLES_IN_LAST_COLLISIONS.append(obstacle)
                return
        row += rows_speed
        column += columns_speed


async def animate_spaceship(canvas, frames_cycle, fire_coroutines, timeout=1):
    multiplier = 0.7
    rows_number, columns_number = canvas.getmaxyx()
    row_speed = column_speed = 0

    while True:

        rows_direction, columns_direction, space_pressed = read_controls(canvas)

        global ROW, COLUMN, GAME_OVER

        current_frame, next_frame = next(frames_cycle)
        draw_frame(canvas, ROW, COLUMN, current_frame, negative=True)

        frame_rows_number, frame_columns_number = get_frame_size(next_frame)

        if space_pressed:
            fire_coroutines.append(fire(canvas, ROW, COLUMN + frame_columns_number / 2))

        for obstacle in OBSTACLES:
            if obstacle.has_collision(ROW, COLUMN + frame_columns_number / 2):
                GAME_OVER = True

        row_speed, column_speed = update_speed(row_speed, column_speed, rows_direction, columns_direction)
        next_start_row = ROW + rows_direction + row_speed
        next_start_column = COLUMN + columns_direction + column_speed

        if rows_number > next_start_row + frame_rows_number and next_start_row > 0:
            ROW = next_start_row
        if columns_number > next_start_column + frame_columns_number and next_start_column > 0:
            COLUMN = next_start_column

        draw_frame(canvas, ROW, COLUMN, next_frame)

        await sleep(int(timeout * multiplier))


async def fly_garbage(canvas, column, garbage_frame, explode_coroutines, speed=0.5, timeout=1, obstacle=None):
    """Animate garbage, flying from top to bottom. Column position will stay same, as specified on start."""
    rows_number, columns_number = canvas.getmaxyx()

    column = max(column, 0)
    column = min(column, columns_number - 1)

    row = 0

    global OBSTACLES_IN_LAST_COLLISIONS, OBSTACLES

    while row < rows_number:
        draw_frame(canvas, row, column, garbage_frame)
        await sleep(int(timeout * 0.2))
        draw_frame(canvas, row, column, garbage_frame, negative=True)
        obstacle.row = row
        obstacle.column = column
        row += speed

        if obstacle in OBSTACLES_IN_LAST_COLLISIONS:
            OBSTACLES_IN_LAST_COLLISIONS.remove(obstacle)
            explode_coroutines.append(
                explode(
                    canvas,
                    row + obstacle.rows_size / 2,
                    column + obstacle.columns_size / 2)
            )
            row = rows_number
    else:
        OBSTACLES.remove(obstacle)


async def fill_orbit_with_garbage(garbage_coroutines, obstacles_coroutines, explode_coroutines, canvas, garbage_frames,
                                  max_column, timeout=1):
    while True:
        frame = random.choice(garbage_frames)
        frame_rows_number, frame_columns_number = get_frame_size(frame)

        frame_column = random.randint(1, max_column - frame_columns_number)
        frame_uid = uuid.uuid4()

        global OBSTACLES
        obstacle = Obstacle(
            1,
            frame_column,
            frame_rows_number,
            frame_columns_number,
            uid=frame_uid
        )
        OBSTACLES.append(obstacle)

        garbage_coroutines.append(
            fly_garbage(
                canvas,
                column=frame_column,
                garbage_frame=frame,
                explode_coroutines=explode_coroutines,
                timeout=timeout,
                obstacle=obstacle
            )
        )

        delay = get_garbage_delay_tics(CURRENT_YEAR)
        await sleep(timeout * (delay if delay else 30))


def check_game_over():
    return GAME_OVER
