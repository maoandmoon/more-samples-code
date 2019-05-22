from django.db import models

# Create your models here.
class employee(models.Model):
    firstname = models.CharField(max_length = 20)
    lastname = models.CharField(max_length = 30)
    emp_id   = models.IntegerField()

    def __str__(self):
        return (self.firstname)
