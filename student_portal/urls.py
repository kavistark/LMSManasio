# candidate/urls.py
from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    # Home
    path('', index, name='candidate_home'),

    # Authentication
    path('student-login/', student_login, name='student_login'),
    path('logout/', candidate_logout_view, name='logout'),

    # Dashboard
    path('student-dashboard/', student_dashboard, name='student_dashboard'),
    path('dashboard-student/', candidate_study_images, name='dashboard_student'),

    # Progress & Reports
    path('student-progress-report/', student_progress_report, name='student_progress_report'),
    path('progress/', progress_tracking_view, name='progress_tracking'),

    # Career
    path('career-opportunities/', career_opportunities_view, name='student_career_opportunities'),
    path('career-opportunities/<int:job_id>/', job_post_view, name='job_post'),

    # Interview & QnA
    path('mock-interview/', student_mock_interview, name='student_mock_interview'),
    path('qna/', qna_forum_view, name='qna_forum'),

    # Feedback
    path('feedback/', feedback_view, name='feedback'),

    # Calendar
    path('student-calendar/', student_calendar_view, name='student_calendar'),

    # Study Material
    path('material/', matrical_page, name='matrical_page'),
    path('material/<int:course_id>/', matrical_page, name='matrical_page'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
