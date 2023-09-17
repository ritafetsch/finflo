from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import *
from django.utils.translation import gettext as _

# Form for registering user
class CustomRegistrationForm(UserCreationForm):
    email = forms.EmailField(max_length=254, required=True, help_text='Required. Enter a valid email address.')
    first_name = forms.CharField(max_length=30, required=True, help_text='Required. Enter your first name.')
    last_name = forms.CharField(max_length=30, required=True, help_text='Required. Enter your last name.')

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = 'Required. 150 characters or fewer. Letters, digits, and @/./+/-/_ only.'
        self.fields['password1'].help_text = 'Your password must contain at least 8 characters, including both letters and numbers.'

# Form for adding transaction
class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['description', 'amount', 'currency', 'date', 'is_recurring', 'category', 'type']

# Form for adding new category
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'color'] 

# Form for editting transaction
class TransactionEditForm(forms.ModelForm):
    date = forms.DateTimeField(
        widget=forms.TextInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M'] 
    )

    class Meta:
        model = Transaction
        fields = ['description', 'amount', 'currency', 'date', 'is_recurring', 'category', 'type']

# Form for adding user profile information
class UserProfileSettingsForm(forms.ModelForm):
    first_name = forms.CharField(
        label=_('First Name'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    last_name = forms.CharField(
        label=_('Last Name'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    username = forms.CharField(
        label=_('Username'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    default_group = forms.ModelChoiceField(
        queryset=Group.objects.none(),
        required=False,
        label=_('Default Group'),
        to_field_name='id',
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = UserProfile
        fields = []

    def __init__(self, user, user_groups, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.user = user
        self.user_groups = user_groups

        # Populate queryset for default_group field with user's groups
        self.fields['default_group'].queryset = user_groups





    





