
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.utils.dateparse import parse_datetime
from django.utils import timezone

from rest_framework import viewsets

from superuser_admin.models import AdminUser
from .models import (
    College, Student, Course, CourseAssignment,
    CourseFolder, CourseMaterial, Task,
    BroadcastMessage, CalendarEvent, StudyImage,
    ProgressReport, CareerOpportunities
)
from .serializers import (
    StudentSerializer, CourseSerializer, TaskSerializer,
    CourseAssignmentSerializer, CalendarEventSerializer
)
from .forms import StudyImageForm


# =====================================================
# 🔐 ADMIN LOGIN DECORATOR (MUST BE ABOVE USAGE)
# =====================================================
def admin_required(view_func):
    """Protect admin pages from unauthorized access"""
    def wrapper(request, *args, **kwargs):
        if not request.session.get("admin_logged_in"):
            return redirect("admin_login")
        return view_func(request, *args, **kwargs)
    return wrapper


# =====================================================
# 🔐 AUTH: LOGIN / LOGOUT
# =====================================================
def admin_login(request):
    """
    Admin logs in using AdminUser created by Superuser.
    Password should be hashed if you used set_password/check_password in AdminUser.
    """
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()

        if not username or not password:
            messages.error(request, "Username and password are required.")
            return render(request, "admin_panel/login.html")

        try:
            admin = AdminUser.objects.get(username=username)
            # hashed password version
            if hasattr(admin, "check_password"):
                valid = admin.check_password(password)
            else:
                # fallback (NOT recommended) if your AdminUser still stores plain password
                valid = (admin.password == password)

            if valid:
                request.session["admin_logged_in"] = True
                request.session["admin_username"] = admin.username
                return redirect("admin_dashboard")

            messages.error(request, "Invalid Admin Credentials")
        except AdminUser.DoesNotExist:
            messages.error(request, "Invalid Admin Credentials")

    return render(request, "admin_panel/login1.html")


def admin_logout(request):
    request.session.flush()
    return redirect("admin_login")


# =====================================================
# 🏠 DASHBOARD
# =====================================================
def admin_dashboard(request):
    # 🔐 Correct session check
    if not request.session.get("admin_logged_in"):
        return redirect("admin_login")

    # 🛡 Safe DB queries (avoid crash if table missing)
    try:
        student_count = Student.objects.count()
    except Exception:
        student_count = 0

    try:
        course_count = Course.objects.count()
    except Exception:
        course_count = 0

    try:
        task_count = Task.objects.filter(
            status__in=["pending", "in_progress"]
        ).count()
    except Exception:
        task_count = 0

    try:
        assignments = list(
            CourseAssignment.objects
            .select_related("student", "course")
            .order_by("-date_assigned")[:5]
        )
    except Exception:
        assignments = []   # ← SAFE EMPTY LIST

    context = {
        "student_count": student_count,
        "course_count": course_count,
        "task_count": task_count,
        "assignments": assignments,
        "admin_name": request.session.get("admin_username"),
    }

    return render(request, "admin_panel\partials\dashboard.html", context)


# =====================================================
# 🎓 COLLEGE VIEWS
# =====================================================
@admin_required
def add_college_view(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        address = request.POST.get("address")
        description = request.POST.get("description")
        student_count = request.POST.get("student_count") or 0
        logo_image = request.FILES.get("logo_image")
        poster_image = request.FILES.get("poster_image")
        mode = request.POST.get("mode")

        if not email:
            messages.error(request, "Email is required.")
            return render(request, "admin_dashboard/partials/add_college.html")

        if College.objects.filter(email=email).exists():
            messages.error(request, "College with this email already exists.")
            return render(request, "admin_dashboard/partials/add_college.html")

        College.objects.create(
            name=name,
            email=email,
            address=address,
            description=description or "",
            student_count=int(student_count),
            logo_image=logo_image,
            poster_image=poster_image,
            mode=mode or "offline",
            status="active",
        )

        messages.success(request, "✅ College registered successfully!")
        return render(request, "admin_panel/partials/add_college.html")

    return render(request, "admin_panel/partials/add_college.html")


@admin_required
def manage_colleges_view(request):
    query = request.GET.get("q", "").strip()
    qs = College.objects.all()

    if query:
        # Your College model has address, not location (avoid crash)
        qs = qs.filter(Q(name__icontains=query) | Q(address__icontains=query) | Q(email__icontains=query))

    return render(
        request,
        "admin_dashboard/partials/manage_colleges.html",
        {"colleges": qs.order_by("-id"), "query": query},
    )


@admin_required
def delete_college_view(request, college_id):
    if request.method == "POST":
        college = get_object_or_404(College, id=college_id)
        college.delete()
        messages.success(request, "College deleted successfully.")
    return redirect("manage_colleges")


# =====================================================
# 👨‍🎓 STUDENT VIEWS
# =====================================================
@admin_required
def add_student_view(request):
    colleges = College.objects.all().order_by("name")

    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        roll = request.POST.get("roll")
        phone = request.POST.get("phone")
        address = request.POST.get("address")
        college_id = request.POST.get("college")
        mode = request.POST.get("mode")

        # 🔴 Required validation
        if not (name and email and roll and college_id):
            messages.error(request, "Name, Email, Roll and College are required.")
            return render(request, "admin_panel/partials/add_student.html", {"colleges": colleges})

        # 🔴 Duplicate checks
        if Student.objects.filter(email=email).exists():
            messages.error(request, "Student with this email already exists.")
            return render(request, "admin_panel/partials/add_student.html", {"colleges": colleges})

        if Student.objects.filter(roll=roll).exists():
            messages.error(request, "Student with this roll number already exists.")
            return render(request, "admin_panel/partials/add_student.html", {"colleges": colleges})

        # ✔ Safe FK lookup using ID
        college = get_object_or_404(College, id=college_id)

        # ✔ Create student
        Student.objects.create(
            name=name,
            email=email,
            roll=roll,
            phone=phone or "",
            address=address or "",
            college=college,
            mode=mode or "offline",
            status="active",
        )

        messages.success(request, "✅ Student added successfully!")
        return redirect("manage_students")   # ← better UX

    return render(request, "admin_panel/partials/add_student.html", {"colleges": colleges})

@admin_required
def manage_students_view(request):
    query = request.GET.get("q", "").strip()
    qs = Student.objects.select_related("college").all()

    if query:
        qs = qs.filter(Q(name__icontains=query) | Q(email__icontains=query) | Q(roll__icontains=query))

    return render(
        request,
        "admin_panel/partials/manage_students.html",
        {"students": qs.order_by("-id"), "query": query},
    )


@admin_required
def delete_student_view(request, student_id):
    if request.method == "POST":
        student = get_object_or_404(Student, id=student_id)
        student.delete()
        messages.success(request, "Student deleted successfully.")
    return redirect("manage_students")


# =====================================================
# 📈 PROGRESS TRACKING
# =====================================================
@admin_required
def progress_tracking_view(request):
    students = Student.objects.all().order_by("roll")

    if request.method == "POST":
        roll_no = (request.POST.get("roll-no") or "").strip()

        def as_int(key):
            try:
                return int(request.POST.get(key) or 0)
            except ValueError:
                return 0

        interview_prep = as_int("interview-prep")
        communication_skills = as_int("communication-skills")
        resume_prep = as_int("resume-prep")
        technical_prep = as_int("technical-prep")
        mock_tests = as_int("mock-tests")
        mock_interviews = as_int("mock-interviews")

        if not roll_no:
            return render(
                request,
                "admin_panel/partials/progress_tracking.html",
                {"error": "❌ Roll number is required!", "students": students},
            )

        try:
            # If your ProgressReport model uses roll_no as string (as you pasted),
            # store it directly; if you later change to FK Student, adjust here.
            ProgressReport.objects.create(
                roll_no=roll_no,
                interview_prep=interview_prep,
                communication_skills=communication_skills,
                resume_prep=resume_prep,
                technical_prep=technical_prep,
                mock_tests=mock_tests,
                mock_interviews=mock_interviews,
            )
            return render(
                request,
                "admin_panel/partials/progress_tracking.html",
                {"success": "✅ Student progress report added successfully!", "students": students},
            )
        except Exception:
            return render(
                request,
                "admin_panel/partials/progress_tracking.html",
                {"error": "❌ Error occurred adding progress report!", "students": students},
            )

    return render(request, "admin_panel/partials/progress_tracking.html", {"students": students})


# =====================================================
# 📚 COURSE VIEWS
# =====================================================
@admin_required
def add_course_view(request):
    if request.method == "POST":
        name = request.POST.get("name")
        code = request.POST.get("code")
        description = request.POST.get("description")
        thumbnail = request.FILES.get("thumbnail")

        if not (name and code):
            messages.error(request, "Course name and code are required.")
            return render(request, "admin_panel/partials/add_course.html")

        if Course.objects.filter(code=code).exists():
            messages.error(request, "Course code already exists.")
            return render(request, "admin_panel/partials/add_course.html")

        Course.objects.create(
            name=name,
            code=code,
            description=description or "",
            thumbnail=thumbnail,
        )
        messages.success(request, "✅ Course created successfully!")
        return render(request, "admin_panel/partials/add_course.html")

    return render(request, "admin_panel/partials/add_course.html")


@admin_required
def manage_courses_view(request):
    courses = Course.objects.all().order_by("-id")
    return render(request, "admin_panel/partials/manage_courses.html", {"courses": courses})


@admin_required
def manage_course_view(request, course_code):
    course = get_object_or_404(Course, code=course_code)
    folders = CourseFolder.objects.filter(course=course).order_by("type", "name")
    materials = CourseMaterial.objects.filter(course=course).select_related("folder").order_by("-uploaded_at")
    return render(
        request,
        "admin_panel/partials/manage_course.html",
        {"course": course, "folders": folders, "materials": materials},
    )


@admin_required
def delete_course_view(request, course_code):
    if request.method == "POST":
        course = get_object_or_404(Course, code=course_code)
        course.delete()
        messages.success(request, "Course deleted successfully.")
    return redirect("manage_courses")



from urllib.parse import urlparse, parse_qs

def convert_video_link(link):
    if not link:
        return link

    parsed = urlparse(link)
    video_id = None

    # =========================
    # 🎥 YOUTUBE HANDLING
    # =========================

    # youtube.com/watch?v=
    if "youtube.com" in parsed.netloc and parsed.path == "/watch":
        query_params = parse_qs(parsed.query)
        video_id = query_params.get("v", [None])[0]

    # youtu.be short link
    elif "youtu.be" in parsed.netloc:
        video_id = parsed.path.lstrip("/")

    # embed link
    elif "youtube.com" in parsed.netloc and "/embed/" in parsed.path:
        video_id = parsed.path.split("/embed/")[-1]

    # shorts link
    elif "youtube.com" in parsed.netloc and "/shorts/" in parsed.path:
        video_id = parsed.path.split("/shorts/")[-1]

    if video_id:
        video_id = video_id.split("?")[0]
        video_id = video_id.split("&")[0]
        return f"https://www.youtube.com/embed/{video_id}"

    # =========================
    # 📁 GOOGLE DRIVE HANDLING
    # =========================
    if "drive.google.com" in parsed.netloc:
        if "/file/d/" in parsed.path:
            file_id = parsed.path.split("/file/d/")[-1].split("/")[0]
            return f"https://drive.google.com/file/d/{file_id}/preview"

    return link

@admin_required
def upload_course_material(request, course_id):
    if request.method == "POST":
        course = get_object_or_404(Course, id=course_id)

        folder_id = request.POST.get("folder_id")
        title = (request.POST.get("title") or "").strip()
        link = (request.POST.get("link") or "").strip()
        mat_type = request.POST.get("type")
        file = request.FILES.get("file")

        if not folder_id:
            messages.error(request, "Folder is required.")
            return redirect("manage_course", course_code=course.code)

        folder = get_object_or_404(CourseFolder, id=folder_id, course=course)

        if mat_type == "video":
            if not link:
                messages.error(request, "Video link required.")
                return redirect("manage_course", course_code=course.code)

            link = convert_video_link(link)

        if mat_type == "material":
            if not file and not link:
                messages.error(request, "Upload file or provide link.")
                return redirect("manage_course", course_code=course.code)

        CourseMaterial.objects.create(
            course=course,
            folder=folder,
            title=title,
            link=link,
            type=mat_type,
            file=file,
        )

        messages.success(request, "Material uploaded successfully.")
        return redirect("manage_course", course_code=course.code)

    return redirect("manage_courses")





# =====================================================
# 📁 COURSE FOLDER / MATERIAL
# =====================================================
@admin_required
def create_folder(request, course_id):
    if request.method == "POST":
        name = (request.POST.get("folder_name") or "").strip()
        folder_type = request.POST.get("folder_type")  # 'video' or 'material'
        course = get_object_or_404(Course, id=course_id)

        if not name:
            messages.error(request, "Folder name is required.")
            return redirect("manage_course", course_code=course.code)

        if folder_type not in ["video", "material"]:
            messages.error(request, "Invalid folder type.")
            return redirect("manage_course", course_code=course.code)

        CourseFolder.objects.create(course=course, name=name, type=folder_type)
        messages.success(request, "Folder created successfully.")
        return redirect("manage_course", course_code=course.code)

    return redirect("manage_courses")


@admin_required
def delete_folder_view(request, folder_id):
    if request.method == "POST":
        folder = get_object_or_404(CourseFolder, id=folder_id)
        course_code = folder.course.code
        folder.delete()
        messages.success(request, "Folder deleted.")
        return redirect("manage_course", course_code=course_code)

    return redirect("manage_courses")


@admin_required
def delete_material_view(request, material_id):
    if request.method == "POST":
        material = get_object_or_404(CourseMaterial, id=material_id)
        course_code = material.course.code
        material.delete()
        messages.success(request, "Material deleted.")
        return redirect("manage_course", course_code=course_code)

    return redirect("manage_courses")


# =====================================================
# ✅ ASSIGNMENT VIEWS
# =====================================================
@admin_required
def assign_course_view(request):
    if request.method == "POST":
        student_id = request.POST.get("student_id")
        course_id = request.POST.get("course_id")

        if student_id and course_id:
            student = get_object_or_404(Student, id=student_id)
            course = get_object_or_404(Course, id=course_id)

            # prevent duplicate assignment
            CourseAssignment.objects.get_or_create(student=student, course=course)

            messages.success(request, "Course assigned successfully.")
            return redirect("assign_course")

        messages.error(request, "Select student and course.")

    context = {
        "students": Student.objects.filter(status="active"),
        "courses": Course.objects.all(),
        "assignments": CourseAssignment.objects.select_related("student", "course").order_by("-date_assigned")[:10],
    }
    return render(request, "admin_panel/partials/assign_course.html", context)


@admin_required
def assign_task_view(request):
    if request.method == "POST":
        student_id = request.POST.get("student_id")
        course_id = request.POST.get("course_id")
        title = request.POST.get("title")
        description = request.POST.get("description")
        deadline = request.POST.get("deadline")
        priority = request.POST.get("priority")

        if not (student_id and title and deadline and priority):
            messages.error(request, "Student, title, deadline and priority are required.")
            return redirect("assign_task")

        student = get_object_or_404(Student, id=student_id)
        course = get_object_or_404(Course, id=course_id) if course_id else None

        Task.objects.create(
            student=student,
            course=course,
            title=title,
            description=description or "",
            deadline=deadline,
            priority=priority,
            status="pending",
        )
        messages.success(request, "Task assigned successfully.")
        return redirect("assign_task")

    context = {
        "students": Student.objects.all(),
        "courses": Course.objects.all(),
        "tasks": Task.objects.select_related("student").order_by("-id")[:10],
    }
    return render(request, "admin_panel/partials/assign_task.html", context)


# =====================================================
# 📢 LIVE CLASS / BROADCAST
# =====================================================
@admin_required
def live_class_view(request):
    message_obj = BroadcastMessage.objects.first()

    if request.method == "POST":
        new_msg = request.POST.get("broadcast_text", "")
        link = request.POST.get("broadcast_link", "")

        if message_obj:
            message_obj.message = new_msg
            message_obj.link = link or None
            message_obj.save()
        else:
            message_obj = BroadcastMessage.objects.create(message=new_msg, link=link or None)

        messages.success(request, "Broadcast updated.")
        return render(
            request,
            "admin_panel/partials/live_class.html",
            {"message": message_obj.message, "broadcast_link": message_obj.link},
        )

    return render(
        request,
        "admin_panel/partials/live_class.html",
        {
            "message": message_obj.message if message_obj else "",
            "broadcast_link": message_obj.link if message_obj and message_obj.link else None,
        },
    )


# =====================================================
# 💼 CAREER OPPORTUNITIES
# =====================================================
@admin_required
def career_opportunities_view(request):
    if request.method == "POST":
        CareerOpportunities.objects.create(
            job_title=request.POST.get("job-title", ""),
            company_name=request.POST.get("company-name", ""),
            location=request.POST.get("location", "Not specified"),
            stipend=request.POST.get("stipend", "Not specified"),
            experience=request.POST.get("experience", "Not specified"),
            link=request.POST.get("link", ""),
            job_description=request.POST.get("job_description", ""),
            mode=request.POST.get("mode", "offline"),
            status="active",
        )
        messages.success(request, "✅ Job post submitted successfully!")

    online_jobs = CareerOpportunities.objects.filter(mode="online").order_by("-updated_at")
    offline_jobs = CareerOpportunities.objects.filter(mode="offline").order_by("-updated_at")

    return render(
        request,
        "admin_panel/partials/career_opportunities.html",
        {"online_students": online_jobs, "offline_students": offline_jobs},
    )


@admin_required
def delete_job_view(request, job_id):
    if request.method == "POST":
        job = get_object_or_404(CareerOpportunities, id=job_id)
        job.delete()
        messages.success(request, "Job deleted.")
    return redirect("career_opportunities")


# =====================================================
# 📅 CALENDAR
# =====================================================
@admin_required
def calendar_event_view(request):
    """
    Supports Create / Edit / Delete from the same form.
    Frontend sends:
      - event-id, title, course, description, meeting-link, start, end
      - allDay ('true'/'false')
      - edit ('true') or delete ('true')
    """

    if request.method == "POST":
        event_id = request.POST.get("event-id")
        title = request.POST.get("title", "")
        course = request.POST.get("course", "")  # kept as string to match your model
        description = request.POST.get("description", "")
        meeting_link = request.POST.get("meeting-link", "")
        start_raw = request.POST.get("start")
        end_raw = request.POST.get("end")
        all_day_raw = request.POST.get("allDay")
        edit = request.POST.get("edit")
        delete = request.POST.get("delete")

        all_day = True if all_day_raw == "true" else False

        # Parse datetimes safely
        start_dt = parse_datetime(start_raw) if start_raw else None
        end_dt = parse_datetime(end_raw) if end_raw else None

        # If parse_datetime returns naive datetime, make it aware (optional)
        if start_dt and timezone.is_naive(start_dt):
            start_dt = timezone.make_aware(start_dt)
        if end_dt and timezone.is_naive(end_dt):
            end_dt = timezone.make_aware(end_dt)

        if delete == "true" and event_id:
            CalendarEvent.objects.filter(id=event_id).delete()

        elif edit == "true" and event_id:
            event = CalendarEvent.objects.filter(id=event_id).first()
            if event:
                event.title = title
                event.course = course or event.course
                event.description = description
                event.meeting_link = meeting_link or None
                if start_dt:
                    event.start = start_dt
                event.end = end_dt
                event.all_day = all_day
                event.save()

        else:
            if start_dt:
                CalendarEvent.objects.create(
                    title=title,
                    course=course or "All Courses",
                    description=description,
                    meeting_link=meeting_link or None,
                    start=start_dt,
                    end=end_dt,
                    all_day=all_day,
                )

    # Build event_list for template
    events = CalendarEvent.objects.all().order_by("start")
    event_list = []
    for event in events:
        payload = {
            "eventId": event.id,
            "title": event.title,
            "course": event.course or "",
            "description": event.description or "",
            "meetingLink": f"{event.meeting_link}" if event.meeting_link else "",
            "start": event.start.isoformat(),
            "end": event.end.isoformat() if event.end else None,
        }
        if event.all_day:
            payload["allDay"] = "true"
        event_list.append(payload)

    return render(
        request,
        "admin_panel/partials/calendar.html",
        {"events": event_list, "courses": Course.objects.all()},
    )

@admin_required
def edit_course_material(request, material_id):

    material = get_object_or_404(CourseMaterial, id=material_id)
    course_code = material.course.code

    if request.method == "POST":
        material.title = request.POST.get("title")
        material.link = request.POST.get("link")

        if material.type == "video":
            material.link = convert_youtube_link(material.link)

        material.save()
        return redirect('manage_course', course_code=course_code)

# =====================================================
# 🖼 STUDY IMAGES
# =====================================================
@admin_required
def upload_study_image(request):
    if request.method == "POST":
        form = StudyImageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Image uploaded successfully.")
            return redirect("upload_study_image")
        messages.error(request, "Invalid form submission.")
    else:
        form = StudyImageForm()

    images = StudyImage.objects.all().order_by("-uploaded_at")
    return render(
        request,
        "admin_panel/partials/upload_image.html",
        {"form": form, "images": images},
    )


@admin_required
def delete_study_image(request, image_id):
    if request.method == "POST":
        image = get_object_or_404(StudyImage, id=image_id)
        image.delete()
        messages.success(request, "Image deleted successfully.")
    return redirect("upload_study_image")


# =====================================================
# 📦 API VIEWSETS
# =====================================================
class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all().order_by("-id")
    serializer_class = StudentSerializer


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all().order_by("-id")
    serializer_class = CourseSerializer


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all().order_by("-id")
    serializer_class = TaskSerializer


class CourseAssignmentViewSet(viewsets.ModelViewSet):
    queryset = CourseAssignment.objects.all().order_by("-id")
    serializer_class = CourseAssignmentSerializer


class CalendarEventViewSet(viewsets.ModelViewSet):
    queryset = CalendarEvent.objects.all().order_by("start")
    serializer_class = CalendarEventSerializer
