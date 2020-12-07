from django.shortcuts import render, redirect, get_object_or_404
from .forms import *
from django.http import JsonResponse
from .ascii_generators import ascii_generators
from PIL import Image
from django.conf import settings
import os
from django.urls import reverse
from django.core.files import File
from django.utils.translation import gettext_lazy as _


def handler400_view(request, *args, **kwargs):
    return render(request, 'errors/400.html', status=400, context={'error_handler_page': True})


def handler404_view(request, *args, **kwargs):
    return render(request, 'errors/404.html', status=404, context={'error_handler_page': True})


def handler500_view(request, *args, **kwargs):
    return render(request, 'errors/500.html', status=500, context={'error_handler_page': True})


def index_page(request, app_txt_mode=False, ascii_obj=None):
    context = {
        'app_page': True,  # indicates if user is on index page with generator's inputs
        'ascii_obj': ascii_obj,  # ascii object when opening shared page
        'app_txt_mode': app_txt_mode,  # indicates if user is opening "Text to ASCII"
    }

    if ascii_obj is not None:
        context['report_form'] = ReportForm()

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


def image_to_ascii_generator(request):
    if request.is_ajax():
        if request.method == 'POST':
            result = ascii_generators.image_to_ascii_generator(request)
            if type(result) == JsonResponse:
                return result
            return JsonResponse(result, status=200)

        return JsonResponse({}, status=405)
    else:
        return redirect('index_page_url')


def text_to_ascii_generator(request):
    if request.is_ajax():
        if request.method == 'POST':
            results = ascii_generators.text_to_ascii_generator(request)
            if len(results) == 0:  # If no results generated, return response 400
                return JsonResponse({}, status=400)
            return JsonResponse({'results': results}, status=200)
        return JsonResponse({}, status=405)
    else:
        return redirect('index_txt_page_url')


def ascii_detail(request, ascii_url_code):
    ascii_obj = get_object_or_404(GeneratedASCII, url_code=ascii_url_code)
    try:
        exists = ascii_obj.image_to_ascii_type
        app_txt_mode = False
    except ImageToASCIIType.DoesNotExist:
        app_txt_mode = True
    return index_page(request, ascii_obj=ascii_obj, app_txt_mode=app_txt_mode)


def _generate_unique_image_path(file_extension, r=0, r_max=10):
    """
    Recursive function that generates random unique file name and path.
    :return: Full path to file, name with extension.
    """
    name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=50))
    y = f'{name}{file_extension}'
    x = os.path.join(settings.MEDIA_ROOT, y)
    if os.path.exists(x):
        if r >= r_max:
            return None, None
        x, y = _generate_unique_image_path(file_extension, r=r + 1)
    return x, y


def ascii_share(request):
    if request.is_ajax():
        if request.method == 'POST':
            if request.POST.get('file_name', False):
                img2ascii_mode = True
                result = ascii_generators.image_to_ascii_generator(request)
            else:
                img2ascii_mode = False
                result = {
                    'txt': request.POST.get('txt', None),
                    'txt_multi': request.POST.get('txt_multi', None),
                    'arts': ascii_generators.text_to_ascii_generator(request)
                }
            preferred_output_method = request.POST.get('preferred_output_method', None)
            ascii_obj = GeneratedASCII.objects.create(preferred_output_method=preferred_output_method)
            ascii_obj.save()
            if img2ascii_mode:
                image_to_ascii_type_obj = ImageToASCIIType.objects.create(
                    generated_ascii=ascii_obj,
                )
                file = open(os.path.join(settings.TEMPORARY_IMAGES, result.get('file_name')), 'rb')
                unused_fn, file_extension = os.path.splitext(file.name)
                unused_path, file_name = _generate_unique_image_path(file_extension)
                image_to_ascii_type_obj.input_image.save(
                    file_name,
                    File(file),
                )
                image_to_ascii_type_obj.save()
                file.close()
                ImageToASCIIOptions.objects.create(
                    image_to_ascii_type=image_to_ascii_type_obj,
                    columns=result.get('num_cols'),
                    brightness=result.get('brightness'),
                    contrast=result.get('contrast'),
                ).save()
                arts = result.get('arts')
                for i in range(len(arts)):
                    OutputASCII.objects.create(
                        generated_ascii=ascii_obj,
                        method_name=str(i + 1),
                        ascii_txt=arts[i]
                    ).save()
            else:
                if not request.POST.get('multiple_strings', False):
                    multi_line_mode = False
                    input_text = result.get('txt', '')
                else:
                    multi_line_mode = True
                    input_text = result.get('txt_multi', '')
                TextToASCIIType.objects.create(
                    generated_ascii=ascii_obj,
                    input_text=input_text,
                    multi_line_mode=multi_line_mode,
                ).save()
                arts = result.get('arts')
                for art in arts:
                    OutputASCII.objects.create(
                        generated_ascii=ascii_obj,
                        method_name=art[0],
                        ascii_txt=art[1],
                    ).save()
            return JsonResponse({
                'shared_redirect_url': reverse('ascii_detail_url', kwargs={'ascii_url_code': ascii_obj.url_code})
            }, status=200)
        return JsonResponse({}, status=405)
    else:
        return redirect('index_page_url')


def ascii_report(request, ascii_url_code):
    if request.is_ajax():
        if request.method == 'POST':
            form = ReportForm(data=request.POST)
            try:
                generated_ascii = GeneratedASCII.objects.get(url_code=ascii_url_code)
            except GeneratedASCII.DoesNotExist:
                return JsonResponse({'errors': {'captcha': [_("Can't find object to report.")]}}, status=400)
            if form.is_valid():
                Report.objects.create(text=form.cleaned_data['text'],
                                      email=form.cleaned_data['email'],
                                      generated_ascii=generated_ascii
                                      ).save()
                return JsonResponse({}, status=200)
            return JsonResponse({'errors': form.errors}, status=400)
        return JsonResponse({}, status=405)  # 405 Method Not Allowed
    else:
        return redirect('index_page_url')
