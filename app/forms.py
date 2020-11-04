from django import forms
from captcha.fields import ReCaptchaField
from .models import *
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class FeedbackForm(forms.ModelForm):
    captcha = ReCaptchaField(required=True)
    agreement = forms.BooleanField(required=False, widget=forms.CheckboxInput(
        attrs={'required': ''}  # required=False is for custom validation error
    ))

    class Meta:
        model = Feedback
        fields = ['text', 'email']
        widgets = {
            'text': forms.Textarea(attrs={'placeholder': _('Your message*')}),
            'email': forms.EmailInput(attrs={'placeholder': _('Email (optional)')})
        }

    def clean_text(self):
        text = self.cleaned_data['text']
        if not text or len(text) < 1:
            raise ValidationError(_('Please write your text there.'))
        if len(text) > 512:
            raise ValidationError(_('Characters limit is 512.'))
        return text

    # def clean_captcha(self):
    #     captcha = self.cleaned_data['captcha']
    #     if not captcha:
    #         raise ValidationError('Captcha is not passed.')  # "required=True" is making this validation useless
    #     return captcha

    def clean_agreement(self):
        agreement = self.cleaned_data['agreement']
        if not agreement:
            raise ValidationError(_("We can't continue without your agreement."))
        return agreement
