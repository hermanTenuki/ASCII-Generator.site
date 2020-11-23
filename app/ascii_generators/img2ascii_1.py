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


ASCII_CHARS = ['.', ',', ':', ';', '+', '*', '?', '%', 'S', '#', '@']
ASCII_CHARS = ASCII_CHARS[::-1]


@jit()
def resize(image, new_width):
    (old_width, old_height) = image.size
    aspect_ratio = float(old_height) / float(old_width)
    new_height = int(aspect_ratio * (new_width / 2))
    new_dim = (new_width, new_height)
    new_image = image.resize(new_dim)
    return new_image


@jit()
def grayscalify(image):
    return image.convert('L')


@jit()
def modify(image, buckets=25):
    initial_pixels = list(image.getdata())
    new_pixels = [ASCII_CHARS[pixel_value // buckets] for pixel_value in initial_pixels]
    return ''.join(new_pixels)


@jit()
def do(image, new_width):
    image = resize(image, new_width)
    image = grayscalify(image)

    pixels = modify(image)
    len_pixels = len(pixels)

    # Construct the image from the character list
    new_image = [pixels[index:index + new_width] for index in range(0, len_pixels, new_width)]

    return '\n'.join(new_image)


def image_to_ascii(path, num_cols=100, brightness=None, contrast=None) -> str:
    image = None
    try:
        image = Image.open(path)
    except Exception:
        return
    if contrast is not None:
        image = ImageEnhance.Contrast(image).enhance(contrast)
    if brightness is not None:
        image = ImageEnhance.Brightness(image).enhance(brightness)
    image = do(image, num_cols)
    return image
