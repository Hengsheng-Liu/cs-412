from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Main page: Displays a list of companies (CompanyListView).
    path('', views.CompanyListView.as_view(), name='main_page'),

    # User registration page: Displayed via `signup_view` (a class-based view).
    path('signup/', views.signup_view.as_view(), name='signup'),

    # Login page: Uses Django's built-in LoginView with a custom template.
    path('login/', auth_views.LoginView.as_view(template_name='rate_my_interviewer/login.html'), name='login'),

    # Logout page: Uses Django's built-in LogoutView and redirects to the main page after logout.
    path('logout/', auth_views.LogoutView.as_view(next_page='main_page'), name='logout'),

    # User profile page: Displays details of the currently logged-in user (UserDetailsView).
    path('profile/', views.UserDetailsView.as_view(), name='profile'),

    # Companies list page: Shows a list of all companies (CompanyListView).
    path('companies/', views.CompanyListView.as_view(), name='company_list'),

    # Company detail page: Displays details of a single company identified by its primary key.
    path('company/<int:pk>/', views.CompanyDetailView.as_view(), name='company_detail'),

    # Add interview experience page: Allows adding a new interview experience for a given company.
    path('company/<int:pk>/add-experience/', views.AddInterviewExperienceView.as_view(), name='add_experience'),

    # Company stats page: Displays statistics about a company (e.g., average ratings, difficulty).
    path('company/<int:pk>/company-stats/', views.CompanyStatsView.as_view(), name='company_stats'),

    # Reviews list page: Displays a list of all shared interview experiences (ReviewListView).
    path('reviews/', views.ReviewListView.as_view(), name='review_list'),

    # Review detail page: Shows a single interview experience (ReviewDetailView).
    path('review/<int:pk>/', views.ReviewDetailView.as_view(), name='review_detail'),

    # Delete experience page: Allows deleting an existing interview experience (DeleteInterviewExperienceView).
    path('review/<int:pk>/delete/', views.DeleteInterviewExperienceView.as_view(), name='delete_experience'),

    # Edit experience page: Allows modifying an existing interview experience (ModifyInterviewExperienceView).
    path('review/<int:pk>/edit/', views.ModifyInterviewExperienceView.as_view(), name='modify_experience'),

    # Add comment page: Allows adding a new comment to an interview experience (CommentCreateView).
    path('comment/<int:pk>/add/', views.CommentCreateView.as_view(), name='add_comment'),

    # Company comparison page: Allows comparing two companies' interview metrics (CompanyComparisonView).
    path('comparison/', views.CompanyComparisonView.as_view(), name='comparison'),

    # Check-in page: Allows users to check in and potentially earn credits (UserCheckInView).
    path('CheckIn/', views.UserCheckInView.as_view(), name='CheckIn'),

    # Unlock review page: Allows a user to unlock an interview experience using credits (UnlockInteriewQuestionView).
    path('unlock_review/<int:owner>/<int:credits>/<int:experience>', views.UnlockInteriewQuestionView.as_view(), name='unlock_review'),

    # Not enough credits page: Redirected to if a user tries to unlock content without sufficient credits.
    path('not_enough_credits/', views.NotEnoughCreditsView.as_view(), name='not_enough_credits'),
]
