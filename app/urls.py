from django.urls import path
from .views import *

urlpatterns = [
    path('', index_page, name='index_page_url'),
    path('t/', index_txt_page, name='index_txt_page_url'),
    path('r/<str:ascii_url_code>/', ascii_detail, name='ascii_detail_url'),
    path('a/ascii_share/', ascii_share, name='ascii_share_url'),  # "a/..." is for actions.
    path('a/ascii_report/<str:ascii_url_code>/', ascii_report, name='ascii_report_url'),
    path('a/image_to_ascii_generator/', image_to_ascii_generator, name='image_to_ascii_generator_url'),
    path('a/text_to_ascii_generator/', text_to_ascii_generator, name='text_to_ascii_generator_url'),
    path('feedback/', feedback, name='feedback_url'),
    path('about/', about, name='about_url'),
    path('policy/privacy/', policy_privacy, name='policy_privacy_url'),
    path('policy/cookie/', policy_cookie, name='policy_cookie_url'),
    path('sitemap.xml/', sitemap_xml, name='sitemap_xml')
]
