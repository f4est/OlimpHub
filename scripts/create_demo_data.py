import os
import sys
import django
import random
from datetime import timedelta

# Настройка окружения Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'olimphub_project.settings')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from olympiad.models import UserProfile, Olympiad, Problem, Enrollment
from django.db import transaction

# Список предметов
SUBJECTS = [
    'Физика', 'Математика', 'Информатика', 'Химия', 'Биология',
    'История', 'Обществознание', 'Литература', 'Русский язык', 'Английский язык',
    'География', 'Астрономия', 'Экономика', 'Право', 'Программирование'
]

# Тексты для описаний
DESCRIPTIONS = [
    'Интересное соревнование для всех желающих. Приглашаем принять участие!',
    'Проверьте свои знания в этой области. Мы подготовили интересные задания.',
    'Уникальная возможность проверить свои навыки и знания в дружественной атмосфере.',
    'Соревнование для энтузиастов и профессионалов. Ждем всех желающих!',
    'Проявите свои аналитические способности в решении наших задач.'
]

# Тексты для правил
RULES = [
    'Для участия необходимо зарегистрироваться. Каждое задание имеет свой вес. Итоговая оценка - сумма баллов.',
    'Запрещено использовать сторонние источники. Все решения должны быть оригинальными.',
    'Участники должны следовать инструкциям к заданиям. Решения принимаются только в указанном формате.',
    'У каждого задания есть свой вес в баллах. Победитель определяется по сумме набранных баллов.',
    'Решения проверяются вручную преподавателями. Результаты будут доступны после завершения соревнования.'
]

# Тексты для названий задач
PROBLEM_TITLES = [
    'Основная задача', 'Творческое задание', 'Теоретическая задача', 'Практическая задача',
    'Тест по базовым знаниям', 'Углубленное исследование', 'Решение уравнений',
    'Анализ данных', 'Проектная работа', 'Финальное испытание'
]

# Тексты для описаний задач
PROBLEM_DESCRIPTIONS = [
    'Решите задачу и загрузите ответ в формате PDF.',
    'Напишите код для решения данной задачи.',
    'Проанализируйте представленные данные и сделайте выводы.',
    'Ответьте на теоретические вопросы в текстовом формате.',
    'Выполните практическое задание и предоставьте отчет.'
]

@transaction.atomic
def create_demo_data():
    print("Создание демонстрационных данных...")
    
    # Создание преподавателей, если их недостаточно
    current_teachers_count = User.objects.filter(profile__role='teacher').count()
    teachers_to_create = max(0, 5 - current_teachers_count)
    
    teachers = []
    for i in range(teachers_to_create):
        teacher_username = f'teacher{i+1}'
        teacher, created = User.objects.get_or_create(
            username=teacher_username,
            defaults={
                'email': f'{teacher_username}@example.com',
                'is_active': True
            }
        )
        
        if created:
            teacher.set_password('password123')
            teacher.save()
            
            # Создание профиля преподавателя
            UserProfile.objects.get_or_create(
                user=teacher,
                defaults={
                    'role': 'teacher',
                    'bio': f'Преподаватель {i+1}',
                    'organization': f'Университет #{random.randint(1, 10)}'
                }
            )
            print(f"Создан преподаватель: {teacher_username}")
        
        teachers.append(teacher)
    
    # Убедимся, что есть как минимум 5 преподавателей для работы
    if not teachers:
        teachers = list(User.objects.filter(profile__role='teacher')[:5])
    
    # Создание 34 соревнований (из них 10 активных)
    now = timezone.now()
    olympiad_count = Olympiad.objects.count()
    olympiads_to_create = max(0, 34 - olympiad_count)
    
    active_olympiads_count = Olympiad.objects.filter(status='active').count()
    active_olympiads_to_create = max(0, 10 - active_olympiads_count)
    upcoming_olympiads_to_create = (olympiads_to_create - active_olympiads_to_create) // 2
    closed_olympiads_to_create = olympiads_to_create - active_olympiads_to_create - upcoming_olympiads_to_create
    
    # Создание активных соревнований
    print(f"Создание {active_olympiads_to_create} активных соревнований...")
    for i in range(active_olympiads_to_create):
        teacher = random.choice(teachers)
        subject = random.choice(SUBJECTS)
        start_date = now - timedelta(days=random.randint(1, 3))
        end_date = now + timedelta(days=random.randint(1, 5))
        
        olympiad = Olympiad.objects.create(
            title=f'Активное соревнование по {subject} #{i+1}',
            subject=subject,
            start_at=start_date,
            end_at=end_date,
            status='active',
            creator=teacher,
            description=random.choice(DESCRIPTIONS),
            rules=random.choice(RULES),
            difficulty=random.choice(['easy', 'medium', 'hard'])
        )
        
        # Создание задач для соревнования (3-7 задач)
        num_problems = random.randint(3, 7)
        for j in range(num_problems):
            Problem.objects.create(
                olympiad=olympiad,
                title=f'{random.choice(PROBLEM_TITLES)} #{j+1}',
                description=random.choice(PROBLEM_DESCRIPTIONS),
                max_score=random.choice([5, 10, 15, 20])
            )
        
        print(f"Создано активное соревнование: {olympiad.title} с {num_problems} заданиями")
    
    # Создание предстоящих соревнований
    print(f"Создание {upcoming_olympiads_to_create} предстоящих соревнований...")
    for i in range(upcoming_olympiads_to_create):
        teacher = random.choice(teachers)
        subject = random.choice(SUBJECTS)
        start_date = now + timedelta(days=random.randint(1, 10))
        end_date = start_date + timedelta(days=random.randint(1, 5))
        
        olympiad = Olympiad.objects.create(
            title=f'Предстоящее соревнование по {subject} #{i+1}',
            subject=subject,
            start_at=start_date,
            end_at=end_date,
            status='upcoming',
            creator=teacher,
            description=random.choice(DESCRIPTIONS),
            rules=random.choice(RULES),
            difficulty=random.choice(['easy', 'medium', 'hard'])
        )
        
        # Создание задач для соревнования (2-5 задач)
        num_problems = random.randint(2, 5)
        for j in range(num_problems):
            Problem.objects.create(
                olympiad=olympiad,
                title=f'{random.choice(PROBLEM_TITLES)} #{j+1}',
                description=random.choice(PROBLEM_DESCRIPTIONS),
                max_score=random.choice([5, 10, 15, 20])
            )
        
        print(f"Создано предстоящее соревнование: {olympiad.title} с {num_problems} заданиями")
    
    # Создание завершенных соревнований
    print(f"Создание {closed_olympiads_to_create} завершенных соревнований...")
    for i in range(closed_olympiads_to_create):
        teacher = random.choice(teachers)
        subject = random.choice(SUBJECTS)
        end_date = now - timedelta(days=random.randint(1, 30))
        start_date = end_date - timedelta(days=random.randint(1, 5))
        
        olympiad = Olympiad.objects.create(
            title=f'Завершенное соревнование по {subject} #{i+1}',
            subject=subject,
            start_at=start_date,
            end_at=end_date,
            status='closed',
            creator=teacher,
            description=random.choice(DESCRIPTIONS),
            rules=random.choice(RULES),
            difficulty=random.choice(['easy', 'medium', 'hard'])
        )
        
        # Создание задач для соревнования (3-8 задач)
        num_problems = random.randint(3, 8)
        for j in range(num_problems):
            Problem.objects.create(
                olympiad=olympiad,
                title=f'{random.choice(PROBLEM_TITLES)} #{j+1}',
                description=random.choice(PROBLEM_DESCRIPTIONS),
                max_score=random.choice([5, 10, 15, 20])
            )
        
        print(f"Создано завершенное соревнование: {olympiad.title} с {num_problems} заданиями")
    
    print("Создание демонстрационных данных завершено!")

if __name__ == '__main__':
    create_demo_data() 