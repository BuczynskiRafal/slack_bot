from django import forms

from .models import SlackProfile, SlackUser


class SlackProfileForm(forms.ModelForm):
    class Meta:
        model = SlackProfile
        fields = '__all__'


class SlackUserForm(forms.ModelForm):
    class Meta:
        model = SlackUser
        fields = '__all__'
