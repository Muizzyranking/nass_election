from django import forms
from .models import Student, Department

class StudentForm(forms.ModelForm):
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        empty_label="Select Department",
        required=False # Department can be optional during registration
    )

    class Meta:
        model = Student
        fields = ['matric', 'first_name', 'middle_name', 'last_name', 'email', 'level', 'sex', 'department']
        widgets = {
            'middle_name': forms.TextInput(attrs={'required': False}),
            'email': forms.EmailInput(attrs={'required': True}),
        }
