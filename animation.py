import asyncio
import curses
import random

SPACE_KEY_CODE = 32
LEFT_KEY_CODE = 260
RIGHT_KEY_CODE = 261
UP_KEY_CODE = 259
DOWN_KEY_CODE = 258

ROW = 1
COLUMN = 40


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



async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
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
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


def draw_frame(canvas, start_row, start_column, text, negative=False):
    """Draw multiline text fragment on canvas, erase text instead of drawing if negative=True is specified."""

    rows_number, columns_number = canvas.getmaxyx()

    for row, line in enumerate(text.splitlines(), round(start_row)):
        if row < 0:
            continue

        if row >= rows_number:
            break

        for column, symbol in enumerate(line, round(start_column)):
            if column < 0:
                continue

            if column >= columns_number:
                break

            if symbol == ' ':
                continue

            # Check that current position it is not in a lower right corner of the window
            # Curses will raise exception in that case. Don`t ask why…
            # https://docs.python.org/3/library/curses.html#curses.window.addch
            if row == rows_number - 1 and column == columns_number - 1:
                continue

            symbol = symbol if not negative else ' '
            canvas.addch(row, column, symbol)


async def animate_spaceship(canvas, frames_cycle, timeout=1):
    multiplier = 0.7
    rows_number, columns_number = canvas.getmaxyx()

    while True:

        rows_direction, columns_direction, space_pressed = read_controls(canvas)
        global ROW, COLUMN

        current_frame, next_frame = next(frames_cycle)

        draw_frame(canvas, ROW, COLUMN, current_frame, negative=True)

        frame_rows_number, frame_columns_number = get_frame_size(next_frame)

        next_start_row = ROW + rows_direction
        next_start_column = COLUMN + columns_direction

        if rows_number > next_start_row + frame_rows_number and next_start_row > 0:
            ROW = next_start_row
        if columns_number > next_start_column + frame_columns_number and next_start_column > 0:
            COLUMN = next_start_column

        draw_frame(canvas, ROW, COLUMN, next_frame)
        await sleep(int(timeout * multiplier))


def read_controls(canvas):
    """Read keys pressed and returns tuple with controls state."""

    rows_direction = columns_direction = 0
    space_pressed = False

    while True:
        pressed_key_code = canvas.getch()

        if pressed_key_code == -1:
            # https://docs.python.org/3/library/curses.html#curses.window.getch
            break

        if pressed_key_code == UP_KEY_CODE:
            rows_direction = -1

        if pressed_key_code == DOWN_KEY_CODE:
            rows_direction = 1

        if pressed_key_code == RIGHT_KEY_CODE:
            columns_direction = 1

        if pressed_key_code == LEFT_KEY_CODE:
            columns_direction = -1

        if pressed_key_code == SPACE_KEY_CODE:
            space_pressed = True

    return rows_direction, columns_direction, space_pressed


def get_frame_size(text):
    """Calculate size of multiline text fragment, return pair — number of rows and colums."""

    lines = text.splitlines()
    rows = len(lines)
    columns = max([len(line) for line in lines])
    return rows, columns


async def fly_garbage(canvas, column, garbage_frame, speed=0.5, timeout=1):
    """Animate garbage, flying from top to bottom. Сolumn position will stay same, as specified on start."""
    rows_number, columns_number = canvas.getmaxyx()

    column = max(column, 0)
    column = min(column, columns_number - 1)

    row = 0

    while row < rows_number:
        draw_frame(canvas, row, column, garbage_frame)
        await sleep(int(timeout * 0.2))
        draw_frame(canvas, row, column, garbage_frame, negative=True)
        row += speed


async def fill_orbit_with_garbage(garbage_coroutines, canvas, garbage_frames, max_column, timeout=1):
    while True:
        garbage_coroutines.append(
            fly_garbage(
                canvas,
                column=random.randint(1, max_column),
                garbage_frame=random.choice(garbage_frames),
                timeout=timeout
            )
        )
        await sleep(int(timeout * 5))


async def sleep(tics=1):
    for _ in range(tics):
        await asyncio.sleep(0)
