from django import forms

class SubmissionForm(forms.Form):
    file = forms.FileField()
