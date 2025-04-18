# olympiad/models.py  (новая ревизия)

from django.db import models
from django.conf import settings
from guardian.shortcuts import assign_perm

class Category(models.Model):
    name = models.CharField(max_length=64, unique=True)
    color = models.CharField(max_length=7, default="#EBC88C")      # хекс‑цвет для бейджа

    def __str__(self):
        return self.name


class Olympiad(models.Model):
    class Status(models.TextChoices):
        UPCOMING = "upcoming", "Upcoming"
        ACTIVE   = "active",   "Active"
        CLOSED   = "closed",   "Closed"

    title       = models.CharField(max_length=120)
    subject     = models.CharField(max_length=120)
    category    = models.ForeignKey(Category, on_delete=models.PROTECT)
    author      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                    related_name="authored_olympiads")            # ↞ «препод»
    start_at    = models.DateTimeField()
    end_at      = models.DateTimeField()
    status      = models.CharField(max_length=12, choices=Status.choices,
                                   default=Status.UPCOMING)

    def __str__(self):
        return self.title


class Problem(models.Model):
    olympiad   = models.ForeignKey(Olympiad, on_delete=models.CASCADE,
                                   related_name="problems")
    title      = models.CharField(max_length=120)
    statement  = models.TextField()
    max_score  = models.PositiveSmallIntegerField(default=100)

    def __str__(self):
        return f"{self.olympiad} – {self.title}"


class TestCase(models.Model):
    problem      = models.ForeignKey(Problem, on_delete=models.CASCADE,
                                     related_name="tests")
    input_data   = models.TextField()
    output_data  = models.TextField()
    weight       = models.PositiveSmallIntegerField(default=1)   # балл за тест

    class Meta:
        unique_together = ("problem", "input_data")              # один пример ‑ один раз


class Submission(models.Model):
    enrollment   = models.ForeignKey("Enrollment", on_delete=models.CASCADE)
    problem      = models.ForeignKey(Problem, on_delete=models.CASCADE)
    file         = models.FileField(upload_to="answers/%Y/%m/%d")
    score        = models.PositiveSmallIntegerField(default=0)
    created_at   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.enrollment} – {self.problem} ({self.score})"


class Enrollment(models.Model):
    user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    olympiad   = models.ForeignKey(Olympiad, on_delete=models.CASCADE)
    is_jury    = models.BooleanField(default=False)   # отметка «оценщик»

    class Meta:
        unique_together = ("user", "olympiad")
enrollment = Enrollment.objects.get(user=user, olympiad=olymp)
assign_perm("change_submission", user, olympiad)     # право оценивать
