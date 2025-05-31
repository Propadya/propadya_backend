# from django.utils.translation import gettext_lazy as _
# from drf_spectacular.extensions import OpenApiAuthenticationExtension
# from rest_framework.exceptions import AuthenticationFailed
# from rest_framework_simplejwt.authentication import JWTAuthentication
# from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
# from rest_framework_simplejwt.tokens import AuthUser, Token
# from rest_framework_simplejwt.utils import get_md5_hash_password
#
# from rest_framework_simplejwt.settings import api_settings
#
#
# class CustomJWTAuthentication(JWTAuthentication):
#     """
#     Custom authentication that extracts account_id and organization_id from JWT.
#     Sets request.user with these attributes dynamically.
#     """
#
#     def get_validated_token(self, raw_token: bytes) -> Token:
#         """
#         Validates an encoded JSON web token and returns a validated token
#         wrapper object.
#         """
#         last_exception = None
#         for AuthToken in api_settings.AUTH_TOKEN_CLASSES:
#             try:
#                 return AuthToken(raw_token)
#             except TokenError as e:
#                 last_exception = e  # Save the last error to raise later
#
#         # If no token class matched, raise the final error
#         raise AuthenticationFailed(
#             detail="Given token is invalid or expired.",
#             code="token_not_valid",
#         )
#
#     def get_user(self, validated_token: Token) -> AuthUser:
#         """
#         Attempts to find and return a user using the given validated token.
#         """
#         try:
#             user_id = validated_token[api_settings.USER_ID_CLAIM]
#         except KeyError:
#             raise InvalidToken(_("Token contained no recognizable user identification"))
#
#         try:
#             user = self.user_model.objects.get(**{api_settings.USER_ID_FIELD: user_id})
#         except self.user_model.DoesNotExist:
#             raise AuthenticationFailed(_("User not found"), code="user_not_found")
#
#         if not user.is_active:
#             raise AuthenticationFailed(_("User is inactive"), code="user_inactive")
#
#         if api_settings.CHECK_REVOKE_TOKEN:
#             if validated_token.get(
#                     api_settings.REVOKE_TOKEN_CLAIM
#             ) != get_md5_hash_password(user.password):
#                 raise AuthenticationFailed(
#                     _("The user's password has been changed."), code="password_changed"
#                 )
#         org_id = validated_token.get("org_id")
#         user = self.set_organization(user, org_id)
#
#         return user
#
#     def set_organization(self, user, org_id):
#         # Attach account_id & organization_id to user dynamically
#         user.org_id = org_id
#         if org_id:
#             org_user = OrganizationUser.objects.filter(user=user, organization_id=org_id).first()
#             user.org = org_user.organization or None
#             user.org_user = org_user
#         else:
#             user.org = None
#             user.org_user = None
#         return user
#
#
# class CustomJWTAuthenticationScheme(OpenApiAuthenticationExtension):
#     target_class = "base.authentication.CustomJWTAuthentication"
#     name = "CustomJWTAuth"
#
#     def get_security_definition(self, auto_schema):
#         return {
#             "type": "http",
#             "scheme": "bearer",
#             "bearerFormat": "JWT",
#         }