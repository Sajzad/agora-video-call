from django.db import models

# Create your models here.



class Session(models.Model):
	session_id = models.CharField(max_length=100)

	def __str__(self):
		return self.session_id