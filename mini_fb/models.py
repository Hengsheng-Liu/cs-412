from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User ## NEW

class Profile(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    city = models.CharField(max_length=100)
    profile_image_url = models.URLField()
    user = models.ForeignKey(User, on_delete=models.CASCADE,default=1) ## NEW
    def __str__(self):
        return f'{self.first_name} {self.last_name}'
    def get_status_messages(self):
        return self.statusmessage_set.all().order_by('-timestamp')
    def get_absolute_url(self):
        return reverse('show_profile', kwargs={'pk': self.pk})
    def get_friends(self):
        friends1 = Friend.objects.filter(profile1=self)
        friends2 = Friend.objects.filter(profile2=self)
        friends = []
        for friend in friends1:
            friends.append(friend.profile2)
        for friend in friends2:
            friends.append(friend.profile1)
        return friends 
    def add_friend(self, other):
        if self != other and not self.is_friends_with(other):
            Friend.objects.create(profile1=self, profile2=other)
    def is_friends_with(self, other):
        return Friend.objects.filter(profile1=self, profile2=other).exists() or Friend.objects.filter(profile1=other, profile2=self).exists()
    def Recommend_friends(self):
        AlreadyFriends = self.get_friends()
        AllProfiles = Profile.objects.all()
        Recommend = []
        for profile in AllProfiles:
            if profile not in AlreadyFriends and profile != self:
                Recommend.append(profile)
        return Recommend
    def get_news_feed(self):
        profile_statuses = StatusMessage.objects.filter(profile=self)

        friends = self.get_friends()

        friends_statuses = StatusMessage.objects.filter(profile__in=friends)

        news_feed = profile_statuses | friends_statuses
        news_feed = news_feed.order_by('-timestamp')  
        return news_feed
class StatusMessage(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f'{self.profile} : {self.message} - {self.timestamp}'
    
    def get_images(self):
        return self.images.all()
    
class Image(models.Model):
    image = models.ImageField(upload_to='images/')
    status_message = models.ForeignKey(StatusMessage, on_delete=models.CASCADE, related_name='images')


class Friend(models.Model):
    profile1 = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='profile1')
    profile2 = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='profile2')
    timestamp = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f'{self.profile1} & {self.profile2}'
    

