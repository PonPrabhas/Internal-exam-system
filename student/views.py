from django.shortcuts import render,redirect,reverse
from . import forms,models
from django.db.models import Sum
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required,user_passes_test
from django.conf import settings
from datetime import date, timedelta
from exam import models as QMODEL
from teacher import models as TMODEL
from exam.views import generate_exam_questions
from student.models import Student # Import Result model
from exam.models import Question, Result, Course    # ✅ Correct import
from django.contrib import messages
from exam.models import Syllabus  # Add this import
from exam.models import AcademicCalendar
from exam.models import SubjectiveQuestion
from exam.models import StudentAnswer
#for showing signup/login button for student
def studentclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'student/studentclick.html')

def student_signup_view(request):
    userForm=forms.StudentUserForm()
    studentForm=forms.StudentForm()
    mydict={'userForm':userForm,'studentForm':studentForm}
    if request.method=='POST':
        userForm=forms.StudentUserForm(request.POST)
        studentForm=forms.StudentForm(request.POST,request.FILES)
        if userForm.is_valid() and studentForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            student=studentForm.save(commit=False)
            student.user=user
            student.save()
            my_student_group = Group.objects.get_or_create(name='STUDENT')
            my_student_group[0].user_set.add(user)
        return HttpResponseRedirect('studentlogin')
    return render(request,'student/studentsignup.html',context=mydict)

def is_student(user):
    return user.groups.filter(name='STUDENT').exists()

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_dashboard_view(request):
    dict = {
        'total_course': QMODEL.Course.objects.all().count(),
        'total_question': QMODEL.Question.objects.all().count(),
        # 'syllabi': QMODEL.Syllabus.objects.all()  # Add this line to pass syllabus files
    }
    return render(request, 'student/student_dashboard.html', context=dict)
@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_syllabus_view(request):
    syllabi = Syllabus.objects.all()
    return render(request, 'student/student_syllabus.html', {'syllabi': syllabi})
def student_academic_calendar(request):
    calendar = AcademicCalendar.objects.last()  # Get latest upload
    return render(request, "student/view_academic_calendar.html", {"calendar": calendar})
@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_exam_view(request):
    courses=QMODEL.Course.objects.all()
    return render(request,'student/student_exam.html',{'courses':courses})

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def take_exam_view(request,pk):
    course=QMODEL.Course.objects.get(id=pk)
    total_questions=QMODEL.Question.objects.all().filter(course=course).count()
    questions=QMODEL.Question.objects.all().filter(course=course)
    total_marks=0
    for q in questions:
        total_marks=total_marks + q.marks

    return render(request,'student/take_exam.html',{'course':course,'total_questions':total_questions,'total_marks':total_marks})
@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def start_exam_view(request, pk):
    course = QMODEL.Course.objects.get(id=pk)
    all_questions = generate_exam_questions(course)
    request.session['course_id'] = pk  # ✅ Store course_id properly
    request.session.modified = True  # ✅ Ensure session updates
    # ✅ Separate MCQs and Subjective Questions
    obj_questions = [q for q in all_questions if hasattr(q, 'question_type') and q.question_type == 'MCQ']
    sub_questions = [q for q in all_questions if isinstance(q, QMODEL.SubjectiveQuestion)]

    # Debugging: Check the count of questions passed
    print("✅ MCQ Questions Count:", len(obj_questions))
    print("✅ Subjective Questions Count:", len(sub_questions))

    # ✅ Debugging Statements
    print("🔵 Session Updated with course_id:", request.session.get('course_id'))
    print("✅ MCQ Questions Count:", len(obj_questions))
    print("✅ Subjective Questions Count:", len(sub_questions))
    obj_questions = []
    sub_questions = []
    for q in all_questions:
        print(q.__dict__)  # Debugging each question object
        if hasattr(q, 'option1'):  # Check if it's an MCQ
            obj_questions.append(q)
        else:  # Otherwise, it's a subjective question
            sub_questions.append(q)
    # Save shown question IDs
    request.session['shown_mcq_ids'] = [q.id for q in obj_questions]
    request.session['shown_subjective_ids'] = [q.id for q in sub_questions]
    request.session.modified = True
    response = render(request, 'student/start_exam.html', {
        'course': course,
        'obj_questions': obj_questions,
        'sub_questions': sub_questions  # ✅ Now `sub_questions` is passed
    })
    return response

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def calculate_marks_view(request):
    if request.method == 'POST':
        print("🔵 Received POST Data:", request.POST)
        print("🔵 Session Data:", request.session.items())

        total_marks = 0
        obtained_marks = 0
        student = Student.objects.get(user_id=request.user.id)

        course_id = request.session.get('course_id')
        if not course_id:
            messages.error(request, "Session expired! Please restart the exam.")
            return redirect('student-exam')  # ✅ Redirect to exam page instead of result page



        try:
            exam = Course.objects.get(id=course_id)
            print("✅ Exam Found:", exam.course_name)
        except Course.DoesNotExist:
            messages.error(request, "Exam not found.")
            return redirect('student-exam')



        questions = Question.objects.filter(course=exam)
        print("✅ Fetched Questions:", list(questions))
        shown_subjective_ids = request.session.get('shown_subjective_ids', [])
        subjective_questions = SubjectiveQuestion.objects.filter(id__in=shown_subjective_ids)

        for sq in subjective_questions:
            answer_text = request.POST.get(f'answer_{sq.id}', "").strip()
            if answer_text:
                StudentAnswer.objects.create(
                    student=student,
                    question=sq,
                    answer_text=answer_text
                )
                print(f"✅ Saved Subjective Answer for QID {sq.id}: {answer_text}")
            else:
                print(f"⚠️ No subjective answer submitted for QID {sq.id}")

        for q in questions:
            correct_option = q.answer
            submitted_answer = request.POST.get(f'answer_{q.id}', None)

            print(f"📌 Question: {q.question}")
            print(f"✅ Correct Answer: {correct_option}")
            print(f"📩 Submitted Answer: {submitted_answer}")

            if submitted_answer == correct_option:
                obtained_marks += q.marks
            total_marks += q.marks

        print(f"🎯 Total Marks: {total_marks}, Obtained Marks: {obtained_marks}")

        # Save the result
        result = Result.objects.create(student=student, exam=exam, marks=obtained_marks)

        print("✅ Result Saved Successfully!")
        # ✅ Pass a flag to the template if there are subjective questions
        has_subjective = subjective_questions.exists()

        return render(request, 'student/check_marks.html', {
            'results': [result],
            'has_subjective': has_subjective
        })

        # return render(request, 'student/check_marks.html', {'results': [result]})

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def check_marks_view(request,pk):
    course=QMODEL.Course.objects.get(id=pk)
    student = models.Student.objects.get(user_id=request.user.id)
    results= QMODEL.Result.objects.all().filter(exam=course).filter(student=student)
    return render(request,'student/check_marks.html',{'results':results})
@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_marks_view(request):
    student = Student.objects.get(user=request.user)
    results = Result.objects.filter(student=student)
    return render(request, 'student/view_result.html', {'results': results})
@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_marks_view(request):
    student = Student.objects.get(user=request.user)
    # Fetch all courses the student has results for
    courses = Course.objects.filter(result__student=student).distinct()
    return render(request, 'student/student_marks.html', {'courses': courses})
@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def view_result_view(request):
    student = Student.objects.get(user=request.user)  # ✅ Get logged-in student
    results = Result.objects.filter(student=student)  # ✅ Fetch all results for this student
    return render(request, 'student/view_result.html', {'results': results})




@login_required(login_url='studentlogin')
def log_malpractice_attempt(request):
    if request.method == "POST":
        student = request.user
        exam_id = request.POST.get("exam_id")
        action = request.POST.get("action")  # e.g., "tab_switch" or "copy_paste"
        models.MalpracticeLog.objects.create(student=student, exam_id=exam_id, action=action)
        return JsonResponse({"status": "logged"})
    return JsonResponse({"error": "Invalid request"}, status=400)
