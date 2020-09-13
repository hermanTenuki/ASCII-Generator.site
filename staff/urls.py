from django.urls import path
from .views import *
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('authentication/', staff_authentication, name='staff_authentication_url'),
    path('logout/', staff_logout, name='staff_logout_url'),
    path('feedback/', staff_feedback, name='staff_feedback_url'),
    path('feedback/del_all/', staff_feedback_del_all, name='staff_feedback_del_all'),
    path('feedback/del_spec/', staff_feedback_del_spec, name='staff_feedback_del_spec')
]
