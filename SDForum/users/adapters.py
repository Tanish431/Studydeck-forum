from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.exceptions import ImmediateHttpResponse
from django.shortcuts import render

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        email = sociallogin.user.email

        if not email or not email.endswith("@pilani.bits-pilani.ac.in"):
            raise ImmediateHttpResponse(
                render(
                    request,
                    "account/access_denied.html",
                    status=403,
                )
            )