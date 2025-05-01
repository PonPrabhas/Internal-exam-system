from django import forms
from django.contrib.auth.models import User
from . import models
from exam import models as QMODEL

class StudentUserForm(forms.ModelForm):
    class Meta:
        model=User
        fields=['first_name','last_name','username','password']
        widgets = {
        'password': forms.PasswordInput()
        }
DEPARTMENT_CHOICES = [
    ('MCA A', 'MCA A'),
    ('MCA B', 'MCA B'),
    ('M.Sc', 'M.Sc'),
]
class StudentForm(forms.ModelForm):
    address = forms.ChoiceField(choices=DEPARTMENT_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    class Meta:
        model=models.Student
        fields=['address','mobile','profile_pic']

