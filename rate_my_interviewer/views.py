from django.shortcuts import render
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Company,User, Role, InterviewExperience
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import CreateUserForm
from django.shortcuts import render
from .models import Company

def main_page(request):
    query = request.GET.get('q', '')  # Get the search query
    companies = Company.objects.filter(name__icontains=query) if query else []
    
    return render(request, 'rate_my_interviewer/base.html', {
        'companies': companies,
        'query': query
    })
class signup_view(CreateView):
    model = User
    form_class = CreateUserForm
    template_name = 'rate_my_interviewer/signup.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'user_form' not in context:
            context['user_form'] = UserCreationForm()
        return context
    def form_valid(self, form):
        user_form = UserCreationForm(self.request.POST)
        print(user_form.errors)

        if user_form.is_valid():
            user = user_form.save()
            form.instance.user = user
            login(self.request, user)
            return super().form_valid(form)
        else:
            return self.form_invalid(form)
    def get_success_url(self):
        return reverse('main_page')
class UserDetailsView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'rate_my_interviewer/profile.html'
    context_object_name = 'user'
    def get_object(self):
        return self.model.objects.get(pk=self.request.user.pk)  
