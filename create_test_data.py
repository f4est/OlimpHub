import os
import sys
import django
import random
from datetime import datetime, timedelta

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'olimphub_project.settings')
django.setup()

# Импорт моделей
from django.contrib.auth.models import User
from olympiad.models import UserProfile, Olympiad, Problem
from django.utils import timezone

# Создание администратора
def create_admin():
    # Проверка, существует ли уже пользователь admin
    if User.objects.filter(username='admin').exists():
        admin_user = User.objects.get(username='admin')
        print(f"Администратор уже существует: {admin_user.username}")
    else:
        admin_user = User.objects.create_user(
            username='admin',
            email='admin@olimphub.com',
            password='Admin123!'
        )
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()
        
        # Обновление профиля
        profile = admin_user.profile
        profile.role = UserProfile.ADMIN
        profile.bio = 'Главный администратор системы'
        profile.save()
        
        print(f"Создан администратор: {admin_user.username}")
        print(f"Логин: admin")
        print(f"Пароль: Admin123!")
    
    return admin_user

# Создание преподавателя
def create_teacher(username='teacher', password='Teacher123!'):
    # Проверка, существует ли уже пользователь
    if User.objects.filter(username=username).exists():
        teacher_user = User.objects.get(username=username)
        print(f"Преподаватель уже существует: {teacher_user.username}")
    else:
        teacher_user = User.objects.create_user(
            username=username,
            email=f'{username}@olimphub.com',
            password=password
        )
        teacher_user.save()
        
        # Обновление профиля
        profile = teacher_user.profile
        profile.role = UserProfile.TEACHER
        profile.bio = 'Преподаватель и организатор олимпиад'
        profile.save()
        
        print(f"Создан преподаватель: {teacher_user.username}")
        print(f"Логин: {username}")
        print(f"Пароль: {password}")
    
    return teacher_user

# Создание студента
def create_student(username='student', password='Student123!'):
    # Проверка, существует ли уже пользователь
    if User.objects.filter(username=username).exists():
        student_user = User.objects.get(username=username)
        print(f"Студент уже существует: {student_user.username}")
    else:
        student_user = User.objects.create_user(
            username=username,
            email=f'{username}@olimphub.com',
            password=password
        )
        student_user.save()
        
        # Обновление профиля
        profile = student_user.profile
        profile.role = UserProfile.STUDENT
        profile.bio = 'Активный участник олимпиад'
        profile.save()
        
        print(f"Создан студент: {student_user.username}")
        print(f"Логин: {username}")
        print(f"Пароль: {password}")
    
    return student_user

# Создание соревнований
def create_olympiads(creator, count=13):
    subjects = [
        'Математика', 'Информатика', 'Физика', 'Химия', 'Биология',
        'История', 'Иностранный язык', 'Экономика', 'Право', 'Литература'
    ]
    
    difficulties = ['easy', 'medium', 'hard']
    
    # Статусы соревнований
    statuses = [Olympiad.UPCOMING, Olympiad.ACTIVE, Olympiad.CLOSED]
    
    # Генерация случайной даты для соревнования
    def random_date():
        now = timezone.now()
        
        # Определяем случайный сдвиг от -30 до +30 дней
        days_offset = random.randint(-30, 30)
        start_date = now + timedelta(days=days_offset)
        
        # Продолжительность от 1 часа до 3 дней
        duration_hours = random.randint(1, 72)
        end_date = start_date + timedelta(hours=duration_hours)
        
        return start_date, end_date
    
    # Шаблоны описаний
    descriptions = [
        "Соревнование для студентов {уровень} уровня. Проверьте свои знания и навыки в области {предмет}.",
        "Ежегодная олимпиада по {предмет}. Победители получат ценные призы и возможность стажировки.",
        "Открытое соревнование для всех желающих по {предмет}. Сложность: {уровень}.",
        "Специализированная олимпиада для будущих профессионалов в области {предмет}.",
        "Проверьте свои знания в {предмет} на {уровень} уровне сложности.",
        "{уровень} олимпиада по {предмет} для студентов всех курсов.",
        "Интенсивное соревнование по {предмет}. Идеально подходит для {уровень} уровня подготовки."
    ]
    
    # Шаблоны правил
    rules = [
        "Участникам запрещается использовать сторонние источники информации. Решения должны быть оригинальными.",
        "Во время соревнования разрешено пользоваться справочными материалами, но запрещено общение с другими участниками.",
        "За каждое правильное решение начисляются баллы в зависимости от сложности задания. Победитель определяется по сумме баллов.",
        "Решения оцениваются по точности, эффективности и оригинальности подхода.",
        "После отправки решения его нельзя изменить. Учитывается только последняя версия решения.",
        "В случае технических проблем, обратитесь к организаторам. Время решения задач не продлевается."
    ]
    
    # Создание соревнований
    created_olympiads = []
    for i in range(count):
        subject = random.choice(subjects)
        difficulty = random.choice(difficulties)
        start_date, end_date = random_date()
        
        # Определение статуса на основе дат
        now = timezone.now()
        if start_date > now:
            status = Olympiad.UPCOMING
        elif end_date < now:
            status = Olympiad.CLOSED
        else:
            status = Olympiad.ACTIVE
        
        # Форматирование описания
        difficulty_text = {
            'easy': 'начального',
            'medium': 'среднего',
            'hard': 'продвинутого'
        }
        
        desc_template = random.choice(descriptions)
        description = desc_template.format(
            предмет=subject.lower(),
            уровень=difficulty_text[difficulty]
        )
        
        # Создание соревнования
        olympiad = Olympiad.objects.create(
            title=f"Соревнование по {subject.lower()} #{i+1}",
            subject=subject,
            start_at=start_date,
            end_at=end_date,
            status=status,
            creator=creator,
            description=description,
            rules=random.choice(rules),
            difficulty=difficulty
        )
        
        created_olympiads.append(olympiad)
        
        # Вывод информации о созданном соревновании
        print(f"Создано соревнование: {olympiad.title}")
        print(f"Статус: {olympiad.get_status_display()}")
        print(f"Сложность: {olympiad.difficulty}")
        print("---")
    
    return created_olympiads

if __name__ == "__main__":
    print("Создание тестовых данных...")
    admin = create_admin()
    teacher = create_teacher()
    student = create_student()
    olympiads = create_olympiads(admin)
    print(f"Создано {len(olympiads)} соревнований.")
    print("Готово!") 