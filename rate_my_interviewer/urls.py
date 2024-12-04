from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
        path('', views.CompanyListView.as_view(), name='main_page'),
        path('signup/', views.signup_view.as_view(), name='signup'),
        path('login/', auth_views.LoginView.as_view(template_name='rate_my_interviewer/login.html'), name='login'),
        path('logout/', auth_views.LogoutView.as_view(next_page='main_page'), name='logout'),
        path('profile/', views.UserDetailsView.as_view(), name='profile'),
        path('companies/', views.CompanyListView.as_view(), name='company_list'),
        path('company/<int:pk>/', views.CompanyDetailView.as_view(), name='company_detail'),
        path('company/<int:pk>/add-experience/', views.AddInterviewExperienceView.as_view(), name='add_experience'),
        path('company/<int:pk>/company-stats/', views.CompanyStatsView.as_view(), name='company_stats'),
        path('reviews/', views.ReviewListView.as_view(), name='review_list'),
        path('review/<int:pk>/', views.ReviewDetailView.as_view(), name='review_detail'),
        path('review/<int:pk>/delete/', views.DeleteInterviewExperienceView.as_view(), name='delete_experience'),
        path('review/<int:pk>/edit/', views.ModifyInterviewExperienceView.as_view(), name='modify_experience'),
        path('comment/<int:pk>/add/', views.CommentCreateView.as_view(), name='add_comment'),
        path('comparison/', views.CompanyComparisonView.as_view(), name='comparison'),
]
