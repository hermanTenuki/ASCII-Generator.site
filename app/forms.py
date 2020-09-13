from django import forms
from captcha.fields import ReCaptchaField
from .models import *
from django.core.exceptions import ValidationError


class FeedbackForm(forms.ModelForm):
    captcha = ReCaptchaField(required=True)
    agreement = forms.BooleanField(required=False, widget=forms.CheckboxInput(
        attrs={'required': ''}  # required=False is for custom validation error
    ))

    class Meta:
        model = Feedback
        fields = ['text', 'email']
        widgets = {
            'text': forms.Textarea(attrs={'placeholder': 'Your message*'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email for reply (optional)'})
        }

    def clean_text(self):
        text = self.cleaned_data['text']
        if not text or len(text) < 1:
            raise ValidationError('Please write your text there.')
        if len(text) > 512:
            raise ValidationError('Characters limit is 512.')
        return text

    # def clean_captcha(self):
    #     captcha = self.cleaned_data['captcha']
    #     if not captcha:
    #         raise ValidationError('Captcha is not passed.')  # "required=True" is making this validation useless
    #     return captcha

    def clean_agreement(self):
        agreement = self.cleaned_data['agreement']
        if not agreement:
            raise ValidationError("We can't continue without your agreement.")
        return agreement
