from django.db import models

class Profile(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    city = models.CharField(max_length=100)
    email_address = models.EmailField()
    profile_image_url = models.URLField()

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
