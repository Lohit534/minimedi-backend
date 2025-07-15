from django.db import models

# Create your models here.

from django.contrib.auth.models import User

class SymptomLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    date_logged = models.DateTimeField(auto_now_add=True)