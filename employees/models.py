from django.db import models

class Employee(models.Model):
    DEPARTMENT_CHOICES = [
        ('Engineering', 'Engineering'),
        ('Human Resources', 'Human Resources'),
        ('Sales', 'Sales'),
        ('Marketing', 'Marketing'),
        ('Finance', 'Finance'),
        ('Operations', 'Operations'),
        ('Design', 'Design'),
    ]

    employee_id = models.CharField(max_length=10, unique=True, verbose_name="Employee ID")
    first_name = models.CharField(max_length=50, verbose_name="First Name")
    last_name = models.CharField(max_length=50, verbose_name="Last Name")
    email = models.EmailField(unique=True, verbose_name="Email Address")
    phone = models.CharField(max_length=15, verbose_name="Phone Number")
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES, verbose_name="Department")
    designation = models.CharField(max_length=100, verbose_name="Designation")
    salary = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Salary (USD)")
    date_of_joining = models.DateField(verbose_name="Date of Joining")
    address = models.TextField(blank=True, null=True, verbose_name="Address")

    class Meta:
        ordering = ['-date_of_joining']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.employee_id})"

    @property
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

