from django.db import models

class Student(models.Model):
    STATUS_CHOICES = [
        ('Borrowed', 'Borrowed'),
        ('Returned', 'Returned'),
    ]

    fullname = models.CharField(max_length=255, default='Unknown')
    email = models.EmailField(default='example@example.com')
    contact_number = models.CharField(max_length=20, default='N/A')
    course = models.CharField(max_length=100, default='Undeclared')
    borrowed_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Borrowed')
    returned_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.fullname
