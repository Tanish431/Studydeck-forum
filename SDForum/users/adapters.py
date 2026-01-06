from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.core.exceptions import PermissionDenied

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        email = sociallogin.user.email

        if not email or not email.endswith("f@pilani.bits-pilani.ac.in"):
            raise PermissionDenied("Access restricted to BITS Pilani email accounts.")