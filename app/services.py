import os
import random
import string
import json

from django.shortcuts import reverse
from django.http import JsonResponse
from django.conf import settings
from django.core.files import File
from django.utils.translation import gettext_lazy as _
from django.http import Http404
from django.core.cache import cache

from app.forms import FeedbackForm, ReportForm
from app.models import (
    GeneratedASCII, Report, ImageToASCIIType,
    ImageToASCIIOptions, TextToASCIIType
)
from app.ascii_generators import ascii_generators


class FeedbackService:
    @staticmethod
    def get_form() -> FeedbackForm:
        return FeedbackForm()

    @staticmethod
    def create(data) -> (FeedbackForm, int):
        """
        Create "Feedback".
        :param data: data for the FeedbackForm.
        :return: Form and status code (200/400).
        """
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
        """
        Create "Report"
        :param data: data for the ReportForm.
        :param ascii_url_code: url code for "GeneratedASCII" object, passed from url.
        :return: Fully built JsonResponse with errors if occurred.
        """
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
        Recursive function that generates random, but unique file name and path.
        :return: Full path to file, name with extension. Return 2 nones if too many recursions.
        """
        name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))
        full_name = f'{name}{file_extension}'
        full_path = os.path.join(settings.MEDIA_ROOT, 'input_images/', full_name)
        if os.path.exists(full_path):
            if r >= r_max:
                return None, None
            full_path, full_name = GeneratedASCIIService._generate_unique_image_path(file_extension, r=r + 1)
        return full_path, full_name

    @staticmethod
    def get_active_object_or_404(ascii_url_code) -> GeneratedASCII:
        # find it in cache, if not found - set it
        key = f'GeneratedASCIIService_get_object_or_404_{ascii_url_code}'
        generated_ascii = cache.get(key)
        if not generated_ascii:
            try:
                generated_ascii = GeneratedASCII.objects.select_related(
                    'image_to_ascii_type__options', 'text_to_ascii_type'
                ).prefetch_related(
                    'reports'
                ).get(url_code=ascii_url_code)
                cache.set(key, generated_ascii)
            except GeneratedASCII.DoesNotExist:
                raise Http404
        # we don't want to return hidden object
        if generated_ascii.is_hidden:
            raise Http404

        return generated_ascii

    @staticmethod
    def is_txt_mode(ascii_obj) -> bool:
        """
        Check if "GeneratedASCII" object is containing TextToASCII arts.
        :param ascii_obj: "GeneratedASCII" object.
        :return: Boolean.
        """
        if hasattr(ascii_obj, 'text_to_ascii_type'):
            return True
        return False

    @staticmethod
    def create(request) -> JsonResponse:
        """
        Create (share) "GeneratedASCII" object with all generated arts stored in "output_ascii" field.
        while input data is stored in "TextToASCIIType" or "ImageToASCIIType" with "ImageToASCIIOptions".
        :param request: Request, so it can access request.POST and request.FILE.
        :return: Fully build JsonResponse with "shared_redirect_url" - relative path to shared object.
        """
        # At first, generate desired results.
        if request.POST.get('file_name', False):
            # Generate ImageToASCII results from request
            img2ascii_mode = True
            result = ascii_generators.image_to_ascii_generator(request)
        else:
            # Generate TextToASCII results from request
            img2ascii_mode = False
            result = {
                'txt': request.POST.get('txt', ''),
                'txt_multi': request.POST.get('txt_multi', ''),
                'arts': ascii_generators.text_to_ascii_generator(request)
            }
        # Check if errors occurred while generating ASCII arts.
        if img2ascii_mode:
            if type(result) == JsonResponse:
                return result
        else:
            if len(result['arts']) == 0:
                return JsonResponse({}, status=400)
        # Get preferred output method from request, if not provided - return error.
        preferred_output_method = request.POST.get('preferred_output_method', None)
        if preferred_output_method is None:
            return JsonResponse({}, status=400)
        # Create "GeneratedASCII" object and all other needed stuff.
        ascii_obj = GeneratedASCII.objects.create(preferred_output_method=preferred_output_method)
        if img2ascii_mode:
            # In ImageToASCII mode - create ImageToASCIIType with input image.
            image_to_ascii_type_obj = ImageToASCIIType(
                generated_ascii=ascii_obj,
            )
            file = open(os.path.join(settings.TEMPORARY_IMAGES, result['file_name']), 'rb')
            _unused_fn, file_extension = os.path.splitext(file.name)
            _unused_path, file_name = GeneratedASCIIService._generate_unique_image_path(file_extension)
            image_to_ascii_type_obj.input_image.save(
                file_name,
                File(file),
            )
            image_to_ascii_type_obj.save()
            file.close()
            # Create "ImageToASCIIOptions".
            ImageToASCIIOptions.objects.create(
                image_to_ascii_type=image_to_ascii_type_obj,
                columns=result['num_cols'],
                brightness=result['brightness'],
                contrast=result['contrast'],
            )
            # Add objects in json to "output_ascii" field for every generated ascii.
            arts = result.get('arts')
            json_list = []
            for i in range(len(arts)):
                json_list.append({
                    'method_name': str(i + 1),
                    'ascii_txt': arts[i]
                })

        else:
            # In TextToASCII mode - create TextToASCIIType with input text.
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
            json_list = []
            for art in arts:
                json_list.append({
                    'method_name': art[0],
                    'ascii_txt': art[1],
                })

        ascii_obj.output_ascii = json.dumps(json_list)
        ascii_obj.save()

        return JsonResponse({
            'shared_redirect_url': reverse('ascii_detail_url', kwargs={'ascii_url_code': ascii_obj.url_code})
        }, status=200)
