from .forms import *
from .models import *
from django.http import JsonResponse
from .ascii_generators import ascii_generators
from django.conf import settings
import os
from django.core.files import File
from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404


class FeedbackService:
    @staticmethod
    def get_form() -> FeedbackForm:
        return FeedbackForm()

    @staticmethod
    def create(data) -> (FeedbackForm, int):
        form = FeedbackForm(data)

        if form.is_valid():
            form.save()
            return form, 200
        return form, 400


class ReportService:
    @staticmethod
    def get_form() -> ReportForm:
        return ReportForm()

    @staticmethod
    def create(data, ascii_url_code) -> JsonResponse:
        form = ReportForm(data)
        try:
            generated_ascii = GeneratedASCII.objects.get(url_code=ascii_url_code)
        except GeneratedASCII.DoesNotExist:
            return JsonResponse({'errors': {'captcha': [_("Can't find object to report.")]}}, status=400)
        if form.is_valid():
            Report.objects.create(text=form.cleaned_data['text'],
                                  email=form.cleaned_data['email'],
                                  generated_ascii=generated_ascii)
            return JsonResponse({}, status=200)
        return JsonResponse({'errors': form.errors}, status=400)


class GeneratedASCIIService:
    @staticmethod
    def _generate_unique_image_path(file_extension, r=0, r_max=10):
        """
        Recursive function that generates random unique file name and path.
        :return: Full path to file, name with extension.
        """
        name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=50))
        y = f'{name}{file_extension}'
        x = os.path.join(settings.MEDIA_ROOT, 'input_images/', y)
        if os.path.exists(x):
            if r >= r_max:
                return None, None
            x, y = GeneratedASCIIService._generate_unique_image_path(file_extension, r=r + 1)
        return x, y

    @staticmethod
    def get_object_or_404(ascii_url_code) -> GeneratedASCII:
        return get_object_or_404(GeneratedASCII, url_code=ascii_url_code)

    @staticmethod
    def is_txt_mode(ascii_obj):
        try:
            _ = ascii_obj.image_to_ascii_type
            app_txt_mode = False
        except ImageToASCIIType.DoesNotExist:
            app_txt_mode = True
        return app_txt_mode

    @staticmethod
    def create(request) -> JsonResponse:
        if request.POST.get('file_name', False):
            img2ascii_mode = True
            result = ascii_generators.image_to_ascii_generator(request)
        else:
            img2ascii_mode = False
            result = {
                'txt': request.POST.get('txt', ''),
                'txt_multi': request.POST.get('txt_multi', ''),
                'arts': ascii_generators.text_to_ascii_generator(request)
            }
        if type(result) == JsonResponse:
            return result
        preferred_output_method = request.POST.get('preferred_output_method', None)
        if preferred_output_method is None:
            return JsonResponse({}, status=400)
        ascii_obj = GeneratedASCII.objects.create(preferred_output_method=preferred_output_method)
        if img2ascii_mode:
            image_to_ascii_type_obj = ImageToASCIIType(
                generated_ascii=ascii_obj,
            )
            file = open(os.path.join(settings.TEMPORARY_IMAGES, result.get('file_name')), 'rb')
            unused_fn, file_extension = os.path.splitext(file.name)
            unused_path, file_name = GeneratedASCIIService._generate_unique_image_path(file_extension)
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
            )
            arts = result.get('arts')
            for i in range(len(arts)):
                OutputASCII.objects.create(
                    generated_ascii=ascii_obj,
                    method_name=str(i + 1),
                    ascii_txt=arts[i]
                )
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
            )
            arts = result.get('arts')
            for art in arts:
                OutputASCII.objects.create(
                    generated_ascii=ascii_obj,
                    method_name=art[0],
                    ascii_txt=art[1],
                )
        return JsonResponse({
            'shared_redirect_url': reverse('ascii_detail_url', kwargs={'ascii_url_code': ascii_obj.url_code})
        }, status=200)
