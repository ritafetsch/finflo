from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
import random
import string
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import Permission

# Currency model
class Currency(models.Model):
    currency_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=64)
    code = models.CharField(max_length=3, unique=True)  
    symbol = models.CharField(max_length=5)  
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=4, default=4)  

    def __str__(self):
        return self.name

# Category model
class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=64)
    color = models.CharField(max_length=7, default='#FFFFFF') 
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return self.name

# Group model
class Group(models.Model):
    name = models.CharField(max_length=256)
    token = models.CharField(max_length=12, unique=True, blank=True, null=True, default=None)
    members = models.ManyToManyField(User, related_name='custom_groups')
    admins = models.ManyToManyField(User, through='GroupAdmin', related_name='admin_groups')
    default_currency = models.ForeignKey(Currency, on_delete=models.CASCADE, default=1)
    categories = models.ManyToManyField(Category, related_name='groups', blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
        super().save(*args, **kwargs)

    # Generate unique token for new group
    def generate_unique_code(self):
        # Generate random code of length 12
        characters = string.ascii_letters + string.digits
        unique_code = ''.join(random.choice(characters) for _ in range(12))
        return unique_code
    
    # Initialize new group with default categories
    def initialize_default_categories(self):
        if not self.categories.exists():
            default_categories = Category.objects.filter(is_default=True)
            self.categories.set(default_categories)

    # Custom group permissions
    class Meta:
        permissions = [
            ("view_group_details", "Can view group details"),
        ]

# Transaction model
class Transaction(models.Model):
    # Define choices for transaction type
    TRANSACTION_TYPE_CHOICES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]
    # Define choices for recurrance optoins
    RECURRENCE_CHOICES = [
        ('once', 'One-time'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]
    
    transaction_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE,  null=False)
    amount = models.DecimalField(max_digits=10, decimal_places=2,  null=False)
    date = models.DateTimeField( null=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE,  null=False)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE,  null=False)
    group = models.ForeignKey(Group, on_delete=models.CASCADE,  null=False) 
    description = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES,  default='expense',  null=False)
    is_recurring = models.BooleanField(default=False,  null=False)
    recurrence_pattern = models.CharField(max_length=20, default='once', choices=RECURRENCE_CHOICES)

    def __str__(self):
        return f"Transaction {self.transaction_id} - {self.amount} {self.currency}" 
    
# UserProfile model
class UserProfile(models.Model):
   
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    groups = models.ManyToManyField(Group, related_name='user_profiles')
    default_group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=False, related_name='default_users', verbose_name=_('Default Group'))

    def __str__(self):
        return self.user.username
    
    # Get user's groups
    def get_user_groups(self):
        return self.groups.all()
# Conjoin user profile updates with User model
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        instance.userprofile.save()

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()

# If user profile is deleted, delete User as well
@receiver(post_delete, sender=User)
def delete_user_profile(sender, instance, **kwargs):
    try:
        instance.userprofile.delete()
    except UserProfile.DoesNotExist:
        pass

# Model for joining users and groups
class GroupAdmin(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    class Meta:
        unique_together = ('user', 'group')

# Group permissions model
class GroupPermission(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    class Meta:
        unique_together = ('group', 'permission')















