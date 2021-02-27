from django.contrib import admin
from django.urls import reverse
from django.utils.html import mark_safe

from app.models import (
    Feedback, GeneratedASCII,
    ImageToASCIIType, ImageToASCIIOptions, TextToASCIIType,
    Report
)


class GeneratedASCIIAdmin(admin.ModelAdmin):
    def text_to_ascii_type_link(self, obj):
        link = reverse('admin:app_texttoasciitype_change', args=[obj.text_to_ascii_type.id])
        return mark_safe(f'<a href="{link}">Open</a>')
    text_to_ascii_type_link.short_description = 'Text to ASCII type'

    def image_to_ascii_type_link(self, obj):
        link = reverse('admin:app_imagetoasciitype_change', args=[obj.image_to_ascii_type.id])
        return mark_safe(f'<a href="{link}">Open</a>')
    image_to_ascii_type_link.short_description = 'Image to ASCII type'

    search_fields = (
        'url_code',
    )

    readonly_fields = (
        'text_to_ascii_type_link',
        'image_to_ascii_type_link',
        'url_code',
        'date_shared',
    )


admin.site.register(GeneratedASCII, GeneratedASCIIAdmin)


class FeedbackAdmin(admin.ModelAdmin):
    readonly_fields = (
        'date',
    )


admin.site.register(Feedback, FeedbackAdmin)


class ImageToASCIITypeAdmin(admin.ModelAdmin):
    def image_to_ascii_options_link(self, obj):
        link = reverse('admin:app_imagetoasciioptions_change', args=[obj.options.id])
        return mark_safe(f'<a href="{link}">Open</a>')
    image_to_ascii_options_link.short_description = 'Options'

    raw_id_fields = ('generated_ascii',)

    readonly_fields = (
        'image_to_ascii_options_link',
    )


admin.site.register(ImageToASCIIType, ImageToASCIITypeAdmin)


class ImageToASCIIOptionsAdmin(admin.ModelAdmin):
    raw_id_fields = ('image_to_ascii_type',)


admin.site.register(ImageToASCIIOptions, ImageToASCIIOptionsAdmin)


class TextToASCIITypeAdmin(admin.ModelAdmin):
    raw_id_fields = ('generated_ascii',)


admin.site.register(TextToASCIIType, TextToASCIITypeAdmin)


class ReportAdmin(admin.ModelAdmin):
    search_fields = ('generated_ascii__url_code',)
    raw_id_fields = ('generated_ascii',)

    readonly_fields = (
        'date_reported',
    )


admin.site.register(Report, ReportAdmin)
