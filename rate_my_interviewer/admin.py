from django.contrib import admin
from .models import User, Company, Role, InterviewExperience

admin.site.register(User)
admin.site.register(Company)
admin.site.register(Role)
admin.site.register(InterviewExperience)