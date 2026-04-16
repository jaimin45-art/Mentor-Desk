from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q
from academics.models import StudentProfile

User = get_user_model()

class EnrollmentNumberBackend(ModelBackend):
    """
    Authenticates against settings.AUTH_USER_MODEL.
    Recognizes:
    1. Username
    2. Email
    3. Enrollment Number (StudentProfile.roll_number)
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)
        
        try:
            # Try to fetch the user by username, email, or enrollment number
            user = User.objects.get(
                Q(username=username) | 
                Q(email=username) | 
                Q(student_profile__roll_number=username)
            )
        except User.DoesNotExist:
            return None
        except User.MultipleObjectsReturned:
            # This shouldn't happen with unique constraints, but good to handle
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
