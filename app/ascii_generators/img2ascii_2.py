import argparse
import cv2
import numpy as np
from PIL import Image
from PIL import ImageEnhance

def image_to_ascii(image_name, num_cols=100, mode='complex', brightness=None, contrast=None) -> str:
    if mode == "simple":
        CHAR_LIST = '@%#*+=-:. '
    elif mode == "bars":
        CHAR_LIST = '█▓▒░'
    else:
        CHAR_LIST = "$@B%8&WM#*zcvunxrjft/\|()1{}[]?-_+~<>i!lI;;::,,,\"\"\"^^^`````'''''.......        "
    num_chars = len(CHAR_LIST)
    image = Image.open(image_name)
    if contrast is not None:
        image = ImageEnhance.Contrast(image).enhance(contrast)
    if brightness is not None:
        image = ImageEnhance.Brightness(image).enhance(brightness)
    image = np.array(image)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    height, width = image.shape
    cell_width = width / num_cols
    cell_height = 2 * cell_width
    num_rows = int(height / cell_height)
    if num_cols > width or num_rows > height:
        cell_width = 6
        cell_height = 12
        num_cols = int(width / cell_width)
        num_rows = int(height / cell_height)
    output_str = ''
    for i in range(num_rows):
        for j in range(num_cols):
            output_str += CHAR_LIST[min(int(np.mean(image[int(i * cell_height):min(int((i + 1) * cell_height), height),
                                          int(j * cell_width):min(int((j + 1) * cell_width),
                                                                  width)]) * num_chars / 255), num_chars - 1)]
        output_str += '\n'
    return output_str
