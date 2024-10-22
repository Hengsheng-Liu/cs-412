from django.urls import path
from .views import CreateFriendView, CreateProfileView, CreateStatusMessageView, DeleteStatusMessageView, ShowAllProfilesView, ShowFriendSuggestionsView, ShowNewsFeedView, ShowProfilePageView, UpdateProfileView, UpdateStatusMessageView

urlpatterns = [
    path('', ShowAllProfilesView.as_view(), name='show_all_profiles'),
    path('profile/<int:pk>/', ShowProfilePageView.as_view(), name='show_profile'),
    path('create_profile/', CreateProfileView.as_view(), name='create_profile'),
    path('profile/<int:pk>/create_status', CreateStatusMessageView.as_view(), name='create_status'),
    path('profile/<int:pk>/update', UpdateProfileView.as_view(), name='update_profile'),
    path('status/<int:pk>/delete', DeleteStatusMessageView.as_view(), name='delete_status'),
    path('status/<int:pk>/update', UpdateStatusMessageView.as_view(), name='update_status'),
    path('profile/<int:pk>/add_friend/<int:other_pk>', CreateFriendView.as_view(), name='add_friend'),
    path('profile/<int:pk>/recommend_friends', ShowFriendSuggestionsView.as_view(), name='recommend_friends'),
    path('profile/<int:pk>/news_feed/', ShowNewsFeedView.as_view(), name='news_feed'),

]
