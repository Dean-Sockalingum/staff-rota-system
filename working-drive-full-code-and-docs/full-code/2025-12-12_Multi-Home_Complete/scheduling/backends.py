from django.contrib.auth.backends import ModelBackend
from .models import User


class SAPAuthenticationBackend(ModelBackend):
    """
    Custom authentication backend that uses SAP number as username.
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate using SAP number as username.
        """
        if username is None or password is None:
            return None
        
        try:
            # Look up user by SAP number
            user = User.objects.get(sap=username)
            
            # Check password
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            # Run the default password hasher once to reduce timing
            # difference between existing and non-existing users
            User().set_password(password)
        
        return None
    
    def get_user(self, user_id):
        """
        Get user by primary key.
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
