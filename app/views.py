from django.shortcuts import render, redirect
from .forms import *
from django.http import JsonResponse
from .ascii_generators import ascii_generators


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
