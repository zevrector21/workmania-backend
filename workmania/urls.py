from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from django.conf.urls.static import static
from django.utils.safestring import mark_safe
from rest_framework_extensions.routers import (
    ExtendedDefaultRouter
)
from rest_framework import permissions
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView
)
from django.contrib.auth import views as auth_views
from core.api import account_views
from core.api import views as api_views
from core import views as core_views
from allauth.account.views import AccountInactiveView


router = ExtendedDefaultRouter()
app_routes = router.register(
    r'users',
    account_views.UserViewSet,
    basename='users'
)
job_postings_routes = router.register(
    r'job_postings',
    api_views.JobPostingViewSet,
    basename='job_postings'
)
job_postings_routes.register(
    r'job_applications',
    api_views.JobApplicationViewSet,
    basename='job_applications',
    parents_query_lookups=['job_posting__id']
)
job_postings_routes.register(
    r'job_invitations',
    api_views.JobInvitationViewSet,
    basename='job_invitations',
    parents_query_lookups=['job_posting__id']
)
router.register(
    r'resources',
    api_views.ResourceViewSet,
    basename='resources'
)

urlpatterns = [
    url(r'^$', core_views.goto_app, name='admin'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Optional UI:
    path(
        'swagger/',
        SpectacularSwaggerView.as_view(url_name='schema'),
        name='swagger-ui'
    ),
    path(
        'redoc/',
        SpectacularRedocView.as_view(url_name='schema'),
        name='redoc'
    ),
    path('api/v1/', include(router.urls)),
    # Support both with and without trailing slash (avoid APPEND_SLASH redirect)
    path('admin/', admin.site.urls),
    path('rest-auth/', include('dj_rest_auth.urls')),
    path('accounts/inactive/', AccountInactiveView.as_view(), name='account_inactive'),
    path(
        'rest-auth/signup/',
        account_views.CustomRegisterView.as_view(),
        name='user_signup'
    ),
    path(
        'rest-auth/password/validate-code/',
        account_views.ValidateCode.as_view(),
        name='validate_code'
    ),
    path(
        'rest-auth/password/new/',
        account_views.ResetPassword.as_view(),
        name='reset_password'
    ),
    # path(
    #     'rest-auth/password/reset-request/',
    #     account_views.ResetPasswordRequest.as_view(),
    #     name='reset_password_request'
    # ),
    # url(
    #     r'^rest-auth/email-verification/(?P<key>[-:\w]+)/$',
    #     account_views.EmailVerification.as_view(),
    #     name='account_confirm_email'
    # ),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Admin Site Config
admin.sites.AdminSite.site_header = 'Workmania Administration'
admin.sites.AdminSite.site_title = 'Workmania Administration'
admin.sites.AdminSite.index_title = 'Workmania Administration'
admin.site.site_header = mark_safe(
    '<img src="{img}" style="margin-right: 8px" alt=""/> {alt}'.format(
        img=settings.STATIC_URL + 'favicon.ico',
        alt=admin.site.site_title,
    )
)
