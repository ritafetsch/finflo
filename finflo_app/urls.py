from django.urls import path
from . import views
from . import api
from django.conf import settings
from django.conf.urls.static import static

# ALL URLS FOR APP
urlpatterns = [
    # Page urls
    path('', views.login_view, name='login_view'),
    path('accounts/login/', views.login_view, name='login_view'),
    path('landing/', views.landing_page, name='landing_page'),
    path('registration/', views.registration, name='registration'),
    path('group_dashboard/<int:group_id>/', views.group_dashboard, name='group_dashboard'),
    path('settings/<int:group_id>/', views.settings, name='settings'),
    path('join_group/', views.join_group, name='join_group'),
    path('choose_group/', views.choose_group, name='choose_group'),
    path('manage_categories/<int:group_id>/', views.manage_categories, name='manage_categories'),
    path('groups/<int:group_id>/', views.groups, name='groups'),
    path('group/<int:group_id>/transactions/', views.transactions_view, name='transactions'),
    path('group/<int:group_id>/reports/', views.reports_view, name='reports'),
    path('health-check/', views.health_check, name='health_check'),
    # Action urls
    path('logout/', views.custom_logout, name='logout'),  
    path('register_user/', views.register_user, name='register_user'),
    # Group actions 
    path('create_group/', views.create_group, name='create_group'), 
    path('join_group_ajax/', views.join_group_ajax, name='join_group_ajax'),  
    path('delete_group/<int:group_id>/', views.delete_group, name='delete_group'),
    # Settings page actions
    path('select_default_group/<int:group_id>/', views.select_default_group, name='select_default_group'),
    path('update_user_profile/', views.update_user_profile, name='update_user_profile'),
    path('update_group_settings/', views.update_group_settings, name='update_group_settings'),
    path('update_currency_settings/', views.update_currency_settings, name='update_currency_settings'),
    path('update_password/', views.update_password, name='update_password'),
    # Category management actions
    path('get_categories/<int:group_id>/', views.get_categories, name='get_categories'),
    path('add/<int:group_id>/', views.add_category, name='add_category'),
    path('delete/<int:group_id>/<int:category_id>/', views.delete_category, name='delete_category'),
    # Transaction management options
    path('add_transaction/', views.add_transaction, name='add_transaction'),
    path('get_transaction_details/', views.get_transaction_details, name='get_transaction_details'),
    path('update_transaction/<int:group_id>/<int:transaction_id>/', views.update_transaction, name='update_transaction'),
    path('delete_transaction/<int:transaction_id>/', views.delete_transaction, name='delete_transaction'),
    # Reports page urls
    path('1_monthly_expense_trends/<int:group_id>/', views.monthly_expense_trends_view, name='1_monthly_expense_trends'),
    path('2_category_expense_trends/<int:group_id>/', views.category_expense_trends_view, name='2_category_expense_trends'),
    path('3_balance_over_time/<int:group_id>/', views.balance_over_time_view, name='3_balance_over_time'),
    path('4_expense_distribution_group/<int:group_id>/', views.expense_distribution_group_view, name='4_expense_distribution_group'),
    path('5_income_distribution_group/<int:group_id>/', views.income_distribution_group_view, name='5_income_distribution_group'),
    path('6_expense_distribution_day/<int:group_id>/', views.expense_distribution_day_view, name='6_expense_distribution_day'),
    path('7_highest_spending_category/<int:group_id>/', views.highest_spending_category_view, name='7_highest_spending_category'),
    path('8_income_expense_time/<int:group_id>/', views.income_expense_time_view, name='8_income_expense_time'),
    path('9_category_wise_monthly/<int:group_id>/', views.category_wise_monthly_view, name='9_category_wise_monthly'),
    # Urls for fetching report dummy data
    path('get_1_monthly_expense_data/<int:group_id>/<int:year>/', views.get_1_monthly_expense_data, name='get_1_monthly_expense_data'),
    path('get_2_monthly_category_expense_trends_data/<int:group_id>/<int:year>/<int:month>/', views.get_2_monthly_category_expense_trends_data, name='get_2_monthly_category_expense_trends_data'),
    path('get_3_balance_over_time_data/<int:group_id>/<int:year>/', views.get_3_balance_over_time_data, name='get_3_balance_over_time_data'),
    path('get_4_expense_distribution_group_data/<int:group_id>/<int:year>/<int:month>/', views.get_4_expense_distribution_group_data, name='get_4_expense_distribution_group_data'),
    path('get_5_income_distribution_group_data/<int:group_id>/<int:year>/<int:month>/', views.get_5_income_distribution_group_data, name='get_5_income_distribution_group_data'),
    path('get_6_expense_distribution_day_data/<int:group_id>/<int:year>/', views.get_6_expense_distribution_day_data, name='get_6_expense_distribution_day_data'),
    path('get_7_highest_spending_category_data/<int:group_id>/<int:year>', views.get_7_highest_spending_category_data, name='get_7_highest_spending_category_data'),
    path('get_8_income_vs_expense_over_time_data/<int:group_id>/', views.get_8_income_vs_expense_over_time_data, name='get_8_income_vs_expense_over_time_data'),
    path('get_9_category_wise_monthly_comparison_data/<int:group_id>/<int:year>/', views.get_9_category_wise_monthly_comparison_data, name='get_9_category_wise_monthly_comparison_data'),
    
    # Urls for REST API 

    # User endpoints
    path('api/users/', api.user_create, name='user_create'),
    path('api/users/<int:user_id>/', api.user_detail, name='user_detail'),
    path('api/users/<int:user_id>/profile/', api.user_profile_detail,  name='user_profile_detail'),
    # Group endpoints
    path('api/groups/', api.group_create, name='group_create'),
    path('api/groups/<int:group_id>/', api.group_detail, name='group_detail'),
    # Currency endpoints
    path('api/currencies/', api.create_currency, name='create_currency'),
    path('api/currencies/<int:currency_id>/', views.currency_detail, name='currency_detail'),
    # Category endpoints
    path('api/categories/', api.create_category, name='create_category'),
    path('api/categories/<int:category_id>/', views.category_detail, name='category_detail'),
    # Transaction endpoints
    path('api/transactions/', api.create_transaction, name='create_transaction'),
    path('api/transactions/<int:transaction_id>/', api.transaction_detail, name='transaction_detail'),
    # Group permission endpoints
    path('api/groups/<int:group_id>/permissions/<int:permission_id>/', api.group_permission_detail, name='group_permission_detail'),
    # Group admin endpoints
    path('api/users/<int:user_id>/groups/<int:group_id>/admin/', api.group_admin_detail, name='group_admin_detail'),

    # Additional data fetching endpoints 
    path('api/all_currencies/', api.currencies, name='currencies'),
    path('api/users/<int:user_id>/groups/', api.user_groups,  name='user_groups'),
    path('api/users/<int:user_id>/transactions/', api.user_transactions,  name='user_transactions'),
    path('api/groups/<int:group_id>/members/', api.groups_members,  name='groups_members'),
    path('api/groups/<int:group_id>/transactions/', api.group_transactions,  name='group_transactions'),
    path('api/groups/<int:group_id>/categories/', api.group_categories,  name='group_categories'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)