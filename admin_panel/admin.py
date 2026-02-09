from django.contrib import admin
from .models import Student,College,Course,StudyImage,CareerOpportunities,ProgressReport,CalendarEvent,BroadcastMessage,Task,CourseMaterial,CourseFolder,CourseAssignment

admin.site.register(Student)
admin.site.register(College)
admin.site.register(Course)
admin.site.register(CourseAssignment)
admin.site.register(CourseFolder)
admin.site.register(CourseMaterial)
admin.site.register(Task)
admin.site.register(BroadcastMessage)
admin.site.register(CalendarEvent)
admin.site.register(ProgressReport)
admin.site.register(CareerOpportunities)
admin.site.register(StudyImage)

