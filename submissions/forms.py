from django import forms
import os

class SubmissionForm(forms.Form):
    file = forms.FileField(
        label='Файл с решением',
        help_text='Загрузите файл с вашим решением (макс. 10MB)',
        error_messages={
            'required': 'Пожалуйста, выберите файл',
            'invalid': 'Пожалуйста, выберите корректный файл',
            'missing': 'Файл не был отправлен',
            'empty': 'Загруженный файл пуст',
            'max_length': 'Имя файла слишком длинное',
        }
    )
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        
        if file:
            # Проверка размера файла
            if file.size > 10 * 1024 * 1024:  # 10MB
                raise forms.ValidationError('Размер файла не должен превышать 10MB')
            
            # Проверка допустимых расширений
            ext = os.path.splitext(file.name)[1].lower()
            allowed_extensions = ['.pdf', '.doc', '.docx', '.txt', '.py', '.cpp', '.c', '.java', '.js', '.zip']
            
            if ext not in allowed_extensions:
                raise forms.ValidationError(
                    f'Недопустимый тип файла. Разрешены следующие типы: {", ".join(allowed_extensions)}'
                )
                
        return file
