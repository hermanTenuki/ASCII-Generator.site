import argparse
import cv2
import numpy as np
from PIL import Image
from PIL import ImageEnhance
from numba import jit as _jit
from django.conf import settings


def jit():
    def wrapped(func, *args, **kwargs):
        if not settings.NUMBA:
            return func
        else:
            return _jit(func, *args, **kwargs)
    return wrapped


@jit()
def get_sizes(image, num_cols):
    height, width = image.shape
    cell_width = width / num_cols
    cell_height = 2 * cell_width
    num_rows = int(height / cell_height)
    return height, width, cell_width, cell_height, num_rows


@jit()
def image_to_ascii(path, num_cols=100, mode='complex', brightness=None, contrast=None) -> (str, int):
    if mode == "simple":
        CHAR_LIST = '@%#*+=-:. '
    elif mode == "bars":
        CHAR_LIST = '█▓▒░'
    else:
        CHAR_LIST = "$@B%8&WM#*zcvunxrjft/\|()1{}[]?-_+~<>i!lI;;::,,,\"\"\"^^^`````'''''.......     "
    num_chars = len(CHAR_LIST)
    image = Image.open(path)
    if contrast is not None:
        image = ImageEnhance.Contrast(image).enhance(contrast)
    if brightness is not None:
        image = ImageEnhance.Brightness(image).enhance(brightness)
    image = np.array(image)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    height, width, cell_width, cell_height, num_rows = get_sizes(image, num_cols)
    output_str = ''
    for i in range(num_rows):
        for j in range(num_cols):
            output_str += CHAR_LIST[min(int(np.mean(image[int(i * cell_height):min(int((i + 1) * cell_height), height),
                                                    int(j * cell_width):min(int((j + 1) * cell_width),
                                                                            width)]) * num_chars / 255), num_chars - 1)]
        output_str += '\n'
    return output_str
