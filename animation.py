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
NEXT_ROW = 15
NEXT_COLUMN = 40


async def blink(canvas, row, column, symbol='*', timeout=1):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        for _ in range(timeout * random.randint(1, 2)):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(int(timeout * 0.3)):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        for _ in range(int(timeout * 0.5)):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(int(timeout * 0.3)):
            await asyncio.sleep(0)


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


async def animate_spaceship(canvas, iterator, timeout=1):
    multiplier = 0.7
    rows_number, columns_number = canvas.getmaxyx()

    while True:

        rows_direction, columns_direction, space_pressed = read_controls(canvas)
        global ROW, COLUMN
        row, column = ROW, COLUMN

        frame1, frame2 = next(iterator)

        draw_frame(canvas, row, column, frame1, negative=True)

        frame_rows_number, frame_columns_number = get_frame_size(frame1)

        next_start_row = ROW+rows_direction
        next_start_column = COLUMN+columns_direction

        if rows_number>next_start_row+frame_rows_number and next_start_row>0:
            ROW += rows_direction
        if columns_number>next_start_column+frame_columns_number and next_start_column>0:
            COLUMN += columns_direction

        row, column = ROW, COLUMN

        draw_frame(canvas, row, column, frame2)
        for _ in range(int(timeout * multiplier)):
            await asyncio.sleep(0)


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


