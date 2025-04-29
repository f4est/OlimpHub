from django import forms
from django.contrib.auth.models import User
from .models import UserProfile, Olympiad, Problem

class SignUpForm(forms.ModelForm):
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Подтверждение пароля', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')
        labels = {
            'username': 'Имя пользователя',
            'email': 'Email',
            'first_name': 'Имя',
            'last_name': 'Фамилия',
        }

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('password1') != cleaned.get('password2'):
            self.add_error('password2', 'Пароли не совпадают')
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('bio', 'role', 'phone', 'organization', 'position', 'avatar', 'additional_info')
        labels = {
            'bio': 'О себе',
            'role': 'Роль',
            'phone': 'Телефон',
            'organization': 'Организация/Учебное заведение',
            'position': 'Должность/Группа',
            'avatar': 'Фото профиля',
            'additional_info': 'Дополнительные сведения',
        }
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3}),
            'additional_info': forms.Textarea(attrs={'rows': 3}),
        }

class OlympiadForm(forms.ModelForm):
    class Meta:
        model = Olympiad
        fields = ('title', 'subject', 'description', 'rules', 'difficulty', 
                 'start_at', 'end_at')
        labels = {
            'title': 'Название',
            'subject': 'Предмет',
            'description': 'Описание',
            'rules': 'Правила',
            'difficulty': 'Сложность',
            'start_at': 'Начало',
            'end_at': 'Завершение',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'rules': forms.Textarea(attrs={'rows': 4}),
            'start_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_at = cleaned_data.get('start_at')
        end_at = cleaned_data.get('end_at')
        
        if start_at and end_at and start_at >= end_at:
            self.add_error('end_at', 'Время завершения должно быть позже времени начала')
        
        return cleaned_data

class ProblemForm(forms.ModelForm):
    class Meta:
        model = Problem
        fields = ('title', 'description', 'max_score', 'statement_file')
        labels = {
            'title': 'Название задачи',
            'description': 'Описание',
            'max_score': 'Максимальный балл',
            'statement_file': 'Файл с заданием (PDF)',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
