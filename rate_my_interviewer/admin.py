from django.contrib import admin
from .models import RMIProfile, Company, Role, InterviewExperience

admin.site.register(RMIProfile)
admin.site.register(Company)
admin.site.register(Role)
admin.site.register(InterviewExperience)