import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from django.core.validators import URLValidator


class CustomURLValidator(URLValidator):
    def __call__(self, value):
        # Check if the URL starts with a scheme (http://, https://)
        if not re.match(r"^(http://|https://)", value):
            # If not, prepend http:// to validate it
            value = "http://" + value
        super().__call__(value)


class StrongPasswordValidator:
    def validate(self, password, user=None):
        if len(password) < 8:
            raise ValidationError(_("Password must be at least 8 characters long."), code='password_too_short')

        if not any(char.isdigit() for char in password):
            raise ValidationError(_("Password must contain at least one digit."), code='password_no_digit')

        if not any(char.isupper() for char in password):
            raise ValidationError(_("Password must contain at least one uppercase letter."), code='password_no_upper')

        if not any(char.islower() for char in password):
            raise ValidationError(_("Password must contain at least one lowercase letter."), code='password_no_lower')

        if not any(char in "!@#$%^&*()-_=+[]{};:'\",.<>?/`~" for char in password):
            raise ValidationError(_("Password must contain at least one special character."), code='password_no_special')

    def get_help_text(self):
        return _(
            "Your password must be at least 8 characters long, contain at least one digit, "
            "one uppercase letter, one lowercase letter, and one special character."
        )