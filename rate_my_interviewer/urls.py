from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
        path('', views.main_page, name='main_page'),
        path('signup/', views.signup_view.as_view(), name='signup'),
        path('login/', auth_views.LoginView.as_view(template_name='rate_my_interviewer/login.html'), name='login'),
        path('logout/', auth_views.LogoutView.as_view(next_page='main_page'), name='logout'),
        path('profile/', views.UserDetailsView.as_view(), name='profile'),

]
