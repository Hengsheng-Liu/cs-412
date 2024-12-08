import csv
import os
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User  # NEW

class RMIProfile(models.Model):
    """
    Represents a user's profile in the Rate My Interviewer (RMI) application.
    This model is linked to the built-in Django `User` model, allowing extended
    attributes such as name, email, college, and credits.

    Fields:
        unique_id (AutoField): Auto-incrementing primary key for each profile.
        name (TextField): The full name of the user.
        email (TextField): The email address of the user.
        college (TextField): The college or institution the user is associated with.
        credits (IntegerField): The number of credits the user currently has.
        user (ForeignKey): A reference to the Django `User` model, creating a one-to-one-like relationship.

    Methods:
        __str__(): Returns a string representation of the profile, typically the user's name.
    """
    unique_id = models.AutoField(primary_key=True)
    name = models.TextField()
    email = models.TextField()
    college = models.TextField()
    credits = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)  # NEW

    def __str__(self):
        return self.name


class Company(models.Model):
    """
    Represents a company entity within the application.

    Fields:
        company_id (AutoField): Auto-incrementing primary key for each company.
        name (TextField): The name of the company.
        industry (TextField): The industry sector of the company.
        location (TextField): The geographical location (e.g., state or region) of the company.

    Methods:
        __str__(): Returns the company's name.
    """
    company_id = models.AutoField(primary_key=True)
    name = models.TextField()
    industry = models.TextField()
    location = models.TextField()

    def __str__(self):
        return self.name


def load_data():
    """
    Loads and populates the database with company data from a CSV file named 'Fortune 500 Companies.csv'.
    This function first clears existing data from the Company model, then inserts new records from the CSV.

    Steps:
        1. Construct the path to the CSV file using BASE_DIR from settings.
        2. Delete all existing Company records.
        3. Open and read the CSV file.
        4. For each row, extract name, industry, and headquarters state.
        5. Check for duplicates based on name and location before creating new company records.

    Note:
        This function should typically be called once or be part of a data-loading script.
    """
    csv_file_path = os.path.join(settings.BASE_DIR, 'Fortune 500 Companies.csv')
    Company.objects.all().delete()
    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            name = row['name']
            industry = row['industry']
            location = row['headquarters_state']
            duplicate = Company.objects.filter(name=name, location=location)
            if not duplicate:
                company = Company(name=name, industry=industry, location=location)
                company.save()


class Role(models.Model):
    """
    Represents a particular role or position within a company.

    Fields:
        role_id (AutoField): Auto-incrementing primary key for each role.
        title (TextField): The title of the position (e.g., Software Engineer).
        company (ForeignKey): A reference to the Company this role belongs to.
        job_type (TextField): The type of job (e.g., Full-time, Internship).

    Methods:
        __str__(): Returns a string with the role title and the associated company's name.
    """
    role_id = models.AutoField(primary_key=True)
    title = models.TextField()
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    job_type = models.TextField()

    def __str__(self):
        return f"{self.title} at {self.company.name}"


class InterviewExperience(models.Model):
    """
    Stores detailed interview experiences shared by users. Each experience corresponds to
    a particular role at a specific company.

    Fields:
        experience_id (AutoField): Auto-incrementing primary key.
        user (ForeignKey): A reference to the RMIProfile of the user who submitted the experience.
                           Can be null if the user is not associated.
        company (ForeignKey): The company for which the interview was conducted.
        role (TextField): The role/position title interviewed for.
        type (CharField): The type of interview (Behavioral, Technical, Case Study).
        question (TextField): The primary question or prompt in the interview.
        job_type (TextField): The job type associated with the role (e.g., Full-time, Internship).
        experience_text (TextField): A descriptive text of the user's entire interview experience.
        date_shared (DateField): The date the experience was created, set automatically.
        rating (IntegerField): A user-assigned rating of the overall experience.
        difficulty (IntegerField): A user-assigned difficulty rating for the interview.
        offer (BooleanField): Indicates whether the user received an offer after the interview.
        credits_required (BooleanField): If True, indicates that unlocking the full experience requires credits.
        credits_amount (IntegerField): The number of credits needed to unlock the experience if credits_required is True.

    Methods:
        __str__(): Returns a string representation, including the user's name (if available) and role/company.
    """
    TYPE_CHOICES = [
        ("Behavioral", "Behavioral"),
        ("Technical", "Technical"),
        ("Case Study", "Case Study"),
    ]
    experience_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(RMIProfile, on_delete=models.CASCADE, null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    role = models.TextField()
    type = models.CharField(max_length=50, choices=TYPE_CHOICES, default="Behavioral")
    question = models.TextField(default="")
    job_type = models.TextField(default="")
    experience_text = models.TextField()
    date_shared = models.DateField(auto_now_add=True)
    rating = models.IntegerField()
    difficulty = models.IntegerField()
    offer = models.BooleanField(default=False)
    credits_required = models.BooleanField(default=False)
    credits_amount = models.IntegerField(default=0)

    def __str__(self):
        if self.user:
            return f"Experience by {self.user.name} for {self.role} at {self.company.name}"
        else:
            return f"{self.role.title if hasattr(self.role, 'title') else self.role} at {self.company.name}"


class Comments(models.Model):
    """
    Represents user comments on specific interview experiences.

    Fields:
        id (AutoField): Auto-incrementing primary key.
        user (ForeignKey): The RMIProfile of the user who left the comment.
        experience (ForeignKey): The InterviewExperience this comment is associated with.
        text (TextField): The text content of the comment.
        date_shared (DateField): The date the comment was created, set automatically.

    Methods:
        __str__(): Returns a string representation including the user's name and the associated role/company.
    """
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(RMIProfile, on_delete=models.CASCADE)
    experience = models.ForeignKey(InterviewExperience, on_delete=models.CASCADE)
    text = models.TextField()
    date_shared = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.name} on {self.experience.role} at {self.experience.company.name}"


class Unlock(models.Model):
    """
    Represents a record of a user unlocking a particular interview experience that requires credits.

    Fields:
        id (AutoField): Auto-incrementing primary key.
        user (ForeignKey): The RMIProfile of the user who unlocked the experience.
        experience (ForeignKey): The InterviewExperience that was unlocked.

    Methods:
        __str__(): Returns a string indicating which user unlocked which experience.
    """
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(RMIProfile, on_delete=models.CASCADE)
    experience = models.ForeignKey(InterviewExperience, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.name} unlocked {self.experience.role} at {self.experience.company.name}"


class CheckIn(models.Model):
    """
    Records daily check-ins by users, allowing them to gain credits for each check-in.

    Fields:
        id (AutoField): Auto-incrementing primary key.
        user (ForeignKey): The RMIProfile of the user checking in.
        date (DateField): The date of the check-in, set automatically when created.

    Methods:
        The default string representation is not overridden.
    """
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(RMIProfile, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    def __str__(self):
        return f"{self.user.name} checked in on {self.date}"
