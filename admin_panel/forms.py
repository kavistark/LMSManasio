# core/forms.py

from django import forms
from .models import StudyImage, CareerOpportunities

class StudyImageForm(forms.ModelForm):
    class Meta:
        model = StudyImage
        fields = ['title', 'image']

class RichTextContentForm(forms.ModelForm):
    class Meta:
        model = CareerOpportunities
        fields = ['job_description']
        widgets = {
            'job_description': forms.HiddenInput(),  # Quill will fill this
        }