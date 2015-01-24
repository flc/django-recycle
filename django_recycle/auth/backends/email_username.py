from django.core import validators
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model


class EmailOrUsernameModelBackend(ModelBackend):

    def authenticate(self, identification, password=None, check_password=True):
        User = get_user_model()
        try:
            validators.validate_email(identification)
            try:
                user = User.objects.get(email__iexact=identification)
                if user.check_password(password):
                    return user
            except User.DoesNotExist:
                # Run the default password hasher once to reduce the timing
                # difference between an existing and a non-existing user (#20760).
                User.set_password(password)
                return None
        except validators.ValidationError:
            return super(EmailOrUsernameModelBackend, self).authenticate(
                username=identification, password=password
                )
