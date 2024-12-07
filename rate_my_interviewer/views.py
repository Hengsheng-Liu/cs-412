from typing import List
from django.shortcuts import render
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import CheckIn, Comments, Company, RMIProfile, Unlock,User, Role, InterviewExperience
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView, View,TemplateView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.timezone import now
from django.shortcuts import redirect

import plotly
import plotly.graph_objs as go
from .forms import CommentForm, CreateUserForm, InterviewExperienceForm,CompanyComparisonForm
from .models import Company, InterviewExperience, Role
class CompanyListView(ListView):
    model = Company
    template_name = 'rate_my_interviewer/base.html'
    context_object_name = 'companies'
    paginate_by = 20  # Show 10 companies per page

    def get_queryset(self):
        # Get the search query from the GET parameters
        query = self.request.GET.get('q', '')
        industry = self.request.GET.get('industry', '')
        location = self.request.GET.get('location', '')
        companies = Company.objects.all()

        # Apply filters
        if query:
            companies = companies.filter(name__icontains=query)
        if industry:
            companies = companies.filter(industry__icontains=industry)
        if location:
            companies = companies.filter(location__icontains=location)

        # Order by name
        return companies.order_by('name')

    def get_context_data(self, **kwargs):
        # Add the search query to the context
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        context['industries'] = sorted(set(Company.objects.values_list('industry', flat=True)))
        context['locations'] = sorted(set(Company.objects.values_list('location', flat=True)))
        
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

class CompanyStatsView(DetailView):
    model = Company
    template_name = 'rate_my_interviewer/company_stats.html'
    context_object_name = 'company'

    def get_object(self):
        return self.model.objects.get(company_id=self.kwargs['pk'])  # Get the company instance by ID

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company = self.get_object()
        reviews = InterviewExperience.objects.filter(company=company)

        ratings = {}
        difficulties = {}

        # Group reviews by role and calculate statistics
        for review in reviews:
            if review.role not in ratings:
                ratings[review.role] = []
                difficulties[review.role] = []
            ratings[review.role].append(review.rating)
            difficulties[review.role].append(review.difficulty)

        # Create data for ratings plot
        roles = list(ratings.keys())
        avg_ratings = [sum(ratings[role]) / len(ratings[role]) for role in ratings]
        rating_fig = go.Figure(
            data=[go.Scatter(
                x=roles,
                y=avg_ratings,
                mode='lines+markers',
                name='Average Rating',
                line=dict(color='blue')
            )],
            layout=go.Layout(
                title='Average Ratings by Role',
                xaxis_title='Roles',
                yaxis_title='Average Rating',
                legend=dict(orientation="h")
            )
        )
        rating_plot_html = rating_fig.to_html(full_html=False)

        # Create data for difficulty plot
        avg_difficulties = [sum(difficulties[role]) / len(difficulties[role]) for role in difficulties]
        difficulty_fig = go.Figure(
            data=[go.Scatter(
                x=roles,
                y=avg_difficulties,
                mode='lines+markers',
                name='Average Difficulty',
                line=dict(color='red')
            )],
            layout=go.Layout(
                title='Average Difficulty by Role',
                xaxis_title='Roles',
                yaxis_title='Average Difficulty',
                legend=dict(orientation="h")
            )
        )
        difficulty_plot_html = difficulty_fig.to_html(full_html=False)

        # Add plots and additional context
        context['rating_plot'] = rating_plot_html
        context['difficulty_plot'] = difficulty_plot_html
        return context

class AddInterviewExperienceView(CreateView):
    model = InterviewExperience
    form_class = InterviewExperienceForm
    template_name = 'rate_my_interviewer/add_experience.html'
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        company = Company.objects.get(company_id = self.kwargs['pk'])  # Get the company instance by ID
        kwargs['company'] = company  
        kwargs['initial'] = {
            'role': self.request.GET.get('role', ''),  # Default to empty string if not provided
            'job_type': self.request.GET.get('job_type', ''),  # Default to empty string if not provided
        }
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
        if not interview_experience.credits_amount:
            interview_experience.credits_amount = 0
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
    def get_object(self):
        return self.model.objects.get(experience_id=self.kwargs['pk'])
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        review = self.get_object()
        if self.request.user.is_authenticated:
            context['owner'] = review.user == RMIProfile.objects.get(user=self.request.user)
            context['unlocked'] = Unlock.objects.filter(user=RMIProfile.objects.get(user=self.request.user), experience=review).exists()
        else:
            context['owner'] = False
            context['unlocked'] = False
        context['review'] = review
        context['requred_credits'] = self.get_object().credits_required
        context['comments'] = Comments.objects.filter(experience=review)
        print(context['owner'])
        print(context['unlocked'])
        print(context['requred_credits'])
        return context
class UnlockInteriewQuestionView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):

        user_profile = RMIProfile.objects.get(user=self.request.user)
        other_user = RMIProfile.objects.get(unique_id=self.kwargs['owner'])
        credits_amount = self.kwargs['credits']
        if user_profile.credits < credits_amount:
            return redirect('not_enough_credits')
        newUnlock = Unlock(
            user=user_profile,
            experience=InterviewExperience.objects.get(experience_id=self.kwargs['experience'])
        )
        newUnlock.save()
        user_profile.credits -= credits_amount
        user_profile.save()
        other_user.credits += credits_amount
        other_user.save()
        return redirect(reverse('review_detail', kwargs={'pk': self.kwargs['experience']}))
class NotEnoughCreditsView(TemplateView):
    model = InterviewExperience
    template_name = 'rate_my_interviewer/not_enough_credits.html'
class ModifyInterviewExperienceView(UpdateView):
    model = InterviewExperience
    form_class = InterviewExperienceForm
    template_name = 'rate_my_interviewer/modify_experience.html'
    def get_object(self):
        return self.model.objects.get(experience_id=self.kwargs['pk'])
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company'] = self.get_object().company
        return kwargs
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company'] = self.get_object().company
        return context
    def get_success_url(self):
        return reverse('review_detail', kwargs={'pk': self.kwargs['pk']})
class DeleteInterviewExperienceView(DeleteView):
    model = InterviewExperience
    template_name = 'rate_my_interviewer/delete_experience.html'
    def get_object(self):
        return self.model.objects.get(experience_id=self.kwargs['pk'])
    def get_success_url(self):
        experience = self.get_object()
        return reverse('review_list') + f'?company={experience.company.company_id}' + f'&role={experience.role}' + f'&job_type={experience.job_type}'
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
        if user_form.is_valid():
            user = user_form.save()
            form.instance.user = user
            form.instance.credits = 500
            
            login(self.request, user)
            return super().form_valid(form)
        else:
            return self.form_invalid(form)
    def get_success_url(self):
        return reverse('main_page')
class UserDetailsView(LoginRequiredMixin, DetailView):
    model = RMIProfile
    template_name = 'rate_my_interviewer/profile.html'
    context_object_name = 'user'
    
    def get_object(self):
        try:
            return self.model.objects.get(user=self.request.user)  
        except RMIProfile.DoesNotExist:
            return None


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_profile = self.get_object()
        today = now().date()
        
        if user_profile:
            context['comments'] = InterviewExperience.objects.filter(user=user_profile)
            context['TodayCheckIn'] = CheckIn.objects.filter(user=user_profile, date=today).exists()
        else:
            context['comments'] = []
            context['TodayCheckIn'] = False

        context['profile'] = user_profile
        return context

class UserCheckInView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        user_profile = RMIProfile.objects.get(user=self.request.user)

        # Check if the user has already checked in today
        today = now().date()
        if not CheckIn.objects.filter(user=user_profile, date=today).exists():
            CheckIn.objects.create(user=user_profile, date=today)
            user_profile.credits += 50  # Increase credits
            user_profile.save()

        return redirect(reverse('profile'))
class CommentCreateView(CreateView):
    model = Comments
    form_class = CommentForm
    template_name = 'rate_my_interviewer/add_comment.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['experience'] = InterviewExperience.objects.get(experience_id=self.kwargs['pk'])
        return context
    def get_success_url(self):
        return reverse('review_detail', kwargs={'pk': self.kwargs['pk']})
    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.user = RMIProfile.objects.get(user=self.request.user)
        comment.experience = InterviewExperience.objects.get(experience_id=self.kwargs['pk'])
        comment.save()
        return super().form_valid(form) 


class CompanyComparisonView(View):
    template_name = 'rate_my_interviewer/comparison.html'

    def get(self, request):
        form = CompanyComparisonForm(request.GET or None)
        context = {'form': form}

        if form.is_valid():
            company1 = form.cleaned_data['company1']
            company2 = form.cleaned_data['company2']

            # Fetch experiences for both companies
            experiences1 = InterviewExperience.objects.filter(company=company1)
            experiences2 = InterviewExperience.objects.filter(company=company2)

            # Calculate average ratings and difficulties for each company
            avg_rating1 = (
                sum(exp.rating for exp in experiences1) / len(experiences1) if experiences1.exists() else 0
            )
            avg_rating2 = (
                sum(exp.rating for exp in experiences2) / len(experiences2) if experiences2.exists() else 0
            )
            avg_difficulty1 = (
                sum(exp.difficulty for exp in experiences1) / len(experiences1) if experiences1.exists() else 0
            )
            avg_difficulty2 = (
                sum(exp.difficulty for exp in experiences2) / len(experiences2) if experiences2.exists() else 0
            )

            # Rating comparison plot
            rating_fig = go.Figure(data=[
                go.Bar(name=company1.name, x=["Average Rating"], y=[avg_rating1], marker_color='blue'),
                go.Bar(name=company2.name, x=["Average Rating"], y=[avg_rating2], marker_color='orange')
            ])
            rating_fig.update_layout(
                title='Average Ratings Comparison',
                xaxis_title='Metric',
                yaxis_title='Average Rating',
                barmode='group'
            )
            rating_plot_html = rating_fig.to_html(full_html=False)

            # Difficulty comparison plot
            difficulty_fig = go.Figure(data=[
                go.Bar(name=company1.name, x=["Average Difficulty"], y=[avg_difficulty1], marker_color='blue'),
                go.Bar(name=company2.name, x=["Average Difficulty"], y=[avg_difficulty2], marker_color='orange')
            ])
            difficulty_fig.update_layout(
                title='Average Difficulties Comparison',
                xaxis_title='Metric',
                yaxis_title='Average Difficulty',
                barmode='group'
            )
            difficulty_plot_html = difficulty_fig.to_html(full_html=False)

            # Add plots and additional context
            context.update({
                'company1': company1,
                'company2': company2,
                'rating_plot': rating_plot_html,
                'difficulty_plot': difficulty_plot_html,
            })

        return render(request, self.template_name, context)