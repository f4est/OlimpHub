from django.db import models
from olympiad.models import Enrollment, Problem
import os
import time

class Submission(models.Model):
    PENDING = 'pending'
    REVIEWED = 'reviewed'
    
    STATUS_CHOICES = [
        (PENDING, 'На проверке'),
        (REVIEWED, 'Проверено'),
    ]
    
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    file = models.FileField(upload_to='solutions/')
    submitted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    score = models.PositiveIntegerField(null=True, blank=True)
    comment = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.enrollment.user.username} - {self.problem.title}"
    
    def filename(self):
        return os.path.basename(self.file.name) if self.file else "Нет файла"
        
    def save(self, *args, **kwargs):
        # Добавляем суффикс с timestamp к имени файла, чтобы избежать конфликтов
        if self.file and not self.id:  # Только для новых объектов
            file_name, file_ext = os.path.splitext(self.file.name)
            time_suffix = int(time.time())
            self.file.name = f"solution_{self.enrollment.user.username}_{time_suffix}{file_ext}"
        
        return super().save(*args, **kwargs)
