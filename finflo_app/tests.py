from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from .models import *
from decimal import Decimal
from . import views
from  . import api
from .serializers import *
from .forms import *
import json
from datetime import datetime
from django.db.models import QuerySet
from rest_framework.test import APITestCase
from rest_framework import status
from datetime import date
from django.test.client import Client



# VIEW CODE TESTS

class ViewsTestCase(TestCase):
    def setUp(self):
        # Test user
        self.user = User.objects.create_user(username='testuser', password='testpass')
        # Login test user
        self.client.login(username='testuser', password='testpass')
        # Test group with test token
        self.group = Group.objects.create(name='Test Group', token='testtoken')
        # Test group members
        self.group.members.add(self.user)
        # Test currency data
        self.currency = Currency.objects.create(name='USD', exchange_rate=1.0)
        self.usd_currency = Currency.objects.create(code='USD',exchange_rate=1.0)
        self.eur_currency = Currency.objects.create(code='EUR',exchange_rate=0.85)   
        # Test category data
        self.category = Category.objects.create(name='Food')
        self.category1 = Category.objects.create(category_id=111, name='Social')
        self.category2 = Category.objects.create(category_id=222, name='Transportation')
        self.group.categories.add(self.category, self.category1, self.category2)

        # Test transaction
        self.test_transaction = Transaction.objects.create(
            group=self.group,
            description='Groceries',
            amount=Decimal('50.00'),
            currency=self.currency,
            date=datetime(2023, 9, 20).date(),
            is_recurring=False,
            category=self.category,
            type='expense',
            user=self.user,
        )
        # Test user profile
        self.user_profile, created = UserProfile.objects.get_or_create(user=self.user, defaults={'default_group': self.group})
        

    # Test reports_view
    def test_reports_view(self):
        # GET reports_view
        response = self.client.get(reverse('reports', args=[self.group.id]))
        self.assertEqual(response.status_code, 200)
        # Check subset of expected variables are being returned in context 
        self.assertIn('monthly_expense_data', response.context)
        self.assertIn('category_expense_data', response.context)
        self.assertIn('balance_over_time_data', response.context)
        # Check if group id in context matches group id in url
        self.assertEqual(response.context['group_id'], self.group.id)
        
        # Check data is in json format on subset of expected data
        context_variables = ['expense_distribution_data', 'income_distribution_data','expense_distribution_by_day_data']
        for name in context_variables:
            value = response.context[name]
            try:
                json.loads(value)
            except json.JSONDecodeError:
                self.fail(f"'{name}' is not in JSON format.")

    # Test transactions_view
    def test_transactions_view(self):
        # GET transactions_view
        response = self.client.get(reverse('transactions', args=[self.group.id]))
        self.assertEqual(response.status_code, 200)
        # Check various expected context points
        self.assertIn('total_expense_month', response.context)
        self.assertIn('transactions', response.context)
        self.assertTrue(isinstance(response.context['currencies'], QuerySet))
        transactions = response.context['transactions']
        self.assertTrue(isinstance(transactions, QuerySet))
        # Check if total month and day totals are valid numbers
        self.assertTrue(isinstance(response.context['total_expense_month'], (int, float)))
        self.assertTrue(isinstance(response.context['total_expense_today'], (int, float)))


    # Test successful registration funcitonality
    def test_successful_registration(self):
        # Simulate successful registration
        response = self.client.post(reverse('register_user'), {
            'username': 'testuser',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'email': 'test@example.com',
        })
        # Check successful response code and that newly registered user is found in Users model
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(username='testuser').exists())

    # Test failed registration with username that already exists
    def test_failed_registration_existing_username(self):
        User.objects.filter(username='testuser').delete()
        # User same username as above
        response = self.client.post(reverse('register_user'), {
            'username': 'testuser',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'email': 'test@example.com',
        })
        # Ensure success is false 
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data['success'])

    # Test invalid registration form
    def test_invalid_registration_form(self):
        # Registration data with invalid username
        response = self.client.post(reverse('register_user'), {
            'username': '',  
            'password1': 'testpass123',
            'password2': 'testpass123',
            'email': 'test@example.com',
        })
        # Assert unsuccesful registration and expected messages / errors 
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'Registration failed. Please check the form and try again.')
        self.assertIn('username', data['field_errors'])  

    # Test create group
    def test_create_group(self):
        self.assertEqual(Group.objects.count(), 1) 
        # Post request to make new test group
        response = self.client.post(reverse('create_group'), {
            'name': 'New Group',
        })
        # Check successful response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        expected_message = data['message']
        self.assertEqual(data['message'], expected_message)
        # Check if the group was created
        self.assertEqual(Group.objects.count(), 2)  
        new_group = Group.objects.get(name='New Group')
        # User that made new group should be both member and admin
        self.assertEqual(new_group.members.count(), 1)  
        self.assertEqual(new_group.admins.count(), 1) 

    # Test join with valid token
    def test_join_group_with_valid_token(self):
        # Post request to join with test token
        response = self.client.post(reverse('join_group_ajax'), {'token': 'testtoken'})
        # Ensure response is successful and that test user was added
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.group.members.filter(username='testuser').exists())
        # Ensure group was added to test user's groups
        user_profile = UserProfile.objects.get(user=self.user)
        self.assertTrue(user_profile.groups.filter(pk=self.group.pk).exists())
        # Check successful response data
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['group_id'], self.group.id)
        self.assertEqual(data['group_name'], self.group.name)

    # Test join group with invalid token
    def test_join_group_with_invalid_token(self):
        self.client.login(username='testuser', password='testpass')
        # Post request with invalid token
        response = self.client.post(reverse('join_group_ajax'), {'token': 'invalidtoken'})
        self.assertEqual(response.status_code, 200)
        # Fetch user's groups after request with invalid token
        user_profile = UserProfile.objects.get(user=self.user)
        user_groups = user_profile.groups.all()
        # Ensure group is not in user's groups 
        self.assertNotIn(self.group, user_groups)
        # Ensure response data indicates failed attempt to join group 
        data = response.json()
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 'Invalid token. Please enter a valid token.')

    # Test group dashboard is accessible by authenticated user
    def test_group_dashboard_authenticated_user(self):
        response = self.client.get(reverse('group_dashboard', kwargs={'group_id': self.group.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'group_dashboard.html')

    # Test data for group dashboard
    def test_group_dashboard_data(self):
        # Check a few different aspects of expected context data
        response = self.client.get(reverse('group_dashboard', kwargs={'group_id': self.group.id}))
        context = response.context
        self.assertContains(response, "Monthly Balance")
        self.assertTrue('variable_expense_data_tuples' in context)
        self.assertTrue('income_grouped' in context)

    # Test add transaction
    def test_add_transaction_success(self):
        # Get initial transaction coint
        initial_transaction_count = Transaction.objects.count()
        # Add transaction call with transaction data
        response = self.client.post(reverse('add_transaction'), {
            'group_id': self.group.id,
            'description': 'Groceries',
            'amount': '50.00',
            'currency': self.currency.currency_id,
            'date': '2023-09-15',
            'is_recurring': 'false',
            'category': self.category.category_id,
            'type': 'expense'
        })
        # Check response data is as expected
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Transaction.objects.count(), initial_transaction_count + 1)
        self.assertEqual(response.json(), {'message': 'Transaction added successfully'})

    # Test get transaction details 
    def test_get_transaction_details_valid(self):
            # Get call to get transaction details using test group id and transaction id
            response = self.client.get(reverse('get_transaction_details'), {
                'group_id': self.group.id,
                'transaction_id': self.test_transaction.transaction_id,
            })
            # Check status of response and that data has been retireved as expected
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()['description_edit'], 'Groceries')
            self.assertEqual(response.json()['amount_edit'], '50.00')

    # Test get transaction with invalid data
    def test_get_transaction_details_invalid_transaction_id(self):
        # Get reuquest for same thing but with invalid data
        response = self.client.get(reverse('get_transaction_details'), {
            'group_id': self.group.id,
            'transaction_id': 9999,  
        })
        # Make sure its not successful
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['error'], 'Transaction not found')

    # Test get categories
    def test_get_categories(self):
        # Get request to get_categories endpoint with test group id
        response = self.client.get(reverse('get_categories', kwargs={'group_id': self.group.id}))
        # Make sure its successful
        self.assertEqual(response.status_code, 200)
        # Decode JSON response 
        data = response.json()
        # Check JSON contains expected categories from test data
        expected_categories = [{'category_id': self.category.category_id, 'name': 'Food'},
                                {'category_id': self.category1.category_id, 'name': 'Social'},
                               {'category_id': self.category2.category_id, 'name': 'Transportation'}]
        self.assertEqual(data['categories'], expected_categories)

    # Test update user profile
    def test_update_user_profile(self):
        # Data for updating user profile
        data = {
            'default_group': self.group.id,
            'first_name': 'Updated',
            'last_name': 'User',
            'username': 'updated_user'
        }
        # Post request to udate_user_profile endpoint 
        response = self.client.post(reverse('update_user_profile'), data)
        # Ensure successful response and data from above is found in updated entry as expected 
        self.assertEqual(response.status_code, 200)
        self.user_profile.refresh_from_db()
        self.user.refresh_from_db()
        self.assertEqual(self.user_profile.default_group, self.group)
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.user.last_name, 'User')
        self.assertEqual(self.user.username, 'updated_user')

    # Test update group settings
    def test_update_group_settings(self): 
        # Data for updating group settings
        data = {
            'group_id': self.group.id,
            'group_name': 'Updated Group Name'
        }
        # Post request to update_group_settings 
        response = self.client.post(reverse('update_group_settings'), data)
        # Ensure successful response and that the group name has been updated 
        self.assertEqual(response.status_code, 200)
        self.group.refresh_from_db()
        self.assertEqual(self.group.name, 'Updated Group Name')

    # Test update currency settings 
    def test_update_currency_settings(self):
        self.client.login(username='testuser', password='testpassword')
        # Data for updating currency settings
        data = {
            'group_id': self.group.id,
            'selected_currency': self.eur_currency.currency_id
        }
        # Post request to update_currency_settings 
        response = self.client.post(reverse('update_currency_settings'), data)
        # Ensure successful response and that default currency has been udpated
        self.assertEqual(response.status_code, 200)
        self.group.refresh_from_db()
        self.assertEqual(self.group.default_currency, self.eur_currency)

    # Test delete existing transaction
    def test_delete_existing_transaction(self):
        # Get transaction id from test transaction
        transaction_id = self.test_transaction.transaction_id
        # Delete transaction request passing in transaction id
        response = self.client.delete(reverse('delete_transaction', args=[transaction_id]))
        # Ensure successful response 
        self.assertEqual(response.status_code, 200)

    # Test delete non existent transaction
    def test_delete_nonexistent_transaction(self):
        nonexistent_transaction_id = 9999 
        # # Delete transaction request passing in nonexistent transaction id
        response = self.client.delete(reverse('delete_transaction', args=[nonexistent_transaction_id]))
        # Ensure unsuccessful response (404)
        self.assertEqual(response.status_code, 404)


# API TESTS

class YourApiTests(APITestCase):

    def setUp(self):
        # Test data set up as before 
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')
        self.group = Group.objects.create(name='Test Group', token='testtoken')
        self.currency = Currency.objects.create(code='USD', exchange_rate=1.0)
        self.category = Category.objects.create(name='Food')
        self.transaction = Transaction.objects.create(
            group=self.group,
            description='Groceries',
            amount=50.00,
            currency=self.currency,
            date='2023-09-20',
            is_recurring=False,
            category=self.category,
            type='expense',
            user=self.user,
        )

    # Test user create endpoint
    def test_user_create(self):
        url = reverse('user_create')
        data = {'username': 'newuser', 'password': 'newpass'} 
        response = self.client.post(url, data, format='json')
        # Check response after posting new user data to ensure successful
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2) 

    # Test user detail endpoint
    def test_user_detail(self):
        url = reverse('user_detail', args=[self.user.id])
        response = self.client.get(url)
        # Ensure successful response status
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # test group create endpoint 
    def test_group_create(self):
        url = reverse('group_create')
        data = {'name': 'New Group', 'token': 'newtoken'} 
        response = self.client.post(url, data, format='json')
        # Check new group was successfully created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Group.objects.count(), 2) 

    # Test group detail
    def test_group_detail(self):
        group = Group.objects.create(name='Test Group')
        url = reverse('group_detail', args=[group.id])
        response = self.client.get(url)
        # Ensure successful response 
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Test PUT request with updated group name
        updated_data = {'name': 'Updated Group Name'}
        response = self.client.put(url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Group.objects.get(id=group.id).name, updated_data['name'])
        # Test DELETE 
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Group.objects.filter(id=group.id).exists())

    # Test create currency
    def test_create_currency(self):
        # New currency object test data
        currency_data = {
            "name": "ABC",
            "exchange_rate": 1.0,
            "code": "ABC",  
            "symbol": "$"
        }
        # Post it to create currency request
        response = self.client.post(reverse('create_currency'), data=currency_data, format='json')
        # Ensure successful response 
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Test create category 
    def test_create_category(self):
        url = reverse('create_category')
        data = {'name': 'Test Category'}
        # Send new category post request to create_category 
        # Ensure successful response and that new category exists in category objects
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Category.objects.filter(name=data['name']).exists())

    # Test category detail 
    def test_category_detail(self):
        # Test category
        category = Category.objects.create(name='Test Category')
        url = reverse('category_detail', args=[category.category_id])
        # Test GET 
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Test PUT request
        updated_data = {'name': 'Updated Category Name'}
        response = self.client.put(url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Category.objects.get(category_id=category.category_id).name, updated_data['name'])
        # Test DELETE 
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(category_id=category.category_id).exists())

    # Test group admin details 
    def test_group_admin_detail(self):
        user = User.objects.create(username="test_user")
        group = Group.objects.create(name="Test Group")
        # Send group admin data to group_admin_detail
        url = reverse('group_admin_detail', args=[user.id, group.id])
        data = {
            "user": user.id,
            "group": group.id
        }
        response = self.client.post(url, data, format='json')
        # Ensure successful response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Test DELETE
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    # Test getting all currencies data
    def test_currencies(self):
        url = reverse('currencies')  
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        currencies = Currency.objects.all()
        serializer = CurrencySerializer(currencies, many=True)
        self.assertEqual(response.data, serializer.data)

    # Test getting all groups given user is a part of
    def test_user_groups(self):
        url = reverse('user_groups', args=[self.user.id]) 
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user_groups = Group.objects.filter(members=self.user)
        serializer = GroupSerializer(user_groups, many=True)
        self.assertEqual(response.data, serializer.data)

    # Test getting all members of a given group
    def test_groups_members(self):
        url = reverse('groups_members', args=[self.group.id])  
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        members = self.group.members.all()
        serializer = UserSerializer(members, many=True)
        self.assertEqual(response.data, serializer.data)

    # Test getting all transactions belonging to a given group
    def test_group_transactions(self):
        url = reverse('group_transactions', args=[self.group.id])  
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        transactions = Transaction.objects.filter(group=self.group)
        serializer = TransactionSerializer(transactions, many=True)
        self.assertEqual(response.data, serializer.data)

    # Test getting all tranasction belonging to a given user
    def test_user_transactions(self):
        url = reverse('user_transactions', args=[self.user.id])  
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        transactions = Transaction.objects.filter(user=self.user)
        serializer = TransactionSerializer(transactions, many=True)
        self.assertEqual(response.data, serializer.data)

    # Test getting all categories belonging to a given group
    def test_group_categories(self):
        url = reverse('group_categories', args=[self.group.id]) 
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        categories = self.group.categories.all()
        serializer = CategorySerializer(categories, many=True)
        self.assertEqual(response.data, serializer.data)



# TESTS FOR FORMS


class FormsTestCase(TestCase):
    def setUp(self):
        # Define test data for testing forms
        self.user = User.objects.create_user(username='testuser', password='testpass', email='test@example.com')
        self.currency = Currency.objects.create(code='USD', exchange_rate=1.0)
        self.category = Category.objects.create(name='Food')
        self.group = Group.objects.create(name='Test Group', token='testtoken')

    # Test custom regitration form against expected fields and dummy data
    def test_custom_registration_form(self):
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'newpassword123',
            'password2': 'newpassword123',
        }
        form = CustomRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())

    # Test transaction form against expected fields and dummy data
    def test_transaction_form(self):
        form_data = {
            'description': 'Groceries',
            'amount': 50.00,
            'currency': self.currency.currency_id,
            'date': '2023-09-20',
            'is_recurring': False,
            'category': self.category.category_id,
            'type': 'expense',
        }
        form = TransactionForm(data=form_data)
        self.assertTrue(form.is_valid())

    # Teste category form against expected fields and dummy data
    def test_category_form(self):
        form_data = {
            'name': 'Entertainment',
            'color': '#FF5733',
        }
        form = CategoryForm(data=form_data)
        self.assertTrue(form.is_valid())

    # Test transaction edit form data against expected fields and dummy data
    def test_transaction_edit_form(self):
        form_data = {
            'description': 'Updated Groceries',
            'amount': 60.00,
            'currency': self.currency.currency_id,
            'date': '2023-09-21T12:00', 
            'is_recurring': True,
            'category': self.category.category_id,
            'type': 'income',
        }
        form = TransactionEditForm(data=form_data)
        self.assertTrue(form.is_valid())


# FRONT END TESTS / TEMPLATE RENDERING

class TemplateRenderTestCase(TestCase):
    # 
    def setUp(self):
        # Test data for template rendering tests
        self.user = User.objects.create_user(username='testuser',password='testpassword')
        self.group = Group.objects.create(name='Test Group')
        self.group.members.add(self.user)
        self.currency = Currency.objects.create(code='USD', exchange_rate=1.0)
        self.client = Client()
        self.client.login(username='testuser', password='password')
        self.category = Category.objects.create(name='Test Category')
        self.group.categories.add(self.category)

    # Test login page render
    def test_login_view_template(self):
        response = self.client.get(reverse('login_view'))
        # Check expeceted template is being used to render page 
        self.assertTemplateUsed(response, 'login.html')

    # Test registration page render
    def test_registration_template(self):
        response = self.client.get(reverse('registration'))
        # Check expeceted template is being used to render page 
        self.assertTemplateUsed(response, 'registration.html')

    # Test group dashboard page render
    def test_group_dashboard_view(self):
        # Login user locally due to permission restrictions on group dashboard view
        self.client.login(username='testuser', password='testpassword')
        group_id = self.group.id
        response = self.client.get(reverse('group_dashboard', args=[group_id]))
        self.assertEqual(response.status_code, 200)

    # Test join group page render
    def test_join_group_template(self):
        response = self.client.get(reverse('join_group'))
        # Check expeceted template is being used to render page 
        self.assertTemplateUsed(response, 'join_group.html')

    # Test choose group page render
    def test_choose_group_template(self):
        # Login user locally due to permission restrictions on view
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('choose_group'))
        self.assertEqual(response.status_code, 200)
        # Check expeceted template is being used to render page 
        self.assertTemplateUsed(response, 'choose_group.html')

    # Test transactions page render
    def test_transactions_view_template(self):
        # Login user locally due to permission restrictions on view
        self.client.login(username='testuser', password='testpassword')
        # Test transaction
        transaction_date = date(2023, 9, 15)
        Transaction.objects.create(
            group=self.group,
            type='expense',
            amount=100,
            date=transaction_date,
            category=self.category,
            currency=self.currency,
            user=self.user 
        )
        # Get request for transactions page
        response = self.client.get(reverse('transactions', args=[self.group.id]))
        # Ensure successful response and that expected template was used
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'transactions.html')

    # Test reports page render
    def test_reports_view_template(self):
        # Login user locally due to permission restrictions on view
        self.client.login(username='testuser', password='testpassword')
        # Test transaction
        category = Category.objects.create(name='Test Category')
        currency = Currency.objects.create(name='Test Currency', code='TST')
        transaction_date = date(2023, 9, 15)
        Transaction.objects.create(
            group=self.group,
            type='expense',
            amount=100,
            date=transaction_date,
            category=category, 
            currency=currency, 
            user=self.user 
        )
        # Get request for reports page
        response = self.client.get(reverse('reports', args=[self.group.id]))
        # Ensure successful response and that expected template was used
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reports.html')