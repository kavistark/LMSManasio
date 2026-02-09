from django.db import models

class AdminUser(models.Model):
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)  # plain for demo
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username
