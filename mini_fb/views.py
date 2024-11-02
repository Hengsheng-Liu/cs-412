from django.views.generic import ListView
from django.urls import reverse
from django.views.generic.detail import DetailView
from django.views import View
from django.views.generic import UpdateView, UpdateView, DeleteView,CreateView
from .models import Friend, Profile, StatusMessage, Image
from .forms import CreateProfileForm, CreateStatusMessageForm, UpdateProfileForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
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
class CreateStatusMessageView(LoginRequiredMixin,CreateView):
    model = StatusMessage
    form_class = CreateStatusMessageForm
    template_name = 'mini_fb/create_status_form.html'
    def get_object(self):
        return self.model.objects.get(pk=self.request.user.pk)  
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = Profile.objects.get(pk=self.request.user.pk)   
        return context
    def form_valid(self, form):
        sm = form.save(commit=False)
        sm.profile = Profile.objects.get(pk=self.request.user.pk)
        sm.save()

        files = self.request.FILES.getlist('files')
        
        for file in files:

            image = Image()
            image.image = file 
            image.status_message = sm
            image.save()

        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('show_profile', kwargs={'pk': self.request.user.pk})
class UpdateProfileView(LoginRequiredMixin,UpdateView):
    model = Profile
    form_class = UpdateProfileForm
    template_name = 'mini_fb/update_profile_form.html'
    def form_valid(self, form):
        return super().form_valid(form)
    def get_object(self):
        return self.model.objects.get(pk=self.request.user.pk)  
    def get_success_url(self):
        return reverse('show_profile', kwargs={'pk': self.request.user.pk})


class DeleteStatusMessageView(LoginRequiredMixin,DeleteView):
    model = StatusMessage
    template_name = 'mini_fb/delete_status_form.html'
    context_object_name = 'status_message'
    def get_object(self):
        return self.model.objects.get(pk=self.request.user.pk)  
    def get_success_url(self):
        return reverse('show_profile', kwargs={'pk': self.request.user.pk})
class UpdateStatusMessageView(LoginRequiredMixin,UpdateView):
    model = StatusMessage
    template_name = 'mini_fb/update_status_form.html'
    fields = ['message']
    context_object_name = 'status_message'
    def get_object(self):
        return self.model.objects.get(pk=self.request.user.pk)  
    def get_success_url(self):
        return reverse('show_profile', kwargs={'pk': self.request.user.pk})
class CreateFriendView(LoginRequiredMixin,View):
    def dispatch(self, request, *args, **kwargs):
        profile = Profile.objects.get(pk=self.request.user.pk)
        other = Profile.objects.get(pk=kwargs['other_pk'])
        profile.add_friend(other)
        return redirect('show_profile', pk=profile.pk)
class ShowFriendSuggestionsView(LoginRequiredMixin,DetailView):
    model = Profile
    template_name = 'mini_fb/recommend_friends.html'
    context_object_name = 'profile'

    def get_object(self):
        return self.model.objects.get(pk=self.request.user.pk)  
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = Profile.objects.get(pk=self.request.user.pk)
        RecommendFriends = profile.Recommend_friends()
        context['RecommendFriends'] = RecommendFriends

        return context
class ShowNewsFeedView(LoginRequiredMixin,DetailView):
    model = Profile
    template_name = 'mini_fb/news_feed.html'
    context_object_name = 'profile'
    def get_object(self):
        return self.model.objects.get(pk=self.request.user.pk)  
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = Profile.objects.get(pk=self.request.user.pk)
        news_feed = profile.get_news_feed()
        context['news_feed'] = news_feed
        return context