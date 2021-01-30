from django.contrib import admin

from app.models import (
    Feedback, GeneratedASCII,
    ImageToASCIIType, ImageToASCIIOptions, TextToASCIIType,
    OutputASCII, Report
)


admin.site.register(Feedback)
admin.site.register(GeneratedASCII)
admin.site.register(ImageToASCIIType)
admin.site.register(ImageToASCIIOptions)
admin.site.register(TextToASCIIType)
admin.site.register(OutputASCII)
admin.site.register(Report)
