from django.shortcuts import redirect, render, get_object_or_404

from GymApp.models import *

from django.contrib import messages
from datetime import timedelta, date
from django.utils import timezone
import json
from django.conf import settings
from django.http import JsonResponse
from openai import OpenAI
import ollama
import base64
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfbase.pdfmetrics import stringWidth
from django.http import HttpResponse
from calendar import monthrange
from functools import wraps
from urllib.parse import quote

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

from django.contrib.auth import authenticate, login, logout

# def admin_login_view(request):
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#         user = authenticate(request, username=username, password=password)
#         if user is not None and getattr(user, 'role', None) == 'ADMIN':  # Check if the user is an admin/staff
#             login(request, user) # log the user in using Django's built-in login function
#             messages.success(request, 'Logged in successfully!.')
#             return redirect('admin_dashboard')  # Redirect to the admin dashboard
#         else:
#             messages.error(request, 'Invalid credentials or not an admin')
#     return render(request, 'admin_login.html')

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

# def member_required(view_func):
#     '''
#     Decorator to ensure that the user is a member.
#     ''' 
#     def wrapper(request, *args, **kwargs):
#         if not request.user.is_authenticated or getattr(request.user, 'role', None) != 'MEMBER':
#             messages.error(request, 'You must be a member to access this page.')
#             return redirect('member_login')
#         return view_func(request, *args, **kwargs)
#     return wrapper
def member_required(view_func):
    """
    Decorator to ensure that the user is an active member
    with a valid membership.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Check login and role
        if (
            not request.user.is_authenticated
            or getattr(request.user, 'role', None) != 'MEMBER'
        ):
            messages.error(request,'You must be a member to access this page.')
            return redirect('login')
        # Get member profile
        try:
            member = request.user.member_profile

        except MemberProfile.DoesNotExist:
            logout(request)
            messages.error(request,'Member profile not found. Please contact the gym owner.')
            return redirect('login')
        # Check manual membership status
        if not member.is_membership_active:
            logout(request)
            messages.error(request,'Your membership is inactive. Please contact the gym owner.'
            )
            return redirect('login')
        # Check membership expiry
        if (
            member.membership_end
            and member.membership_end < timezone.localdate()
        ):
            logout(request)
            messages.error(request,'Your membership plan has ended. Please contact the gym owner.'
            )
            return redirect('login')
        # Everything is valid
        return view_func(request, *args, **kwargs)
    return wrapper

# def member_login_view(request):
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#         user = authenticate(request, username=username, password=password)
#         if user is not None and getattr(user, 'role', None) == 'MEMBER':  # Check if the user is a member
#             login(request, user) # log the user in using Django's built-in login function
#             messages.success(request, 'Logged in successfully!.')
#             return redirect('member_dashboard')  # Redirect to the admin dashboard
#         else:
#             messages.error(request, 'Invalid credentials or not a member')
#     return render(request, 'member_login.html')

# def login_view(request):
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#         # save user to the database

#         user = authenticate(
#             request,
#             username=username,
#             password=password
#         )

#         if user is not None:
#             login(request, user)

#             if getattr(user, 'role', None) == 'ADMIN':
#                 messages.success(request, 'Admin logged in successfully!')
#                 return redirect('admin_dashboard')

#             elif getattr(user, 'role', None) == 'MEMBER':
#                 messages.success(request, 'Member logged in successfully!')
#                 return redirect('member_dashboard')

#             else:
#                 logout(request)
#                 messages.error(request, 'Invalid user role.')
#         else:
#             messages.error(request, 'Invalid username or password.')

#     return render(request, 'login.html')
def login_view(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            # ADMIN
            if getattr(user, 'role', None) == 'ADMIN':

                login(request, user)

                messages.success(request, 'Admin logged in successfully!')

                return redirect('admin_dashboard')


            # MEMBER
            elif getattr(user, 'role', None) == 'MEMBER':

                try:
                    member = user.member_profile

                except MemberProfile.DoesNotExist:

                    messages.error(
                        request,
                        'Member profile not found. Please contact the gym owner.'
                    )

                    return render(request,'login.html')

                # 1. Manual membership status check
                if not member.is_membership_active:

                    messages.error(request,'Your membership is inactive. Please contact the gym owner.')

                    return render(request,'login.html')
                # 2. Membership expiry check
                if (
                    member.membership_end
                    and member.membership_end < timezone.localdate()
                ):

                    messages.error(request, 'Your membership plan has ended. Please contact the gym owner.')
                    return render(request,'login.html')

                # Everything is OK
                login(request, user)

                messages.success(request,'Member logged in successfully!'
                )
                return redirect('member_dashboard')

            # INVALID ROLE
            else:
                messages.error(request,'Invalid user role.')

        else:
            messages.error(request,'Invalid username or password.')

    return render(request, 'login.html')
@member_required
def member_dashboard_view(request):
    member = request.user.member_profile
    total_attendance = member.attendances.count()
    total_payments = member.payments.count()
    return render(request, 'member_dashboard.html', {
        'member':member,
        'total_attendance':total_attendance,
        'total_payments':total_payments,
    })

@member_required
def member_feedback(request):
    member = request.user.member_profile
    if request.method == 'POST':
        message = request.POST.get('message')
        if message:
            Feedback.objects.create(member=member, message=message)
            messages.success(request, "Your Feedback has been submitted successfully!")
            return redirect('member_feedback')
        else:
            messages.error(request, 'Please enter your feedback before submitting.')
    feedbacks = member.feedbacks.all().order_by('-created_at')
    return render(request, 'member_feedback.html', {'feedbacks':feedbacks})

@admin_required
def admin_dashboard_view(request):
    total_members = MemberProfile.objects.all().count()
    active_memberships = MemberProfile.objects.filter(membership_end__gte=timezone.now().date()).count()
    today_registrations = MemberProfile.objects.filter(join_date=timezone.now().date()).count()
    pending_payments = Payment.objects.filter(status='PENDING').count()
    return render(request, 'admin_dashboard.html', {
        'total_members':total_members,
        'active_memberships': active_memberships,
        'today_registrations':today_registrations,
        'pending_payments':pending_payments,
    })

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
    return render(request, 'admin_members_list.html', {'members': members, 'search' : search, 'today': timezone.now().date()}) 

# @admin_required
# def admin_member_add(request):
#     plans = MembershipPlan.objects.all().order_by('duration_months')  # Fetch all membership plans to display in the form
#     trainers = Trainer.objects.all().order_by('name')  # Fetch all trainers to display in the form

#     if request.method == 'POST':
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#         full_name = request.POST.get('full_name')
#         mobile = request.POST.get('mobile')
#         age = request.POST.get('age')
#         gender = request.POST.get('gender')
#         address = request.POST.get('address')
#         join_date = request.POST.get('join_date') or timezone.now().date()  # Default to today's date if not provided
#         plan_id = request.POST.get('plan_id')
#         trainer_id = request.POST.get('trainer_id')    

#         if User.objects.filter(username=username).exists():
#             messages.error(request, 'Username already exists. Please choose a different username.')
#             return redirect('admin_member_add')

#         user = User.objects.create_user(username=username, password=password, role='MEMBER')  # Create a new user with the role of MEMBER
        
#         plan = MembershipPlan.objects.get(id=plan_id) if plan_id else None
#         trainer = Trainer.objects.get(id=trainer_id) if trainer_id else None

#         MemberProfile.objects.create(
#             user=user,
#             full_name=full_name,
#             mobile=mobile,
#             age=age,
#             gender=gender,
#             address=address,    
#             join_date=join_date,
#             plan=plan,
#             trainer=trainer,
#             # membership_start=join_date  # Set membership_start to the join_date
#         )
#         messages.success(request, 'Member added successfully!')
#         return redirect('admin_members_list')
#     return render(request, 'admin_member_form.html', {'plans': plans, 'trainers': trainers, 'mode': 'add'})  # Pass mode to the template to indicate it's an add operation

@admin_required
def admin_member_add(request):
    plans = MembershipPlan.objects.all().order_by('duration_months')
    trainers = Trainer.objects.all().order_by('name')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        full_name = request.POST.get('full_name', '').strip()
        mobile = request.POST.get('mobile', '').strip()
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        address = request.POST.get('address', '').strip()

        join_date = (
            request.POST.get('join_date')
            or timezone.now().date()
        )

        plan_id = request.POST.get('plan_id')
        trainer_id = request.POST.get('trainer_id')

        # Active / Inactive toggle
        membership_active = (
            request.POST.get('membership_active') == 'on'
        )

        # Send WhatsApp button
        send_whatsapp = (
            request.POST.get('send_whatsapp') == '1'
        )

        # Required fields
        if not username or not password or not full_name or not mobile:
            messages.error(request,
                'Username, password, full name and mobile are required.'
            )
            return redirect('admin_member_add')

        # Check username
        if User.objects.filter(username=username).exists():
            messages.error(request,
                'Username already exists. Please choose a different username.'
            )
            return redirect('admin_member_add')

        # Get plan
        plan = (
            MembershipPlan.objects.get(id=plan_id)
            if plan_id
            else None
        )

        # Get trainer
        trainer = (
            Trainer.objects.get(id=trainer_id)
            if trainer_id
            else None
        )

        # Convert join date
        if isinstance(join_date, str):
            join_date = date.fromisoformat(join_date)
        # Create User
        user = User.objects.create_user(
            username=username,
            password=password,
            role='MEMBER'
        )
        membership_start = None
        membership_end = None

        if plan:
            membership_start = join_date

            month = (
                membership_start.month
                - 1
                + plan.duration_months
            )
            year = (
                membership_start.year
                + month // 12
            )
            month = month % 12 + 1
            day = min(
                membership_start.day,
                monthrange(year, month)[1]
            )

            membership_end = date(
                year,
                month,
                day
            )
        member = MemberProfile.objects.create(
            user=user,
            full_name=full_name,
            mobile=mobile,
            age=age,
            gender=gender,
            address=address,
            join_date=join_date,
            plan=plan,
            trainer=trainer,
            is_membership_active=membership_active,
            membership_start=membership_start,
            membership_end=membership_end
        )

        # WhatsApp
        if send_whatsapp and mobile:
            whatsapp_number = ''.join(
                character
                for character in mobile
                if character.isdigit()
            )
            # Nepal number
            if whatsapp_number.startswith('0'):
                whatsapp_number = (
                    '977' + whatsapp_number[1:]
                )
            elif (
                len(whatsapp_number) == 10
                and whatsapp_number.startswith('9')
            ):
                whatsapp_number = (
                    '977' + whatsapp_number
                )
            elif whatsapp_number.startswith('+977'):
                whatsapp_number = (
                    whatsapp_number[1:]
                )
            elif not whatsapp_number.startswith('977'):
                whatsapp_number = (
                    '977' + whatsapp_number
                )
            # Membership information
            membership_start_text = (
                member.membership_start.strftime(
                    '%d %B %Y'
                )
                if member.membership_start
                else 'Not assigned'
            )
            membership_end_text = (
                member.membership_end.strftime(
                    '%d %B %Y'
                )
                if member.membership_end
                else 'Not assigned'
            )
            membership_status = (
                'Active'
                if member.is_membership_active
                else 'Inactive'
            )
            plan_name = (
                member.plan.name
                if member.plan
                else 'No Plan'
            )
            # whatsapp message
            whatsapp_message = f"""Hello {member.full_name} 👋

Welcome to Mero.Gym!

Your gym member account has been created successfully.

Username: {username}
Password: {password}

Membership Plan: {plan_name}
Membership Status: {membership_status}

Please keep your login credentials secure.
You are requested to change your password at least once.

Thank you!
Mero.Gym"""

            encoded_message = quote(
                whatsapp_message.strip()
            )

            # IMPORTANT: Correct WhatsApp URL
            whatsapp_url = (
                f"https://wa.me/{whatsapp_number}"
                f"?text={encoded_message}"
            )

            return redirect(whatsapp_url)
        
        messages.success(request,'Member added successfully!')
        return redirect('admin_members_list')

    return render(request,'admin_member_form.html',
        {
            'plans': plans,
            'trainers': trainers,
            'mode': 'add'
        })

# @admin_required
# def admin_member_edit(request, member_id):
#     member = MemberProfile.objects.get(id=member_id)
#     plans = MembershipPlan.objects.all().order_by('duration_months')
#     trainers = Trainer.objects.all().order_by('name')

#     if request.method == 'POST':
#         full_name = request.POST.get('full_name')
#         mobile = request.POST.get('mobile')
#         age = request.POST.get('age')
#         gender = request.POST.get('gender')
#         address = request.POST.get('address')
#         join_date = request.POST.get('join_date') or member.join_date  # Default to existing join_date if not provided
#         plan_id = request.POST.get('plan_id')
#         trainer_id = request.POST.get('trainer_id') 
#         membership_active = request.POST.get('membership_active') == 'on'    

#         plan = MembershipPlan.objects.get(id=plan_id) if plan_id else None
#         trainer = Trainer.objects.get(id=trainer_id) if trainer_id else None

#         if full_name and mobile and age and gender and address and join_date and plan and trainer:
#             member.full_name = full_name
#             member.mobile = mobile
#             member.age = age
#             member.gender = gender
#             member.address = address
#             member.join_date = join_date
#             member.plan = plan
#             member.trainer = trainer
#             member.is_membership_active = membership_active
#             member.save()
#             messages.success(request, 'Member updated successfully!')
#             return redirect('admin_members_list')
#         else:
#             messages.error(request, 'Please fill in all the required fields.')

#     return render(request, 'admin_member_form.html', {'member': member, 'plans': plans, 'trainers': trainers, 'mode': 'edit'})
@admin_required
def admin_member_edit(request, member_id):
    member = get_object_or_404(
        MemberProfile,
        id=member_id
    )
    plans = MembershipPlan.objects.all().order_by('duration_months')
    trainers = Trainer.objects.all().order_by('name')

    if request.method == 'POST':
        full_name = request.POST.get('full_name','').strip()
        mobile = request.POST.get( 'mobile','').strip()
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        address = request.POST.get('address','').strip()
        join_date = (
            request.POST.get('join_date')
            or member.join_date
        )

        plan_id = request.POST.get('plan_id')
        trainer_id = request.POST.get('trainer_id')

        # Active / inactive toggle
        membership_active = (
            request.POST.get('membership_active')
            == 'on'
        )

        # WhatsApp button
        send_whatsapp = (
            request.POST.get('send_whatsapp')
            == '1'
        )

        # Get plan
        plan = (MembershipPlan.objects.get(id=plan_id)
            if plan_id
            else None
        )

        # Get trainer
        trainer = (Trainer.objects.get(id=trainer_id)
            if trainer_id
            else None
        )
        if not full_name or not mobile or not age or not gender or not join_date:
            messages.error(request,'Please fill in all the required fields.')
            return render(request,'admin_member_form.html',
                {
                    'member': member,
                    'plans': plans,
                    'trainers': trainers,
                    'mode': 'edit'
                })
        # Convert date
        if isinstance(join_date, str):

            join_date = date.fromisoformat(
                join_date
            )

        # Update member
        member.full_name = full_name
        member.mobile = mobile
        member.age = age
        member.gender = gender
        member.address = address
        member.join_date = join_date

        member.plan = plan
        member.trainer = trainer

        # Membership toggle
        member.is_membership_active = (membership_active)

        # Membership dates
        if plan:
            member.membership_start = join_date
            month = (
                join_date.month
                - 1
                + plan.duration_months
            )
            year = (
                join_date.year
                + month // 12
            )
            month = month % 12 + 1
            day = min(
                join_date.day,
                monthrange(year, month)[1]
            )
            member.membership_end = date(
                year,
                month,
                day
            )
        else:
            member.membership_start = None
            member.membership_end = None

        # Automatically deactivate
        # expired membership
        if (
            member.membership_end
            and member.membership_end < timezone.now().date()
        ):

            member.is_membership_active = False
        member.save()

        # Send WhatsApp
        if send_whatsapp and member.mobile:
            whatsapp_number = ''.join(
                character
                for character in member.mobile
                if character.isdigit()
            )

            # Nepal number handling
            if whatsapp_number.startswith('0'):

                whatsapp_number = (
                    '977' + whatsapp_number[1:]
                )
            elif whatsapp_number.startswith('+977'):
                whatsapp_number = (
                    whatsapp_number[1:]
                )
            elif (
                len(whatsapp_number) == 10
                and whatsapp_number.startswith('9')
            ):
                whatsapp_number = (
                    '977' + whatsapp_number
                )
            elif not whatsapp_number.startswith('977'):

                whatsapp_number = (
                    '977' + whatsapp_number
                )
            # Membership information
            membership_start = (
                member.membership_start.strftime(
                    '%d %B %Y'
                )
                if member.membership_start
                else 'Not assigned'
            )
            membership_end = (
                member.membership_end.strftime(
                    '%d %B %Y'
                )
                if member.membership_end
                else 'Not assigned'
            )
            membership_status = (
                'Active'
                if member.is_membership_active
                else 'Inactive'
            )
            plan_name = (
                member.plan.name
                if member.plan
                else 'No Plan'
            )
            # whatsapp message
            message = f"""Hello {member.full_name} 

Your Mero.Gym membership information has been updated.

Username: {member.user.username}

Membership Plan: {plan_name}

Membership Status: {membership_status}

You are requested to change your password at least once. 
If you have any questions, please contact the gym owner.

Thank you!
MeroGym"""

            encoded_message = quote(
                message.strip()
            )

            # IMPORTANT: Correct URL
            whatsapp_url = (
                f"https://wa.me/{whatsapp_number}"
                f"?text={encoded_message}"
            )
            return redirect(whatsapp_url)
        messages.success(request,'Member updated successfully!')

        return redirect('admin_members_list')
    return render(request, 'admin_member_form.html',
        {
            'member': member,
            'plans': plans,
            'trainers': trainers,
            'mode': 'edit'
        })

@admin_required
def admin_member_delete(request, member_id):
    member = MemberProfile.objects.get(id=member_id)
    if request.method == 'POST':
        user = member.user  # Get the associated user
        user.delete()  # Delete the user, which will also delete the associated MemberProfile due
        member.delete()  # Delete the member profile from the database
        messages.success(request, 'Member deleted successfully!')
        return redirect('admin_members_list')
    return redirect('admin_members_list')

@admin_required
def admin_attendance_list(request):
    today = timezone.now().date()

    date = request.GET.get('date', today)

    attendances = Attendance.objects.all().select_related('member').filter(date=date)
    members = MemberProfile.objects.all().order_by('full_name')
    member_id = request.GET.get('member_id')

    if member_id:
        attendances = attendances.filter(member_id=member_id)
    return render(request, 'admin_attendance_list.html', {'attendances' : attendances, 
                                                          'members': members,
                                                          'today' : today,
                                                          'selected_member_id' : member_id,
                                                          'selected_date': date,
                                                          })

@admin_required
def admin_attendance_add(request):
    members = MemberProfile.objects.all().order_by('full_name')

    if request.method == 'POST':
        member_id = request.POST.get('member_id')
        date = request.POST.get('date')
        time_in = request.POST.get('time_in')

        if not member_id:
            messages.error(request, 'Please select a member.')
            return redirect('admin_attendance_add')

        member = MemberProfile.objects.get(id=member_id)

        attendance, created = Attendance.objects.get_or_create(
            member=member, date=date, time_in=time_in
        )

        if not created:
            attendance.time_in = time_in
            attendance.save()
            messages.info(request, "Attendance updated successfully.")
        messages.success(request, 'Attendance recorded succesfully.')
    return render(request, 'admin_attendance_form.html', {'members' : members})

@admin_required
def admin_equipment_list(request):
    search = request.GET.get('search', '')

    equipments = Equipment.objects.all().order_by('name') # order equipment by name

    if search:
        equipments = equipments.filter(name__icontains=search)

    
    total_units = equipments.aggregate(
        total=Sum('units')
    )['total'] or 0

    total_investment = equipments.aggregate(
        total=Sum('price')
    )['total'] or 0

    return render(request, 'admin_equipment_list.html', {
        'equipments' : equipments, 
        'search':search,
        'total_units':total_units,
        'total_investment': total_investment
    })

@admin_required
def admin_equipment_add(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        units = request.POST.get('units')
        price = request.POST.get('price')
        purchase_date = request.POST.get('purchase_date') or timezone.now().date()

        if name and units and price:
            Equipment.objects.create(
                name=name,
                units=units,
                price=price,
                purchase_date=purchase_date
            )
            messages.success(request, 'Equipment added successfully!')
            return redirect('admin_equipment_list')
        else:
            messages.error(request, 'Please fill in all required fields.')
    return render(request, 'admin_equipment_form.html', {'mode':'add'})

@admin_required
def admin_equipment_edit(request, equipment_id):
    equipment = Equipment.objects.get(id=equipment_id)

    if request.method == 'POST':
        name = request.POST.get('name')
        units = request.POST.get('units')
        price = request.POST.get('price')
        purchase_date = request.POST.get('purchase_date') or equipment.purchase_date

        if name and units and price and purchase_date:
            equipment.name = name
            equipment.units =units
            equipment.price = price
            equipment.purchase_date = purchase_date
            equipment.save()  # Save the updated equipment details to the database
            messages.success(request, 'Equipment updated successfully!')
            return redirect('admin_equipment_list')  # Redirect to the euipment list after successful update
        else:
            messages.error(request, 'Please fill in all the required fields.')

    return render(request, 'admin_equipment_form.html', {'equipment': equipment, 'mode': 'edit'})  # Pass mode to the template to indicate it's an edit operation

@admin_required
def admin_equipment_delete(request, equipment_id):
    equipment = Equipment.objects.get(id=equipment_id)  # Fetch the specific equipment based on the provided ID
    if request.method == 'POST':
        equipment.delete()  # Delete the equipment from the database
        messages.success(request, 'Equipment deleted successfully!')
        return redirect('admin_equipment_list')  # Redirect to the equipment list after successful deletion
    return redirect('admin_equipment_list', {'equipment': equipment})  # Render a confirmation page before deletion

@admin_required
def admin_enquiries_list(request):
    enquiries = Enquiry.objects.all().order_by('-created_at')
    return render(request, 'admin_enquiries_list.html', {'enquiries': enquiries})

@admin_required
def admin_enquiry_update_status(request, enquiry_id):
    if request.method == 'POST':
        status = request.POST.get('status')
        enquiry = Enquiry.objects.get(id=enquiry_id)
        if status in ['NEW', 'SEEN', 'RESOLVED']:
            enquiry.status = status 
            enquiry.save()
            messages.success(request, 'Enquiry status updated!')
    return redirect('admin_enquiries_list')

# @admin_required
# def admin_workout_plans_list(request):
#     member_id = request.GET.get('member_id')
#     workout_plans = WorkoutPlan.objects.select_related('member').all().order_by('-created_at')
#     if member_id:
#         workout_plans = workout_plans.filter(member__id=member_id)
#     return render(request, 'admin_workout_plans_list.html', {'workout_plans': workout_plans, })
@admin_required
def admin_payments_list(request):

    member_id = request.GET.get('member_id')
    status = request.GET.get('status')

    # Get all payments
    payments = (
        Payment.objects
        .select_related('member', 'plan')
        .all()
        .order_by('-payment_date')
    )

    # Filter by member
    if member_id:
        payments = payments.filter(member__id=member_id)

    # Filter by payment status
    if status in ['PENDING', 'PAID']:
        payments = payments.filter(status=status)

    # Get all members for dropdown
    members = MemberProfile.objects.all().order_by('full_name')

    # Today's date
    today = timezone.now().date()

    # Calculate information for each payment
    for payment in payments:

        # REMAINING PAYMENT AMOUNT
        if payment.plan and payment.plan.fee:

            total_paid = (
                Payment.objects
                .filter(
                    member=payment.member,
                    plan=payment.plan,
                    status='PAID'
                )
                .aggregate(total=Sum('amount'))['total'] or 0
            )

            remaining = float(payment.plan.fee) - float(total_paid)

            # Prevent negative remaining amount
            if remaining < 0:
                remaining = 0

            # Temporary value for template
            payment.remaining = remaining

        else:
            payment.remaining = None

        # MEMBERSHIP END DATE
    
        payment.membership_end = payment.member.membership_end

        # MEMBERSHIP REMAINING DAYS
        if payment.member.membership_end:

            days_remaining = (
                payment.member.membership_end - today
            ).days

            if days_remaining < 0:

                payment.membership_days_remaining = 0
                payment.membership_expired = True

            else:

                payment.membership_days_remaining = days_remaining
                payment.membership_expired = False

        else:

            payment.membership_days_remaining = None
            payment.membership_expired = False


    return render(
        request,
        'admin_payments_list.html',
        {
            'payments': payments,
            'members': members,

            'selected_status': status,

            'selected_member': (
                int(member_id)
                if member_id
                else None
            ),
        }
    )
 
@admin_required
def admin_payment_add(request):
    members = MemberProfile.objects.all().order_by('full_name')
    plans = MembershipPlan.objects.all().order_by('duration_months')
    if request.method == 'POST':
        member_id = request.POST.get('member_id')
        plan_id = request.POST.get('plan_id')
        amount = request.POST.get('amount')
        payment_date = request.POST.get('payment_date') or timezone.now().date()
        mode = request.POST.get('mode')
        status = request.POST.get('status')
        notes = request.POST.get('notes')

        set_membership = request.POST.get('set_membership') 
        membership_start = request.POST.get('membership_start')

        if not member_id or not plan_id or not amount or not payment_date or not mode or not status:
            messages.error(request, 'Please fill in all required fields.')
            return redirect('admin_payment_add')

        member = MemberProfile.objects.get(id=member_id)
        plan = MembershipPlan.objects.get(id=plan_id)

        # overpayment check
        if plan and plan.fee:
            total_paid = Payment.objects.filter(
                member=member, plan=plan, status='PAID'
            ).aggregate(total=models.Sum('amount'))['total'] or 0
            if float(total_paid) + float(amount) > plan.fee:
                remaining_amount = plan.fee - total_paid
                messages.error(request, f'Total paid amount exceeds the plan fee of {plan.fee}. Remaining amount: {remaining_amount}. Please check the amount.')
                return redirect('admin_payment_add')

        Payment.objects.create(
            member=member,
            plan=plan,
            amount=amount,
            status=status,
            payment_date=payment_date,
            mode=mode,
            notes=notes,
        )
        if set_membership == 'on' and plan and membership_start:
            try:
                membership_start = timezone.datetime.strptime(membership_start, '%Y-%m-%d').date()
            except ValueError:
                messages.error(request, 'Invalid membersip start date format. Please use YYYY-MM-DD')
                return redirect('admin_payment_add')
            member.plan = plan
            member.membership_start = membership_start
            member.membership_end = member.membership_start + timedelta(days=plan.duration_months*30)
            member.save()

        messages.success(request, 'Payment recorded successfully!')
        return redirect('admin_payments_list')
    return render(request, 'admin_payment_form.html', {'members': members, 'plans':plans})

@member_required
def member_attendance(request):
    member_profile = MemberProfile.objects.get(user=request.user)
    attendances = Attendance.objects.filter(member=member_profile).order_by('-date')
    return render(request, 'member_attendance.html', {'attendances':attendances})


@member_required
def ai_workout_plan(request):
    return render(request, "ai_workout.html")

# @member_required
# def generate_workout_plan(request):

#     if request.method != "POST":
#         return JsonResponse({
#             "success": False,
#             "error": "Only POST requests are allowed."
#         }, status=405)

#     try:

#         # Get data from frontend
#         data = json.loads(request.body)

#         goal = data.get("goal")
#         experience = data.get("experience")
#         days = data.get("days")
#         duration = data.get("duration")
#         equipment = data.get("equipment")

#         # Validate input
#         if not goal:
#             return JsonResponse({
#                 "success": False,
#                 "error": "Please select your workout goal."
#             }, status=400)

#         if not experience:
#             return JsonResponse({
#                 "success": False,
#                 "error": "Please select your experience level."
#             }, status=400)

#         if not days:
#             return JsonResponse({
#                 "success": False,
#                 "error": "Please select workout days."
#             }, status=400)

#         if not duration:
#             return JsonResponse({
#                 "success": False,
#                 "error": "Please select workout duration."
#             }, status=400)

#     #  prompt
#         prompt = f"""
# Create a simple and easy-to-follow workout plan.

# User information:
# - Goal: {goal}
# - Experience: {experience}
# - Workout days per week: {days}
# - Workout duration: {duration} minutes
# - Equipment: {equipment}

# You MUST create exactly {days} workout days.
# Do not stop early.
# Do not create fewer than {days} days.

# For each day provide:
# - Muscle groups
# - Maximum 4 exercises
# - Each exercise: name, sets, reps, rest

# Also include:
# - Warm-up: one short sentence
# - Cool-down: one short sentence

# IMPORTANT:
# - Keep it short and easy to read.
# - No long explanations or fitness theory.
# - No overview.
# - No Markdown headings, bold text, or "---".
# - Use plain text.
# - Do not provide medical diagnosis or treatment.

# Example:

# DAY 1 - FULL BODY

# Muscle Groups:
# Chest, Back, Legs

# 1. Dumbbell Squat
# Sets: 3
# Reps: 10
# Rest: 60 sec

# 2. Dumbbell Bench Press
# Sets: 3
# Reps: 10
# Rest: 60 sec

# WARM-UP:
# 5 minutes light cardio and dynamic stretching.

# COOL-DOWN:
# 5 minutes light stretching.

# Repeat the same format for all workout days.
# """
#         if not settings.OPENROUTER_API_KEY:
#             return JsonResponse({
#                 "success": False,
#                 "error": "AI service is not configured."
#             }, status=500)

#         client = OpenAI(
#             base_url="https://openrouter.ai/api/v1",
#             api_key=settings.OPENROUTER_API_KEY,
#         )
#         response = client.chat.completions.create(
#             model="openai/gpt-5.1",
#             # model="openrouter/free",
#             # model="google/gemma-4-31b-it:free",
#             messages=[
#                 {
#                     "role": "system",
#                     "content": (
#                         "You are a concise fitness workout "
#                         "planning assistant."
#                     )
#                 },
#                 {
#                     "role": "user",
#                     "content": prompt
#                 }
#             ],

#             temperature=0.2,
#             max_tokens=255,
#         )
#         workout_text = response.choices[0].message.content

#         if not workout_text:
#             return JsonResponse({
#                 "success": False,
#                 "error": "The AI returned an empty workout plan."
#             }, status=500)
        
#         member = get_object_or_404(
#             MemberProfile,
#             user=request.user
#         )

#         workout_plan = WorkoutPlan.objects.create(
#             member=member,
#             title=f"{goal} Workout Plan",
#             description=workout_text
#         )

#         return JsonResponse({
#             "success": True,
#             "workout": workout_text,
#             "plan_id": workout_plan.id
#         })
    
#     except Exception as e:
#         print("====================================")
#         print("AI ERROR:", repr(e))
#         print("====================================")

#         error_message = str(e).lower()

#         # OpenRouter credit/token error
#         if (
#             "more credits" in error_message
#             or "insufficient" in error_message
#             or "max_tokens" in error_message
#             or "can only afford" in error_message
#         ):

#             return JsonResponse({
#                 "success": False,
#                 "error": (
#                     "The AI service currently has insufficient "
#                     "credits. Please try again later."
#                 )
#             }, status=402)

#         # API key error
#         if (
#             "api key" in error_message
#             or "authentication" in error_message
#             or "unauthorized" in error_message
#         ):

#             return JsonResponse({
#                 "success": False,
#                 "error": "The AI service authentication failed."
#             }, status=401)

#         # Rate limit
#         if (
#             "rate limit" in error_message
#             or "too many requests" in error_message
#         ):

#             return JsonResponse({
#                 "success": False,
#                 "error": (
#                     "Too many requests. Please wait a moment "
#                     "and try again."
#                 )
#             }, status=429)
#         # Other errors
#         return JsonResponse({
#             "success": False,
#             "error": (
#                 "Unable to generate the workout plan right now. "
#                 "Please try again."
#             )
#         }, status=500)

@member_required
def generate_workout_plan(request):
    if request.method != "POST":
        return JsonResponse({
            "success": False,
            "error": "Only POST requests are allowed."
        }, status=405)

    try:
        # Get data from frontend
        data = json.loads(request.body)
        goal = data.get("goal")
        experience = data.get("experience")
        days = data.get("days")
        duration = data.get("duration")
        equipment = data.get("equipment")

        # Validate input
        if not goal:
            return JsonResponse({
                "success": False,
                "error": "Please select your workout goal."
            }, status=400)
        if not experience:
            return JsonResponse({
                "success": False,
                "error": "Please select your experience level."
            }, status=400)
        if not days:
            return JsonResponse({
                "success": False,
                "error": "Please select workout days."
            }, status=400)
        if not duration:
            return JsonResponse({
                "success": False,
                "error": "Please select workout duration."
            }, status=400)

        # Convert days to integer
        days = int(days)

        # Workout prompt
        prompt = f"""
Create a simple and easy-to-follow workout plan.

User information:
- Goal: {goal}
- Experience: {experience}
- Workout days per week: {days}
- Workout duration: {duration} minutes
- Equipment: {equipment}

You MUST create exactly {days} workout days.

Do not stop early.
Do not create fewer than {days} days.

For each day provide:
- Muscle groups
- Maximum 4 exercises
- Each exercise: name, sets, reps, rest

Also include:
- Warm-up: one short sentence
- Cool-down: one short sentence

IMPORTANT:
- Keep it short and easy to read.
- No long explanations or fitness theory.
- No overview.
- No Markdown headings, bold text, or "---".
- Use plain text.
- Do not provide medical diagnosis or treatment.

Example:

DAY 1 - FULL BODY

Muscle Groups:

Chest, Back, Legs

1. Dumbbell Squat

Sets: 3
Reps: 10
Rest: 60 sec

2. Dumbbell Bench Press

Sets: 3
Reps: 10
Rest: 60 sec

WARM-UP:

5 minutes light cardio and dynamic stretching.

COOL-DOWN:

5 minutes light stretching.

Repeat the same format for all workout days.
"""
        response = ollama.chat(
            model="llama3.2",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a concise fitness workout "
                        "planning assistant."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            options={
                "temperature": 0.2
            }
        )
        workout_text = response["message"]["content"]

        # Check AI response
        if not workout_text:
            return JsonResponse({
                "success": False,
                "error": "The AI returned an empty workout plan."
            }, status=500)
        # Get logged-in member
        member = get_object_or_404(
            MemberProfile,
            user=request.user
        )
        # Save workout plan
        workout_plan = WorkoutPlan.objects.create(
            member=member,
            title=f"{goal} Workout Plan",
            description=workout_text
        )

        # Return response to frontend
        return JsonResponse({
            "success": True,
            "workout": workout_text,
            "plan_id": workout_plan.id
        })

    except Exception as e:
        print("OLLAMA ERROR:", repr(e))

        return JsonResponse({
            "success": False,
            "error": (
                "Unable to generate the workout plan right now. "
                "Please make sure Ollama is running."
            )
        }, status=500)

@member_required
def my_workout_plans(request):

    member = get_object_or_404(
        MemberProfile,
        user=request.user
    )

    workout_plans = WorkoutPlan.objects.filter(
        member=member
    ).order_by('-created_at')

    return render(
        request,
        'my_workout_plans.html',
        {
            'workout_plans': workout_plans
        }
    )


@member_required
def workout_plan_detail(request, plan_id):

    member = get_object_or_404(
        MemberProfile,
        user=request.user
    )

    workout_plan = get_object_or_404(
        WorkoutPlan,
        id=plan_id,
        member=member
    )

    return render(
        request,
        'workout_plan_detail.html',
        {
            'workout_plan': workout_plan
        }
    )
@member_required
def download_workout_plan_pdf(request, plan_id):
    member = get_object_or_404(
        MemberProfile,
        user=request.user
    )
    workout_plan = get_object_or_404(
        WorkoutPlan,
        id=plan_id,
        member=member
    )
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (f'attachment; filename="{workout_plan.title}.pdf"')

    pdf = canvas.Canvas(response, pagesize=A4)

    width, height = A4
    # Title
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(
        50,
        height - 60,
        workout_plan.title
    )
    # Created date
    pdf.setFont("Helvetica", 10)
    pdf.drawString(
        50,
        height - 85,
        f"Created on: {workout_plan.created_at.strftime('%B %d, %Y')}"
    )
    # Line
    pdf.line(
        50,
        height - 100,
        width - 50,
        height - 100
    )

    # Description
    pdf.setFont("Helvetica", 11)
    text = pdf.beginText(
        50,
        height - 130
    )
    text.setLeading(16)
    # Split description into lines
    for paragraph in workout_plan.description.split('\n'):
        words = paragraph.split()
        line = ""

        for word in words:
            test_line = line + " " + word
            if stringWidth(
                test_line,
                "Helvetica",
                11
            ) < width - 100:

                line = test_line.strip()
            else:

                text.textLine(line)
                line = word

        if line:
            text.textLine(line)

        text.textLine("")

        # New page if necessary
        if text.getY() < 50:

            pdf.drawText(text)
            pdf.showPage()

            pdf.setFont("Helvetica", 11)

            text = pdf.beginText(
                50,
                height - 50
            )

            text.setLeading(16)
    pdf.drawText(text)
    pdf.save()
    return response

@member_required
def delete_workout_plan(request, plan_id):

    member = get_object_or_404(
        MemberProfile,
        user=request.user
    )

    workout_plan = get_object_or_404(
        WorkoutPlan,
        id=plan_id,
        member=member
    )

    if request.method == 'POST':
        workout_plan.delete()
        messages.success(request,'Workout plan deleted successfully.')
        return redirect('my_workout_plans')
    return render(request, 'delete_workout_plan.html',{'workout_plan': workout_plan})

from django.db.models import Sum
@member_required
def member_membership(request):
    member = request.user.member_profile

    days_remaining = None
    total_paid = 0
    remaining = None

    membership_status = "No Active Membership"

    if member.membership_end:
        days_remaining = (
            member.membership_end - timezone.now().date()
        ).days

        if days_remaining < 0:
            days_remaining = 0
            membership_status = "Membership Ended"
        else:
            membership_status = 'Active'

    if member.plan:
        agg = Payment.objects.filter(
            member=member,
            plan = member.plan,
            status = 'PAID',
        ).aggregate(total=Sum('amount'))

        total_paid = agg['total'] or 0

        if member.plan.fee:
            remaining = float(member.plan.fee) - float(total_paid)

    context = {
        'member': member,
        'membership_status': membership_status,
        'days_remaining': days_remaining,
        'total_paid' : total_paid,
        'remaining': remaining,
    }
    return render(request, 'member_membership.html', context)

@member_required
def member_payments(request):
    member_profile = MemberProfile.objects.get(user=request.user)
    payments = Payment.objects.filter(member=member_profile).select_related('plan')
    return render(request, 'member_payments.html', {'payments':payments})

@member_required
def member_profile (request):
    member = request.user.member_profile
    return render(request, 'member_profile.html', {'member':member})

@member_required
def member_profile_edit(request):
    member = request.user.member_profile
    if request.method == 'POST':
        member.full_name = request.POST.get('full_name')
        member.mobile = request.POST.get('mobile')
        member.age = request.POST.get('age')
        member.gender = request.POST.get('gender')
        member.address = request.POST.get('address')
        member.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('member_profile')
    return render(request, 'member_profile_edit.html', {'member':member})

@member_required
def member_change_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if not request.user.check_password(current_password):
            messages.error(request, 'Current password is incorrect.')
            return redirect('member_change_password')

        if new_password != confirm_password:
            messages.error(request, 'New password and confirm password do not match.')
            return redirect('member_change_password')

        request.user.set_password(new_password)
        request.user.save()
        messages.success(request, 'Password changed successfully! Please log in again.')
        return redirect('login')
    return render(request, 'member_change_password.html')

@admin_required
def admin_feedbacks_list(request):
    member_id = request.GET.get('member')
    feedbacks = Feedback.objects.select_related('member').all().order_by('-created_at')
    members = MemberProfile.objects.all().order_by('full_name')
    if member_id:
        feedbacks = feedbacks.filter(member_id=member_id)

    context = {
        'feedbacks':feedbacks,
        'members':members,
        'selected_members': int(member_id) if member_id else None,
    }
    return render(request, 'admin_feedbacks_list.html', context)

@admin_required
def admin_feedback_delete(request, feedback_id):
    feedback = Feedback.objects.get(id=feedback_id)  # Fetch the specific feedback plan based on the provided ID
    if request.method == 'POST':
        feedback.delete()  # Delete the feedback from the database
        messages.success(request, 'Feedback deleted successfully!')
        return redirect('admin_feedbacks_list')  # Redirect to the feedback list after successful deletion
    return redirect('admin_feedbacks_list')  # Render a confirmation page before deletion

@member_required
def food_analyzer(request):

    if request.method != "POST":
        return render(request, "food_analyzer.html")

    # Get uploaded image
    image = request.FILES.get("food_image")

    if not image:
        return render(request, "food_analyzer.html", {
            "error": "Please upload a food image."
        })

    # Optional: check file type
    allowed_types = [
        "image/jpeg",
        "image/png",
        "image/webp"
    ]

    if image.content_type not in allowed_types:
        return render(request, "food_analyzer.html", {
            "error": "Please upload a JPG, PNG or WEBP image."
        })

    try:
        # Convert image to Base64
        image_data = base64.b64encode(
            image.read()
        ).decode("utf-8")

        client = OpenAI(
            api_key=settings.OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1"
        )

        prompt = """
Analyze the food in this image.

Give an ESTIMATED nutritional analysis.

Identify:

1. Food name
2. Estimated calories
3. Protein in grams
4. Carbohydrates in grams
5. Fat in grams

Return ONLY valid JSON.

Use exactly this format:

{
    "food_name": "food name",
    "calories": 0,
    "protein": 0,
    "carbohydrates": 0,
    "fat": 0
}

Do not include markdown.
Do not include explanations.
"""

        # Call AI
        response = client.chat.completions.create(
            model="google/gemini-2.5-flash",  # google gemini model is used here.
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": (
                                    f"data:{image.content_type};"
                                    f"base64,{image_data}"
                                )
                            }
                        }
                    ]
                }
            ],

            temperature=0.2,
            max_tokens=500
        )
        # Get AI response
        result = response.choices[0].message.content
        if not result:
            return render(request, "food_analyzer.html", {
                "error": "The AI did not return any result. Please try again."
            })
        # Remove markdown if AI accidentally adds it
        result = result.replace("```json", "")
        result = result.replace("```", "")
        result = result.strip()

        # Convert AI response to Python dictionary
        try:
            nutrition = json.loads(result)

        except json.JSONDecodeError:
            print("INVALID AI RESPONSE:")
            print(result)

            return render(request, "food_analyzer.html", {
                "error": "The AI returned an invalid result. Please try again."
            })

        # Make sure required fields exist
        required_fields = [
            "food_name",
            "calories",
            "protein",
            "carbohydrates",
            "fat"
        ]

        for field in required_fields:
            if field not in nutrition:
                return render(request, "food_analyzer.html", {
                    "error": "The AI returned incomplete nutrition information. Please try again."
                })

        # Everything successful
        return render(request,"food_result.html", {"nutrition": nutrition})

    except Exception as e:
        # Print actual error in terminal
        print("FOOD AI ERROR:")
        print(repr(e))
        error_message = str(e).lower()

        # OpenRouter credit/token error
        if (
            "more credits" in error_message
            or "insufficient" in error_message
            or "max_tokens" in error_message
            or "402" in error_message
        ):
            return render(request, "food_analyzer.html", {
                "error": (
                    "The AI service does not have enough credits "
                    "for this request. Please try again later."
                )
            })
        # API / connection error
        if (
            "connection" in error_message
            or "timeout" in error_message
            or "rate limit" in error_message
        ):
            return render(request, "food_analyzer.html", {
                "error": (
                    "The AI service is temporarily unavailable. "
                    "Please try again."
                )
            })
        # General error
        return render(request, "food_analyzer.html", {
            "error": (
                "Unable to analyze the food image. "
                "Please try again."
            )
        })