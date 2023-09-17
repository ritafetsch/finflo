from django.contrib.auth import authenticate, login,logout, update_session_auth_hash
from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from .forms import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseForbidden, JsonResponse, HttpResponse, HttpResponse, HttpResponseRedirect
from django.utils import timezone
from datetime import datetime
import calendar
from django.views.decorators.http import require_POST
from django.core import serializers
from decimal import Decimal
import json
from .api import *
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.db.models.functions import ExtractMonth
from django.db.models import Sum, Case, When, Value, FloatField, F, Max
from django.db import IntegrityError
from django.core import serializers


# View code to use as decorator for ensuring user is authenticated via whether or not they have the token of the group account they are trying to access
def user_has_group_token(view_func):
    def _wrapped_view(request, *args, **kwargs):
        group_id = kwargs.get('group_id')
        group = get_object_or_404(Group, id=group_id)
        desired_group_token = group.token
        # If they don't have the token, return forbidden page
        if not Group.objects.filter(members=request.user, token=desired_group_token).exists():
            return HttpResponseForbidden("You do not have permission to access this page")
        return view_func(request, *args, **kwargs)
    return _wrapped_view


# Reports page 
@login_required
@user_has_group_token
def reports_view(request, group_id):
    group = Group.objects.get(id=group_id)

    # Get dummy data for charts - functions are defined in api.py
    monthly_expense_data = get_monthly_expense_data()
    category_expense_data = get_category_expense_data()
    balance_over_time_data = get_balance_over_time()

    expense_distribution_data = get_expense_distribution_data()
    income_distribution_data = get_income_distribution_data()
    expense_distribution_by_day_data = get_expense_distribution_by_day_data()

    category_monthly_comparison_data = get_category_monthly_comparison_data()
    total_income_expense_data = get_total_income_expense_balance_over_time() 
    highest_spending_category_for_year = get_highest_spending_category_for_year()
   
    
    # Convert data to JSON format
    monthly_expense_data_json = json.dumps(monthly_expense_data)
    category_expense_data_json = json.dumps(category_expense_data)
    balance_over_time_data_json = json.dumps(balance_over_time_data)
    
    expense_distribution_data_json = json.dumps(expense_distribution_data)
    income_distribution_data_json = json.dumps(income_distribution_data)
    expense_distribution_by_day_data_json = json.dumps(expense_distribution_by_day_data)
    
    category_monthly_comparison_data_json = json.dumps(category_monthly_comparison_data)
    total_income_expense_data_json = json.dumps(total_income_expense_data)
    highest_spending_category_for_year__json = json.dumps(highest_spending_category_for_year)
    

    # Context data 
    context = {
        'monthly_expense_data': monthly_expense_data_json,
        'category_expense_data': category_expense_data_json,
        'balance_over_time_data': balance_over_time_data_json,

        'expense_distribution_data': expense_distribution_data_json,
        'income_distribution_data': income_distribution_data_json,
        'expense_distribution_by_day_data': expense_distribution_by_day_data_json,
        
        'highest_spending_category_for_year': highest_spending_category_for_year__json,  
        'total_income_expense_data': total_income_expense_data_json,
        'category_monthly_comparison_data': category_monthly_comparison_data_json,

        'group_id': group_id,
        'group': group
    }
    return render(request, 'reports.html',context)


# Transactions page
@login_required
@user_has_group_token
def transactions_view(request, group_id):
    group = Group.objects.get(id=group_id)
    categories = list(group.categories.all().values())
    currencies = Currency.objects.all()  

    # Calculate total monthly and daily expenses
    today = timezone.localdate()
    first_day_of_month = today.replace(day=1)

    # Get total summed expenses for the month
    total_expense_month = Transaction.objects.filter(
        group=group,
        type='expense',
        date__gte=first_day_of_month,
        date__lte=today
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Get total summed expenses for today
    total_expense_today = Transaction.objects.filter(
        group=group,
        type='expense',
        date__date=today  
    ).aggregate(total=Sum('amount'))['total'] or 0

    # Get transactions ordered by date
    transactions = Transaction.objects.filter(group=group).order_by('-date')
    
    # Context data
    context = {
        'group_id': group_id,
        'group': group,
        'total_expense_month': total_expense_month,
        'total_expense_today': total_expense_today,
        'transactions': transactions,
        'group_id': group_id,
        'currencies': currencies,
        'categories': categories
    }
    return render(request, 'transactions.html', context)

# Registration page 
def registration(request):
    return render(request, 'registration.html')

# Function to handle user registration
def register_user(request):
    # If the request is a post 
    if request.method == 'POST':
        # Get custom registration form from backend
        form = CustomRegistrationForm(request.POST)
        if form.is_valid():
            try:
                # Set new user with form details
                user = form.save()
                # Log user in
                authenticated_user = authenticate(request, username=user.username, password=request.POST['password1'])
                if authenticated_user is not None:
                    login(request, authenticated_user)
                    messages.success(request, 'Registration successful. You are now logged in.')
                    
        # RETURN ERROR MESSAGES ACCORDING TO WHETHER OR NOT SUCCESS OR SPECIFIC ERRORS
                    return JsonResponse({'success': True, 'message': 'Registration successful'})
                else:
                    # Authentication failed
                    return JsonResponse({'success': False, 'message': 'Authentication failed.'})
            except IntegrityError as e:
                if 'unique constraint' in str(e).lower():
                    # Evaluate which field caused unique constraint error
                    if 'username' in str(e).lower():
                        return JsonResponse({'success': False, 'message': 'The provided username is already in use. Please choose a different one.'})
                    elif 'email' in str(e).lower():
                        return JsonResponse({'success': False, 'message': 'The provided email is already in use. Please use a different one.'})
                    else:
                        # Integrity error
                        return JsonResponse({'success': False, 'message': str(e)})
                else:
                    # Other integrity error
                    return JsonResponse({'success': False, 'message': 'An error occurred during registration. Please try again.'})
        else:
            # Else if form is not valid, return validation errors
            field_errors = {field: errors[0] for field, errors in form.errors.items()}
            return JsonResponse({'success': False, 'message': 'Registration failed. Please check the form and try again.', 'field_errors': field_errors})
    else:
        # Else if not post request, render form
        form = CustomRegistrationForm()
        return render(request, 'registration.html', {'form': form})


# Login page and login handling 
def login_view(request):
    if request.method == 'POST':
        # Get authentication form 
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            # Get username and password from form
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            # Use it to try to authenticate user
            user = authenticate(request, username=username, password=password)
            # If user is authenticated
            if user is not None:
                # Log them in
                login(request, user)
                # Get users default group
                default_group = user.userprofile.default_group
                user_groups = Group.objects.filter(members=user)
                # Redirect to group dashboard of default group
                if default_group:
                    group_dashboard_url = reverse('group_dashboard', args=[default_group.id])
                    return redirect(group_dashboard_url)
                # IF user is a member of groups but has none of them set as default
                elif user_groups:
                    # Redirect them to choose group page
                    return redirect('choose_group')
                else:
                    # Else if user doesn't have any groups at all, redirect them to the landing page 
                    return redirect('landing_page')
        else:
            # Else if form isn't valid, display form errors
            messages.error(request, 'Invalid username or password. Please try again.')  
    else:
        # Else if not post request, render form
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

# Choose group page 
@login_required
def choose_group(request):
    user = request.user
    user_groups = Group.objects.filter(members=user)
    return render(request, 'choose_group.html', {'groups': user_groups})

# Select default group functionality 
@login_required
def select_default_group(request, group_id):
    user = request.user
    # Get default group 
    selected_group = Group.objects.get(id=group_id)
    user.userprofile.default_group = selected_group
    user.userprofile.save() 
    return redirect('group_dashboard', group_id=group_id)

# Landing page
@login_required
def landing_page(request):
    return render(request, 'landing.html')

# Create new group functionality 
def create_group(request):
    if request.method == 'POST':
        # Handle group creation from form data
        name = request.POST.get('name')
        group = Group.objects.create(name=name)
        # Add user as member of group
        group.members.add(request.user)
        # Add user as admin
        group.admins.add(request.user)
        # Set newly created group as user's default group
        user_profile = UserProfile.objects.get(user=request.user)
        if not user_profile.default_group:
            user_profile.default_group = group
            user_profile.save()
        user_profile.save()
        # Call function to initialize group with default categories
        group.initialize_default_categories()
        # If there are additional admins from form, add them
        selected_admins = request.POST.getlist('admins')
        group.admins.add(*selected_admins)
        # Succesful group creation response data 
        response_data = {
            'status': 'success',
            'message': f'You have successfully created the group "{group.name}". Your unique token for this group account is: {group.token}. Users wanting to gain access to this account will require provision of this token. The token will be stored and accessible in your settings page.',
            'redirect_url': reverse('group_dashboard', kwargs={'group_id': group.id}),
        }
        return JsonResponse(response_data)
    return render(request, 'create_group.html')

# Join group page
def join_group(request):
    return render(request, 'join_group.html')

# Join group functionality
@login_required
def join_group_ajax(request):
    response_data = {}

    if request.method == 'POST':
        # Get token from form
        token = request.POST.get('token')
        try:
            # Add user to group
            group = Group.objects.get(token=token)
            group.members.add(request.user)
            # Add group in user's groups
            user_profile = UserProfile.objects.get(user=request.user)
            user_profile.groups.add(group)
            # If the user doesn't already have a default group, add the one they just joined as default
            if not user_profile.default_group:
                user_profile.default_group = group
                user_profile.save()
            # Append response data
            response_data['success'] = True
            response_data['group_id'] = group.id
            response_data['group_name'] = group.name 
        # Else if group doesn't exist, return appropriate response data instead 
        except Group.DoesNotExist:
            response_data['success'] = False
            response_data['error'] = 'Invalid token. Please enter a valid token.'
    return JsonResponse(response_data)


# Group dashboard page
@user_has_group_token
@login_required
def group_dashboard(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    # Make sure user has token for accessing group account 
    desired_group_token = group.token
    if not request.user.is_authenticated:
        return HttpResponseForbidden("You do not have permission to access this page")
    if not Group.objects.filter(members=request.user, token=desired_group_token).exists():
        return HttpResponseForbidden("You do not have permission to access this page")
    
    # Get data for dashabord page
    today = timezone.now().date()
    current_month = datetime.now().month
    current_year = today.year
    month_name = calendar.month_name[current_month]
    members = group.members.all()
    is_admin = group.admins.filter(id=request.user.id).exists()
    currencies = Currency.objects.all() 
    categories = group.categories.all()
    transactions = Transaction.objects.filter(group=group,date__month=current_month,date__year=current_year)

    # Calculate total income and expenses 
    total_income = transactions.filter(type='income').aggregate(total=Sum('amount'))['total'] or Decimal('0')
    total_expense = transactions.filter(type='expense').aggregate(total=Sum('amount'))['total'] or Decimal('0')
    # Calculate monthly balance
    monthly_balance = total_income - total_expense
    # Calculate fixed expense 
    fixed_expenses = transactions.filter(type='expense', is_recurring=True)
    total_fixed_expenses = fixed_expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0')
    # Fetch income transactions for current month
    income_transactions = Transaction.objects.filter(group=group, type='income', date__month=current_month)
    # Fetch expense transactions for current month
    expense_transactions = Transaction.objects.filter(group=group, type='expense', date__month=current_month)
    # Fetch category-wise income data
    income_category_data = (income_transactions.values('category__name').annotate(monthly_amount=Sum('amount')))
    # Fetch category-wise expense data
    expense_category_data = (expense_transactions.values('category__name').annotate(monthly_amount=Sum('amount')))
    # Calculate total fixed expenses
    total_fixed_expenses = fixed_expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0')

    # Fetch category-wise expense data for variable expenses 
    variable_expense_category_data = (
        expense_transactions
        .filter(is_recurring=False)
        .values('category__name')
        .annotate(monthly_amount=Sum('amount'))
    )
    # Fetch category-wise expense data for fixed expenses 
    fixed_expense_category_data = (
        expense_transactions
        .filter(is_recurring=True)
        .values('category__name')
        .annotate(monthly_amount=Sum('amount'))
    )
    # List of tuples for fixed expenses 
    fixed_expense_pie_data = [{'label': entry['category__name'], 'data': float(entry['monthly_amount'])} for entry in fixed_expense_category_data]
    fixed_expense_data_tuples = [(entry['label'], entry['data']) for entry in fixed_expense_pie_data]

    # List of tuples for variable expenses 
    variable_expense_pie_data = [{'label': entry['category__name'], 'data': float(entry['monthly_amount'])} for entry in variable_expense_category_data]
    variable_expense_data_tuples = [(entry['label'], entry['data']) for entry in variable_expense_pie_data]

    # Income and expense data for pie charts - converted to json data
    income_pie_data = [{'label': entry['category__name'], 'data': float(entry['monthly_amount'])} for entry in income_category_data]
    expense_pie_data = [{'label': entry['category__name'], 'data': float(entry['monthly_amount'])} for entry in expense_category_data]
    income_pie_data_json = json.dumps(income_pie_data)
    expense_pie_data_json = json.dumps(expense_pie_data)

    # List of tuples for income transactions 
    income_pie_data = json.loads(income_pie_data_json)
    income_data_tuples = [(entry['label'], entry['data']) for entry in income_pie_data]

    # Total fixed expenses
    total_variable_expense = sum(entry[1] for entry in variable_expense_data_tuples)

    context = {
        # Metadata
        'group': group,
        'members': members,
        'is_admin': is_admin,
        'DESIRED_GROUP_TOKEN': desired_group_token,
        'group_id': group.id,
        'today': today,
        'current_month': month_name,
        'currencies': currencies,
        'categories': categories,

        # Data for charts
        'income_pie_data': income_pie_data_json,
        'expense_pie_data': expense_pie_data_json,
        'total_expense': total_expense,  
        'monthly_balance': monthly_balance,

        # Data for variable monthly expenses / total for section
        'variable_expense_data_tuples': variable_expense_data_tuples,
        'total_variable_expenses': total_variable_expense,

        # Data for variable fixed expenses / total for section
        'fixed_expenses': fixed_expense_data_tuples,
        'total_fixed_expenses': total_fixed_expenses,

        # Data for income section
        'income_grouped': income_data_tuples,
        'total_income': total_income,
    
    }
    return render(request, 'group_dashboard.html', context)

# Add new transaction functionality
@login_required
@require_POST
def add_transaction(request):
    try:
        group_id = request.POST.get('group_id')
        # Extract form data from request
        description = request.POST.get('description')
        amount = request.POST.get('amount')
        currency_id = int(request.POST.get('currency'))
        selected_date_iso = request.POST.get('date')
        is_recurring = request.POST.get('is_recurring')
        category_id = request.POST.get('category')
        transaction_type = request.POST.get('type')
        # Process is_recurring data
        if is_recurring is not None:
            is_recurring = is_recurring.lower() == 'true'
        else:
            is_recurring = False

        # Check if currency has changed, if it has calculate new value according to exchange rate with respect to default currency
        group = Group.objects.get(id=group_id)
        default_currency = group.default_currency
        selected_currency = Currency.objects.get(currency_id=currency_id)

        # Convert user entered amount to USD (reference rate) using exchange rate
        user_entered_amount = Decimal(amount)
        usd_exchange_rate = selected_currency.exchange_rate  
        amount_in_usd = user_entered_amount / usd_exchange_rate

        # Convert amount from USD to user's default currency 
        default_currency_exchange_rate = default_currency.exchange_rate  
        amount_in_default_currency = amount_in_usd * default_currency_exchange_rate

        # If selected currency is same as default, no need to convert, final amount is amount user enetered
        if selected_currency == default_currency:
            converted_amount = user_entered_amount
            # Else final amount is calculated amount from above
        else:
            converted_amount = amount_in_default_currency

        # Create form instance with data
        form = TransactionForm(request.POST)
        # Set selected date
        form.instance.date = datetime.fromisoformat(selected_date_iso).date()  

        # If the form is valid, save transaction and return success response
        if form.is_valid():
            transaction = form.save(commit=False)  
            transaction.user = request.user  
            transaction.group_id = group_id  
            transaction.amount = converted_amount
            transaction.save()  
            return JsonResponse({'message': 'Transaction added successfully'})
        else:
            # Else if form is not valid, return form errors as JSON response
            errors = form.errors.as_json()
            return JsonResponse({'errors': errors}, status=400)
    except Exception as e:
        return JsonResponse({'error': 'An error occurred'})



# Get transaction details functionality
def get_transaction_details(request):
    group_id = request.GET.get('group_id')
    transaction_id = request.GET.get('transaction_id')
    
    try:
        # Get transaction data of incoming transaction id
        transaction = Transaction.objects.get(transaction_id=transaction_id)
        group = transaction.group
        categories = list(group.categories.all().values())
        currencies = list(Currency.objects.all().values()) 
        users = list(group.members.all().values()) 
        user = transaction.user 
        formatted_date = transaction.date.strftime("%B %d, %Y")
        
        # Prepare transaction details as dict
        transaction_details = {
            'description_edit': transaction.description,
            'category_edit': transaction.category.name,
            'amount_edit': str(transaction.amount),  
            'date_edit': str(formatted_date),     
            'currency_edit': transaction.currency.code,
            'type_edit': transaction.type,
            'is_recurring_edit': transaction.is_recurring,
            'user_edit': user.id, 
            'categories_edit': categories,
            'currencies_edit': currencies,  
            'users_edit': users, 
        }
        # Return as json
        return JsonResponse(transaction_details)
    except Transaction.DoesNotExist:
        # If transaction id doesn't exist
        return JsonResponse({'error': 'Transaction not found'}, status=404)
    except Exception as e:
        # Any other errors
        return JsonResponse({'error': 'An error occurred'}, status=500)


# Update transaction functionality 
@require_POST
def update_transaction(request, group_id, transaction_id):
    try:
        # Get transaction data for incoming transaction
        transaction = get_object_or_404(Transaction, transaction_id=transaction_id)
        existing_date_time = transaction.date
        user_id = request.POST.get('editUser')
        transaction.user_id = user_id
        group = get_object_or_404(Group, id=group_id)
        currency_code = request.POST.get('editCurrency') 
        selected_currency = Currency.objects.get(code=currency_code)
        # Calculate converted amount based on currency conversion rate (similar to how it is done in add transaction for reference)
        amount_str = request.POST.get('editAmount')
        amount = Decimal(amount_str) if amount_str else None
        default_currency = group.default_currency
        # Check if user has changed currency, set amount accordingly 
        if selected_currency == default_currency:
            converted_amount = amount
        else:
            usd_exchange_rate = selected_currency.exchange_rate
            amount_in_usd = amount / usd_exchange_rate
            default_currency_exchange_rate = default_currency.exchange_rate
            converted_amount = amount_in_usd * default_currency_exchange_rate

        # Dict for mapping modal names to field names
        field_name_mapping = {
            'editDescription': 'description',
            'editAmount': 'amount',
            'editDate': 'date',
            'editCurrency': 'currency',
            'editType': 'type',
            'editIsRecurring': 'is_recurring',
            'editUser': 'user',
            'editTransactionDetailsCategory': 'category'
        }
        cleaned_data = {}

        # Map frontend field names to model field names - store in cleaned data dict
        for frontend_field, model_field in field_name_mapping.items():
            # Category
            if model_field == 'category':
                category_name = request.POST.get(frontend_field)
                if category_name:
                    try:
                        category = Category.objects.get(name=category_name)
                        cleaned_data[model_field] = str(category.category_id)
                    except Category.DoesNotExist:
                        print("Category not found:", category_name)
                else:
                    cleaned_data[model_field] = None  
            # Currency
            elif model_field == 'currency':
                # Extract currency name from request.POST
                currency_name = request.POST.get(frontend_field)
                if currency_name:
                    try:
                        currency = Currency.objects.get(code=currency_name)
                        cleaned_data[model_field] = str(currency.currency_id)
                    except Currency.DoesNotExist:
                        print("Currency not found:", currency_name)
                else:
                    cleaned_data[model_field] = None  
            # Amount
            elif model_field == 'amount':
                amount_str = request.POST.get(frontend_field)
                if amount_str:
                    cleaned_data[model_field] = Decimal(amount_str)
                else:
                    cleaned_data[model_field] = None 
            else:
                cleaned_data[model_field] = request.POST.get(frontend_field)

        # Create transaction edit form instance with cleaned data
        form = TransactionEditForm(data=cleaned_data, instance=transaction)

        # If form is valid, updat transaction with cleaned data / converted amount
        if form.is_valid():
            updated_transaction = form.save(commit=False)
            updated_transaction.amount = converted_amount
            updated_transaction.currency = group.default_currency
            updated_transaction = form.save()

            # Updated transaction details as dict
            transaction_details = {
                'description': updated_transaction.description,
                'amount': updated_transaction.amount,
                'category': updated_transaction.category, 
                'currency': updated_transaction.currency,  
                'type': updated_transaction.type,  
                'is_recurring': updated_transaction.is_recurring, 
                'user': updated_transaction.user, 
            }
            # If date is different, update transaction details with new date
            if transaction.date.date() != existing_date_time.date():
                transaction_details['date'] = transaction.date.strftime('%Y-%m-%d %H:%M:%S')
            else:
                transaction_details['date'] = existing_date_time.strftime('%Y-%m-%d %H:%M:%S')
            new_datetime = datetime.combine(form.cleaned_data['date'], existing_date_time.time())
            transaction.date = new_datetime
            # Save transaction
            transaction.save()
            # Store transaction details as json
            transaction_details_json = json.dumps(transaction_details)
            # Return success response with updated details
            return JsonResponse({'success': 'Transaction updated', 'transaction_details': transaction_details_json})

        else:
            # Else print errors as json
            errors = form.errors.as_json()
            return HttpResponse(errors, content_type='application/json', status=400)

    except Exception as e:
        # Any other exceptions
        return JsonResponse({'error': 'An error occurred'}, status=500)


# Get categories functionality 
@login_required
def get_categories(request, group_id):
    try:
        # Retrieve categories associated with incoming group
        group = get_object_or_404(Group, id=group_id)
        categories = group.categories.all()
        # Prepare category data as list of dicts
        category_data = [{'category_id': category.category_id, 'name': category.name} for category in categories]
        # Return it as json
        return JsonResponse({'categories': category_data})
    except Exception as e:
        # Handle exceptions
        return JsonResponse({'error': 'An error occurred'}, status=500)


# Manage categories page
@login_required
@user_has_group_token
def manage_categories(request, group_id):
    # Get current user's group based on group_id
    user_group = Group.objects.get(id=group_id)
    # Get categories as json data
    group_categories = user_group.categories.all()
    categories_json = serializers.serialize('json', group_categories)
    # Context data
    context = {
        'categories': categories_json,
        'group_id': group_id,
        'group_name': user_group.name,
    }
    return render(request, 'manage_categories.html', context)


# Add categories functionality 
def add_category(request, group_id):
    if request.method == 'POST':
        group = Group.objects.get(id=group_id)
        # Extract category name and color from form data
        name = request.POST.get('name')
        color = request.POST.get('color')
        # Create new category for incoming group
        new_category = Category(name=name, color=color)
        new_category.save()
        # Add new category to group's categories field
        group.categories.add(new_category)
        # Redirect to the manage_categories page
        return redirect('manage_categories', group_id=group.id)


# Delete category functionality 
def delete_category(request, group_id, category_id):
    if request.method == 'POST':
        group = get_object_or_404(Group, id=group_id)
        category = get_object_or_404(Category, pk=category_id)
        # Delete incoming category
        group.categories.remove(category)
        # Redirect to manage_categories page
        return redirect('manage_categories', group_id=group.id)


# Groups page
@user_has_group_token
@login_required
def groups(request, group_id):
    # Get user, user's groups, and groups where user is admin
    user = request.user  
    groups = user.custom_groups.all()  
    admin_groups = user.admin_groups.all()  
    # Current group based on incoming group_id
    current_group = get_object_or_404(Group, id=group_id)
    group_id = group_id
    # Render groups page with context data
    return render(request, 'groups.html', {
        'user': user,
        'groups': groups,
        'admin_groups': admin_groups,
        'current_group': current_group,
        'group_id': group_id 
    })


# Delete group functionality 
@login_required
def delete_group(request, group_id):
    user = request.user
    current_group_id = request.GET.get('current_group_id')
    try:
        group = Group.objects.get(id=group_id)
    except Group.DoesNotExist:
        return HttpResponse("Group not found", status=404)

    # Check if the user is an admin of group they are deleting
    if user in group.admins.all():
        # Get id of current group before deletion
        try:
            current_group_id = int(group.id) if current_group_id is None else int(current_group_id)
        except ValueError:
            # If group id is not a valid nummber
            return HttpResponse("Invalid current_group_id", status=400)
        # Delete the group
        group.delete()
        # If user deleted group account they were currently on, log them out and redirect them to login page
        if current_group_id == int(group_id):
            logout(request)
            return HttpResponseRedirect(reverse('login_view'))
        # Else have them stay on groups page with current group id
        return HttpResponseRedirect(reverse('groups', args=[current_group_id]))
    # Else have them stay on groups page with current group id
    return HttpResponseRedirect(reverse('groups', args=[current_group_id]))


# Settings page
@login_required
@user_has_group_token
def settings(request, group_id):
    # Get data for settings page relevant to user and group
    user = request.user
    group = get_object_or_404(Group, id=group_id)
    group_name = group.name
    group_token = group.token
    user_groups = Group.objects.filter(members=user)
    user_profile = UserProfile.objects.get(user=request.user)
    currencies = Currency.objects.all()
    default_currency = group.default_currency
    default_group = user_profile.default_group.id

    # Context data
    context = {
        'group': group,
        'group_id': group_id,
        'user_groups': user_groups,
        'group_name': group_name,
        'currencies': currencies,
        'default_currency': default_currency,
        'group_token': group_token,
        'default_group': default_group,
    }

    return render(request, 'settings.html', context)

# Update user profile functionality 
@login_required
def update_user_profile(request):
    if request.method == 'POST':
        # Get data for user profile form
        default_group_id = request.POST.get('default_group')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')

        try:
            selected_group = Group.objects.get(id=default_group_id)
            user_profile = UserProfile.objects.get(user=request.user)

            # Update user's data
            user_profile.default_group = selected_group
            request.user.first_name = first_name
            request.user.last_name = last_name
            request.user.username = username

            # Save changes
            user_profile.save()
            request.user.save()

            # Return json success response
            return JsonResponse({'message': 'Profile updated successfully'})
        except Exception as e:
            # Handle any errors that occur during update
            return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=400)
    # Else if request not post, return json error response 
    return JsonResponse({'error': 'Invalid request method'}, status=400)

# Update group settings functionality 
@login_required
def update_group_settings(request):
    if request.method == 'POST':
        # Get data from group settings form
        group_id = request.POST.get('group_id')  
        group_name = request.POST.get('group_name')

        try:
            group = Group.objects.get(id=group_id)
            # Update group name
            group.name = group_name
            # Save changes
            group.save()

            # Return json success response
            return JsonResponse({'message': 'Group settings updated successfully'})
        except Group.DoesNotExist:
            # Return json reponse if group doesn't exist 
            return JsonResponse({'error': 'Group not found'}, status=404)
        # Return appropriate json response if any exceptions
        except Exception as e:
            return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=400)
    # Else if request not post, return appropriate json error response 
    return JsonResponse({'error': 'Invalid request method'}, status=400)

# Update currency settings functionality 
@login_required
def update_currency_settings(request):
    if request.method == 'POST':
        try:
            # Get selected currency id from form
            new_default_currency_id = request.POST.get('selected_currency')
            # Update group's default currency 
            group_id = request.POST.get('group_id')
            group = Group.objects.get(id=group_id)
            new_default_currency = Currency.objects.get(currency_id=new_default_currency_id)
            group.default_currency = new_default_currency
            # Save changes
            group.save()
            # Update transaction amounts (all group's transactions) given new default currency (Process below is 
            # similar to how it's been calculated a few other times in the view code)
            transactions = Transaction.objects.filter(group=group)
            for transaction in transactions:
                current_currency = transaction.currency
                if current_currency.currency_id == new_default_currency_id:
                    converted_amount = transaction.amount
                else:
                    usd_exchange_rate = current_currency.exchange_rate
                    amount_in_usd = transaction.amount / usd_exchange_rate
                    new_default_currency = Currency.objects.get(currency_id=new_default_currency_id)
                    new_default_currency_exchange_rate = new_default_currency.exchange_rate
                    converted_amount = amount_in_usd * new_default_currency_exchange_rate

                # Update each transaction amount with converted amount
                transaction.amount = converted_amount
                # Update transaction currency back to default (since it's been converted)
                transaction.currency = new_default_currency 
                # Save updated trasnaction
                transaction.save()

            # Return approporate json responses
            return JsonResponse({'message': 'Currency settings updated successfully'})
        except Group.DoesNotExist:
            return JsonResponse({'error': 'Group not found'}, status=404)
        except Currency.DoesNotExist:
            return JsonResponse({'error': 'Invalid currency selected'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=400)
    return JsonResponse({'error': 'Invalid request method or form submission'}, status=400)


# Update password functionality 
@login_required
def update_password(request):
    if request.method == 'POST':
        # Create instance of password change form (a django form for updating passwords)
        password_change_form = PasswordChangeForm(request.user, request.POST)
        if password_change_form.is_valid():
            password_change_form.save()
            update_session_auth_hash(request, password_change_form.user)
            # Handle response messages and return json data appropriately 
            messages.success(request, 'Your password was successfully updated.')
            return JsonResponse({'message': 'Password changed successfully'})
        else:
            errors = dict(password_change_form.errors)
            return JsonResponse({'errors': errors}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=400)


# Delete transaction functionality 
def delete_transaction(request, transaction_id):
    if request.method == 'DELETE':
        try:
            # Fetch specific trnansaction and delete it
            transaction = Transaction.objects.get(transaction_id=transaction_id)
            transaction.delete()
            # Return apprpriate json reponses messages
            return JsonResponse({'success': True})
        except Transaction.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Transaction not found'}, status=404)
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)

# Custom logout functionality 
def custom_logout(request):
    # Log user out
    logout(request)
    # Redirect the user to the login page
    login_url = reverse('login_view')  
    return redirect(login_url)


# REPORTS PAGES 

# Render pages for all charts passing in group id as context
def monthly_expense_trends_view(request, group_id):
    context = {'group_id': group_id}
    return render(request, 'reports/1_monthly_expense_trends.html', context)

def category_expense_trends_view(request, group_id):
    context = {'group_id': group_id}
    return render(request, 'reports/2_category_expense_trends.html', context)

def balance_over_time_view(request, group_id):
    context = {'group_id': group_id}
    return render(request, 'reports/3_balance_over_time.html', context)

def expense_distribution_group_view(request, group_id):
    context = {'group_id': group_id}
    return render(request, 'reports/4_expense_distribution_group.html', context)

def income_distribution_group_view(request, group_id):
    context = {'group_id': group_id}
    return render(request, 'reports/5_income_distribution_group.html', context)

def expense_distribution_day_view(request, group_id):
    context = {'group_id': group_id}
    return render(request, 'reports/6_expense_distribution_day.html', context)

def highest_spending_category_view(request, group_id):
    context = {'group_id': group_id}
    return render(request, 'reports/7_highest_spending_category.html', context)

def income_expense_time_view(request, group_id):
    context = {'group_id': group_id}
    return render(request, 'reports/8_income_expense_time.html', context)

def category_wise_monthly_view(request, group_id):
    context = {'group_id': group_id}
    return render(request, 'reports/9_category_wise_monthly.html', context)

# DATA FOR REPORTS PAGES

# Calculate data for monthly expense trends chart 
def get_1_monthly_expense_data(request,group_id, year):
    # Query to fetch monthly expenses
    monthly_expenses = Transaction.objects.filter(
        date__year=year,
        type='expense',
        group_id=group_id, 
    ).annotate(month=ExtractMonth('date')).values('month') \
        .annotate(total_expenses=Sum('amount')).order_by('month')
    # List of dicts for returned data
    data = [{'label': calendar.month_abbr[month['month']], 'data': float(month['total_expenses'])} for month in monthly_expenses]
    # Return data as JSON response
    return JsonResponse(data, safe=False)


# Calculate data for category expense trends chart
def get_2_monthly_category_expense_trends_data(request, group_id, year, month):
    # Get incoming year and month
    try:
        year = int(year)
        month = int(month)
    except ValueError:
        return JsonResponse({'error': 'Invalid year or month input'}, status=400)
    # Get group
    try:
        group = Group.objects.get(id=group_id)
    except Group.DoesNotExist:
        return JsonResponse({'error': 'Group not found'}, status=404)

    # Query to fetch monthly expenses sums by category
    category_expenses = Transaction.objects.filter(
        group=group,
        date__year=year,
        date__month=month,
        type='expense'
    ).values('category__name').annotate(
        total_expense=Sum('amount')
    ).filter(total_expense__gt=0)

    # Data as list of dicts
    data = [{'category': expense['category__name'], 'total_expense': float(expense['total_expense'])} for expense in category_expenses]

    # Return data as JSON response
    return JsonResponse(data, safe=False)



# Calculate data for yearly balance chart
def get_3_balance_over_time_data(request, group_id, year):
    # Filter transactions for incoming group and year, group data by month, calculate total income and expense, order results by month
    transactions = Transaction.objects.filter(
        group_id=group_id,
        date__year=year
    ).annotate(month=ExtractMonth('date')).values('month') \
        .annotate(
            total_income=Sum(
                Case(
                    When(type='income', then=F('amount')),
                    default=Value(0),
                    output_field=FloatField()
                )
            ),
            total_expenses=Sum(
                Case(
                    When(type='expense', then=F('amount')),
                    default=Value(0),
                    output_field=FloatField()
                )
            )
        ).order_by('month')

    # Calculate balance for each month
    data = []
    balance = 0
    for month_data in transactions:
        income = month_data['total_income'] or 0
        expenses = month_data['total_expenses'] or 0
        balance += income - expenses
        # Append calculations - income, expense, and balance data, along with labels, to data
        data.append({
            'label': calendar.month_abbr[month_data['month']],
            'income': float(income),
            'expenses': float(expenses),
            'balance': float(balance)
        })
    # Return data as JSON response
    return JsonResponse(data, safe=False)

# Calculate data for category expense distribution by group members chart
def get_4_expense_distribution_group_data(request, group_id, year, month):
    # Get selected date and group, handle errors and exceptions
    try:
        year = int(year)
        month = int(month)
    except ValueError:
        return JsonResponse({'error': 'Invalid year or month input'}, status=400)
    try:
        group = Group.objects.get(id=group_id)
    except Group.DoesNotExist:
        return JsonResponse({'error': 'Group not found'}, status=404)

    # Query to get monthly expense sums by user
    user_expenses = Transaction.objects.filter(
        group=group,
        date__year=year,
        date__month=month,
        type='expense'
    ).values('user__username').annotate(
        total_expense=Sum('amount')
    ).filter(total_expense__gt=0)

    # Data as list of dicts
    data = [{'user': expense['user__username'], 'total_expense': float(expense['total_expense'])} for expense in user_expenses]

    # Return data as JSON response
    return JsonResponse(data, safe=False)

# Calculate data for category income distribution by group members chart
def get_5_income_distribution_group_data(request, group_id, year, month):
    # Get selected date and group, handle errors and exceptions
    try:
        year = int(year)
        month = int(month)
    except ValueError:
        return JsonResponse({'error': 'Invalid year or month input'}, status=400)
    try:
        group = Group.objects.get(id=group_id)
    except Group.DoesNotExist:
        return JsonResponse({'error': 'Group not found'}, status=404)

    #  Query to get monthly income sums by user
    user_income = Transaction.objects.filter(
        group=group,
        date__year=year,
        date__month=month,
        type='income'
    ).values('user__username').annotate(
        total_income=Sum('amount')
    ).filter(total_income__gt=0)

    # Data as list of dicts
    data = [{'user': income['user__username'], 'total_income': float(income['total_income'])} for income in user_income]

    # Return data as JSON response
    return JsonResponse(data, safe=False)

# Calculate data for category expense distribution by day of week chart
def get_6_expense_distribution_day_data(request, group_id, year):
    # Get selected date and group, handle errors and exceptions
    try:
        year = int(year)
    except ValueError:
        return JsonResponse({'error': 'Invalid year input'}, status=400)
    try:
        group = Group.objects.get(id=group_id)
    except Group.DoesNotExist:
        return JsonResponse({'error': 'Group not found'}, status=404)

    #  Query to get monthly expense sums by day of week
    expenses = Transaction.objects.filter(
        group=group,
        date__year=year,
        type='expense'
    )

    # Dict to store total expenses per day of week numerically
    day_expenses = {
        '0': 0,  # Sunday
        '1': 0,  # Monday
        '2': 0,  # Tuesday
        '3': 0,  # Wednesday
        '4': 0,  # Thursday
        '5': 0,  # Friday
        '6': 0,  # Saturday
    }

    # Calculate totals for each day of the week
    for expense in expenses:
        day_of_week = datetime.weekday(expense.date)
        day_expenses[str(day_of_week)] += expense.amount

    # Data as list of dicts
    data = [{'day_of_week': day, 'total_expense': float(total)} for day, total in day_expenses.items()]

    # Return data as JSON response
    return JsonResponse(data, safe=False)


# Calculate data highest spending category chart
def get_7_highest_spending_category_data(request, group_id, year):
    # Get selected date and group, handle errors and exceptions
    try:
        year = int(year)
    except ValueError:
        return JsonResponse({'error': 'Invalid year input'}, status=400)
    try:
        group = Group.objects.get(id=group_id)
    except Group.DoesNotExist:
        return JsonResponse({'error': 'Group not found'}, status=404)

    # Query to get the highest categorical spending for each month in selected year
    highest_spending_data = Transaction.objects.filter(
        group=group,
        date__year=year,
        type='expense'
    ).values('date__month').annotate(
        highest_spending=Max('amount')
    )

    # Data as list of dicts
    data = [{'month': spending['date__month'], 'highest_spending': float(spending['highest_spending'])} for spending in highest_spending_data]

    # Return data as JSON response
    return JsonResponse(data, safe=False)

# Calculate data for income vs expense over time chart
def get_8_income_vs_expense_over_time_data(request, group_id):
    # Get group, handle errors and exceptions
    try:
        group = Group.objects.get(id=group_id)
    except Group.DoesNotExist:
        return JsonResponse({'error': 'Group not found'}, status=404)

    # Query to get monthly income and expenses sums 
    transaction_data = Transaction.objects.filter(
        group=group,
        type__in=['income', 'expense']  
    ).values('date__year', 'date__month', 'type').annotate(
        total_amount=Sum('amount')
    )

    # Organize data by month
    data_dict = {}
    for entry in transaction_data:
        year = entry['date__year']
        month = entry['date__month']
        amount = entry['total_amount']
        transaction_type = entry['type']

        # Create label in 'MMM YYYY' format
        label = f'{calendar.month_abbr[month]} {year}'
        if label not in data_dict:
            data_dict[label] = {'income': 0, 'expense': 0}
        data_dict[label][transaction_type] = amount

    # Extract data into separate lists
    months = list(data_dict.keys())
    income = [data_dict[label]['income'] for label in months]
    expenses = [data_dict[label]['expense'] for label in months]

    # Store as response data 
    response_data = {
        'income': income,
        'expense': expenses,
        'months': months,
    }
    # Return as json
    return JsonResponse(response_data)


# Calculate data for category wise monthly comparison chart
def get_9_category_wise_monthly_comparison_data(request, group_id, year):
    # Get selected date and group, handle errors and exceptions
    try:
        year = int(year)
    except ValueError:
        return JsonResponse({'error': 'Invalid year input'}, status=400)
    try:
        group = Group.objects.get(id=group_id)
    except Group.DoesNotExist:
        return JsonResponse({'error': 'Group not found'}, status=404)

    # Query to fetch distinct categories for expenses in specified year
    categories = Transaction.objects.filter(
        group=group,
        date__year=year,
        type='expense'
    ).values('category__name').distinct()  

    # Dict to store monthly category totals
    monthly_category_totals = {}
    # Set category names as dict keys
    for category in categories:
        category_name = category['category__name']
        monthly_category_totals[category_name] = [0] * 12  

    # Query to fetch monthly expense sums by category
    expenses = Transaction.objects.filter(
        group=group,
        date__year=year,
        type='expense'
    ).values('date__month', 'category__name').annotate(
        total_expense=Sum('amount')
    )

    # Populate dic with totals relative to category
    for expense in expenses:
        month = expense['date__month']
        category_name = expense['category__name']
        total_expense = expense['total_expense']
        monthly_category_totals[category_name][month - 1] = total_expense

    # Store as response data
    response_data = {
        'categories': list(categories.values_list('category__name', flat=True)),  
        'months': list(calendar.month_abbr[1:]),  
        'data': list(monthly_category_totals.values()),  
    }

    # Return as json
    return JsonResponse(response_data)


# DUMMY DATA FOR MAIN REPORTS PAGE GRID (THESE FUNCTIONS ARE CALLED IN VIEW)

# Function to create dummy data for monthly expense trends chart
def get_monthly_expense_data():
    # Dummy data 5 months
    num_months = 5
    # Generate random series of expenses for each month
    data = []
    for month in range(1, num_months + 1):
        month_name = calendar.month_abbr[month]
        total_expenses = round(random.uniform(1000, 5000), 2) 
        data.append({'label': month_name, 'data': total_expenses})
    return data

# Function to create dummy data for category expense trends chart
def get_category_expense_data():
    categories = ['Groceries', 'Entertainment', 'Utilities', 'Dining', 'Transportation']
    data = [{'label': category, 'data': random.randint(100, 500)} for category in categories]
    return data

# Function to create dummy data for balance over time chart
def get_balance_over_time():
    # Year's worth of data
    balance_data = [
        {'label': 'Jan', 'income': 1000, 'expense': 800, 'balance': 200},
        {'label': 'Feb', 'income': 1100, 'expense': 820, 'balance': 280},
        {'label': 'Mar', 'income': 1200, 'expense': 850, 'balance': 350},
        {'label': 'Apr', 'income': 1300, 'expense': 900, 'balance': 400},
        {'label': 'May', 'income': 1400, 'expense': 950, 'balance': 450},
        {'label': 'Jun', 'income': 1500, 'expense': 1000, 'balance': 500},
        {'label': 'Jul', 'income': 1600, 'expense': 1050, 'balance': 550},
        {'label': 'Aug', 'income': 1700, 'expense': 1100, 'balance': 600},
        {'label': 'Sep', 'income': 1800, 'expense': 1150, 'balance': 650},
        {'label': 'Oct', 'income': 1900, 'expense': 1200, 'balance': 700},
        {'label': 'Nov', 'income': 2000, 'expense': 1250, 'balance': 750},
        {'label': 'Dec', 'income': 2100, 'expense': 1300, 'balance': 800},
    ]
    return balance_data

# Function to create dummy data for exepense distribution by group member chart
def get_expense_distribution_data():
    data = [{'label': f'User {i}', 'data': random.randint(100, 500)} for i in range(1, 5)]  
    return data

# Function to create dummy data for income distribution by group member chart
def get_income_distribution_data():
    data = [{'label': f'User {i}', 'data': random.randint(300, 800)} for i in range(1, 4)]  
    return data

# Function to create dummy data for exepense distribution by day chart
def get_expense_distribution_by_day_data():
    days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    data = [{'label': day, 'data': random.randint(100, 500)} for day in days_of_week]
    return data

# Function to create dummy data for highest spending category chart
def get_highest_spending_category_for_year():
    dummy_categories = ['Food', 'Transportation', 'Housing', 'Entertainment', 'Utilities', 'Shopping', 'Healthcare']
    highest_spending_for_year = []
    for month in range(1, 13):
        highest_spending = {'label': calendar.month_abbr[month], 'category': 'Unknown', 'amount': 0}
        for category_name in dummy_categories:
            monthly_expense = round(random.uniform(600, 1000), 2)
            if monthly_expense > highest_spending['amount']:
                highest_spending['category'] = category_name
                highest_spending['amount'] = monthly_expense
        highest_spending_for_year.append(highest_spending)
    return highest_spending_for_year

# Function to create dummy data for total income vs expense over time chart
def get_total_income_expense_balance_over_time():
    # Year's worth of data
    total_data = [{'label': 'Jan', 'income': 1000, 'expense': 800, 'balance': 200},
                 {'label': 'Feb', 'income': 1100, 'expense': 820, 'balance': 280},
                 {'label': 'Mar', 'income': 1200, 'expense': 850, 'balance': 350},
                 {'label': 'Apr', 'income': 1300, 'expense': 870, 'balance': 430},
                 {'label': 'May', 'income': 1400, 'expense': 900, 'balance': 500},
                 {'label': 'Jun', 'income': 1500, 'expense': 920, 'balance': 580},
                 {'label': 'Jul', 'income': 1600, 'expense': 950, 'balance': 650},
                 {'label': 'Aug', 'income': 1700, 'expense': 980, 'balance': 720},
                 {'label': 'Sep', 'income': 1800, 'expense': 1000, 'balance': 800},
                 {'label': 'Oct', 'income': 1900, 'expense': 1020, 'balance': 880},
                 {'label': 'Nov', 'income': 2000, 'expense': 1050, 'balance': 950},
                 {'label': 'Dec', 'income': 2100, 'expense': 1080, 'balance': 1020}
                 ]
    return total_data

# Function to create dummy data for category monthly comparison chart
def get_category_monthly_comparison_data():
    categories = Category.objects.all()[:4] 
    data = [{'label': category.name, 'data': [random.randint(100, 500) for _ in range(12)]} for category in categories]
    return data
