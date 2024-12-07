
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Company, InterviewExperience, RMIProfile, Comments

class CreateUserForm(forms.ModelForm):
    name = forms.CharField(label="Name", required=True)
    email = forms.EmailField(label="Email", required=True)
    college = forms.CharField(label="College", required=True)

    class Meta:
        model = RMIProfile
        fields = ['name', 'email', 'college']

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')

        if RMIProfile.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")

        return cleaned_data

class CompanyComparisonForm(forms.Form):
    company1 = forms.ModelChoiceField(
        queryset=Company.objects.all().order_by('name').distinct(),
        label="Select Company 1",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    company2 = forms.ModelChoiceField(
        queryset=Company.objects.all().order_by('name').distinct(),
        label="Select Company 2",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

from .models import InterviewExperience, Company

class InterviewExperienceForm(forms.ModelForm):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)] 
    JOB_TYPE_CHOICES = [
        ('Full-time', 'Full-time'),
        ('Part-time', 'Part-time'),
        ('Internship', 'Internship'),
        ('Contract', 'Contract'),
        ('Other', 'Other'),
    ]
    TYPE_CHOICES = [
        ("Behavioral", "Behavioral"),
        ("Technical", "Technical"),
        ("Case Study", "Case Study"),
    ]

    company = forms.ModelChoiceField(
        queryset=Company.objects.all(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    role = forms.CharField(
        label="Role",
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter the role', 'class': 'form-control'})
    )
    type = forms.ChoiceField(
        label="Type",
        choices=TYPE_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    question = forms.CharField(
        label="Question",
        required=False,
        widget=forms.Textarea(attrs={'placeholder': 'Enter the question (if any)', 'class': 'form-control'})
    )
    experience_text = forms.CharField(
        label="Experience",
        required=False,
        widget=forms.Textarea(attrs={'placeholder': 'Share your experience', 'class': 'form-control'})
    )
    rating = forms.ChoiceField(
        label="Rating",
        choices=RATING_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    difficulty = forms.ChoiceField(
        label="Difficulty",
        choices=RATING_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    job_type = forms.ChoiceField(
        label="Job Type",
        choices=JOB_TYPE_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    offer = forms.BooleanField(
        label="Received Offer?",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    credits_required = forms.BooleanField(
        label="Charge for credits?",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    credits_amount = forms.IntegerField(
        label="Credits",
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Enter the number of credits', 'class': 'form-control'}),
        min_value=0
    )

    class Meta:
        model = InterviewExperience
        fields = [
            'company', 'role', 'type', 'question', 'job_type',
            'experience_text', 'rating', 'difficulty', 'offer', 'credits_required',
            'credits_amount'
        ]

    def __init__(self, *args, **kwargs):
        company = kwargs.pop('company', None)  # Capture the company instance if provided
        super().__init__(*args, **kwargs)
        if company:
            self.fields['company'].queryset = Company.objects.filter(pk=company.pk)
            self.fields['company'].initial = company
            self.fields['company'].disabled = True

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ['text']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['text'].widget.attrs.update({'placeholder': 'Write your reply here...'})
