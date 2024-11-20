from typing import List
from django.shortcuts import render
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Company, RMIProfile,User, Role, InterviewExperience
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import CreateUserForm, InterviewExperienceForm
from django.shortcuts import render
from .models import Company

class CompanyListView(ListView):
    model = Company
    template_name = 'rate_my_interviewer/base.html'
    context_object_name = 'companies'
    paginate_by = 10
    def get_queryset(self):
        query = self.request.GET.get('q', '')  
        companies = Company.objects.filter(name__icontains=query).distinct()
        return [company for company in companies]
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')  # Get the search query
        return context
class CompanyDetailView(DetailView):
    model = Company
    template_name = 'rate_my_interviewer/company_detail.html'
    context_object_name = 'company'
    def get_object(self):
        return self.model.objects.get(company_id=self.kwargs['pk'])  # Get the company instance by ID
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company = self.get_object()
        query = self.request.GET.get('q', '')  # Get the search query
        
        # Get all roles associated with this company
        if query:
            roles = Role.objects.filter(company=company, title__icontains=query).distinct()
        else:
            roles = Role.objects.filter(company=company).distinct()
        
        context['roles'] = roles
        context['query'] = query  # Pass the query to the template
        return context

class AddInterviewExperienceView(CreateView):
    model = InterviewExperience
    form_class = InterviewExperienceForm
    template_name = 'rate_my_interviewer/add_experience.html'
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        company = Company.objects.get(company_id = self.kwargs['pk'])  # Get the company instance by ID
        kwargs['company'] = company  # Pass the company to the form
        return kwargs
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company = Company.objects.get(company_id=self.kwargs['pk'])
        context['company'] = company
        return context
    def get_success_url(self):
        return reverse('company_detail', kwargs={'pk': self.kwargs['pk']})  # Redirect to the company detail page
    def form_valid(self, form):
        interview_experience = form.save(commit=False)
        interview_experience.company = Company.objects.get(company_id=self.kwargs['pk'])
        if self.request.user.is_authenticated:
            try:
                rmi_profile = RMIProfile.objects.get(user=self.request.user)
                interview_experience.user = rmi_profile
            except RMIProfile.DoesNotExist:
                interview_experience.user = None  
        role_exist = Role.objects.filter(company=interview_experience.company, title=interview_experience.role)
        if not role_exist:
            role = Role(company=interview_experience.company, title=interview_experience.role, job_type=interview_experience.job_type)
            role.save()
        interview_experience.save()
        return super().form_valid(form)
class ReviewDetailView(DetailView):
    model = InterviewExperience
    template_name = 'rate_my_interviewer/review_detail.html'  # Path to the template
    context_object_name = 'review'  # Name of the object in the template

class ReviewListView(ListView):
    model = InterviewExperience
    template_name = 'rate_my_interviewer/review_list.html'
    context_object_name = 'reviews'

    def get_queryset(self):
        company_id = self.request.GET.get('company')
        role = self.request.GET.get('role')
        job_type = self.request.GET.get('job_type')
        company = Company.objects.get(company_id=company_id) if company_id else None
        if company and role:
            queryset = InterviewExperience.objects.filter(company=company, role=role, job_type=job_type)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company = Company.objects.get(company_id=self.request.GET.get('company')) if self.request.GET.get('company') else None
        context['company'] = company
        context['role'] = self.request.GET.get('role')
        context['job_type'] = self.request.GET.get('job_type')
        return context
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
