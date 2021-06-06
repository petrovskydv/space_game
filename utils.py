import asyncio
from itertools import cycle


def get_frame(filename):
    with open(filename, "r") as file:
        return file.read()


def get_garbage_frames():
    return [
        get_frame('frames/duck.txt'),
        get_frame('frames/hubble.txt'),
        get_frame('frames/lamp.txt'),
        get_frame('frames/trash_large.txt'),
        get_frame('frames/trash_small.txt'),
        get_frame('frames/trash_xl.txt'),
    ]


# TODO избавиться от захардкоженных путей

def ger_rocket_frames():
    frame1 = get_frame('frames/rocket_frame_1.txt')
    frame2 = get_frame('frames/rocket_frame_2.txt')
    return frame1, frame2


def get_cycle_frames(frame1, frame2):
    frames = [
        (frame1, frame2),
        (frame2, frame1)
    ]
    frames_cycle = cycle(frames)
    return frames_cycle


async def sleep(tics=1):
    for _ in range(tics):
        await asyncio.sleep(0)