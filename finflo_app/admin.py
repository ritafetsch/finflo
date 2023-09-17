from django.contrib import admin
from .models import *

# Admin class for GroupPermission model
class GroupPermissionInline(admin.TabularInline):
    model = GroupPermission

# Define and configure Group model for admin interface 
class GroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'token', 'list_members', 'list_admins','default_currency', 'list_categories')
    filter_horizontal = ('members','categories')

    # Get group members to display as list
    def list_members(self, obj):
        return ', '.join([user.username for user in obj.members.all()])
    list_members.short_description = 'Members'

    # Get group admins to display as list
    def list_admins(self, obj):
        return ', '.join([user.username for user in obj.admins.all()])
    list_admins.short_description = 'Admins'

    # Get groups's categories to display as list
    def list_categories(self, obj):
        return ', '.join([category.name for category in obj.categories.all()])
    list_categories.short_description = 'Categories'

    class Meta:
        permissions = [
            ("view_group_dashboard", "Can view group dashboard"),
        ]

# Define and configure User Profile model for admin interface 
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'get_groups', 'default_group', 'id')
    readonly_fields = ('first_name', 'last_name', 'get_groups')

    fieldsets = (
    ('User Information', {
        'fields': ('user', 'first_name', 'last_name', 'get_groups')
    }),
    ('Group Information', {
        'fields': ('groups', 'default_group')
    }),
    )

    # Get first name, last name, and groups via User model
    def first_name(self, obj):
        return obj.user.first_name
    first_name.short_description = 'First Name'

    def last_name(self, obj):
        return obj.user.last_name
    last_name.short_description = 'Last Name'

    def get_groups(self, obj):
        groups = Group.objects.filter(members=obj.user)
        return ', '.join([group.name for group in groups])

# Define and configure Category model for admin interface 
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_id', 'name', 'color', 'is_default')
    list_filter = ('is_default',)
    search_fields = ('name',)

# Define and configure Currency model for admin interface 
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('currency_id', 'name', 'code', 'symbol', 'exchange_rate')

# Define and configure Transaction model for admin interface 
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'description', 'user', 'amount', 'date', 'category', 'currency', 'group', 'type', 'is_recurring')
    list_filter = ('user', 'category', 'currency', 'group', 'type', 'is_recurring')
    search_fields = ('transaction_id', 'user__username', 'category__name', 'currency__name', 'group__name', 'type')

# Register the models as defined above to the admin interface
admin.site.register(Group, GroupAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Currency, CurrencyAdmin)
admin.site.register(Category, CategoryAdmin)