from django import forms
from django.contrib.auth.models import User
from . import models
from .models import SubjectiveQuestion

class TeacherUserForm(forms.ModelForm):
    class Meta:
        model=User
        fields=['first_name','last_name','username','password']
        widgets = {
        'password': forms.PasswordInput()
        }

class TeacherForm(forms.ModelForm):
    class Meta:
        model=models.Teacher
        fields=['address','mobile','profile_pic']


class SubjectiveQuestionForm(forms.ModelForm):
    class Meta:
        model = SubjectiveQuestion
        fields = ['course']

    content = forms.FileField(label="Upload Content File (TXT/PDF)")
