from django.views.generic import ListView
from django.views.generic.detail import DetailView
from .models import Profile

class ShowAllProfilesView(ListView):
    model = Profile
    template_name = 'mini_fb/show_all_profiles.html'
    context_object_name = 'profiles'
class ShowProfilePageView(DetailView):
    model = Profile
    template_name = 'mini_fb/show_profile_page.html'
    context_object_name = 'profile'