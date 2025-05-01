from django import forms
from django.contrib.auth.models import User
from . import models
from .models import AcademicCalendar


class ContactusForm(forms.Form):
    Name = forms.CharField(max_length=30)
    Email = forms.EmailField()
    Message = forms.CharField(max_length=500,widget=forms.Textarea(attrs={'rows': 3, 'cols': 30}))

class TeacherSalaryForm(forms.Form):
    salary=forms.IntegerField()

class CourseForm(forms.ModelForm):
    class Meta:
        model=models.Course
        fields=['course_name','question_number','total_marks']
class QuestionForm(forms.ModelForm):
    courseID = forms.ModelChoiceField(
        queryset=models.Course.objects.all(),
        empty_label="Course Name",
        to_field_name="id"
    )
    question_type = forms.ChoiceField(
        choices=models.Question.QUESTION_TYPES,
        required=True,
        widget=forms.Select(attrs={'onchange': 'toggleQuestionType()'})
    )

    class Meta:
        model = models.Question
        fields = ['courseID', 'question_type', 'marks', 'question', 'option1', 'option2', 'option3', 'option4', 'answer']
        widgets = {
            'question': forms.Textarea(attrs={'rows': 3, 'cols': 50}),
            'answer': forms.Textarea(attrs={'rows': 2, 'cols': 50})  # Supports long subjective answers
        }


class SyllabusUploadForm(forms.Form):
    file = forms.FileField(label="Upload Syllabus")



class AcademicCalendarUploadForm(forms.ModelForm):
    class Meta:
        model = AcademicCalendar
        fields = ['file']


class SubjectiveQuestionForm(forms.ModelForm):
    courseID = forms.ModelChoiceField(
        queryset=models.Course.objects.all(),
        empty_label="Course Name",
        to_field_name="id"
    )

    class Meta:
        model = models.SubjectiveQuestion
        fields = ['courseID', 'marks', 'question', 'answer']
        widgets = {
            'question': forms.Textarea(attrs={'rows': 3, 'cols': 50}),
            'answer': forms.Textarea(attrs={'rows': 3, 'cols': 50, 'class': 'form-control', 'placeholder': 'Enter the expected answer'})
        }



