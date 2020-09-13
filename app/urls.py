from django.urls import path
from .views import *

urlpatterns = [
    path('', index_page, name='index_page_url'),
    path('t/', index_txt_page, name='index_txt_page_url'),
    path('image_to_ascii_generator/', image_to_ascii_generator, name='image_to_ascii_generator_url'),
    path('text_to_ascii_generator/', text_to_ascii_generator, name='text_to_ascii_generator_url'),
    path('feedback/', feedback, name='feedback_url'),
    path('about/', about, name='about_url'),
    path('policy/privacy/', policy_privacy, name='policy_privacy_url'),
    path('policy/cookie/', policy_cookie, name='policy_cookie_url')
]
