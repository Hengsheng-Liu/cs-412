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
         path('reviews/', views.ReviewListView.as_view(), name='review_list'),
]
