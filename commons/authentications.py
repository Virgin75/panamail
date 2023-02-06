from rest_framework import authentication
from rest_framework import exceptions

from trackerapi.models import TrackerAPIKey


class TrackerAPIAuthenticator(authentication.BaseAuthentication):
    """
    Custom authentication backend used for the Tracker API.

    Allows users to authenticate using an API key generated with /api/api_keys.
    """

    def authenticate(self, request):
        api_token = request.headers.get('Authorization')
        try:
            token_obj = TrackerAPIKey.objects.get(token=api_token)
            user = token_obj.owner
            if user:
                return user
            else:
                raise exceptions.AuthenticationFailed('Invalid token or Authorization headers.')
        except Exception:
            raise exceptions.AuthenticationFailed('Invalid token or Authorization headers.')
