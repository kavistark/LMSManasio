from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from admin_panel.models import *


# ================= HELPER =================
def get_logged_in_student(request):
    student_id = request.session.get('student_id')
    if not student_id:
        return None
    return get_object_or_404(Student, id=student_id)


def student_mock_interview(request):
    broadcast = BroadcastMessage.objects.first()
    return render(request, 'student_portal/cantidates/mock_interviews.html', {
        'broadcast_message': broadcast.message if broadcast else None
    })


# ================= AUTH =================
def student_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        roll = request.POST.get('roll')

        try:
            student = Student.objects.get(email=email, roll=roll, status='active')
            request.session['student_id'] = student.id
            return redirect('student_dashboard')
        except Student.DoesNotExist:
            return render(request, 'student_portal/cantidates/student_login.html', {'error': 'Invalid credentials'})

    return render(request, 'student_portal/cantidates/student_login.html')


def candidate_logout_view(request):
    request.session.flush()
    return redirect('student_login')


# ================= HOME =================
def index(request):
    return render(request, 'student_portal/cantidates/index.html')


# ================= DASHBOARD =================
def student_dashboard(request):
    student = get_logged_in_student(request)
    if not student:
        return redirect('student_login')

    assignments = CourseAssignment.objects.filter(student=student).select_related('course')
    tasks = Task.objects.filter(student=student).order_by('-deadline')
    broadcast = BroadcastMessage.objects.first()

    return render(request, 'student_portal/cantidates/student_dashboard.html', {
        'student': student,
        'assignments': assignments,
        'tasks': tasks,
        'broadcast_message': broadcast.message if broadcast else None
    })


def candidate_study_images(request):
    student = get_logged_in_student(request)
    if not student:
        return redirect('student_login')

    assignments = CourseAssignment.objects.filter(student=student).select_related('course')
    tasks = Task.objects.filter(student=student).order_by('-deadline')
    broadcast = BroadcastMessage.objects.first()
    images = StudyImage.objects.all().order_by('-uploaded_at')

    return render(request, 'student_portal/cantidates/dashboard.html', {
        'student': student,
        'assignments': assignments,
        'tasks': tasks,
        'images': images,
        'broadcast_message': broadcast.message if broadcast else None
    })


# ================= PROGRESS REPORT =================
def student_progress_report(request):
    student_id = request.session.get('student_id')
    if not student_id:
        return redirect('student_login')

    student = get_object_or_404(Student, id=student_id)

    reports = ProgressReport.objects.filter(student=student).order_by('id')

    if reports.count() > 1:
        latest = reports.last()
        previous = reports[reports.count() - 2]

        improvement = {
            'interview_prep': latest.interview_prep - previous.interview_prep,
            'communication_skills': latest.communication_skills - previous.communication_skills,
            'resume_prep': latest.resume_prep - previous.resume_prep,
            'technical_prep': latest.technical_prep - previous.technical_prep,
            'mock_tests': latest.mock_tests - previous.mock_tests,
            'mock_interviews': latest.mock_interviews - previous.mock_interviews,
        }

        progress = latest

    elif reports.count() == 1:
        progress = reports.first()
        improvement = {
            'interview_prep': progress.interview_prep,
            'communication_skills': progress.communication_skills,
            'resume_prep': progress.resume_prep,
            'technical_prep': progress.technical_prep,
            'mock_tests': progress.mock_tests,
            'mock_interviews': progress.mock_interviews,
        }

    else:
        progress = {
            'interview_prep': 0,
            'communication_skills': 0,
            'resume_prep': 0,
            'technical_prep': 0,
            'mock_tests': 0,
            'mock_interviews': 0,
        }
        improvement = None

    return render(request, 'student_portal/cantidates/progress_report.html', {
        'student': student,
        'progress_report': progress,
        'improvement': improvement,
    })


# ================= CAREER =================
def career_opportunities_view(request):
    student = get_logged_in_student(request)
    if not student:
        return redirect('student_login')

    jobs = CareerOpportunities.objects.filter(mode=student.mode)

    return render(request, 'student_portal/cantidates/career_opportunities.html', {
        'student': student,
        'jobs': jobs
    })


def job_post_view(request, job_id):
    job = get_object_or_404(CareerOpportunities, id=job_id)
    return render(request, 'student_portal/cantidates/job_post.html', {'job': job})


# ================= PROGRESS TRACKING =================
def progress_tracking_view(request):
    student = get_logged_in_student(request)
    if not student:
        return redirect('student_login')

    tasks = Task.objects.filter(student=student)
    broadcast = BroadcastMessage.objects.first()

    completed = tasks.filter(status='completed').count()
    total = tasks.count()
    score = int((completed / total) * 100) if total else 0

    return render(request, 'student_portal/cantidates/progress_tracking.html', {
        'student': student,
        'tasks': tasks,
        'score': score,
        'broadcast_message': broadcast.message if broadcast else None
    })


# ================= QNA =================
def qna_forum_view(request):
    broadcast = BroadcastMessage.objects.first()
    return render(request, 'student_portal/cantidates/Q&A_forum.html', {
        'broadcast_message': broadcast.message if broadcast else None
    })


# ================= FEEDBACK =================
@csrf_protect
def feedback_view(request):
    broadcast = BroadcastMessage.objects.first()
    submitted = False

    if request.method == 'POST':
        message = request.POST.get('message')
        student = get_logged_in_student(request)

        if message and student:
            Feedback.objects.create(student=student, message=message)
            submitted = True

    return render(request, 'student_portal/cantidates/feedback.html', {
        'submitted': submitted,
        'broadcast_message': broadcast.message if broadcast else None
    })


# ================= STUDY MATERIAL =================
def matrical_page(request, course_id=None):
    student = get_logged_in_student(request)
    if not student:
        return redirect('student_login')

    assignments = CourseAssignment.objects.filter(student=student).select_related('course')
    broadcast = BroadcastMessage.objects.first()

    course = get_object_or_404(Course, id=course_id) if course_id else None

    return render(request, 'student_portal/cantidates/matrial_page.html', {
        'student': student,
        'assignments': assignments,
        'broadcast_message': broadcast.message if broadcast else None,
        'course': course,
    })


# ================= CALENDAR =================
def student_calendar_view(request):
    student = get_logged_in_student(request)
    if not student:
        return redirect('student_login')

    course_codes = CourseAssignment.objects.filter(student=student).values_list('course__code', flat=True)
    events = CalendarEvent.objects.filter(course__in=course_codes)

    event_list = []
    for e in events:
        event_list.append({
            'title': e.title,
            'course': e.course,
            'description': e.description or "",
            'meetingLink': e.meeting_link or "",
            'start': e.start.isoformat(),
            'end': e.end.isoformat() if e.end else None,
            'allDay': bool(e.all_day),   # ✅ FIXED
        })

    return render(request, 'student_portal/cantidates/calendar.html', {
        'events': event_list,
        'student': student
    })
