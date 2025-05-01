from django import forms
from django.contrib.auth.models import User
from .models import UserProfile, Olympiad, Problem

class SignUpForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Пароль', 
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль',
        })
    )
    password2 = forms.CharField(
        label='Подтверждение пароля', 
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Повторите пароль',
        })
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')
        labels = {
            'username': 'Имя пользователя',
            'email': 'Email',
            'first_name': 'Имя',
            'last_name': 'Фамилия',
        }
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите имя пользователя',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите email',
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите имя',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите фамилию',
            }),
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
    first_name = forms.CharField(
        max_length=150,
        required=False,
        label='Имя',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=150,
        required=False,
        label='Фамилия',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

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
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, 'user'):
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            
    def save(self, commit=True):
        profile = super().save(commit=False)
        if hasattr(profile, 'user'):
            profile.user.first_name = self.cleaned_data['first_name']
            profile.user.last_name = self.cleaned_data['last_name']
            profile.user.save()
        if commit:
            profile.save()
        return profile

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
