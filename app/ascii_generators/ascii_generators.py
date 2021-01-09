from . import img2ascii_1, img2ascii_2, txt2ascii_1
import random
import string
import numpy as np
import cv2
from PIL import Image
from django.http import JsonResponse
import os
from django.conf import settings
import threading


def _calculate_num_cols(path: str, num_cols: int) -> int:
    """
    Recursive function to calculate biggest optimal num_cols for small images.
    :return: num_cols.
    """
    image = Image.open(path)
    image = np.array(image)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    height, width = image.shape
    cell_width = width / num_cols
    cell_height = 2 * cell_width
    num_rows = int(height / cell_height)
    if num_cols > width or num_rows > height:
        num_cols -= 1
        num_cols = _calculate_num_cols(path, num_cols)
    return num_cols


def _generate_unique_image_path(file_extension, r=0, r_max=10):
    """
    Recursive function that generates random unique file name and path.
    :return: Full path to file, name with extension.
    """
    # Random name to image
    name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=30))  # 30 symbols for security
    # Making file name
    full_name = f'{name}{file_extension}'
    # Making path
    full_path = os.path.join(settings.TEMPORARY_IMAGES, full_name)
    # Checking if it already exist
    if os.path.exists(full_path):
        if r >= r_max:
            return None, None
        full_path, full_name = _generate_unique_image_path(file_extension, r=r + 1)  # Recursion
    return full_path, full_name


def _generator_thread_1_hub(l, args, kwargs, kwargs1, kwargs2):  # custom args/kwargs, others not accepted
    art1 = img2ascii_2.image_to_ascii(*args, **kwargs, **kwargs1)
    art2 = img2ascii_2.image_to_ascii(*args, **kwargs, **kwargs2)
    l[0], l[1] = art1, art2  # mutable list, return is not needed


def _generator_thread_2_hub(l, args, kwargs):
    art1 = img2ascii_2.image_to_ascii(*args, **kwargs)
    art2 = img2ascii_1.image_to_ascii(*args, **kwargs)
    l[0], l[1] = art1, art2


def image_to_ascii_generator(request):
    """
    Generate ascii from image.
    :param request: Request with data.
    :return: JsonResponse in case of error or dictionary with "file_name", "num_cols", "brightness", "contrast" and "arts".
    """
    file_name = request.POST.get('file_name', None)
    num_cols = request.POST.get('num_cols', 90)
    brightness = request.POST.get('brightness', 100)
    contrast = request.POST.get('contrast', 100)

    # Validating user's input
    try:
        brightness = float(brightness) / 100
    except:
        brightness = 1
    try:
        contrast = float(contrast) / 100
    except:
        contrast = 1
    try:
        num_cols = int(num_cols)
    except:
        num_cols = 90
    if num_cols > 300:
        num_cols = 300
    img = request.FILES.get('img', None)

    if file_name is not None:  # If we are already having image saved - just need to re-generate arts
        path = os.path.join(settings.TEMPORARY_IMAGES, file_name)
        if not os.path.exists(path):
            path = os.path.join(settings.MEDIA_ROOT, file_name)
            if not os.path.exists(path):
                return JsonResponse({}, status=400)
    elif img is not None:  # If we are uploading new image
        # Getting extension of image
        unused_fn, file_extension = os.path.splitext(img.name)

        # If .bmp or .gif uploaded, convert it to .png
        converted_to_png = False
        if file_extension in '.bmp .gif':
            file_extension = '.png'
            converted_to_png = True

        # Generating unique full path to image (None if many recursions for some reason)
        path, file_name = _generate_unique_image_path(file_extension)
        if path is None:
            return JsonResponse({}, status=400)

        #  Trying to open user's image (and convert it if needed)
        try:
            input_img = Image.open(img)
            if converted_to_png:
                if file_extension == '.bmp':
                    input_img = input_img.convert('RGB')
                elif file_extension == '.gif':
                    input_img = input_img.convert("RGBA")
                    bg = Image.new("RGBA", input_img.size)
                    input_img = Image.composite(input_img, bg, input_img)
        except Exception as error:
            # print(error)
            return JsonResponse({'error': error.args}, status=400)

        # Saving image to defined path with some compression and removing transparency from png
        if file_extension == '.png':
            try:
                image = input_img.convert('RGBA')
                background = Image.new('RGBA', image.size, (255, 255, 255))
                image = Image.alpha_composite(background, image)
            except:
                image = input_img
        else:
            image = input_img
        if image.height > 1000 or image.width > 1000:
            image.thumbnail((1000, 1000), Image.ANTIALIAS)
        image.save(path, optimize=True, quality=95)
    else:
        return JsonResponse({}, status=400)

    # Calculating optimal num_cols for small images
    num_cols = _calculate_num_cols(path, num_cols)

    # Calling image_to_ascii generators in 2 threads, giving them full path to image and options
    args = [path]
    kwargs = {'num_cols': num_cols, 'contrast': contrast, 'brightness': brightness}

    # ---- Thread 1
    arts_1_list = [None, None]
    kwargs1 = {'mode': 'simple'}
    kwargs2 = {'mode': 'bars'}
    arts_1_thread = threading.Thread(target=_generator_thread_1_hub, daemon=True, args=(
        arts_1_list, args, kwargs, kwargs1, kwargs2
    ))
    arts_1_thread.start()

    # ---- Thread 2
    arts_2_list = [None, None]
    arts_2_thread = threading.Thread(target=_generator_thread_2_hub, daemon=True, args=(
        arts_2_list, args, kwargs
    ))
    arts_2_thread.start()

    # Converting some options back to percentage
    brightness = int(brightness * 100)
    contrast = int(contrast * 100)

    # ---- Wait Wait for threads to join here
    arts_1_thread.join()
    arts_2_thread.join()

    return {
        'file_name': file_name,
        'num_cols': num_cols,
        'brightness': brightness,
        'contrast': contrast,
        'arts': [*arts_1_list, *arts_2_list]
    }


def text_to_ascii_generator(request) -> list:
    """
    Generate ascii from text.
    :param request: Request with data.
    :return: List, containing arts in format [font, generated_ascii].
    """
    if not request.POST.get('multiple_strings', False):  # If input is in single-line mode
        input_text = request.POST.get('txt', '')
        if len(input_text) == 0:
            input_text = 'Hello World'
        lines = 1
    else:  # If input is in multi-line mode
        input_text = request.POST.get('txt_multi', '')
        if len(input_text) == 0:
            input_text = 'Hello\nWorld'
        lines = 1 + input_text.count('\n')
    results = []
    for font in txt2ascii_1.FONT_NAMES:
        generated_ascii = txt2ascii_1.text2art(text=input_text, font=font)
        if len(generated_ascii.split('\n')) > (3 * lines):  # Do not append very small arts
            cut = 0
            for line in generated_ascii[::-1].split('\n'):  # Remove some empty lines at the end of arts
                if len(line.replace(' ', '').replace('	', '').replace(' ', '')) == 0:  # don't work great tho
                    cut += 1
                else:
                    break
            if cut != 0:
                generated_ascii = generated_ascii[:-cut]
            results.append([font, generated_ascii])
    return results
