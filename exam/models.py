from django.db import models

from student.models import Student
class Course(models.Model):
   course_name = models.CharField(max_length=50)
   question_number = models.PositiveIntegerField()
   total_marks = models.PositiveIntegerField()
   def __str__(self):
        return self.course_name


class Question(models.Model):
    QUESTION_TYPES = [
        ('MCQ', 'Multiple Choice'),
        ('SUB', 'Subjective'),
    ]

    question = models.TextField()
    course = models.ForeignKey('Course', on_delete=models.CASCADE)
    question_type = models.CharField(max_length=3, choices=QUESTION_TYPES, default='MCQ')  # Add this field
    option1 = models.CharField(max_length=200, blank=True, null=True)
    option2 = models.CharField(max_length=200, blank=True, null=True)
    option3 = models.CharField(max_length=200, blank=True, null=True)
    option4 = models.CharField(max_length=200, blank=True, null=True)
    answer = models.TextField(blank=True, null=True)
    marks = models.IntegerField(default=1)
class Result(models.Model):
    student = models.ForeignKey(Student,on_delete=models.CASCADE)
    exam = models.ForeignKey(Course,on_delete=models.CASCADE)
    marks = models.PositiveIntegerField()
    date = models.DateTimeField(auto_now=True)
class Syllabus(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    file = models.FileField(upload_to="syllabus/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Syllabus for {self.course.course_name}"

class AcademicCalendar(models.Model):
    file = models.FileField(upload_to="academic_calendar/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Academic Calendar uploaded on {self.uploaded_at.strftime('%Y-%m-%d')}"



class SubjectiveQuestion(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="exam_subjective_questions")
    marks = models.PositiveIntegerField()
    question = models.CharField(max_length=600)
    answer = models.TextField()  # Teacher's answer for evaluation

    def __str__(self):
        return f"Subjective: {self.question[:50]}"

class StudentAnswer(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, null=True, blank=True, on_delete=models.CASCADE)  # Objective question
    subjective_question = models.ForeignKey(SubjectiveQuestion, null=True, blank=True, on_delete=models.CASCADE)  # Subjective question
    answer = models.TextField()
    marks_obtained = models.FloatField(default=0)  # Store marks after evaluation

    def evaluate(self):
        if self.subjective_question:
            self.marks_obtained = evaluate_subjective_answer(self.answer, self.subjective_question.answer)
        self.save()
class QuestionPattern(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    num_mcq = models.IntegerField(default=0)
    num_subjective = models.IntegerField(default=0)

    def __str__(self):
        return f"Pattern for {self.course.course_name}"