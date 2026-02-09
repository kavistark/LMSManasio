
from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('superuser/', include('superuser_admin.urls')),
    path('admin_panel/', include('admin_panel.urls')),
    path('', include('student_portal.urls')),
]
