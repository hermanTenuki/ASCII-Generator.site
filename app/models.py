import random
import string

from django.db import models
from django.urls import reverse


class Feedback(models.Model):
    """People can leave their feedback messages with email address if reply is expected"""
    text = models.TextField(max_length=1024, blank=False)
    email = models.EmailField(blank=True, null=True)
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'Feedback: ' + self.text[:40]


class GeneratedASCII(models.Model):
    """Main model for generated ASCII results (only published)"""
    #  image_to_ascii_type
    #  text_to_ascii_type
    #  outputs
    #  reports
    preferred_output_method = models.CharField(  # Specifying what output method should be displayed on default
        max_length=128
    )
    url_code = models.CharField(max_length=6, unique=True, editable=False)  # Unique url code
    is_hidden = models.BooleanField(default=False)  # If we need to restrict access without actually deleting
    date_shared = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'GeneratedASCII: ' + self.url_code

    def save(self, *args, **kwargs):
        if not self.url_code:
            self.url_code = self.generate_random_unique_url_code()
        super().save(*args, **kwargs)

    def generate_random_unique_url_code(self):
        url_code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
        try:
            GeneratedASCII.objects.get(url_code=url_code)
            url_code = self.generate_random_unique_url_code()
        except GeneratedASCII.DoesNotExist:
            return url_code
        return url_code

    def get_absolute_url(self):
        return reverse('ascii_detail_url', kwargs={'ascii_url_code': self.url_code})


class ImageToASCIIType(models.Model):
    """Storing input data for image to ASCII type"""
    #  options
    generated_ascii = models.OneToOneField(
        to=GeneratedASCII, on_delete=models.CASCADE, related_name='image_to_ascii_type'
    )
    input_image = models.ImageField(upload_to='input_images')

    def __str__(self):
        return self.input_image.name

    def get_absolute_url(self):
        return reverse('ascii_detail_url', kwargs={'ascii_url_code': self.generated_ascii.url_code})


class ImageToASCIIOptions(models.Model):
    image_to_ascii_type = models.OneToOneField(
        to=ImageToASCIIType, on_delete=models.CASCADE, related_name='options'
    )
    columns = models.CharField(max_length=64)
    brightness = models.CharField(max_length=64)
    contrast = models.CharField(max_length=64)

    def __str__(self):
        return 'Options for ' + self.image_to_ascii_type.generated_ascii.url_code

    def get_absolute_url(self):
        return reverse('ascii_detail_url', kwargs={'ascii_url_code': self.image_to_ascii_type.generated_ascii.url_code})


class TextToASCIIType(models.Model):
    """Storing input data for text to ASCII type"""
    generated_ascii = models.OneToOneField(
        to=GeneratedASCII, on_delete=models.CASCADE, related_name='text_to_ascii_type'
    )
    input_text = models.TextField(max_length=256)
    multi_line_mode = models.BooleanField(default=False)

    def __str__(self):
        return 'TextToASCII: ' + self.input_text[:40]

    def get_absolute_url(self):
        return reverse('ascii_detail_url', kwargs={'ascii_url_code': self.generated_ascii.url_code})


class OutputASCII(models.Model):
    """All the generated ASCII outputs stored here"""
    generated_ascii = models.ForeignKey(to=GeneratedASCII, on_delete=models.CASCADE, related_name='outputs')
    method_name = models.CharField(max_length=128)
    ascii_txt = models.TextField(default='')

    class Meta:
        ordering = ['id']


class Report(models.Model):
    """Reports for shared ASCII"""
    generated_ascii = models.ForeignKey(to=GeneratedASCII, on_delete=models.CASCADE, related_name='reports')
    text = models.TextField(max_length=1024)
    email = models.EmailField(blank=True, null=True)
    date_reported = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'Report: ' + self.text[:60]

    def get_absolute_url(self):
        return reverse('ascii_detail_url', kwargs={'ascii_url_code': self.generated_ascii.url_code})
