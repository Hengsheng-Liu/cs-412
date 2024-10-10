from django.views.generic import ListView
from django.urls import reverse
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView

from .models import Profile
from .forms import CreateProfileForm
class ShowAllProfilesView(ListView):
    model = Profile
    template_name = 'mini_fb/show_all_profiles.html'
    context_object_name = 'profiles'
class ShowProfilePageView(DetailView):
    model = Profile
    template_name = 'mini_fb/show_profile_page.html'
    context_object_name = 'profile'
class CreateProfileView(CreateView):
    model = Profile
    form_class = CreateProfileForm
    template_name = 'mini_fb/create_profile_form.html'

    