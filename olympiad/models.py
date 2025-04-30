from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator, MaxValueValidator
from django.utils import timezone
import os

def validate_file_size(value):
    filesize = value.size
    if filesize > 10 * 1024 * 1024:  # 10MB
        raise ValidationError('Максимальный размер файла не должен превышать 10MB')

def validate_pdf(value):
    """Валидация PDF-файлов - для поддержки существующих миграций"""
    filesize = value.size
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.pdf']
    
    if filesize > 10 * 1024 * 1024:  # 10MB
        raise ValidationError('Максимальный размер файла не должен превышать 10MB')
    
    if not ext.lower() in valid_extensions:
        raise ValidationError('Файл должен быть в формате PDF')

# Модель для ролей пользователей
class UserProfile(models.Model):
    STUDENT = 'student'       # Участник/студент
    TEACHER = 'teacher'       # Преподаватель/создатель соревнований
    ADMIN = 'admin'           # Администратор системы
    
    ROLE_CHOICES = [
        (STUDENT, 'Студент'),
        (TEACHER, 'Преподаватель'),
        (ADMIN, 'Администратор'),
    ]
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=STUDENT)
    bio = models.TextField(max_length=500, blank=True)
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    organization = models.CharField(max_length=100, blank=True, verbose_name='Организация/Учебное заведение')
    position = models.CharField(max_length=100, blank=True, verbose_name='Должность/Группа')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='Фото профиля')
    additional_info = models.TextField(max_length=500, blank=True, verbose_name='Дополнительные сведения')
    
    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"
    
    def save(self, *args, **kwargs):
        # Создаем директорию для аватарок, если она не существует
        avatar_dir = os.path.join(settings.MEDIA_ROOT, 'avatars')
        if not os.path.exists(avatar_dir):
            os.makedirs(avatar_dir, exist_ok=True)
        
        # Сохраняем модель
        super().save(*args, **kwargs)
    
    @property
    def is_teacher(self):
        return self.role == self.TEACHER
    
    @property
    def is_admin(self):
        return self.role == self.ADMIN
    
    @property
    def is_student(self):
        return self.role == self.STUDENT

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
    # Добавляем поле для создателя соревнования
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                               related_name='created_olympiads', null=True)
    description = models.TextField(blank=True)
    rules = models.TextField(blank=True)
    difficulty = models.CharField(max_length=10, choices=[
        ('easy', 'Легкий'),
        ('medium', 'Средний'),
        ('hard', 'Сложный')
    ], blank=True)

    def __str__(self):
        return self.title
    
    @property
    def participants(self):
        return User.objects.filter(enrollment__olympiad=self)
    
    def update_status(self):
        """Обновляет статус соревнования в зависимости от текущего времени"""
        now = timezone.now()
        
        if self.start_at > now:
            new_status = self.UPCOMING
        elif self.end_at < now:
            new_status = self.CLOSED
        else:
            new_status = self.ACTIVE
            
        if new_status != self.status:
            self.status = new_status
            self.save(update_fields=['status'])
        
        return self.status

class Enrollment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    olympiad = models.ForeignKey(Olympiad, on_delete=models.CASCADE)
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'olympiad')

    def __str__(self):
        return f"{self.user} -> {self.olympiad}"

class Problem(models.Model):
    olympiad = models.ForeignKey(Olympiad, related_name='problems', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    max_score = models.PositiveIntegerField(default=100)
    statement_file = models.FileField(upload_to='statements/', validators=[validate_file_size])
    
    def __str__(self):
        return self.title
        
    @property
    def filename(self):
        """Возвращает имя файла без пути"""
        return os.path.basename(self.statement_file.name) if self.statement_file else ""
