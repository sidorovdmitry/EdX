# Create your views here.
from django.shortcuts import render_to_response, redirect
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods

from third_party_auth.decorators import xframe_allow_whitelisted

from student.helpers import get_next_url_for_login_page


# @require_http_methods(['GET'])
# @ensure_csrf_cookie
# @xframe_allow_whitelisted
# def login_and_registration_form(request, initial_mode="login"):
#     """Render the combined login/registration form, defaulting to login
#
#     This relies on the JS to asynchronously load the actual form from
#     the user_api.
#
#     Keyword Args:
#         initial_mode (string): Either "login" or "register".
#
#     """
#     # Determine the URL to redirect to following login/registration/third_party_auth
#     redirect_to = get_next_url_for_login_page(request)
#
#     # If we're already logged in, redirect to the dashboard
#     if request.user.is_authenticated():
#         return redirect(redirect_to)
#
#     # Retrieve the form descriptions from the user API
#     form_descriptions = _get_form_descriptions(request)
#
#     # If this is a microsite, revert to the old login/registration pages.
#     # We need to do this for now to support existing themes.
#     # Microsites can use the new logistration page by setting
#     # 'ENABLE_COMBINED_LOGIN_REGISTRATION' in their microsites configuration file.
#     if microsite.is_request_in_microsite() and not microsite.get_value('ENABLE_COMBINED_LOGIN_REGISTRATION', False):
#         if initial_mode == "login":
#             return old_login_view(request)
#         elif initial_mode == "register":
#             return old_register_view(request)
#
#     # Allow external auth to intercept and handle the request
#     ext_auth_response = _external_auth_intercept(request, initial_mode)
#     if ext_auth_response is not None:
#         return ext_auth_response
#
#     # Our ?next= URL may itself contain a parameter 'tpa_hint=x' that we need to check.
#     # If present, we display a login page focused on third-party auth with that provider.
#     third_party_auth_hint = None
#     if '?' in redirect_to:
#         try:
#             next_args = urlparse.parse_qs(urlparse.urlparse(redirect_to).query)
#             provider_id = next_args['tpa_hint'][0]
#             if third_party_auth.provider.Registry.get(provider_id=provider_id):
#                 third_party_auth_hint = provider_id
#                 initial_mode = "hinted_login"
#         except (KeyError, ValueError, IndexError):
#             pass
#
#     # Otherwise, render the combined login/registration page
#     context = {
#         'data': {
#             'login_redirect_url': redirect_to,
#             'initial_mode': initial_mode,
#             'third_party_auth': _third_party_auth_context(request, redirect_to),
#             'third_party_auth_hint': third_party_auth_hint or '',
#             'platform_name': settings.PLATFORM_NAME,
#
#             # Include form descriptions retrieved from the user API.
#             # We could have the JS client make these requests directly,
#             # but we include them in the initial page load to avoid
#             # the additional round-trip to the server.
#             'login_form_desc': json.loads(form_descriptions['login']),
#             'registration_form_desc': json.loads(form_descriptions['registration']),
#             'password_reset_form_desc': json.loads(form_descriptions['password_reset']),
#         },
#         'login_redirect_url': redirect_to,  # This gets added to the query string of the "Sign In" button in header
#         'responsive': True,
#         'allow_iframing': True,
#         'disable_courseware_js': True,
#     }
#
#     return render_to_response(''student/labster/login_and_register.html'', context)
#
#
# @require_http_methods(['GET'])
# def login(request):
#     username = request.POST['username']
#     password = request.POST['password']
#
