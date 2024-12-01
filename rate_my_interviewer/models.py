import csv
import os
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User ## NEW
class RMIProfile(models.Model):
    unique_id = models.AutoField(primary_key=True)  # Auto incrementing primary key
    name = models.TextField()
    email = models.TextField()
    college = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE,default=1) ## NEW


    def __str__(self):
        return self.name


class Company(models.Model):
    company_id = models.AutoField(primary_key=True)  # Auto incrementing primary key
    name = models.TextField()
    industry = models.TextField()
    location = models.TextField()

    def __str__(self):
        return self.name
def load_data():
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
    role_id = models.AutoField(primary_key=True)  # Auto incrementing primary key
    title = models.TextField()
    company = models.ForeignKey(Company, on_delete=models.CASCADE)  # Foreign key to Company
    job_type = models.TextField()

    def __str__(self):
        return f"{self.title} at {self.company.name}"


class InterviewExperience(models.Model):
    experience_id = models.AutoField(primary_key=True)  # Auto incrementing primary key
    user = models.ForeignKey(RMIProfile, on_delete=models.CASCADE, null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)  # Foreign key to Company
    role = models.TextField()
    job_type = models.TextField(default="")
    experience_text = models.TextField()
    date_shared = models.DateField(auto_now_add=True)  # Automatically set to now when created
    rating = models.IntegerField()
    difficulty = models.IntegerField()
    def __str__(self):
        if self.user:
            return f"Experience by {self.user.name} for {self.role} at {self.company.name}"
        else:   
            return f" {self.role.title} at {self.company.name}"
class Comments(models.Model):
    id = models.AutoField(primary_key=True)  # Auto incrementing primary key
    user = models.ForeignKey(RMIProfile, on_delete=models.CASCADE)
    experience = models.ForeignKey(InterviewExperience, on_delete=models.CASCADE)
    text = models.TextField()
    date_shared = models.DateField(auto_now_add=True)  # Automatically set to now when created
    def __str__(self):
        return f"Comment by {self.user.name} on {self.experience.role} at {self.experience.company.name}"
class Likes(models.Model):
    id = models.AutoField(primary_key=True)  # Auto incrementing primary key
    user = models.ForeignKey(RMIProfile, on_delete=models.CASCADE)
    experience = models.ForeignKey(InterviewExperience, on_delete=models.CASCADE)
    def __str__(self):
        return f"Like by {self.user.name} on {self.experience.role} at {self.experience.company.name}"
class Dislikes(models.Model):
    id = models.AutoField(primary_key=True)  # Auto incrementing primary key
    user = models.ForeignKey(RMIProfile, on_delete=models.CASCADE)
    experience = models.ForeignKey(InterviewExperience, on_delete=models.CASCADE)
    def __str__(self):
        return f"Dislike by {self.user.name} on {self.experience.role} at {self.experience.company.name}"