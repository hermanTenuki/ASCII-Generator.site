from django.shortcuts import render, redirect
from .forms import *
from django.contrib.auth import authenticate, login, logout
from app.models import Feedback
from django.http import JsonResponse


#  Staff pages is scuffed on purpose (for now)
def staff_authentication(request):
    if request.user.is_authenticated:
        return redirect('index_page_url')

    elif request.method == 'GET':
        form = StaffAuthenticationForm()
        return render(request, 'staff/staff_authentication.html', context={'form': form})

    elif request.method == 'POST':
        form = StaffAuthenticationForm(request.POST)
        invalid_input = False
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'],
                                password=form.cleaned_data['password'])
            if user is not None and user.is_staff:
                login(request, user)
                return redirect('index_page_url')
            invalid_input = True
        context = {'form': form}
        if invalid_input:
            context['errors'] = ['Username or password is incorrect.']
        return render(request, 'staff/staff_authentication.html', context=context)


def staff_logout(request):
    if request.user.is_authenticated and request.user.is_staff:
        logout(request)
    return redirect('index_page_url')


def staff_feedback(request):
    if (not request.user.is_authenticated) or (not request.user.is_staff):
        return redirect('index_page_url')

    elif request.method == 'GET':
        objs = Feedback.objects.all()
        return render(request, 'staff/feedback.html', context={'objs': objs})


def staff_feedback_del_all(request):
    if request.is_ajax():
        if request.method == 'POST':
            if request.user.is_authenticated and request.user.is_staff:
                Feedback.objects.all().delete()
                return JsonResponse({}, status=200)
        return JsonResponse({}, status=400)


def staff_feedback_del_spec(request):
    if request.is_ajax():
        if request.method == 'POST':
            if request.user.is_authenticated and request.user.is_staff:
                obj_id = request.POST.get('obj_id', None)
                if obj_id is not None:
                    try:
                        obj = Feedback.objects.get(id=obj_id)
                        obj.delete()
                        return JsonResponse({}, status=200)
                    except Feedback.DoesNotExist:
                        pass
        return JsonResponse({}, status=400)
