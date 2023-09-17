from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *
from django.shortcuts import get_object_or_404

# USER ENDPOINTS 

# Create user endpoint - Define POST method 
@api_view(['POST'])
def user_create(request):
    if request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
# User detail endpoint - Define GET, PUT, and DELETE methods
@api_view(['GET', 'PUT', 'DELETE'])
def user_detail(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
        if request.method == 'GET':
            serializer = UserSerializer(user)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = UserSerializer(user, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

# User profile detail endpoint - Define GET and PUT methods
@api_view(['GET', 'PUT'])
def user_profile_detail(request, user_id):
    try:
        user_profile = UserProfile.objects.get(user_id=user_id)
        if request.method == 'GET':
            serializer = UserProfileSerializer(user_profile)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = UserProfileSerializer(user_profile, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except UserProfile.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)




# GROUP ENDPOINTS

# Create group endpoint - Define POST method 
@api_view(['POST'])
def group_create(request):
    if request.method == 'POST':
        serializer = GroupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Group detail endpoint - Define GET, PUT, and DELETE methods
@api_view(['GET', 'PUT', 'DELETE'])
def group_detail(request, group_id):
    try:
        group = Group.objects.get(pk=group_id)
        if request.method == 'GET':
            serializer = GroupSerializer(group)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = GroupSerializer(group, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            group.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
    except Group.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)




# CURRENCY ENPOINTS

# Create currency endpoint - Define POST method 
@api_view(['POST'])
def create_currency(request):
    if request.method == 'POST':
        serializer = CurrencySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# Currency detail endpoint - Define GET, PUT, and DELETE methods
@api_view(['GET', 'PUT', 'DELETE'])
def currency_detail(request, currency_id):
    try:
        currency = Currency.objects.get(pk=currency_id)
        if request.method == 'GET':
            serializer = CurrencySerializer(currency)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = CurrencySerializer(currency, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            currency.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
    except Currency.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)





# CATEGORY ENPOINTS

# Create category endpoint - Define POST method 
@api_view(['POST'])
def create_category(request):
    if request.method == 'POST':
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Category detail endpoint - Define GET, PUT, and DELETE methods
@api_view(['GET', 'PUT', 'DELETE'])
def category_detail(request, category_id):
    try:
        category = Category.objects.get(pk=category_id)
        if request.method == 'GET':
            serializer = CategorySerializer(category)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = CategorySerializer(category, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            category.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
    except Category.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)





# TRANSACTION ENDPOINTS

# Create transaction endpoint - Define POST method 
@api_view(['POST'])
def create_transaction(request):
    if request.method == 'POST':
        serializer = TransactionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Transaction detail endpoint - Define GET, PUT, and DELETE methods
@api_view(['GET', 'PUT', 'DELETE'])
def transaction_detail(request, transaction_id):
    try:
        transaction = Transaction.objects.get(pk=transaction_id)
        if request.method == 'GET':
            serializer = TransactionSerializer(transaction)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = TransactionSerializer(transaction, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            transaction.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
    except Transaction.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)





# GROUP PERMISSION AND ADMIN ENDPOINTS

# Group Permission Endpoints - Define POST and DELETE methods
@api_view(['POST', 'DELETE'])
def group_permission_detail(request, group_id, permission_id):
    if request.method == 'POST':
        serializer = GroupPermissionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        try:
            group_permission = GroupPermission.objects.get(group=group_id, permission=permission_id)
            group_permission.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except GroupPermission.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


# Group admin enpoints - Define POST and DELETE methods
@api_view(['POST', 'DELETE'])
def group_admin_detail(request, user_id, group_id):
    if request.method == 'POST':
        serializer = GroupAdminSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        try:
            group_admin = GroupAdmin.objects.get(user=user_id, group=group_id)
            group_admin.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except GroupAdmin.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        




# FURTHER DATA FETCHING ENPOINTS

# Get all currencies
@api_view(['GET'])
def currencies(request):
    currencies = Currency.objects.all()
    serializer = CurrencySerializer(currencies, many=True)
    return Response(serializer.data)

# Get all groups user is a member of 
@api_view(['GET'])
def user_groups(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    user_groups = Group.objects.filter(members=user)
    serializer = GroupSerializer(user_groups, many=True)
    return Response(serializer.data)

# Get all group members of given group
@api_view(['GET'])
def groups_members(request, group_id):
    group = Group.objects.get(pk=group_id)
    members = group.members.all()
    serializer = UserSerializer(members, many=True)
    return Response(serializer.data)

# Get all transactions of given group
@api_view(['GET'])
def group_transactions(request, group_id):
    transactions = Transaction.objects.filter(group_id=group_id)
    serializer = TransactionSerializer(transactions, many=True)
    return Response(serializer.data)

# Get all transactions associated with given user
@api_view(['GET'])
def user_transactions(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    transactions = Transaction.objects.filter(user=user)
    serializer = TransactionSerializer(transactions, many=True)
    return Response(serializer.data)

# Get all categories of given group
@api_view(['GET'])
def group_categories(request, group_id):
    group = Group.objects.get(pk=group_id)
    categories = group.categories.all()
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)