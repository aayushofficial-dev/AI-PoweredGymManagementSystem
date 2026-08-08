from django.shortcuts import redirect, render

from GymApp.models import *

from django.contrib import messages

# Create your views here.
def home(request):
    '''
    Simple homepage + contact/enquiry form
    '''
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        message = request.POST.get('message')

        if name and email and mobile and message:
            Enquiry.objects.create(
                name=name, 
                email=email,
                mobile=mobile,
                message=message
            )
            messages.success(request, 'Your enquiry has been submitted successfully!')
            return redirect('home') # redirect to the home page after successful submission
        else:
            messages.error(request, 'Please fill in all the fields before submitting the form.')

    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')


from django.contrib.auth import authenticate, login, logout

def admin_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and getattr(user, 'role', None) == 'ADMIN':  # Check if the user is an admin/staff
            login(request, user) # log the user in using Django's built-in login function
            messages.success(request, 'Logged in successfully!.')
            return redirect('admin_dashboard')  # Redirect to the admin dashboard
        else:
            messages.error(request, 'Invalid credentials or not an admin')
    return render(request, 'admin_login.html')

def admin_required(view_func):
    '''
    Decorator to ensure that the user is an admin before accessing certain views.
    '''
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or getattr(request.user, 'role', None) != 'ADMIN':
            messages.error(request, 'You must be logged in as an admin to access this page.')
            return redirect('admin_login')  # Redirect to the admin login page
        return view_func(request, *args, **kwargs)
    return wrapper

@admin_required
def admin_dashboard_view(request):
    return render(request, 'admin_dashboard.html')

def logout_view(request):
    logout(request) #log the user out using Django's built-in logout function
    messages.success(request, 'Logged out successfully!')
    return redirect('home') # Redirect to the home page after logout

@admin_required
def admin_plans_list(request):
    plans = MembershipPlan.objects.all().order_by('duration_months') # Fetch all membership plans from the database and order them by duration
    return render(request, 'admin_plans_list.html', {'plans': plans})

@admin_required
def admin_plan_add(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        duration_months = request.POST.get('duration_months')
        fee = request.POST.get('fee')
        description = request.POST.get('description')

        if name and duration_months and fee:
            MembershipPlan.objects.create(
                name=name,
                duration_months=duration_months,
                fee=fee,
                description=description
            )
            messages.success(request, 'Membership plan added successfully!')
            return redirect('admin_plans_list')  # Redirect to the plans list after successful addition
        else:
            messages.error(request, 'Please fill in all the required fields.')

    return render(request, 'admin_plan_form.html', {'mode': 'add'})  # Pass mode to the template to indicate it's an add operation

@admin_required
def admin_plan_edit(request, plan_id):
    plan = MembershipPlan.objects.get(id=plan_id)  # Fetch the specific membership plan based on the provided ID

    if request.method == 'POST':
        name = request.POST.get('name')
        duration_months = request.POST.get('duration_months')
        fee = request.POST.get('fee')
        description = request.POST.get('description')

        if name and duration_months and fee:
            plan.name = name
            plan.duration_months = duration_months
            plan.fee = fee
            plan.description = description
            plan.save()  # Save the updated plan details to the database
            messages.success(request, 'Membership plan updated successfully!')
            return redirect('admin_plans_list')  # Redirect to the plans list after successful update
        else:
            messages.error(request, 'Please fill in all the required fields.')

    return render(request, 'admin_plan_form.html', {'plan': plan, 'mode': 'edit'})  # Pass mode to the template to indicate it's an edit operation

@admin_required
def admin_plan_delete(request, plan_id):
    plan = MembershipPlan.objects.get(id=plan_id)  # Fetch the specific membership plan based on the provided ID
    if request.method == 'POST':
        plan.delete()  # Delete the plan from the database
        messages.success(request, 'Membership plan deleted successfully!')
        return redirect('admin_plans_list')  # Redirect to the plans list after successful deletion
    return redirect('admin_plans_list')  # Render a confirmation page before deletion



@admin_required
def admin_trainers_list(request):
    trainers = Trainer.objects.all().order_by('name')  # Fetch all trainers from the database and order them by name
    return render(request, 'admin_trainers_list.html', {'trainers': trainers})

@admin_required
def admin_trainer_add(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        mobile = request.POST.get('mobile')
        specialization = request.POST.get('specialization')
        shift_timing = request.POST.get('shift_timing')

        if name and mobile and specialization and shift_timing:
            Trainer.objects.create(
                name=name,
                mobile=mobile,
                specialization=specialization,
                shift_timing=shift_timing
            )
            messages.success(request, 'Trainer added successfully!')
            return redirect('admin_trainers_list')  # Redirect to the trainers list after successful addition
        else:
            messages.error(request, 'Please fill in all the required fields.')

    return render(request, 'admin_trainer_form.html', {'mode': 'add'})  # Pass mode to the template to indicate it's an add operation

@admin_required
def admin_trainer_edit(request, trainer_id):
    trainer = Trainer.objects.get(id=trainer_id)  # Fetch the specific trainer based on the provided ID

    if request.method == 'POST':
        name = request.POST.get('name')
        mobile = request.POST.get('mobile')
        specialization = request.POST.get('specialization')
        shift_timing = request.POST.get('shift_timing')

        if name and mobile and specialization and shift_timing:
            trainer.name = name
            trainer.mobile = mobile
            trainer.specialization = specialization
            trainer.shift_timing = shift_timing
            trainer.save()  # Save the updated trainer details to the database
            messages.success(request, 'Trainer updated successfully!')
            return redirect('admin_trainers_list')  # Redirect to the trainers list after successful update
        else:
            messages.error(request, 'Please fill in all the required fields.')

    return render(request, 'admin_trainer_form.html', {'trainer': trainer, 'mode': 'edit'})  # Pass mode to the template to indicate it's an edit operation

@admin_required
def admin_trainer_delete(request, trainer_id):
    trainer = Trainer.objects.get(id=trainer_id)  # Fetch the specific trainer based on the provided ID
    if request.method == 'POST':
        trainer.delete()  # Delete the trainer from the database
        messages.success(request, 'Trainer deleted successfully!')
        return redirect('admin_trainers_list')  # Redirect to the trainers list after successful deletion
    return redirect('admin_trainers_list')  # Render a confirmation page before deletion

@admin_required
def admin_members_list(request):
    search = request.GET.get('search', '')

    members = MemberProfile.objects.all().select_related('user', 'plan') 

    if search:
        members = members.filter(full_name__icontains=search)
    return render(request, 'admin_members_list.html', {'members': members}) 

@admin_required
def admin_member_add(request):
    plans = MembershipPlan.objects.all().order_by('duration_months')  # Fetch all membership plans to display in the form
    trainers = Trainer.objects.all().order_by('name')  # Fetch all trainers to display in the form

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        full_name = request.POST.get('full_name')
        mobile = request.POST.get('mobile')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        address = request.POST.get('address')
        join_date = request.POST.get('join_date') or timezone.now().date()  # Default to today's date if not provided
        plan_id = request.POST.get('plan_id')
        trainer_id = request.POST.get('trainer_id')    

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists. Please choose a different username.')
            return redirect('admin_member_add')

        user = User.objects.create_user(username=username, password=password, role='MEMBER')  # Create a new user with the role of MEMBER
        
        plan = MembershipPlan.objects.get(id=plan_id) if plan_id else None
        trainer = Trainer.objects.get(id=trainer_id) if trainer_id else None

        MemberProfile.objects.create(
            user=user,
            full_name=full_name,
            mobile=mobile,
            age=age,
            gender=gender,
            address=address,    
            join_date=join_date,
            plan=plan,
            trainer=trainer,
            # membership_start=join_date  # Set membership_start to the join_date
        )
        messages.success(request, 'Member added successfully!')
        return redirect('admin_members_list')
    return render(request, 'admin_member_form.html', {'plans': plans, 'trainers': trainers, 'mode': 'add'})  # Pass mode to the template to indicate it's an add operation

@admin_required
def admin_member_edit(request, member_id):
    member = MemberProfile.objects.get(id=member_id)
    plans = MembershipPlan.objects.all().order_by('duration_months')
    trainers = Trainer.objects.all().order_by('name')

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        mobile = request.POST.get('mobile')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        address = request.POST.get('address')
        join_date = request.POST.get('join_date') or member.join_date  # Default to existing join_date if not provided
        plan_id = request.POST.get('plan_id')
        trainer_id = request.POST.get('trainer_id')     

        plan = MembershipPlan.objects.get(id=plan_id) if plan_id else None
        trainer = Trainer.objects.get(id=trainer_id) if trainer_id else None

        if full_name and mobile and age and gender and address and join_date and plan and trainer:
            member.full_name = full_name
            member.mobile = mobile
            member.age = age
            member.gender = gender
            member.address = address
            member.join_date = join_date
            member.plan = plan
            member.trainer = trainer
            member.save()
            messages.success(request, 'Member updated successfully!')
            return redirect('admin_members_list')
        else:
            messages.error(request, 'Please fill in all the required fields.')

    return render(request, 'admin_member_form.html', {'member': member, 'plans': plans, 'trainers': trainers, 'mode': 'edit'})

@admin_required
def admin_member_delete(request, member_id):
    member = MemberProfile.objects.get(id=member_id)
    if request.method == 'POST':
        user = member.user  # Get the associated user
        user.delete()  # Delete the user, which will also delete the associated MemberProfile due
        member.delete()  # Delete the member profile from the database
        messages.success(request, 'Member deleted successfully!')
        return redirect('admin_members_list')
    return render(request, 'admin_member_confirm_delete.html', {'member': member})