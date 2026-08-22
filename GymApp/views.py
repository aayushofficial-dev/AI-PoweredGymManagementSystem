from django.shortcuts import redirect, render, get_object_or_404

from GymApp.models import *

from django.contrib import messages
from datetime import timedelta
import json
from django.conf import settings
from django.http import JsonResponse
from openai import OpenAI
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

def member_required(view_func):
    '''
    Decorator to ensure that the user is a member.
    ''' 
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or getattr(request.user, 'role', None) != 'MEMBER':
            messages.error(request, 'You must be a member to access this page.')
            return redirect('member_login')
        return view_func(request, *args, **kwargs)
    return wrapper

def member_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and getattr(user, 'role', None) == 'MEMBER':  # Check if the user is a member
            login(request, user) # log the user in using Django's built-in login function
            messages.success(request, 'Logged in successfully!.')
            return redirect('member_dashboard')  # Redirect to the admin dashboard
        else:
            messages.error(request, 'Invalid credentials or not a member')
    return render(request, 'member_login.html')

@member_required
def member_dashboard_view(request):
    return render(request, 'member_dashboard.html')
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
    return render(request, 'admin_members_list.html', {'members': members, 'search' : search}) 

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
    return render(request, 'admin_equipment_list.html', {'equipments' : equipments, 'search':search})

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
    payments = Payment.objects.select_related('member', 'plan').all().order_by('-payment_date')
    if member_id:
        payments = payments.filter(member__id=member_id)
    if status in ['PENDING', 'PAID']:
        payments = payments.filter(status=status)

    members = MemberProfile.objects.all().order_by('full_name')
    return render(request, 'admin_payments_list.html', {'payments':payments, 
                                                        'members':members, 
                                                        'selected_member_id': member_id, 
                                                        'selected_status': status
                                                        })

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

@member_required
def generate_workout_plan(request):

    if request.method != "POST":
        return JsonResponse({
            "error": "Only POST requests are allowed."
        }, status=405)

    try:
        print("API KEY EXISTS:", bool(settings.OPENROUTER_API_KEY))
        data = json.loads(request.body)

        goal = data.get("goal")
        experience = data.get("experience")
        days = data.get("days")
        duration = data.get("duration")
        equipment = data.get("equipment")

        if not goal:
            return JsonResponse({
                "error": "Please select your workout goal."
            }, status=400)

        if not experience:
            return JsonResponse({
                "error": "Please select your experience level."
            }, status=400)

        if not days:
            return JsonResponse({
                "error": "Please select workout days."
            }, status=400)

        if not duration:
            return JsonResponse({
                "error": "Please select workout duration."
            }, status=400)

        prompt = f"""
Create a simple and easy-to-follow workout plan.

User information:
- Goal: {goal}
- Experience: {experience}
- Workout days per week: {days}
- Workout duration: {duration} minutes
- Equipment: {equipment}

Create exactly a {days}-day workout plan.

For each day provide:

Day name
Muscle groups
4 to 6 exercises only

For every exercise show:
- Exercise name
- Sets
- Reps
- Rest

Also include a short warm-up and cool-down.

IMPORTANT:
- Keep the answer short and simple.
- Do not write long explanations.
- Do not include an overview section.
- Do not include unnecessary fitness theory.
- Do not use "---".
- Do not use Markdown headings such as ## or ###.
- Do not use bold text.
- Use simple plain text.
- Make the plan easy for a gym member to read.

Example format:

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

3. Dumbbell Row
   Sets: 3
   Reps: 10
   Rest: 60 sec

WARM-UP:
5 minutes light cardio and dynamic stretching.

COOL-DOWN:
5 minutes light stretching.

Repeat the same simple format for all workout days.

Do not provide medical diagnosis or treatment.
"""

        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=settings.OPENROUTER_API_KEY,
        )

        response = client.chat.completions.create(
            model="openai/gpt-5.1",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful fitness workout planning assistant."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=2000,
        )

        workout_text = response.choices[0].message.content
        member = MemberProfile.objects.get(user=request.user)

        WorkoutPlan.objects.create(
            member=member,
            title=f"{goal} Workout Plan",
            description=workout_text
        )
        return JsonResponse({
            "success": True,
            "workout": workout_text
        })

    except Exception as e:
        print("====================================")
        print("AI ERROR:", repr(e))
        print("====================================")

        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)

@member_required
def my_workout_plans(request):
    member = MemberProfile.objects.get(user=request.user)
    workout_plans = WorkoutPlan.objects.filter(
        member=member
    ).order_by('-created_at')

    return render(request, 'my_workout_plans.html', {'workout_plans':workout_plans})

@member_required
def workout_plan_detail(request, plan_id):

    member = MemberProfile.objects.get(user=request.user)

    workout_plan = get_object_or_404(
        WorkoutPlan,
        id=plan_id,
        member=member
    )

    return render(
        request,
        "workout_plan_detail.html",
        {
            "workout_plan": workout_plan
        }
    )