from django.db import models
from django.utils import timezone
from django.urls import reverse

class Profile(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    city = models.CharField(max_length=100)
    profile_image_url = models.URLField()

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
    def get_status_messages(self):
        return self.statusmessage_set.all().order_by('-timestamp')
    def get_absolute_url(self):
        return reverse('show_profile', kwargs={'pk': self.pk})
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
