from django.shortcuts import render,redirect,reverse
from . import forms,models
from django.db.models import Sum
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required,user_passes_test
from django.conf import settings
from datetime import date, timedelta
from exam import models as QMODEL
from student import models as SMODEL
from exam import forms as QFORM
import numpy as np
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from .models import SubjectiveQuestion
from .forms import SubjectiveQuestionForm
import PyPDF2
from django.http import JsonResponse
from exam.models import SubjectiveQuestion, StudentAnswer  # make sure these imports exist
import json



#for showing signup/login button for teacher
def teacherclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'teacher/teacherclick.html')

def teacher_signup_view(request):
    userForm=forms.TeacherUserForm()
    teacherForm=forms.TeacherForm()
    mydict={'userForm':userForm,'teacherForm':teacherForm}
    if request.method=='POST':
        userForm=forms.TeacherUserForm(request.POST)
        teacherForm=forms.TeacherForm(request.POST,request.FILES)
        if userForm.is_valid() and teacherForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            teacher=teacherForm.save(commit=False)
            teacher.user=user
            teacher.save()
            my_teacher_group = Group.objects.get_or_create(name='TEACHER')
            my_teacher_group[0].user_set.add(user)
        return HttpResponseRedirect('teacherlogin')
    return render(request,'teacher/teachersignup.html',context=mydict)



def is_teacher(user):
    return user.groups.filter(name='TEACHER').exists()

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_dashboard_view(request):
    dict={
    'total_course':QMODEL.Course.objects.all().count(),
    'total_question':QMODEL.Question.objects.all().count(),
    'total_student':SMODEL.Student.objects.all().count()
    }
    return render(request,'teacher/teacher_dashboard.html',context=dict)

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_exam_view(request):
    return render(request,'teacher/teacher_exam.html')


@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_add_exam_view(request):
    courseForm=QFORM.CourseForm()
    if request.method=='POST':
        courseForm=QFORM.CourseForm(request.POST)
        if courseForm.is_valid():        
            courseForm.save()
        else:
            print("form is invalid")
        return HttpResponseRedirect('/teacher/teacher-view-exam')
    return render(request,'teacher/teacher_add_exam.html',{'courseForm':courseForm})

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_view_exam_view(request):
    courses = QMODEL.Course.objects.all()
    return render(request,'teacher/teacher_view_exam.html',{'courses':courses})

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def delete_exam_view(request,pk):
    course=QMODEL.Course.objects.get(id=pk)
    course.delete()
    return HttpResponseRedirect('/teacher/teacher-view-exam')

@login_required(login_url='adminlogin')
def teacher_question_view(request):
    return render(request,'teacher/teacher_question.html')


@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_add_question_view(request):
    questionForm = QFORM.QuestionForm()

    if request.method == 'POST':
        questionForm = QFORM.QuestionForm(request.POST)

        if questionForm.is_valid():
            question = questionForm.save(commit=False)
            try:
                course = QMODEL.Course.objects.get(id=request.POST.get('courseID'))
                question.course = course
                question.save()
                return HttpResponseRedirect('/teacher/teacher-view-question')
            except QMODEL.Course.DoesNotExist:
                print("❌ Error: Course not found")
        else:
            print("❌ Form Errors:", questionForm.errors)  # Debugging

    return render(request, 'teacher/teacher_add_question.html', {'questionForm': questionForm})


@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_view_question_view(request):
    courses= QMODEL.Course.objects.all()
    return render(request,'teacher/teacher_view_question.html',{'courses':courses})

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def see_question_view(request,pk):
    questions=QMODEL.Question.objects.all().filter(course_id=pk)
    return render(request,'teacher/see_question.html',{'questions':questions})
def extract_text_from_file(file):
    """Extract text from a given file (TXT or PDF)"""
    text = ""
    if file.name.endswith('.txt'):
        text = file.read().decode('utf-8')
    elif file.name.endswith('.pdf'):
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text() + " "
    return text
@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_generate_subjective_questions_view(request):
    if request.method == "POST":
        form = SubjectiveQuestionForm(request.POST, request.FILES)
        if form.is_valid():
            teacher = request.user.teacher
            course = form.cleaned_data['course']
            file = request.FILES['content']
            text = extract_text_from_file(file)

            question_patterns = [
                "Explain in detail ",
                "Define ",
                "Write a short note on ",
                "What do you mean by "
            ]

            grammar = r"""
                CHUNK: {<NN>+<IN|DT>*<NN>+}
                {<NN>+<IN|DT>*<NNP>+}
                {<NNP>+<NNS>*}
            """

            sentences = sent_tokenize(text)
            cp = nltk.RegexpParser(grammar)
            question_answer_dict = {}

            for sentence in sentences:
                tagged_words = nltk.pos_tag(word_tokenize(sentence))
                tree = cp.parse(tagged_words)

                for subtree in tree.subtrees():
                    if subtree.label() == "CHUNK":
                        temp = " ".join(word for word, _ in subtree).strip().upper()
                        if temp not in question_answer_dict and len(word_tokenize(sentence)) > 20:
                            question_answer_dict[temp] = sentence

            keyword_list = list(question_answer_dict.keys())
            for _ in range(min(10, len(keyword_list))):  # Generate up to 10 questions
                rand_num = np.random.randint(0, len(keyword_list))
                selected_key = keyword_list[rand_num]
                answer = question_answer_dict[selected_key]
                question = question_patterns[rand_num % 4] + selected_key + "."

                # Save the question to the database
                SubjectiveQuestion.objects.create(
                    teacher=teacher,
                    course=course,
                    question_text=question,
                    answer_text=answer
                )

            return redirect('teacher-view-subjective-questions')

    else:
        form = SubjectiveQuestionForm()

    return render(request, 'teacher/teacher_generate_subjective_questions.html', {'form': form})
def teacher_subjective_questions(request):
    return render(request, 'teacher/teacher_subjective_questions.html')
@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_upload_subjective_questions_view(request):
    if request.method == "POST":
        form = SubjectiveQuestionForm(request.POST, request.FILES)
        if form.is_valid():
            teacher = request.user.teacher
            course = form.cleaned_data['course']
            file = request.FILES['content']
            text = extract_text_from_file(file)  # Extract text using existing function

            # Splitting extracted text into questions based on line breaks
            questions = text.split("\n")
            for line in questions:
                line = line.strip()
                if line and "?" in line:  # Assuming each question ends with '?'
                    SubjectiveQuestion.objects.create(
                        teacher=teacher,
                        course=course,
                        question_text=line,
                        answer_text="Answer to be provided"
                    )

            return redirect('teacher-view-subjective-questions')

    else:
        form = SubjectiveQuestionForm()

    return render(request, 'teacher/teacher_upload_subjective_questions.html', {'form': form})

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def view_subjective_questions(request):
    # Get all questions ordered by course
    questions = SubjectiveQuestion.objects.all().order_by('course')
    print("DEBUG: Questions passed to template:", questions)  # Add this line
    # Group questions by course
    course_questions = {}
    for question in questions:
        course = question.course
        if course not in course_questions:
            course_questions[course] = []
        course_questions[course].append({
            "id": question.id,
            "question_text": question.question,

            "marks": question.marks if question.marks is not None else 0,  # Ensure marks persist
        } )

    return render(request, 'teacher/teacher_view_subjective_questions.html', {'course_questions': course_questions})

def update_marks(request, question_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))  # Ensure correct data parsing
            new_marks = data.get("marks")

            if new_marks is None or new_marks.strip() == "":
                return JsonResponse({"success": False, "error": "Invalid marks input."})

            question = SubjectiveQuestion.objects.get(id=question_id)
            print(f"Before Update: Question ID {question.id}, Marks: {question.marks}")  # Debugging

            question.marks = int(new_marks)
            question.save()

            print(f"After Update: Question ID {question.id}, Marks: {question.marks}")  # Debugging

            return JsonResponse({"success": True, "marks": question.marks})
        except Exception as e:
            print("Error:", str(e))  # Debugging
            return JsonResponse({"success": False, "error": str(e)})
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

@user_passes_test(is_teacher)
def delete_subjective_question(request, pk):
    question = SubjectiveQuestion.objects.get(id=pk)
    question.delete()

    return redirect('teacher-view-subjective-questions')


@login_required
def review_subjective_answers_view(request):
    # Fetch all subjective answers submitted by students
    answers = StudentAnswer.objects.filter(question__question_type='subjective')  # or however you define subjective
    context = {
        'answers': answers,
    }
    return render(request, 'teacher/review_subjective_answers.html', context)

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def remove_question_view(request,pk):
    question=QMODEL.Question.objects.get(id=pk)
    question.delete()
    return HttpResponseRedirect('/teacher/teacher-view-question')
