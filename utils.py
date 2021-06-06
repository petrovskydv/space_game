import asyncio
import glob
from itertools import cycle


def get_frame(filename):
    with open(filename, "r") as file:
        return file.read()


def get_frames(folder_path):
    images_paths = glob.glob(f'{folder_path}*.txt')
    return [get_frame(file_path) for file_path in images_paths]


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
