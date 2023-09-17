
from django.http import HttpResponseForbidden

# Define custom middleware for group token ensuring user globally that user is autenticated 
class GroupTokenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        # Check if user is authenticated and has the correct group token
        if request.user.is_authenticated:
            desired_group_token = request.session.get('desired_group_token', None)
            if desired_group_token and not request.user.groups.filter(token=desired_group_token).exists():
                return HttpResponseForbidden() 
        return response
