# import jwt
# from django.conf import settings
# from django.contrib.auth import get_user_model
# from rest_framework.authentication import BaseAuthentication
# from rest_framework.exceptions import AuthenticationFailed
# from rest_framework_simplejwt.tokens import AccessToken
#
#
# User = get_user_model()
#
# class CustomJWTAuthentication(BaseAuthentication):
#     """
#     Custom authentication that extracts account_id and organization_id from JWT.
#     Sets request.user with these attributes dynamically.
#     """
#
#     def authenticate(self, request):
#         auth_header = request.headers.get("Authorization")
#
#         if not auth_header or not auth_header.startswith("Bearer "):
#             return None  # No authentication attempt
#
#         token = auth_header.split(" ")[1]  # Extract JWT
#
#         try:
#             decoded_token = AccessToken(token)  # Decode using DRF SimpleJWT
#             organization_id = decoded_token.get("organization_id")
#             user_id = decoded_token.get("user_id")  # Extract user ID from token
#
#             if not organization_id or not user_id:
#                 raise AuthenticationFailed("Invalid token: missing account_id or user_id.")
#
#             # Fetch user
#             user = User.objects.filter(id=user_id).first()
#             if not user:
#                 raise AuthenticationFailed("User not found.")
#
#             # Fetch organization_id from OrganizationUser mapper table
#             organization_user = OrganizationUser.objects.filter(user=user).first()
#             organization_id = organization_user.organization.id if organization_user else None
#
#             # Attach account_id & organization_id to user dynamically
#             user.organization_id = organization_id
#
#             return (user, token)  # DRF sets request.user and request.auth
#
#         except jwt.ExpiredSignatureError:
#             raise AuthenticationFailed("Token has expired.")
#         except jwt.DecodeError:
#             raise AuthenticationFailed("Invalid token.")
#         except Exception as e:
#             raise AuthenticationFailed(f"Authentication error: {str(e)}")
