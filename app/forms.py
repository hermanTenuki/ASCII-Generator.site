from captcha.fields import ReCaptchaField
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from app.models import Feedback, Report


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
            'email': forms.EmailInput(attrs={'placeholder': _('Email (optional)')}),
        }

    def clean_text(self):
        text = self.cleaned_data['text']
        if not text or len(text) < 1:
            raise ValidationError(_('Please write your text there.'))
        if len(text) > 1024:
            raise ValidationError(_('Characters limit is 1024.'))
        return text

    def clean_agreement(self):
        agreement = self.cleaned_data['agreement']
        if not agreement:
            raise ValidationError(_("We can't continue without your agreement."))
        return agreement


class ReportForm(forms.ModelForm):
    captcha = ReCaptchaField(required=True)

    class Meta:
        model = Report
        fields = ['text', 'email']
        widgets = {
            'text': forms.Textarea(attrs={'placeholder': _('Your message*')}),
            'email': forms.EmailInput(attrs={'placeholder': _('Email (optional)')}),
        }

    def clean_text(self):
        text = self.cleaned_data['text']
        if not text or len(text) < 1:
            raise ValidationError(_('Please write your text there.'))
        if len(text) > 1024:
            raise ValidationError(_('Characters limit is 1024.'))
        return text
