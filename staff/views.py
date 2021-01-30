from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout

from staff.forms import StaffAuthenticationForm


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
