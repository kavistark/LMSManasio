from django.db import models
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


# =====================================================
# 🎓 COLLEGE
# =====================================================

class College(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    address = models.CharField(max_length=255)
    logo_image = models.ImageField(upload_to="college_logos/", blank=True, null=True)
    poster_image = models.ImageField(upload_to="college_posters/", blank=True, null=True)
    description = models.TextField(blank=True)
    student_count = models.PositiveIntegerField(default=0)

    mode = models.CharField(
        max_length=10,
        choices=[("online", "Online"), ("offline", "Offline"), ("hybrid", "Hybrid")],
        default="offline",
    )

    status = models.CharField(
        max_length=10,
        choices=[("active", "Active"), ("inactive", "Inactive")],
        default="active",
    )

    def __str__(self):
        return self.name


# =====================================================
# 👨‍🎓 STUDENT
# =====================================================

class Student(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    roll = models.CharField(max_length=20, unique=True, db_index=True)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)

    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name="students")

    mode = models.CharField(
        max_length=10,
        choices=[("online", "Online"), ("offline", "Offline")],
        default="offline",
    )

    status = models.CharField(max_length=10, default="active")

    def __str__(self):
        return self.name


# =====================================================
# 📚 COURSE
# =====================================================

class Course(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True, db_index=True)
    description = models.TextField(blank=True)
    thumbnail = models.ImageField(upload_to="course_thumbnails/", blank=True, null=True)

    def __str__(self):
        return self.name


# =====================================================
# 📌 COURSE ASSIGNMENT
# =====================================================

class CourseAssignment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date_assigned = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=10, default="assigned")

    class Meta:
        unique_together = ("student", "course")

    def __str__(self):
        return f"{self.student.name} → {self.course.name}"


# =====================================================
# 📁 COURSE FOLDER
# =====================================================

class CourseFolder(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="folders")
    name = models.CharField(max_length=100)

    type = models.CharField(
        max_length=10,
        choices=[("video", "Video"), ("material", "Material")],
        default="material",
    )

    def __str__(self):
        return f"{self.course.name} - {self.name}"


# =====================================================
# 📄 COURSE MATERIAL
# =====================================================

class CourseMaterial(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="materials")
    folder = models.ForeignKey(CourseFolder, on_delete=models.SET_NULL, null=True, blank=True)

    file = models.FileField(upload_to="materials/", null=True, blank=True)
    link = models.URLField(blank=True)

    type = models.CharField(
        max_length=10,
        choices=[("video", "Video"), ("material", "Material")],
        default="material",
    )

    title = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.link:
            if "youtube.com/watch?v=" in self.link:
                self.link = self.link.replace("watch?v=", "embed/")
            elif "youtu.be/" in self.link:
                self.link = self.link.replace("youtu.be/", "www.youtube.com/embed/")
            elif "drive.google.com/file/d/" in self.link and "/view" in self.link:
                self.link = self.link.replace("/view", "/preview")

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title or self.link or "Material"


# =====================================================
# 📝 TASK
# =====================================================

class Task(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)

    title = models.CharField(max_length=100)
    description = models.TextField()
    deadline = models.DateField(db_index=True)

    priority = models.CharField(
        max_length=10,
        choices=[("low", "Low"), ("medium", "Medium"), ("high", "High")],
        default="medium",
    )

    status = models.CharField(
        max_length=15,
        choices=[("pending", "Pending"), ("in_progress", "In Progress"), ("completed", "Completed")],
        default="pending",
    )

    def __str__(self):
        return f"{self.title} → {self.student.name}"


# =====================================================
# 📢 BROADCAST
# =====================================================

class BroadcastMessage(models.Model):
    message = models.TextField()
    link = models.URLField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Broadcast Message"


# =====================================================
# 📅 CALENDAR EVENT
# =====================================================

class CalendarEvent(models.Model):
    title = models.CharField(max_length=200)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    meeting_link = models.URLField(blank=True, null=True)
    start = models.DateTimeField()
    end = models.DateTimeField(null=True, blank=True)
    all_day = models.BooleanField(default=True)

    def __str__(self):
        return self.title


# =====================================================
# 📊 PROGRESS REPORT
# =====================================================

class ProgressReport(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)

    interview_prep = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    communication_skills = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    resume_prep = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    technical_prep = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    mock_tests = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    mock_interviews = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])

    def __str__(self):
        return self.student.roll


# =====================================================
# 💼 CAREER OPPORTUNITIES
# =====================================================

class CareerOpportunities(models.Model):
    job_title = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    location = models.CharField(max_length=255, default="Not specified")
    stipend = models.CharField(max_length=100, default="Not specified")
    experience = models.CharField(max_length=100, default="Not specified")

    link = models.URLField()
    job_description = models.TextField()

    mode = models.CharField(max_length=10, default="offline")
    status = models.CharField(max_length=10, default="active")

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.job_title} - {self.company_name}"

class StudyImage(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='study_images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
