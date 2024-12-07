from django.contrib import admin
from .models import RMIProfile, Company, Role, InterviewExperience, Comments, Unlock, CheckIn

admin.site.register(RMIProfile)
admin.site.register(Company)
admin.site.register(Role)
admin.site.register(InterviewExperience)
admin.site.register(Comments)
admin.site.register(Unlock)
admin.site.register(CheckIn)
