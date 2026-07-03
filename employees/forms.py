from django import forms
from .models import Employee

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            'employee_id',
            'first_name',
            'last_name',
            'email',
            'phone',
            'department',
            'designation',
            'salary',
            'date_of_joining',
            'address'
        ]
        widgets = {
            'employee_id': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g., EMP101'}),
            'first_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'email@company.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Phone Number'}),
            'department': forms.Select(attrs={'class': 'form-input'}),
            'designation': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Job Title'}),
            'salary': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Monthly/Annual Salary'}),
            'date_of_joining': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'address': forms.Textarea(attrs={'class': 'form-input form-textarea', 'placeholder': 'Street Address, City, Country', 'rows': 3}),
        }

    def clean_employee_id(self):
        employee_id = self.cleaned_data.get('employee_id')
        # Check if ID already exists, but exclude the current employee if editing
        exists = Employee.objects.filter(employee_id=employee_id)
        if self.instance and self.instance.pk:
            exists = exists.exclude(pk=self.instance.pk)
        if exists.exists():
            raise forms.ValidationError("An employee with this ID already exists.")
        return employee_id

    def clean_email(self):
        email = self.cleaned_data.get('email')
        exists = Employee.objects.filter(email=email)
        if self.instance and self.instance.pk:
            exists = exists.exclude(pk=self.instance.pk)
        if exists.exists():
            raise forms.ValidationError("An employee with this email address already exists.")
        return email
