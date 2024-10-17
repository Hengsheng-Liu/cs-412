from django.views.generic import ListView
from django.urls import reverse
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView
from django.views.generic import UpdateView, UpdateView, DeleteView
from .models import Profile, StatusMessage, Image
from .forms import CreateProfileForm, CreateStatusMessageForm, UpdateProfileForm
class ShowAllProfilesView(ListView):
    model = Profile
    template_name = 'mini_fb/show_all_profiles.html'
    context_object_name = 'profiles'
class ShowProfilePageView(DetailView):
    model = Profile
    template_name = 'mini_fb/show_profile.html'
    context_object_name = 'profile'
class CreateProfileView(CreateView):
    model = Profile
    form_class = CreateProfileForm
    template_name = 'mini_fb/create_profile_form.html'
class CreateStatusMessageView(CreateView):
    model = StatusMessage
    form_class = CreateStatusMessageForm
    template_name = 'mini_fb/create_status_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = Profile.objects.get(pk=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        sm = form.save(commit=False)
        sm.profile = Profile.objects.get(pk=self.kwargs['pk'])
        sm.save()

        files = self.request.FILES.getlist('files')
        
        for file in files:

            image = Image()
            image.image = file 
            image.status_message = sm
            image.save()

        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('show_profile', kwargs={'pk': self.kwargs['pk']})
class UpdateProfileView(UpdateView):
    model = Profile
    form_class = UpdateProfileForm
    template_name = 'mini_fb/update_profile_form.html'
    def form_valid(self, form):
        return super().form_valid(form)
    def get_success_url(self):
        return reverse('show_profile', kwargs={'pk': self.kwargs['pk']})


class DeleteStatusMessageView(DeleteView):
    model = StatusMessage
    template_name = 'mini_fb/delete_status_form.html'
    context_object_name = 'status_message'
    def get_success_url(self):
        return reverse('show_profile', kwargs={'pk': self.object.profile.pk})
class UpdateStatusMessageView(UpdateView):
    model = StatusMessage
    template_name = 'mini_fb/update_status_form.html'
    fields = ['message']
    context_object_name = 'status_message'

    def get_success_url(self):
        return reverse('show_profile', kwargs={'pk': self.object.profile.pk})

    