from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

def validate_pdf(value):
    if not value.name.lower().endswith('.pdf'):
        raise ValidationError('Только PDF‑файлы.')

class Olympiad(models.Model):
    UPCOMING = 'upcoming'
    ACTIVE = 'active'
    CLOSED = 'closed'
    STATUS_CHOICES = [
        (UPCOMING, 'Upcoming'),
        (ACTIVE, 'Active'),
        (CLOSED, 'Closed'),
    ]

    title = models.CharField(max_length=200)
    subject = models.CharField(max_length=120, blank=True)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=UPCOMING)

    def __str__(self):
        return self.title

class Enrollment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    olympiad = models.ForeignKey(Olympiad, on_delete=models.CASCADE)
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'olympiad')

    def __str__(self):
        return f"{self.user} -> {self.olympiad}"

class Problem(models.Model):
    olympiad = models.ForeignKey(Olympiad, on_delete=models.CASCADE, related_name='problems')
    title = models.CharField(max_length=200)
    max_score = models.PositiveIntegerField(default=100)
    statement_file = models.FileField(upload_to='statements/')
    statement_file = models.FileField(upload_to='statements/', validators=[validate_pdf])

    def __str__(self):
        return self.title
