import csv
import os
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User  # Django's built-in User model

class RMIProfile(models.Model):
    """
    Represents a user's profile in the Rate My Interviewer (RMI) application.
    This model is linked to the built-in Django `User` model, allowing extended
    attributes such as name, email, college, and credits.

    **Fields:**
        - unique_id (AutoField): Auto-incrementing primary key for each profile.
        - name (TextField): The full name of the user.
        - email (TextField): The email address of the user.
        - college (TextField): The college or institution the user is associated with.
        - credits (IntegerField): The number of credits the user currently has.
        - user (ForeignKey to User): A reference to the Django `User` model, creating a 
          one-to-one-like relationship for authentication and profile management.

    **Methods:**
        - __str__(): Returns a string representation of the profile, typically the user's name.
    """
    # Primary key for the profile.
    unique_id = models.AutoField(primary_key=True)
    # The user's full name.
    name = models.TextField()
    # The user's email address.
    email = models.TextField()
    # The college or institution the user is associated with.
    college = models.TextField()
    # The number of credits a user currently holds.
    credits = models.IntegerField(default=0)
    # Link to the built-in Django User model (one-to-many, but often used as one-to-one).
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)

    def __str__(self):
        return self.name


class Company(models.Model):
    """
    Represents a company entity within the application.

    **Fields:**
        - company_id (AutoField): Auto-incrementing primary key for each company.
        - name (TextField): The name of the company.
        - industry (TextField): The industry sector of the company.
        - location (TextField): The geographical location (e.g., state or region) of the company.

    **Methods:**
        - __str__(): Returns the company's name.
    """
    # Primary key for the company.
    company_id = models.AutoField(primary_key=True)
    # The company's name.
    name = models.TextField()
    # The industry sector the company operates in.
    industry = models.TextField()
    # The geographical location of the company (e.g., state).
    location = models.TextField()

    def __str__(self):
        return self.name


def load_data():
    """
    Loads and populates the database with company data from a CSV file named 'Fortune 500 Companies.csv'.
    This function first clears existing data from the Company model, then inserts new records from the CSV.

    **Steps:**
        1. Construct the path to the CSV file using `settings.BASE_DIR`.
        2. Delete all existing Company records to ensure a clean slate.
        3. Open and read the CSV file.
        4. For each row, extract `name`, `industry`, and `headquarters_state` as `location`.
        5. Check for duplicates based on `name` and `location` before creating new company records.

    **Note:**
        This function should typically be called once or be part of a data-loading script.
    """
    # Build the path to the CSV file.
    csv_file_path = os.path.join(settings.BASE_DIR, 'Fortune 500 Companies.csv')
    # Clear existing Company data.
    Company.objects.all().delete()
    # Open the CSV file and read data.
    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            name = row['name']
            industry = row['industry']
            location = row['headquarters_state']
            # Check for duplicates based on name and location.
            duplicate = Company.objects.filter(name=name, location=location)
            # If no duplicate found, create a new Company record.
            if not duplicate:
                company = Company(name=name, industry=industry, location=location)
                company.save()


class Role(models.Model):
    """
    Represents a particular role or position within a company.

    **Fields:**
        - role_id (AutoField): Auto-incrementing primary key for each role.
        - title (TextField): The title of the position (e.g., 'Software Engineer').
        - company (ForeignKey to Company): The company this role belongs to.
        - job_type (TextField): The type of job (e.g., 'Full-time', 'Internship').

    **Methods:**
        - __str__(): Returns a string with the role title and the associated company's name.
    """
    # Primary key for the role.
    role_id = models.AutoField(primary_key=True)
    # The title of the position (e.g., 'Data Scientist').
    title = models.TextField()
    # Link this role to a specific company.
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    # The job type (e.g., 'Full-time', 'Internship').
    job_type = models.TextField()

    def __str__(self):
        return f"{self.title} at {self.company.name}"


class InterviewExperience(models.Model):
    """
    Stores detailed interview experiences shared by users. Each experience corresponds to
    a particular role at a specific company.

    **Fields:**
        - experience_id (AutoField): Auto-incrementing primary key.
        - user (ForeignKey to RMIProfile): The profile of the user who submitted the experience.
        - company (ForeignKey to Company): The company for which the interview was conducted.
        - role (TextField): The role or position title interviewed for.
        - type (CharField with choices): The type of interview (Behavioral, Technical, Case Study).
        - question (TextField): The primary question or prompt asked during the interview.
        - job_type (TextField): The job type (Full-time, Internship, etc.).
        - experience_text (TextField): A descriptive text of the user's entire interview experience.
        - date_shared (DateField): The date the experience was created, set automatically.
        - rating (IntegerField): User-assigned rating of the overall experience.
        - difficulty (IntegerField): User-assigned difficulty rating.
        - offer (BooleanField): Indicates if the user received an offer.
        - credits_required (BooleanField): If True, indicates that unlocking the full experience requires credits.
        - credits_amount (IntegerField): Number of credits needed to unlock the experience if credits_required is True.

    **Methods:**
        - __str__(): Returns a string representation, including the user's name (if available) and role/company.
    """
    # Predefined choices for interview type.
    TYPE_CHOICES = [
        ("Behavioral", "Behavioral"),
        ("Technical", "Technical"),
        ("Case Study", "Case Study"),
    ]
    # Primary key for the interview experience.
    experience_id = models.AutoField(primary_key=True)
    # The user (RMIProfile) who shared the experience.
    user = models.ForeignKey(RMIProfile, on_delete=models.CASCADE, null=True, blank=True)
    # The company associated with the interview.
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    # The role/position that was interviewed for.
    role = models.TextField()
    # The interview type (Behavioral, Technical, Case Study).
    type = models.CharField(max_length=50, choices=TYPE_CHOICES, default="Behavioral")
    # The main question asked during the interview.
    question = models.TextField(default="")
    # The job type (e.g., Full-time, Internship).
    job_type = models.TextField(default="")
    # Detailed text describing the user's interview experience.
    experience_text = models.TextField()
    # The date this experience was shared; auto-populated.
    date_shared = models.DateField(auto_now_add=True)
    # User-assigned overall rating for the experience.
    rating = models.IntegerField()
    # User-assigned difficulty rating.
    difficulty = models.IntegerField()
    # Indicates if the user received an offer from this interview.
    offer = models.BooleanField(default=False)
    # Indicates if credits are required to unlock full experience details.
    credits_required = models.BooleanField(default=False)
    # The number of credits needed if credits_required is True.
    credits_amount = models.IntegerField(default=0)

    def __str__(self):
        # If user is linked, display their name; otherwise, just the role and company.
        if self.user:
            return f"Experience by {self.user.name} for {self.role} at {self.company.name}"
        else:
            # Check if role has a title attribute (Role object) or just role text.
            return f"{getattr(self.role, 'title', self.role)} at {self.company.name}"


class Comments(models.Model):
    """
    Represents user comments on specific interview experiences.

    **Fields:**
        - id (AutoField): Auto-incrementing primary key.
        - user (ForeignKey to RMIProfile): The profile of the user who posted the comment.
        - experience (ForeignKey to InterviewExperience): The experience this comment belongs to.
        - text (TextField): The text content of the comment.
        - date_shared (DateField): The date the comment was created, set automatically.

    **Methods:**
        - __str__(): Returns a string representation including the user's name and associated role/company.
    """
    # Primary key for the comment.
    id = models.AutoField(primary_key=True)
    # The user who wrote the comment.
    user = models.ForeignKey(RMIProfile, on_delete=models.CASCADE)
    # The interview experience this comment is associated with.
    experience = models.ForeignKey(InterviewExperience, on_delete=models.CASCADE)
    # The content of the comment.
    text = models.TextField()
    # The date this comment was shared; auto-populated.
    date_shared = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.name} on {self.experience.role} at {self.experience.company.name}"


class Unlock(models.Model):
    """
    Represents a record of a user unlocking a particular interview experience that requires credits.

    **Fields:**
        - id (AutoField): Auto-incrementing primary key.
        - user (ForeignKey to RMIProfile): The profile of the user who unlocked the experience.
        - experience (ForeignKey to InterviewExperience): The interview experience that was unlocked.

    **Methods:**
        - __str__(): Returns a string indicating which user unlocked which experience.
    """
    # Primary key for the unlock record.
    id = models.AutoField(primary_key=True)
    # The user who unlocked the experience.
    user = models.ForeignKey(RMIProfile, on_delete=models.CASCADE)
    # The experience that was unlocked.
    experience = models.ForeignKey(InterviewExperience, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.name} unlocked {self.experience.role} at {self.experience.company.name}"


class CheckIn(models.Model):
    """
    Records daily check-ins by users, allowing them to gain credits for each check-in.

    **Fields:**
        - id (AutoField): Auto-incrementing primary key.
        - user (ForeignKey to RMIProfile): The profile of the user checking in.
        - date (DateField): The date of the check-in, set automatically when created.

    **Methods:**
        - __str__(): Returns a string representation of which user checked in and when.
    """
    # Primary key for the check-in record.
    id = models.AutoField(primary_key=True)
    # The user who performed the check-in.
    user = models.ForeignKey(RMIProfile, on_delete=models.CASCADE)
    # The date of the check-in; auto-populated.
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.name} checked in on {self.date}"
