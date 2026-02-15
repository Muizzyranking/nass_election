from django import forms
from .models import Candidate

class CandidateForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = ['matric', 'first_name', 'last_name', 'manifesto', 'position', 'photo']
