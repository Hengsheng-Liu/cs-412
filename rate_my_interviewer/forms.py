from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class CreateUserForm(forms.ModelForm):
    name = forms.CharField(label="Name", required=True)
    email = forms.EmailField(label="Email", required=True)
    college = forms.CharField(label="College", required=True)
    class Meta:
        model = User
        fields = ['name', 'email', 'college']
    def clean(self):
        cleaned_data = super().clean()
        if User.objects.filter(email=cleaned_data.get('email')).exists():
            raise forms.ValidationError("This email is already in use.")
        return cleaned_data