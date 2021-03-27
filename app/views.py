from django.shortcuts import render, redirect
from django.http import JsonResponse

from app.services import ReportService, FeedbackService, GeneratedASCIIService
from app.ascii_generators import ascii_generators
from app.decorators import redirect_if_not_ajax


def handler400_view(request, *args, **kwargs):
    return render(request, 'errors/400.html', status=400, context={'error_handler_page': True})


def handler404_view(request, *args, **kwargs):
    return render(request, 'errors/404.html', status=404, context={'error_handler_page': True})


def handler500_view(request, *args, **kwargs):
    return render(request, 'errors/500.html', status=500, context={'error_handler_page': True})


def index_page(request, app_txt_mode=False, ascii_obj=None):
    context = {
        'app_page': True,  # indicates if user is on index page with generator's inputs
        'app_txt_mode': app_txt_mode,  # indicates if user is opening "Text to ASCII"
        'ascii_obj': ascii_obj,  # ascii object when opening shared page
    }

    # if ascii_obj is passed in, add report form to context
    if ascii_obj is not None:
        context['report_form'] = ReportService.get_form()

    return render(request, 'app/index.html', context=context)


def index_txt_page(request):
    # Open index_page with txt input mode
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
            form, status = FeedbackService.create(request.POST)
            response = {}
            if status == 400:
                response['errors'] = form.errors
            return JsonResponse(response, status=status)
        return JsonResponse({}, status=405)

    if request.method == 'GET':
        form = FeedbackService.get_form()
        return render(request, 'app/feedback.html', context={'form': form})

    elif request.method == 'POST':
        form, status = FeedbackService.create(request.POST)
        if status == 200:
            return redirect('feedback_url')
        return render(request, 'app/feedback.html', context={'form': form})


@redirect_if_not_ajax(url='index_page_url')
def image_to_ascii_generator(request):
    if request.method == 'POST':
        result = ascii_generators.image_to_ascii_generator(request)
        if isinstance(result, JsonResponse):
            return result
        return JsonResponse(result, status=200)
    return JsonResponse({}, status=405)


@redirect_if_not_ajax(url='index_txt_page_url')
def text_to_ascii_generator(request):
    if request.method == 'POST':
        results = ascii_generators.text_to_ascii_generator(request)
        if not results:
            return JsonResponse({}, status=400)
        return JsonResponse({'results': results}, status=200)
    return JsonResponse({}, status=405)


def ascii_detail(request, ascii_url_code):
    ascii_obj = GeneratedASCIIService.get_active_object_or_404(ascii_url_code)
    app_txt_mode = GeneratedASCIIService.is_txt_mode(ascii_obj)
    return index_page(request, ascii_obj=ascii_obj, app_txt_mode=app_txt_mode)


@redirect_if_not_ajax(url='index_page_url')
def ascii_share(request):
    if request.method == 'POST':
        json_response = GeneratedASCIIService.create(request)
        return json_response
    return JsonResponse({}, status=405)


@redirect_if_not_ajax(url='index_page_url')
def ascii_report(request, ascii_url_code):
    if request.method == 'POST':
        json_response = ReportService.create(request.POST, ascii_url_code)
        return json_response
    return JsonResponse({}, status=405)
