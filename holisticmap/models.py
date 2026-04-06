from django.db import models

# Create your models here.
class Executive (models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
        
class Company (models.Model):
    executive = models.ForeignKey(Executive, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    join_secret_hash = models.CharField(max_length=255)
    company_size = models.IntegerField()
    address = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Employee (models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name