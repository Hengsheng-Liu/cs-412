from django.db import models
from django.contrib.auth.models import User ## NEW
class User(models.Model):
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


class Role(models.Model):
    role_id = models.AutoField(primary_key=True)  # Auto incrementing primary key
    title = models.TextField()
    company = models.ForeignKey(Company, on_delete=models.CASCADE)  # Foreign key to Company
    job_type = models.TextField()

    def __str__(self):
        return f"{self.title} at {self.company.name}"


class InterviewExperience(models.Model):
    experience_id = models.AutoField(primary_key=True)  # Auto incrementing primary key
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Foreign key to User
    company = models.ForeignKey(Company, on_delete=models.CASCADE)  # Foreign key to Company
    role = models.ForeignKey(Role, on_delete=models.CASCADE)  # Foreign key to Role
    experience_text = models.TextField()
    date_shared = models.DateField(auto_now_add=True)  # Automatically set to now when created
    rating = models.IntegerField()
    difficulty = models.IntegerField()
    like = models.IntegerField(default=0)
    dislike = models.IntegerField(default=0)

    def __str__(self):
        return f"Experience by {self.user.name} for {self.role.title} at {self.company.name}"
