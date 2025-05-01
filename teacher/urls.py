from django.urls import path
from teacher import views
from django.contrib.auth.views import LoginView

urlpatterns = [
path('teacherclick', views.teacherclick_view),
path('teacherlogin', LoginView.as_view(template_name='teacher/teacherlogin.html'),name='teacherlogin'),
path('teachersignup', views.teacher_signup_view,name='teachersignup'),
path('teacher-dashboard', views.teacher_dashboard_view,name='teacher-dashboard'),
path('teacher-exam', views.teacher_exam_view,name='teacher-exam'),
path('teacher-add-exam', views.teacher_add_exam_view,name='teacher-add-exam'),
path('teacher-upload-subjective-questions/', views.teacher_upload_subjective_questions_view, name='teacher-upload-subjective-questions'),

path('teacher-view-exam', views.teacher_view_exam_view,name='teacher-view-exam'),
path('update-marks/<int:question_id>/', views.update_marks, name='update-marks'),
path('delete-exam/<int:pk>', views.delete_exam_view,name='delete-exam'),


path('teacher-question', views.teacher_question_view,name='teacher-question'),
path('teacher-add-question', views.teacher_add_question_view,name='teacher-add-question'),
path('teacher-view-question', views.teacher_view_question_view,name='teacher-view-question'),
path('see-question/<int:pk>', views.see_question_view,name='see-question'),
path('remove-question/<int:pk>', views.remove_question_view,name='remove-question'),
path('teacher-generate-subjective-questions', views.teacher_generate_subjective_questions_view, name='teacher-generate-subjective-questions'),
path('teacher-subjective-questions', views.teacher_subjective_questions, name='teacher-subjective-questions'),
path('teacher-view-subjective-questions/', views.view_subjective_questions, name='teacher-view-subjective-questions'),  # ADD THIS
path('delete-subjective-question/<int:pk>/', views.delete_subjective_question, name='delete-subjective-question'),
path('teacher-review-subjective-answers/', views.review_subjective_answers_view, name='teacher-review-subjective-answers'),

]