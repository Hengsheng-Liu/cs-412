from typing import List
from django.shortcuts import render
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import CheckIn, Comments, Company, RMIProfile, Unlock, User, Role, InterviewExperience
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView, View, TemplateView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.timezone import now
from django.shortcuts import redirect

import plotly
import plotly.graph_objs as go
from .forms import CommentForm, CreateUserForm, InterviewExperienceForm, CompanyComparisonForm
from .models import Company, InterviewExperience, Role


class CompanyListView(ListView):
    """
    A view that displays a paginated list of companies, with optional search and filtering.

    **Attributes:**
        - model (Model): The model to use (Company).
        - template_name (str): The template file used to render the list.
        - context_object_name (str): The context variable name for the list of companies.
        - paginate_by (int): The number of companies to display per page.

    **Methods:**
        - get_queryset(): Returns a filtered and ordered queryset of companies based on search parameters.
        - get_context_data(**kwargs): Adds search parameters and filter options to the template context.
    """
    model = Company
    template_name = 'rate_my_interviewer/base.html'
    context_object_name = 'companies'
    paginate_by = 20  # Show 20 companies per page

    def get_queryset(self):
        """
        Returns a list of companies filtered by query, industry, and location if provided.
        Orders the companies by their name.

        **Returns:**
            QuerySet: The filtered and ordered list of Company objects.
        """
        query = self.request.GET.get('q', '')
        industry = self.request.GET.get('industry', '')
        location = self.request.GET.get('location', '')
        companies = Company.objects.all()

        # Filter by search query if provided
        if query:
            companies = companies.filter(name__icontains=query)
        # Filter by industry if provided
        if industry:
            companies = companies.filter(industry__icontains=industry)
        # Filter by location if provided
        if location:
            companies = companies.filter(location__icontains=location)

        return companies.order_by('name')

    def get_context_data(self, **kwargs):
        """
        Adds search query and filter lists for industries and locations to the template context.

        **Returns:**
            dict: The context dictionary with additional keys 'query', 'industries', 'locations'.
        """
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        # Get a sorted list of unique industries and locations for dropdown filters
        context['industries'] = sorted(set(Company.objects.values_list('industry', flat=True)))
        context['locations'] = sorted(set(Company.objects.values_list('location', flat=True)))
        return context


class CompanyDetailView(DetailView):
    """
    Displays detailed information about a specific company, including associated roles.

    **Attributes:**
        - model (Model): Company model.
        - template_name (str): The template used to render the company detail.
        - context_object_name (str): The name of the company object in the template context.

    **Methods:**
        - get_object(): Retrieves the company instance based on the provided primary key.
        - get_context_data(**kwargs): Adds filtered roles based on search query and adds them to the context.
    """
    model = Company
    template_name = 'rate_my_interviewer/company_detail.html'
    context_object_name = 'company'

    def get_object(self):
        """
        Retrieves the company instance by its primary key (company_id).

        **Returns:**
            Company: The Company instance.
        """
        return self.model.objects.get(company_id=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        """
        Adds roles associated with the company to the context. If a search query is provided, filters roles by title.

        **Returns:**
            dict: The context dictionary including 'roles' and 'query'.
        """
        context = super().get_context_data(**kwargs)
        company = self.get_object()
        query = self.request.GET.get('q', '')
        # Filter roles by query if provided
        if query:
            roles = Role.objects.filter(company=company, title__icontains=query).distinct()
        else:
            roles = Role.objects.filter(company=company).distinct()
        context['roles'] = roles
        context['query'] = query
        return context


class CompanyStatsView(DetailView):
    """
    Displays statistical data (average ratings and difficulties) for a given company.

    **Attributes:**
        - model (Model): Company model.
        - template_name (str): The template for displaying company stats.
        - context_object_name (str): The variable name for the company object.

    **Methods:**
        - get_object(): Retrieves the company instance.
        - get_context_data(**kwargs): Calculates average ratings and difficulties per role and generates Plotly graphs.
    """
    model = Company
    template_name = 'rate_my_interviewer/company_stats.html'
    context_object_name = 'company'

    def get_object(self):
        """
        Retrieves a specific company instance by its company_id.

        **Returns:**
            Company: The specified Company instance.
        """
        return self.model.objects.get(company_id=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        """
        Calculates and plots average rating and difficulty for each role associated with the company.
        Adds the resulting Plotly charts to the template context.

        **Returns:**
            dict: The context dictionary including rating_plot and difficulty_plot HTML.
        """
        context = super().get_context_data(**kwargs)
        company = self.get_object()
        reviews = InterviewExperience.objects.filter(company=company)

        ratings = {}
        difficulties = {}

        # Collect ratings and difficulties by role
        for review in reviews:
            if review.role not in ratings:
                ratings[review.role] = []
                difficulties[review.role] = []
            ratings[review.role].append(review.rating)
            difficulties[review.role].append(review.difficulty)

        # Calculate average ratings
        roles = list(ratings.keys())
        avg_ratings = [sum(ratings[role]) / len(ratings[role]) for role in ratings]

        # Create the rating figure (line chart)
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

        # Calculate average difficulties
        avg_difficulties = [sum(difficulties[role]) / len(difficulties[role]) for role in difficulties]

        # Create the difficulty figure (line chart)
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

        # Add plots to context
        context['rating_plot'] = rating_plot_html
        context['difficulty_plot'] = difficulty_plot_html
        return context


class AddInterviewExperienceView(LoginRequiredMixin, CreateView):
    """
    A view that allows users to add their interview experiences for a given company.

    **Attributes:**
        - model (Model): InterviewExperience model.
        - form_class (Form): InterviewExperienceForm.
        - template_name (str): Template for creating an experience.

    **Methods:**
        - get_form_kwargs(): Provides the company instance and initial data to the form.
        - get_context_data(**kwargs): Adds the company to the context.
        - get_success_url(): Redirects to the company detail page upon success.
        - form_valid(form): Assigns the company and user, creates a Role if it doesn't exist, and saves the experience.
    """
    model = InterviewExperience
    form_class = InterviewExperienceForm
    template_name = 'rate_my_interviewer/add_experience.html'

    def get_form_kwargs(self):
        """
        Passes the company and initial form data (role, job_type from GET params) to the form.

        **Returns:**
            dict: Keyword arguments passed to the form, including 'company' and 'initial'.
        """
        kwargs = super().get_form_kwargs()
        company = Company.objects.get(company_id=self.kwargs['pk'])
        kwargs['company'] = company
        # Pre-fill role and job_type if available as GET parameters
        kwargs['initial'] = {
            'role': self.request.GET.get('role', ''),
            'job_type': self.request.GET.get('job_type', ''),
        }
        return kwargs

    def get_context_data(self, **kwargs):
        """
        Adds the company to the context.

        **Returns:**
            dict: The context dictionary including the 'company' object.
        """
        context = super().get_context_data(**kwargs)
        company = Company.objects.get(company_id=self.kwargs['pk'])
        context['company'] = company
        return context

    def get_success_url(self):
        """
        Returns the URL to the company detail page after a successful form submission.

        **Returns:**
            str: The URL to the company detail page.
        """
        return reverse('company_detail', kwargs={'pk': self.kwargs['pk']})

    def form_valid(self, form):
        """
        Sets the company and user to the interview experience. If a role does not exist for the given title and company,
        creates one. Saves the interview experience and returns the response of the parent form_valid method.

        **Returns:**
            HttpResponse: The response after the form is successfully processed.
        """
        interview_experience = form.save(commit=False)
        # Ensure credits_amount has a default value if not provided
        if not interview_experience.credits_amount:
            interview_experience.credits_amount = 0

        # Set the company on the interview experience
        interview_experience.company = Company.objects.get(company_id=self.kwargs['pk'])

        # Associate the interview with the logged-in user's profile if possible
        if self.request.user.is_authenticated:
            try:
                rmi_profile = RMIProfile.objects.get(user=self.request.user)
                interview_experience.user = rmi_profile
            except RMIProfile.DoesNotExist:
                interview_experience.user = None

        # Create new role if it doesn't exist
        role_exist = Role.objects.filter(company=interview_experience.company, title=interview_experience.role)
        if not role_exist:
            role = Role(company=interview_experience.company, title=interview_experience.role, job_type=interview_experience.job_type)
            role.save()

        interview_experience.save()
        return super().form_valid(form)


class ReviewDetailView(DetailView):
    """
    A view that displays the details of a single interview experience (review).

    **Attributes:**
        - model (Model): InterviewExperience
        - template_name (str): The template for showing review details.
        - context_object_name (str): The variable name for the review in the template.

    **Methods:**
        - get_object(): Retrieves the review by its experience_id.
        - get_context_data(**kwargs): Adds ownership, unlock status, required credits, and comments to context.
    """
    model = InterviewExperience
    template_name = 'rate_my_interviewer/review_detail.html'
    context_object_name = 'review'

    def get_object(self):
        """
        Retrieves the specific InterviewExperience instance by its experience_id.

        **Returns:**
            InterviewExperience: The requested experience object.
        """
        return self.model.objects.get(experience_id=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        """
        Adds contextual data such as whether the current user is the owner of the review, 
        whether the review is unlocked for them, how many credits are required to unlock, and the associated comments.

        **Returns:**
            dict: The context dictionary with ownership info, unlock status, credits requirement, and comments.
        """
        context = super().get_context_data(**kwargs)
        review = self.get_object()
        if self.request.user.is_authenticated:
            current_profile = RMIProfile.objects.get(user=self.request.user)
            # Check if the current user is the owner of the experience
            context['owner'] = (review.user == current_profile)
            # Check if the experience is unlocked for the current user
            context['unlocked'] = Unlock.objects.filter(user=current_profile, experience=review).exists()
        else:
            context['owner'] = False
            context['unlocked'] = False

        context['review'] = review
        context['requred_credits'] = review.credits_required
        # Fetch all comments associated with this review
        context['comments'] = Comments.objects.filter(experience=review)
        # Display 'Yes'/'No' for offer field
        context['offer'] = "Yes" if review.offer else "No"
        return context


class UnlockInteriewQuestionView(LoginRequiredMixin, View):
    """
    Handles the logic of unlocking an interview experience's questions using credits.

    **Methods:**
        - post(request, *args, **kwargs): Transfers credits from the current user to the owner of the experience,
          creates an Unlock record, and redirects to the review detail page.
    """

    def post(self, request, *args, **kwargs):
        """
        Deducts credits from the current user's RMIProfile and adds them to the owner's RMIProfile,
        then creates an Unlock record for the current user and the specified InterviewExperience.
        Redirects the user to the review detail view.

        **Returns:**
            HttpResponseRedirect: Redirects to the review detail page.
        """
        user_profile = RMIProfile.objects.get(user=self.request.user)
        other_user = RMIProfile.objects.get(unique_id=self.kwargs['owner'])
        credits_amount = self.kwargs['credits']

        # Check if the user has enough credits to unlock
        if user_profile.credits < credits_amount:
            return redirect('not_enough_credits')

        # Create an Unlock record
        newUnlock = Unlock(
            user=user_profile,
            experience=InterviewExperience.objects.get(experience_id=self.kwargs['experience'])
        )
        newUnlock.save()

        # Transfer credits
        user_profile.credits -= credits_amount
        user_profile.save()

        other_user.credits += credits_amount
        other_user.save()

        return redirect(reverse('review_detail', kwargs={'pk': self.kwargs['experience']}))


class NotEnoughCreditsView(TemplateView):
    """
    A view that displays a "Not Enough Credits" page when a user tries to unlock 
    an experience but doesn't have sufficient credits.

    Attributes:
        - model (Model): InterviewExperience (not directly used here, but kept for consistency).
        - template_name (str): The template for "not enough credits" message.
    """
    model = InterviewExperience
    template_name = 'rate_my_interviewer/not_enough_credits.html'


class ModifyInterviewExperienceView(UpdateView):
    """
    A view that allows a user to modify (update) their existing interview experience.

    **Attributes:**
        - model (Model): InterviewExperience
        - form_class (Form): InterviewExperienceForm
        - template_name (str): The template for modifying an experience.

    **Methods:**
        - get_object(): Retrieves the interview experience.
        - get_form_kwargs(): Passes the related company to the form.
        - get_context_data(**kwargs): Adds the company to the context.
        - get_success_url(): Redirects to the updated review detail page.
    """
    model = InterviewExperience
    form_class = InterviewExperienceForm
    template_name = 'rate_my_interviewer/modify_experience.html'

    def get_object(self):
        """
        Retrieves the interview experience instance by its experience_id.

        **Returns:**
            InterviewExperience: The specified experience to modify.
        """
        return self.model.objects.get(experience_id=self.kwargs['pk'])

    def get_form_kwargs(self):
        """
        Passes the company instance of the interview experience to the form.

        **Returns:**
            dict: The form arguments including 'company'.
        """
        kwargs = super().get_form_kwargs()
        kwargs['company'] = self.get_object().company
        return kwargs

    def get_context_data(self, **kwargs):
        """
        Adds the company to the context.

        **Returns:**
            dict: The context dictionary including 'company'.
        """
        context = super().get_context_data(**kwargs)
        context['company'] = self.get_object().company
        return context

    def get_success_url(self):
        """
        Redirects back to the review detail page after a successful update.

        **Returns:**
            str: URL of the updated review detail page.
        """
        return reverse('review_detail', kwargs={'pk': self.kwargs['pk']})


class DeleteInterviewExperienceView(DeleteView):
    """
    A view that allows users to delete an existing interview experience.

    **Attributes:**
        - model (Model): InterviewExperience
        - template_name (str): Template for confirming deletion.

    **Methods:**
        - get_object(): Retrieves the specific interview experience.
        - get_success_url(): Redirects to the review list page for the related company and role.
    """
    model = InterviewExperience
    template_name = 'rate_my_interviewer/delete_experience.html'

    def get_object(self):
        """
        Retrieves the interview experience instance by its experience_id.

        **Returns:**
            InterviewExperience: The experience to delete.
        """
        return self.model.objects.get(experience_id=self.kwargs['pk'])

    def get_success_url(self):
        """
        Constructs a URL to the review list page with the associated company, role, and job type query parameters.

        **Returns:**
            str: The URL to the filtered review list page.
        """
        experience = self.get_object()
        return (reverse('review_list') + f'?company={experience.company.company_id}'
                + f'&role={experience.role}' + f'&job_type={experience.job_type}')


class ReviewListView(ListView):
    """
    Displays a list of interview experiences (reviews) filtered by company, role, and job type.

    **Attributes:**
        - model (Model): InterviewExperience
        - template_name (str): The template to display the list of reviews.
        - context_object_name (str): The variable name for the reviews in the template.

    **Methods:**
        - get_queryset(): Filters reviews by company, role, and job type.
        - get_context_data(**kwargs): Adds company, role, and job_type to the context.
    """
    model = InterviewExperience
    template_name = 'rate_my_interviewer/review_list.html'
    context_object_name = 'reviews'

    def get_queryset(self):
        """
        Filters the InterviewExperience queryset based on GET parameters: company, role, and job_type.

        **Returns:**
            QuerySet: Filtered InterviewExperience objects or none if parameters are missing.
        """
        company_id = self.request.GET.get('company')
        role = self.request.GET.get('role')
        job_type = self.request.GET.get('job_type')

        company = Company.objects.get(company_id=company_id) if company_id else None
        if company and role:
            queryset = InterviewExperience.objects.filter(company=company, role=role, job_type=job_type)
        else:
            queryset = InterviewExperience.objects.none()

        return queryset

    def get_context_data(self, **kwargs):
        """
        Adds the company, role, and job_type parameters to the context for template usage.

        **Returns:**
            dict: The context dictionary with keys 'company', 'role', and 'job_type'.
        """
        context = super().get_context_data(**kwargs)
        company = Company.objects.get(company_id=self.request.GET.get('company')) if self.request.GET.get('company') else None
        context['company'] = company
        context['role'] = self.request.GET.get('role')
        context['job_type'] = self.request.GET.get('job_type')
        return context


class signup_view(CreateView):
    """
    Allows a new user to sign up and create their RMIProfile with initial credits.

    **Attributes:**
        - model (Model): User
        - form_class (Form): CreateUserForm
        - template_name (str): The signup page.

    **Methods:**
        - get_context_data(**kwargs): Adds a UserCreationForm to the context.
        - form_valid(form): Creates a User, assigns credits, logs the user in, and creates an RMIProfile.
        - get_success_url(): Redirects to the main page upon successful signup.
    """
    model = User
    form_class = CreateUserForm
    template_name = 'rate_my_interviewer/signup.html'

    def get_context_data(self, **kwargs):
        """
        Adds a UserCreationForm to the context if not already present.

        **Returns:**
            dict: The context dictionary including 'user_form'.
        """
        context = super().get_context_data(**kwargs)
        if 'user_form' not in context:
            context['user_form'] = UserCreationForm()
        return context

    def form_valid(self, form):
        """
        Validates the user creation form, creates the User and their RMIProfile with initial credits (500),
        logs the user in, and returns the result of the parent form_valid method.

        **Returns:**
            HttpResponse: The response after successful form submission.
        """
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
        """
        Redirects the new user to the main page after a successful signup.

        **Returns:**
            str: The URL of the main page.
        """
        return reverse('main_page')


class UserDetailsView(LoginRequiredMixin, DetailView):
    """
    Displays details of the currently logged-in user's profile, including their interview experiences and 
    whether they have checked in today.

    **Attributes:**
        - model (Model): RMIProfile
        - template_name (str): The profile template.
        - context_object_name (str): 'user'

    **Methods:**
        - get_object(): Retrieves the RMIProfile associated with the current user.
        - get_context_data(**kwargs): Adds user experiences, check-in status, and profile details to the context.
    """
    model = RMIProfile
    template_name = 'rate_my_interviewer/profile.html'
    context_object_name = 'user'

    def get_object(self):
        """
        Retrieves the RMIProfile for the currently logged-in user, or None if not found.

        **Returns:**
            RMIProfile or None: The logged-in user's profile.
        """
        try:
            return self.model.objects.get(user=self.request.user)
        except RMIProfile.DoesNotExist:
            return None

    def get_context_data(self, **kwargs):
        """
        Adds the user's interview experiences, today's check-in status, and the profile details to the context.

        **Returns:**
            dict: The context dictionary including 'comments', 'TodayCheckIn', and 'profile'.
        """
        context = super().get_context_data(**kwargs)
        user_profile = self.get_object()
        today = now().date()

        # Add all experiences created by this user
        if user_profile:
            context['comments'] = InterviewExperience.objects.filter(user=user_profile)
            # Check if the user has checked in today
            context['TodayCheckIn'] = CheckIn.objects.filter(user=user_profile, date=today).exists()
        else:
            context['comments'] = []
            context['TodayCheckIn'] = False

        context['profile'] = user_profile
        return context


class UserCheckInView(LoginRequiredMixin, View):
    """
    Handles a user's daily check-in, awarding credits if they haven't checked in today.

    **Methods:**
        - post(request, *args, **kwargs): Creates a CheckIn entry if not existing for today and awards credits.
    """

    def post(self, request, *args, **kwargs):
        """
        Checks if the user has checked in today. If not, creates a CheckIn record and adds 50 credits to the user's profile.

        **Returns:**
            HttpResponseRedirect: Redirects to the user's profile page.
        """
        user_profile = RMIProfile.objects.get(user=self.request.user)
        today = now().date()

        # Award credits only if the user hasn't checked in today
        if not CheckIn.objects.filter(user=user_profile, date=today).exists():
            CheckIn.objects.create(user=user_profile, date=today)
            user_profile.credits += 50
            user_profile.save()

        return redirect(reverse('profile'))


class CommentCreateView(CreateView):
    """
    Allows users to add comments to an interview experience.

    **Attributes:**
        - model (Model): Comments
        - form_class (Form): CommentForm
        - template_name (str): The template for adding a comment.

    **Methods:**
        - get_context_data(**kwargs): Adds the associated experience to the context.
        - get_success_url(): Redirects to the review detail page.
        - form_valid(form): Associates the comment with the current user and the experience.
    """
    model = Comments
    form_class = CommentForm
    template_name = 'rate_my_interviewer/add_comment.html'

    def get_context_data(self, **kwargs):
        """
        Adds the InterviewExperience instance related to the comment to the context.

        **Returns:**
            dict: The context dictionary including the related 'experience'.
        """
        context = super().get_context_data(**kwargs)
        context['experience'] = InterviewExperience.objects.get(experience_id=self.kwargs['pk'])
        return context

    def get_success_url(self):
        """
        Redirects to the review detail page after adding a comment.

        **Returns:**
            str: The URL of the review detail page.
        """
        return reverse('review_detail', kwargs={'pk': self.kwargs['pk']})

    def form_valid(self, form):
        """
        Sets the user and experience for the comment and saves it.

        **Returns:**
            HttpResponse: The response after the form is successfully processed.
        """
        comment = form.save(commit=False)
        comment.user = RMIProfile.objects.get(user=self.request.user)
        comment.experience = InterviewExperience.objects.get(experience_id=self.kwargs['pk'])
        comment.save()
        return super().form_valid(form)


class CompanyComparisonView(View):
    """
    A view for comparing two companies side-by-side based on their average ratings and difficulties.

    **Attributes:**
        - template_name (str): The template file for displaying the comparison.

    **Methods:**
        - get(request): Renders the form for selecting two companies and displays comparison charts if valid input.
    """
    template_name = 'rate_my_interviewer/comparison.html'

    def get(self, request):
        """
        Displays a form to select two companies. If both companies are selected and the form is valid,
        it fetches their interview experiences, calculates average ratings and difficulties, 
        and creates comparison charts using Plotly.

        **Returns:**
            HttpResponse: The rendered template with the comparison form and optional charts.
        """
        form = CompanyComparisonForm(request.GET or None)
        context = {'form': form}

        # If the form is valid and both companies are selected
        if form.is_valid():
            company1 = form.cleaned_data['company1']
            company2 = form.cleaned_data['company2']

            experiences1 = InterviewExperience.objects.filter(company=company1)
            experiences2 = InterviewExperience.objects.filter(company=company2)

            avg_rating1 = (sum(exp.rating for exp in experiences1) / len(experiences1) if experiences1.exists() else 0)
            avg_rating2 = (sum(exp.rating for exp in experiences2) / len(experiences2) if experiences2.exists() else 0)
            avg_difficulty1 = (sum(exp.difficulty for exp in experiences1) / len(experiences1) if experiences1.exists() else 0)
            avg_difficulty2 = (sum(exp.difficulty for exp in experiences2) / len(experiences2) if experiences2.exists() else 0)

            # Create rating comparison chart (bar chart)
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

            # Create difficulty comparison chart (bar chart)
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

            # Add charts to the context
            context.update({
                'company1': company1,
                'company2': company2,
                'rating_plot': rating_plot_html,
                'difficulty_plot': difficulty_plot_html,
            })

        return render(request, self.template_name, context)
