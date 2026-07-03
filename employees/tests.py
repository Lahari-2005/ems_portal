from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Employee
from .forms import EmployeeForm
import datetime

class EmployeeModelTest(TestCase):
    def setUp(self):
        self.employee = Employee.objects.create(
            employee_id="EMP999",
            first_name="Jane",
            last_name="Doe",
            email="jane.doe@example.com",
            phone="1234567890",
            department="Engineering",
            designation="Software Engineer",
            salary=85000.00,
            date_of_joining=datetime.date(2026, 1, 15),
            address="123 Silicon Valley Road"
        )

    def test_employee_creation(self):
        self.assertTrue(isinstance(self.employee, Employee))
        self.assertEqual(self.employee.__str__(), "Jane Doe (EMP999)")
        self.assertEqual(self.employee.get_full_name, "Jane Doe")


class EmployeeFormTest(TestCase):
    def setUp(self):
        # Create a pre-existing employee to test unique constraints
        Employee.objects.create(
            employee_id="EMP101",
            first_name="Alice",
            last_name="Smith",
            email="alice@example.com",
            phone="0987654321",
            department="Human Resources",
            designation="HR Manager",
            salary=70000.00,
            date_of_joining=datetime.date(2025, 5, 20)
        )

    def test_valid_form(self):
        form_data = {
            'employee_id': 'EMP102',
            'first_name': 'Bob',
            'last_name': 'Jones',
            'email': 'bob.jones@example.com',
            'phone': '1122334455',
            'department': 'Sales',
            'designation': 'Sales Executive',
            'salary': 50000.00,
            'date_of_joining': '2026-06-01',
            'address': '789 Commercial Street'
        }
        form = EmployeeForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_duplicate_employee_id(self):
        form_data = {
            'employee_id': 'EMP101',  # Duplicate ID
            'first_name': 'Bob',
            'last_name': 'Jones',
            'email': 'bob.jones@example.com',
            'phone': '1122334455',
            'department': 'Sales',
            'designation': 'Sales Executive',
            'salary': 50000.00,
            'date_of_joining': '2026-06-01'
        }
        form = EmployeeForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('employee_id', form.errors)

    def test_duplicate_email(self):
        form_data = {
            'employee_id': 'EMP102',
            'first_name': 'Bob',
            'last_name': 'Jones',
            'email': 'alice@example.com',  # Duplicate email
            'phone': '1122334455',
            'department': 'Sales',
            'designation': 'Sales Executive',
            'salary': 50000.00,
            'date_of_joining': '2026-06-01'
        }
        form = EmployeeForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)


class EmployeeViewsTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='hradmin',
            password='testpassword123'
        )
        self.employee = Employee.objects.create(
            employee_id="EMP001",
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            phone="1234567890",
            department="Engineering",
            designation="Manager",
            salary=90000.00,
            date_of_joining=datetime.date(2025, 1, 10)
        )

    def test_login_page_renders(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'employees/login.html')

    def test_dashboard_redirects_if_unauthenticated(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)  # Should redirect to login

    def test_dashboard_accessible_if_authenticated(self):
        self.client.login(username='hradmin', password='testpassword123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'employees/dashboard.html')
        self.assertEqual(response.context['total_employees'], 1)

    def test_employee_list_search_and_filter(self):
        self.client.login(username='hradmin', password='testpassword123')
        
        # Test default load
        response = self.client.get(reverse('employee_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "John Doe")
        
        # Test Search
        response = self.client.get(reverse('employee_list') + '?search=John')
        self.assertContains(response, "John Doe")
        
        # Test Search (No match)
        response = self.client.get(reverse('employee_list') + '?search=NonExistent')
        self.assertNotContains(response, "John Doe")
        
        # Test Filter by Department
        response = self.client.get(reverse('employee_list') + '?department=Engineering')
        self.assertContains(response, "John Doe")
        
        # Test Filter by Department (No match)
        response = self.client.get(reverse('employee_list') + '?department=Sales')
        self.assertNotContains(response, "John Doe")

    def test_employee_add_post(self):
        self.client.login(username='hradmin', password='testpassword123')
        form_data = {
            'employee_id': 'EMP002',
            'first_name': 'Mark',
            'last_name': 'Spencer',
            'email': 'mark@example.com',
            'phone': '555666777',
            'department': 'Marketing',
            'designation': 'Coordinator',
            'salary': 45000.00,
            'date_of_joining': '2026-05-15'
        }
        response = self.client.post(reverse('employee_add'), data=form_data)
        self.assertEqual(response.status_code, 302)  # Redirects to list on success
        self.assertTrue(Employee.objects.filter(employee_id='EMP002').exists())

    def test_employee_delete_post(self):
        self.client.login(username='hradmin', password='testpassword123')
        response = self.client.post(reverse('employee_delete', kwargs={'pk': self.employee.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Employee.objects.filter(pk=self.employee.pk).exists())

