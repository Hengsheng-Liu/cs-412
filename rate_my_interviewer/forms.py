from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Company, InterviewExperience, RMIProfile, Comments


class CreateUserForm(forms.ModelForm):
    """
    A form for creating a new user and their associated RMIProfile.
    This form extends `forms.ModelForm`, linked to the `RMIProfile` model,
    and captures additional user details like name, email, and college.

    **Fields:**
        - name (CharField): The user's full name, required.
        - email (EmailField): The user's email address, required.
        - college (CharField): The college/institution the user is associated with, required.

    **Validation:**
        - Ensures the email is not already in use by another RMIProfile.

    **Methods:**
        - clean(): Validates that the email is not already registered with an RMIProfile.
    """
    # A character field for the user's name.
    name = forms.CharField(label="Name", required=True)
    # An email field for the user's email address, must be unique.
    email = forms.EmailField(label="Email", required=True)
    # A character field for the user's college or institution.
    college = forms.CharField(label="College", required=True)

    class Meta:
        # Link this form to the RMIProfile model.
        model = RMIProfile
        # Include only these three fields from the model.
        fields = ['name', 'email', 'college']

    def clean(self):
        """
        Validates that the email provided is unique among RMIProfiles.
        Raises a ValidationError if the email already exists in the database.
        """
        cleaned_data = super().clean()
        email = cleaned_data.get('email')

        # Check if another RMIProfile with this email already exists.
        if RMIProfile.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")

        return cleaned_data


class CompanyComparisonForm(forms.Form):
    """
    A form for selecting two different companies to compare their interview metrics.

    **Fields:**
        - company1 (ModelChoiceField): A dropdown to select the first Company.
        - company2 (ModelChoiceField): A dropdown to select the second Company.
    """
    # First company selection field, sorted and distinct by name.
    company1 = forms.ModelChoiceField(
        queryset=Company.objects.all().order_by('name').distinct(),
        label="Select Company 1",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    # Second company selection field, sorted and distinct by name.
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

    **Fields:**
        - company (ModelChoiceField): The company associated with the experience.
        - role (CharField): The role or position interviewed for.
        - type (ChoiceField): The type of interview (e.g., Behavioral, Technical, Case Study).
        - question (CharField): An optional interview question.
        - experience_text (CharField): Detailed description of the interview experience.
        - rating (ChoiceField): Overall rating (1 to 5).
        - difficulty (ChoiceField): Difficulty rating (1 to 5).
        - job_type (ChoiceField): The type of job (Full-time, Part-time, Internship, etc.).
        - offer (BooleanField): Whether the user received an offer.
        - credits_required (BooleanField): Whether viewing details requires credits.
        - credits_amount (IntegerField): Number of credits required if `credits_required` is true.

    **Custom Initialization:**
        - If a `company` instance is provided in the form kwargs, the company field is set to that instance
          and disabled. This ensures that the experience is recorded for that specific company without changes.

    **Example:**
        form = InterviewExperienceForm(company=my_company)
    """
    # Rating choices from 1 to 5.
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)] 
    # Job type choices for the interviewed position.
    JOB_TYPE_CHOICES = [
        ('Full-time', 'Full-time'),
        ('Part-time', 'Part-time'),
        ('Internship', 'Internship'),
        ('Contract', 'Contract'),
        ('Other', 'Other'),
    ]
    # Interview type choices.
    TYPE_CHOICES = [
        ("Behavioral", "Behavioral"),
        ("Technical", "Technical"),
        ("Case Study", "Case Study"),
    ]

    # Company field linked to the Company model.
    company = forms.ModelChoiceField(
        queryset=Company.objects.all(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    # Role field for the position interviewed for.
    role = forms.CharField(
        label="Role",
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter the role', 'class': 'form-control'})
    )
    # Type of interview: Behavioral, Technical, or Case Study.
    type = forms.ChoiceField(
        label="Type",
        choices=TYPE_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    # Optional field to note a question asked during the interview.
    question = forms.CharField(
        label="Question",
        required=False,
        widget=forms.Textarea(attrs={'placeholder': 'Enter the question (if any)', 'class': 'form-control'})
    )
    # Detailed experience text field.
    experience_text = forms.CharField(
        label="Experience",
        required=False,
        widget=forms.Textarea(attrs={'placeholder': 'Share your experience', 'class': 'form-control'})
    )
    # Overall rating field.
    rating = forms.ChoiceField(
        label="Rating",
        choices=RATING_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    # Difficulty rating field.
    difficulty = forms.ChoiceField(
        label="Difficulty",
        choices=RATING_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    # Type of job applied for.
    job_type = forms.ChoiceField(
        label="Job Type",
        choices=JOB_TYPE_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    # Whether an offer was received.
    offer = forms.BooleanField(
        label="Received Offer?",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    # Indicates if credits are required to view details.
    credits_required = forms.BooleanField(
        label="Charge for credits?",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    # Credits amount field, if credits_required is checked.
    credits_amount = forms.IntegerField(
        label="Credits",
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Enter the number of credits', 'class': 'form-control'}),
        min_value=0
    )

    class Meta:
        # Link this form to the InterviewExperience model.
        model = InterviewExperience
        # Include these fields in the form.
        fields = [
            'company', 'role', 'type', 'question', 'job_type',
            'experience_text', 'rating', 'difficulty', 'offer', 'credits_required',
            'credits_amount'
        ]

    def __init__(self, *args, **kwargs):
        """
        Custom initializer. If a `company` instance is provided in kwargs, set the company field
        to that specific company and disable it, preventing users from changing it.
        """
        company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)
        # If company is provided, restrict the company queryset and disable the field.
        if company:
            self.fields['company'].queryset = Company.objects.filter(pk=company.pk)
            self.fields['company'].initial = company
            self.fields['company'].disabled = True


class CommentForm(forms.ModelForm):
    """
    A simple form for adding comments to an interview experience.

    **Fields:**
        - text (CharField): The comment text.

    **Initialization:**
        - Adds a placeholder to the text field to prompt the user for input.
    """
    class Meta:
        # Link this form to the Comments model.
        model = Comments
        # Include only the text field.
        fields = ['text']

    def __init__(self, *args, **kwargs):
        """
        Initializes the form and updates the widget for 'text' to include a placeholder.
        """
        super().__init__(*args, **kwargs)
        # Add a placeholder to guide the user about what to write.
        self.fields['text'].widget.attrs.update({'placeholder': 'Write your reply here...'})
