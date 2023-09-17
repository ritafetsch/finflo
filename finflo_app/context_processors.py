from django.conf import settings
from .models import Group

# Context processor to determine if a user is authenticated based on whether or not they have group token
def desired_group_token(request):
    if request.user.is_authenticated:
        group_id = request.resolver_match.kwargs.get('group_id')
        if group_id:
            group = Group.objects.filter(id=group_id, members=request.user).first()
            if group:
                return {'DESIRED_GROUP_TOKEN': group.token}
    return {'DESIRED_GROUP_TOKEN': None}