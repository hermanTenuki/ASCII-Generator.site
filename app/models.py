from django.db import models


class Feedback(models.Model):
    """People can leave their feedback messages with email address if reply is expected"""
    text = models.TextField(max_length=512, blank=False)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.text[:40]


class GeneratedASCII(models.Model):
    """Main model for generated ASCII results (only published)"""
    #  image_to_ascii_type
    #  text_to_ascii_type
    #  outputs
    #  reports
    preferred_output_method = models.CharField(  # Specifying what output method should be displayed on default
        max_length=128
    )
    url_code = models.CharField(max_length=7, unique=True)  # Unique url code "r######", ex. "r2Cx5pO".
    is_hidden = models.BooleanField(default=False)  # If we need to restrict access without actually deleting
    date_shared = models.DateTimeField(auto_now=True)


class ImageToASCIIType(models.Model):
    """Storing input data for image to ASCII type"""
    generated_ascii = models.OneToOneField(
        to='GeneratedASCII', on_delete=models.CASCADE, related_name='image_to_ascii_type'
    )
    input_image = models.ImageField(upload_to='input_images')

    def __str__(self):
        return self.input_image.path


class TextToASCIIType(models.Model):
    """Storing input data for text to ASCII type"""
    generated_ascii = models.OneToOneField(
        to='GeneratedASCII', on_delete=models.CASCADE, related_name='text_to_ascii_type'
    )
    input_text = models.TextField(max_length=256)

    def __str__(self):
        return self.input_text[:40]


class OutputASCII(models.Model):
    """All the generated ASCII outputs stored here"""
    generated_ascii = models.ForeignKey(to='GeneratedASCII', on_delete=models.CASCADE, related_name='outputs')
    method_name = models.CharField(max_length=128)
    ascii_txt = models.TextField()


class Report(models.Model):
    """Reports for shared ASCII"""
    generated_ascii = models.ForeignKey(to='GeneratedASCII', on_delete=models.CASCADE, related_name='reports')
    text = models.TextField(max_length=512)
    date_reported = models.DateTimeField(auto_now=True)
