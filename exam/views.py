from django.shortcuts import render,redirect,reverse
from . import forms,models
from django.db.models import Sum
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required,user_passes_test
from django.conf import settings
from datetime import date, timedelta
from django.db.models import Q
from django.core.mail import send_mail
from teacher import models as TMODEL
from student import models as SMODEL
from teacher import forms as TFORM
from student import forms as SFORM
from django.contrib.auth.models import User
from .forms import SyllabusUploadForm, AcademicCalendarUploadForm
from .models import Course, Syllabus, AcademicCalendar
import random
from teacher import models as TMODEL
from exam import models as QMODEL  # Import the models correctly
from difflib import SequenceMatcher


from .models import Question, SubjectiveQuestion
import traceback  # Import to capture errors
from django.contrib import messages
def home_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')  
    return render(request,'exam/index.html')


def is_teacher(user):
    return user.groups.filter(name='TEACHER').exists()

def is_student(user):
    return user.groups.filter(name='STUDENT').exists()

def afterlogin_view(request):
    if is_student(request.user):      
        return redirect('student/student-dashboard')
                
    elif is_teacher(request.user):
        accountapproval=TMODEL.Teacher.objects.all().filter(user_id=request.user.id,status=True)
        if accountapproval:
            return redirect('teacher/teacher-dashboard')
        else:
            return render(request,'teacher/teacher_wait_for_approval.html')
    else:
        return redirect('admin-dashboard')



def adminclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return HttpResponseRedirect('adminlogin')


@login_required(login_url='adminlogin')
def admin_dashboard_view(request):
    dict={
    'total_student':SMODEL.Student.objects.all().count(),
    'total_teacher':TMODEL.Teacher.objects.all().filter(status=True).count(),
    'total_course':models.Course.objects.all().count(),
    'total_question':models.Question.objects.all().count(),
    }
    return render(request,'exam/admin_dashboard.html',context=dict)
@login_required(login_url='adminlogin')
def upload_academic_calendar(request):
    if request.method == "POST":
        form = AcademicCalendarUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Academic Calendar uploaded successfully!")
            return redirect("admin-dashboard")
    else:
        form = AcademicCalendarUploadForm()
    return render(request, "exam/upload_academic_calendar.html", {"form": form})

@login_required(login_url='adminlogin')
def admin_teacher_view(request):
    dict={
    'total_teacher':TMODEL.Teacher.objects.all().filter(status=True).count(),
    'pending_teacher':TMODEL.Teacher.objects.all().filter(status=False).count(),
    'salary':TMODEL.Teacher.objects.all().filter(status=True).aggregate(Sum('salary'))['salary__sum'],
    }
    return render(request,'exam/admin_teacher.html',context=dict)

@login_required(login_url='adminlogin')
def admin_view_teacher_view(request):
    teachers= TMODEL.Teacher.objects.all().filter(status=True)
    return render(request,'exam/admin_view_teacher.html',{'teachers':teachers})


@login_required(login_url='adminlogin')
def update_teacher_view(request,pk):
    teacher=TMODEL.Teacher.objects.get(id=pk)
    user=TMODEL.User.objects.get(id=teacher.user_id)
    userForm=TFORM.TeacherUserForm(instance=user)
    teacherForm=TFORM.TeacherForm(request.FILES,instance=teacher)
    mydict={'userForm':userForm,'teacherForm':teacherForm}
    if request.method=='POST':
        userForm=TFORM.TeacherUserForm(request.POST,instance=user)
        teacherForm=TFORM.TeacherForm(request.POST,request.FILES,instance=teacher)
        if userForm.is_valid() and teacherForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            teacherForm.save()
            return redirect('admin-view-teacher')
    return render(request,'exam/update_teacher.html',context=mydict)



@login_required(login_url='adminlogin')
def delete_teacher_view(request,pk):
    teacher=TMODEL.Teacher.objects.get(id=pk)
    user=User.objects.get(id=teacher.user_id)
    user.delete()
    teacher.delete()
    return HttpResponseRedirect('/admin-view-teacher')




@login_required(login_url='adminlogin')
def admin_view_pending_teacher_view(request):
    teachers= TMODEL.Teacher.objects.all().filter(status=False)
    return render(request,'exam/admin_view_pending_teacher.html',{'teachers':teachers})


@login_required(login_url='adminlogin')
def approve_teacher_view(request,pk):
    teacherSalary=forms.TeacherSalaryForm()
    if request.method=='POST':
        teacherSalary=forms.TeacherSalaryForm(request.POST)
        if teacherSalary.is_valid():
            teacher=TMODEL.Teacher.objects.get(id=pk)
            teacher.salary=teacherSalary.cleaned_data['salary']
            teacher.status=True
            teacher.save()
        else:
            print("form is invalid")
        return HttpResponseRedirect('/admin-view-pending-teacher')
    return render(request,'exam/salary_form.html',{'teacherSalary':teacherSalary})

@login_required(login_url='adminlogin')
def reject_teacher_view(request,pk):
    teacher=TMODEL.Teacher.objects.get(id=pk)
    user=User.objects.get(id=teacher.user_id)
    user.delete()
    teacher.delete()
    return HttpResponseRedirect('/admin-view-pending-teacher')

@login_required(login_url='adminlogin')
def admin_view_teacher_salary_view(request):
    teachers= TMODEL.Teacher.objects.all().filter(status=True)
    return render(request,'exam/admin_view_teacher_salary.html',{'teachers':teachers})




@login_required(login_url='adminlogin')
def admin_student_view(request):
    dict={
    'total_student':SMODEL.Student.objects.all().count(),
    }
    return render(request,'exam/admin_student.html',context=dict)

@login_required(login_url='adminlogin')
def admin_view_student_view(request):
    students= SMODEL.Student.objects.all()
    return render(request,'exam/admin_view_student.html',{'students':students})



@login_required(login_url='adminlogin')
def update_student_view(request,pk):
    student=SMODEL.Student.objects.get(id=pk)
    user=SMODEL.User.objects.get(id=student.user_id)
    userForm=SFORM.StudentUserForm(instance=user)
    studentForm=SFORM.StudentForm(request.FILES,instance=student)
    mydict={'userForm':userForm,'studentForm':studentForm}
    if request.method=='POST':
        userForm=SFORM.StudentUserForm(request.POST,instance=user)
        studentForm=SFORM.StudentForm(request.POST,request.FILES,instance=student)
        if userForm.is_valid() and studentForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            studentForm.save()
            return redirect('admin-view-student')
    return render(request,'exam/update_student.html',context=mydict)



@login_required(login_url='adminlogin')
def delete_student_view(request,pk):
    student=SMODEL.Student.objects.get(id=pk)
    user=User.objects.get(id=student.user_id)
    user.delete()
    student.delete()
    return HttpResponseRedirect('/admin-view-student')


@login_required(login_url='adminlogin')
def admin_course_view(request):
    return render(request,'exam/admin_course.html')


@login_required(login_url='adminlogin')
def admin_add_course_view(request):
    courseForm=forms.CourseForm()
    if request.method=='POST':
        courseForm=forms.CourseForm(request.POST)
        if courseForm.is_valid():        
            courseForm.save()
        else:
            print("form is invalid")
        return HttpResponseRedirect('/admin-view-course')
    return render(request,'exam/admin_add_course.html',{'courseForm':courseForm})


@login_required(login_url='adminlogin')
def admin_view_course_view(request):
    courses = models.Course.objects.all()
    return render(request,'exam/admin_view_course.html',{'courses':courses})

@login_required(login_url='adminlogin')
def delete_course_view(request,pk):
    course=models.Course.objects.get(id=pk)
    course.delete()
    return HttpResponseRedirect('/admin-view-course')



@login_required(login_url='adminlogin')
def admin_question_view(request):
    return render(request,'exam/admin_question.html')
@login_required(login_url='adminlogin')
def admin_add_question_view(request):
    questionForm = forms.QuestionForm()  # Default MCQ Form

    if request.method == 'POST':
        question_type = request.POST.get("questionType")  # Get question type
        print(f"✅ Received Question Type: {question_type}")  # Debugging

        # Select form based on question type
        if question_type == "MCQ":
            questionForm = forms.QuestionForm(request.POST)  # MCQ Form
        else:
            questionForm = forms.SubjectiveQuestionForm(request.POST)  # Subjective Form

        if not questionForm.is_valid():
            print("❌ Form Validation Failed:", questionForm.errors)  # Debugging
            messages.error(request, f"Form validation failed: {questionForm.errors}")
            return render(request, 'exam/admin_add_question.html', {'questionForm': questionForm})

        try:
            print("✅ Form is Valid! Received POST Data:", request.POST)  # Debugging

            # Get course ID
            course_id = request.POST.get('courseID')
            if not course_id:
                print("❌ Course ID is missing!")  # Debugging
                messages.error(request, "Course ID is missing. Please select a course.")
                return render(request, 'exam/admin_add_question.html', {'questionForm': questionForm})

            # Fetch the course object
            course = models.Course.objects.get(id=course_id)
            print(f"✅ Retrieved Course: {course}")  # Debugging

            # Save the question
            question = questionForm.save(commit=False)
            question.course = course
            question.save()

            print(f"✅ Question Saved: {question}")  # Debugging
            messages.success(request, "✅ Question added successfully!")
            return HttpResponseRedirect('/admin-view-question')

        except models.Course.DoesNotExist:
            print(f"❌ Error: Course with ID {course_id} does not exist!")  # Debugging
            messages.error(request, f"Error: Course with ID {course_id} does not exist.")
        except Exception as e:
            print(f"❌ Error Saving Question: {e}")  # Debugging
            print(traceback.format_exc())  # Full error details
            messages.error(request, f"Error Saving Question: {e}")

    return render(request, 'exam/admin_add_question.html', {'questionForm': questionForm})
import json

def extract_question_pattern(pattern_file):
    """
    Extracts the question distribution pattern from the uploaded JSON file.
    Example format:
    {
        "MCQ": 5,
        "SUB": 2
    }
    """
    try:
        with pattern_file.open('r') as file:
            data = json.load(file)
        return data
    except Exception as e:
        print(f"Error parsing question pattern: {e}")
        return {"MCQ": 5, "SUB": 2}  # Default values

@login_required(login_url='adminlogin')
def admin_view_question_view(request):
    courses= models.Course.objects.all()
    print(f"✅ Retrieved Courses: {courses}")
    return render(request,'exam/admin_view_question.html',{'courses':courses})

@login_required(login_url='adminlogin')
def view_question_view(request,pk):
    questions=models.Question.objects.all().filter(course_id=pk)
    print(f"✅ Retrieved Questions: {questions}")
    return render(request,'exam/view_question.html',{'questions':questions})

@login_required(login_url='adminlogin')
def delete_question_view(request,pk):
    question=models.Question.objects.get(id=pk)
    question.delete()
    return HttpResponseRedirect('/admin-view-question')

@login_required(login_url='adminlogin')
def admin_view_student_marks_view(request):
    students= SMODEL.Student.objects.all()
    return render(request,'exam/admin_view_student_marks.html',{'students':students})

@login_required(login_url='adminlogin')
def admin_view_marks_view(request,pk):
    courses = models.Course.objects.all()
    response =  render(request,'exam/admin_view_marks.html',{'courses':courses})
    response.set_cookie('student_id',str(pk))
    return response

@login_required(login_url='adminlogin')
def admin_check_marks_view(request,pk):
    course = models.Course.objects.get(id=pk)
    student_id = request.COOKIES.get('student_id')
    student= SMODEL.Student.objects.get(id=student_id)

    results= models.Result.objects.all().filter(exam=course).filter(student=student)
    return render(request,'exam/admin_check_marks.html',{'results':results})


@login_required(login_url='adminlogin')
def upload_syllabus(request):
    if request.method == "POST":
        form = SyllabusUploadForm(request.POST, request.FILES)
        if form.is_valid():
            course_id = request.POST.get("course_id")  # Get selected course
            print("Received course_id:", course_id)  # Debugging line
            course = Course.objects.get(id=course_id)
            syllabus = Syllabus(file=request.FILES["file"], course=course)
            syllabus.save()
            messages.success(request, "Syllabus uploaded successfully!")
            return redirect("admin-dashboard")
    else:
        form = SyllabusUploadForm()
    courses = Course.objects.all()
    return render(request, "exam/upload_syllabus.html", {"form": form, "courses": courses})


def aboutus_view(request):
    return render(request,'exam/aboutus.html')

def contactus_view(request):
    sub = forms.ContactusForm()
    if request.method == 'POST':
        sub = forms.ContactusForm(request.POST)
        if sub.is_valid():
            email = sub.cleaned_data['Email']
            name=sub.cleaned_data['Name']
            message = sub.cleaned_data['Message']
            send_mail(str(name)+' || '+str(email),message,settings.EMAIL_HOST_USER, settings.EMAIL_RECEIVING_USER, fail_silently = False)
            return render(request, 'exam/contactussuccess.html')
    return render(request, 'exam/contactus.html', {'form':sub})
def generate_exam_questions(course):
    try:
        question_pattern = QMODEL.QuestionPattern.objects.get(course=course)
        mcq_count = question_pattern.mcq_count
        sub_count = question_pattern.sub_count
    except QMODEL.QuestionPattern.DoesNotExist:
        mcq_count = 5  # Default MCQ count
        sub_count = 2  # Default Subjective count
        print(f"⚠️ No QuestionPattern found for {course}. Using default values: MCQ={mcq_count}, SUB={sub_count}")

    # ✅ Fetch MCQs from the Question model
    obj_questions = list(QMODEL.Question.objects.filter(course=course, question_type='MCQ').order_by('?')[:mcq_count])

    # ✅ Fetch subjective questions from BOTH models (Ensuring we access the right field)
    sub_questions_exam = list(QMODEL.SubjectiveQuestion.objects.filter(course=course).order_by('?')[:sub_count])
    sub_questions_teacher = list(TMODEL.SubjectiveQuestion.objects.filter(course=course).order_by('?')[:sub_count])

    # ✅ Combine and shuffle
    all_sub_questions = sub_questions_teacher + sub_questions_exam
    all_questions = obj_questions + all_sub_questions
    random.shuffle(all_questions)

    # ✅ Debugging: Print retrieved questions
    print(f"✅ Retrieved {len(obj_questions)} MCQ Questions:", obj_questions)
    print(f"✅ Retrieved {len(sub_questions_exam)} Exam Subjective Questions:", sub_questions_exam)
    print(f"✅ Retrieved {len(sub_questions_teacher)} Teacher Subjective Questions:", sub_questions_teacher)
    print(f"✅ Final Shuffled Exam Questions ({len(all_questions)}):", all_questions)

    return all_questions

def evaluate_subjective_answer(student_answer, correct_answer):
    if not student_answer:  # If no answer provided
        return 0
    return round(SequenceMatcher(None, student_answer.lower(), correct_answer.lower()).ratio() * 100)


@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def calculate_marks_view(request):
    if request.COOKIES.get('course_id'):
        course_id = request.COOKIES.get('course_id')
        course = QMODEL.Course.objects.get(id=course_id)

        total_marks = 0
        questions = list(QMODEL.Question.objects.filter(course=course)) + list(
            QMODEL.SubjectiveQuestion.objects.filter(course=course))

        student = models.Student.objects.get(user_id=request.user.id)
        result = QMODEL.Result()
        result.exam = course
        result.student = student

        for question in questions:
            selected_ans = request.COOKIES.get(str(question.id))

            if question.question_type == 'MCQ':  # Multiple Choice
                if selected_ans == question.answer:
                    total_marks += question.marks

            elif question.question_type == 'Subjective':  # Subjective Answer
                if selected_ans:
                    similarity = evaluate_subjective_answer(selected_ans, question.answer)
                    obtained_marks = round((similarity / 100) * question.marks)
                    total_marks += obtained_marks

        result.marks = total_marks
        result.save()

        return HttpResponseRedirect('view-result')
