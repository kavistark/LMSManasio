from django.urls import path
from . import views

urlpatterns = [

    # =====================================================
    # 🔐 AUTH
    # =====================================================
    path('', views.admin_login, name='admin_login'),
    path('logout/', views.admin_logout, name='admin_logout'),

    # =====================================================
    # 🏠 DASHBOARD
    # =====================================================
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # =====================================================
    # 🎓 COLLEGE
    # =====================================================
    path('colleges/add/', views.add_college_view, name='add_college'),
    path('colleges/manage/', views.manage_colleges_view, name='manage_colleges'),
    path('colleges/delete/<int:college_id>/', views.delete_college_view, name='delete_college'),

    # =====================================================
    # 👨‍🎓 STUDENTS
    # =====================================================
    path('students/add/', views.add_student_view, name='add_student'),
    path('students/manage/', views.manage_students_view, name='manage_students'),
    path('students/delete/<int:student_id>/', views.delete_student_view, name='delete_student'),

    # =====================================================
    # 📈 PROGRESS TRACKING
    # =====================================================
    path('students/progress/', views.progress_tracking_view, name='progress_tracking_view'),

    # =====================================================
    # 📚 COURSES
    # =====================================================
    path('courses/add/', views.add_course_view, name='add_course'),
    path('courses/manage/', views.manage_courses_view, name='manage_courses'),
    path('courses/<str:course_code>/', views.manage_course_view, name='manage_course'),
    path('courses/delete/<str:course_code>/', views.delete_course_view, name='delete_course'),

    # Course folders & materials
    path('courses/<int:course_id>/create-folder/', views.create_folder, name='create_folder'),
    path('courses/<int:course_id>/upload-material/', views.upload_course_material, name='upload_course_material'),
    path('folders/delete/<int:folder_id>/', views.delete_folder_view, name='delete_folder'),
    path('materials/delete/<int:material_id>/', views.delete_material_view, name='delete_material'),

    # =====================================================
    # 📌 ASSIGNMENTS & TASKS
    # =====================================================
    path('assign-course/', views.assign_course_view, name='assign_course'),
    path('assign-task/', views.assign_task_view, name='assign_task'),

    # =====================================================
    # 📢 LIVE CLASS / BROADCAST
    # =====================================================
    path('live-class/', views.live_class_view, name='live_class'),

    # =====================================================
    # 💼 CAREER OPPORTUNITIES
    # =====================================================
    path('careers/', views.career_opportunities_view, name='career_opportunities'),
    path('careers/delete/<int:job_id>/', views.delete_job_view, name='delete_job'),

    # =====================================================
    # 📅 CALENDAR
    # =====================================================
    path('calendar/', views.calendar_event_view, name='calendar'),

    # =====================================================
    # 🖼 STUDY IMAGES
    # =====================================================
    path('study-images/', views.upload_study_image, name='upload_study_image'),
    path('study-images/delete/<int:image_id>/', views.delete_study_image, name='delete_study_image'),
    path('upload-image/', views.upload_study_image, name='upload_study_image'),
    path('delete-study-image/<int:image_id>/', views.delete_study_image, name='delete_study_image'),
    path('edit-material/<int:material_id>/',views.edit_course_material,name='edit_course_material'),

    path('schedule-event/', views.calendar_event_view, name='schedule_event'),

]
