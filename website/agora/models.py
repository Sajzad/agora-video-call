from django.db import models

# Create your models here.



class User(models.Model):
	user = models.CharField(max_length=50, blank=True, null=True)
	email = models.EmailField(null=True, blank=True)
	session_id = models.CharField(max_length=100)

	def __str__(self):
		return self.user