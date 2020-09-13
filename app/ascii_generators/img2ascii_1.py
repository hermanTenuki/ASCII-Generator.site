from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from PIL import ImageEnhance
import string
import collections


def char_density(c):
    font = ImageFont.load_default()
    image = Image.new('1', font.getsize(c), color=255)
    draw = ImageDraw.Draw(image)
    draw.text((0, 0), c, font=font)
    return collections.Counter(image.getdata())[0]


def generate_art(image, width=None, height=None):
    chars = list(
        sorted(string.ascii_letters + string.digits + string.punctuation + ' ', key=char_density, reverse=True))
    char_width, char_height = ImageFont.load_default().getsize('X')
    width = width or image.size[0]
    height = int((height or image.size[1]) * char_width / float(char_height))
    image = image.resize((width, height), Image.ANTIALIAS).convert('L')
    pix = image.load()
    for y in range(height):
        for x in range(width):
            yield chars[int(pix[x, y] / 255. * (len(chars) - 1) + 0.5)]
        yield '\n'


def image_to_ascii(image_name, num_cols=100, brightness=None, contrast=None) -> str:
    image = Image.open(image_name)
    if num_cols is not None:
        scale = float(num_cols) / image.size[0]
    else:
        scale = 1
    if contrast is not None:
        image = ImageEnhance.Contrast(image).enhance(contrast)
    if brightness is not None:
        image = ImageEnhance.Brightness(image).enhance(brightness)
    return ''.join(generate_art(image, int(image.size[0] * scale), int(image.size[1] * scale)))
