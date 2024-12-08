from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Company, InterviewExperience, RMIProfile, Comments


class CreateUserForm(forms.ModelForm):
    """
    A form for creating a new user and their associated RMIProfile.
    This form extends `forms.ModelForm`, linked to the `RMIProfile` model,
    and captures additional user details like name, email, and college.

    Fields:
        name (CharField): The user's full name, required.
        email (EmailField): The user's email address, required.
        college (CharField): The college/institution the user is associated with, required.

    Validation:
        Checks if the provided email is already in use by an existing RMIProfile.

    Methods:
        clean(): Validates that the email is not already registered with an RMIProfile.
    """
    name = forms.CharField(label="Name", required=True)
    email = forms.EmailField(label="Email", required=True)
    college = forms.CharField(label="College", required=True)

    class Meta:
        model = RMIProfile
        fields = ['name', 'email', 'college']

    def clean(self):
        """
        Ensures that the email provided is unique among RMIProfiles.
        Raises a ValidationError if the email already exists in the database.
        """
        cleaned_data = super().clean()
        email = cleaned_data.get('email')

        if RMIProfile.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")

        return cleaned_data


class CompanyComparisonForm(forms.Form):
    """
    A form for selecting two different companies to compare their interview metrics.

    Fields:
        company1 (ModelChoiceField): A dropdown to select the first Company.
        company2 (ModelChoiceField): A dropdown to select the second Company.
    """
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


class InterviewExperienceForm(forms.ModelForm):
    """
    A form for adding or editing an interview experience.
    This form is linked to the `InterviewExperience` model and includes fields
    for company, role, interview type, question, experience details, rating, difficulty,
    job type, offer status, and optional credit charging details.

    Fields:
        company (ModelChoiceField): The company the experience is associated with.
        role (CharField): The role or position interviewed for.
        type (ChoiceField): The type of interview (Behavioral, Technical, Case Study).
        question (CharField): A question asked during the interview, if any.
        experience_text (CharField): A detailed description of the interview experience.
        rating (ChoiceField): A rating for the overall experience (1 to 5).
        difficulty (ChoiceField): A difficulty rating (1 to 5).
        job_type (ChoiceField): The type of job (Full-time, Part-time, Internship, Contract, Other).
        offer (BooleanField): Whether the user received an offer from this interview.
        credits_required (BooleanField): If true, other users must pay credits to view details.
        credits_amount (IntegerField): The amount of credits required if credits_required is true.

    Custom Initialization:
        If a `company` instance is provided in the form kwargs, the company field is set to that instance
        and disabled, ensuring that the experience is recorded for that specific company without changes.

    Example:
        form = InterviewExperienceForm(company=my_company)
    """
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
        """
        If a `company` instance is provided in kwargs, the company field is set to that specific company
        and disabled, preventing users from changing it.
        """
        company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)
        if company:
            self.fields['company'].queryset = Company.objects.filter(pk=company.pk)
            self.fields['company'].initial = company
            self.fields['company'].disabled = True


class CommentForm(forms.ModelForm):
    """
    A simple form for adding comments to an interview experience.

    Fields:
        text (CharField): The comment text.

    Initialization:
        Adds a placeholder to the text field to prompt the user for input.
    """
    class Meta:
        model = Comments
        fields = ['text']

    def __init__(self, *args, **kwargs):
        """
        Initializes the form and updates the widget for 'text' to include a placeholder.
        """
        super().__init__(*args, **kwargs)
        self.fields['text'].widget.attrs.update({'placeholder': 'Write your reply here...'})
