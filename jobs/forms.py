from django import forms
from .models import Job, Applications

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'description']

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Applications
        fields = ['cover_letter']