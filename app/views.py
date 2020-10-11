from django.shortcuts import render, redirect
from .forms import *
from django.http import JsonResponse
from .ascii_generators import img2ascii_1, img2ascii_2, txt2ascii_1
import random
import string
import os
from django.conf import settings
from PIL import Image


def handler400_view(request, *args, **kwargs):
    return render(request, 'errors/400.html', status=400, context={'error_handler_page': True})


def handler404_view(request, *args, **kwargs):
    return render(request, 'errors/404.html', status=404, context={'error_handler_page': True})


def handler500_view(request, *args, **kwargs):
    return render(request, 'errors/500.html', status=500, context={'error_handler_page': True})


def index_page(request, app_txt_mode=False):
    context = {
        'app_page': True  # indicates if user is on index page with generator's inputs
    }
    if app_txt_mode:
        context['app_txt_mode'] = True
    return render(request, 'app/index.html', context=context)


# Open index_page with txt input mode
def index_txt_page(request):
    return index_page(request, app_txt_mode=True)


def about(request):
    return render(request, 'app/about.html')


def policy_privacy(request):
    return render(request, 'app/policy_privacy.html')


def policy_cookie(request):
    return render(request, 'app/policy_cookie.html')


def sitemap_xml(request):
    return render(request, 'sitemap.xml', content_type='text/xml')


def feedback(request):
    if request.is_ajax():
        if request.method == 'POST':
            form = FeedbackForm(data=request.POST)
            if form.is_valid():
                form.save()
                return JsonResponse({}, status=200)
            return JsonResponse({'errors': form.errors}, status=400)
        return JsonResponse({}, status=405)  # 405 Method Not Allowed
    else:
        if request.method == 'GET':
            form = FeedbackForm()
            context = {'form': form}
            return render(request, 'app/feedback.html', context=context)

        if request.method == 'POST':
            form = FeedbackForm(request.POST)
            context = {'form': form}
            if form.is_valid():
                form.save()
                return redirect('feedback_url')
            return render(request, 'app/feedback.html', context=context)


def _generate_unique_image_path(file_extension, r=0, r_max=10):
    """
    :return: full path to file, name with extension
    """
    # Random name to image
    name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=100))  # 100 symbols for security
    # Making file name
    y = f'{name}{file_extension}'
    # Making path
    x = f'{settings.BASE_DIR}/_temporary_images/{y}'
    # Checking if it already exist
    if os.path.exists(x):
        if r >= r_max:
            return None, None
        x, y = _generate_unique_image_path(file_extension, r=r + 1)  # Recursion
    return x, y


def image_to_ascii_generator(request):
    if request.is_ajax():
        if request.method == 'POST':
            file_name = request.POST.get('file_name', None)
            num_cols = request.POST.get('num_cols', 90)
            brightness = request.POST.get('brightness', 100)
            contrast = request.POST.get('contrast', 100)
            try:  # Validating user's input
                brightness = float(brightness) / 100
            except:
                brightness = 1
            try:  # Validating user's input
                contrast = float(contrast) / 100
            except:
                contrast = 1
            try:  # Validating user's input
                num_cols = int(num_cols)
            except:
                num_cols = 90
            if num_cols > 300:
                num_cols = 300
            img = request.FILES.get('img', None)
            if file_name is not None:  # If we are already having image saved - just need to re-generate arts
                path = f'{settings.BASE_DIR}/_temporary_images/{file_name}'
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
                # !DEPRECATED! # If uploaded image is small, configure num_cols to it's width
                # elif image.width < 95:
                #     num_cols = image.width - 5
                image.save(path, optimize=True, quality=95)
            else:
                return JsonResponse({}, status=400)
            # Calling image_to_ascii generators, giving them full path to image and options
            # Getting new num_cols from img2ascii_2 so we can set it to img2ascii_1
            art1, num_cols = img2ascii_2.image_to_ascii(path, num_cols=num_cols, mode='simple',
                                                        contrast=contrast, brightness=brightness)
            art2, _ = img2ascii_2.image_to_ascii(path, num_cols=num_cols, mode='bars',
                                                 contrast=contrast, brightness=brightness)
            art3 = img2ascii_1.image_to_ascii(path, num_cols=num_cols, contrast=contrast,
                                              brightness=brightness)
            art4, _ = img2ascii_2.image_to_ascii(path, num_cols=num_cols, contrast=contrast,
                                                 brightness=brightness)
            # Converting some options back to percentage
            brightness = int(brightness * 100)
            contrast = int(contrast * 100)

            return JsonResponse({
                'file_name': file_name,
                'num_cols': num_cols,
                'brightness': brightness,
                'contrast': contrast,
                'arts': [art1, art2, art3, art4]
            }, status=200)

        return JsonResponse({}, status=405)
    else:
        return redirect('index_page_url')


def text_to_ascii_generator(request):
    if request.is_ajax():
        if request.method == 'POST':
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
            if len(results) == 0:  # If no results generated, return response 400
                return JsonResponse({}, status=400)
            return JsonResponse({'results': results}, status=200)
        return JsonResponse({}, status=405)
    else:
        return redirect('index_txt_page_url')
