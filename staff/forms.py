from django import forms
from captcha.fields import ReCaptchaField


class StaffAuthenticationForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    captcha = ReCaptchaField(required=True)
