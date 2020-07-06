from django import forms
from .models import Site, Fossil
from django.forms import ModelForm


class UpdateSitesForm(forms.Form):
    site = forms.FileField(
        label='Update sites to',
    )

class UpdateSitesModelForm(ModelForm):
    class Meta:
        model = Fossil
        fields = ['site']
