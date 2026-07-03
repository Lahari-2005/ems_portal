from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Count, Q
from django.core.paginator import Paginator
from .models import Employee
from .forms import EmployeeForm

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")
            
    return render(request, 'employees/login.html')

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('login')

@login_required
def dashboard(request):
    total_employees = Employee.objects.count()
    avg_salary_dict = Employee.objects.aggregate(avg=Avg('salary'))
    avg_salary = avg_salary_dict['avg'] or 0.0
    
    dept_distribution = Employee.objects.values('department').annotate(count=Count('id')).order_by('-count')
    recent_employees = Employee.objects.order_by('-date_of_joining')[:5]
    
    context = {
        'total_employees': total_employees,
        'avg_salary': avg_salary,
        'total_departments': len(dept_distribution),
        'dept_distribution': dept_distribution,
        'recent_employees': recent_employees,
        'active_tab': 'dashboard',
    }
    return render(request, 'employees/dashboard.html', context)

@login_required
def employee_list(request):
    query = request.GET.get('search', '').strip()
    dept_filter = request.GET.get('department', '').strip()
    
    employees = Employee.objects.all()
    
    if query:
        employees = employees.filter(
            Q(employee_id__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(designation__icontains=query)
        )
        
    if dept_filter:
        employees = employees.filter(department=dept_filter)
        
    # Department choices for the dropdown filter
    departments = [choice[0] for choice in Employee.DEPARTMENT_CHOICES]
    
    paginator = Paginator(employees, 10)  # Show 10 employees per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': query,
        'dept_filter': dept_filter,
        'departments': departments,
        'active_tab': 'employees',
    }
    return render(request, 'employees/employee_list.html', context)

@login_required
def employee_add(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Employee added successfully!")
            return redirect('employee_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = EmployeeForm()
        
    context = {
        'form': form,
        'title': 'Add New Employee',
        'submit_text': 'Add Employee',
        'active_tab': 'add_employee',
    }
    return render(request, 'employees/employee_form.html', context)

@login_required
def employee_edit(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, "Employee details updated successfully!")
            return redirect('employee_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = EmployeeForm(instance=employee)
        
    context = {
        'form': form,
        'title': f'Edit Employee: {employee.get_full_name}',
        'submit_text': 'Update Employee',
        'active_tab': 'employees',
    }
    return render(request, 'employees/employee_form.html', context)

@login_required
def employee_delete(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        name = employee.get_full_name
        employee.delete()
        messages.success(request, f"Employee {name} has been deleted successfully.")
        return redirect('employee_list')
    return render(request, 'employees/employee_confirm_delete.html', {'employee': employee})

