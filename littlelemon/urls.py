"""
URL configuration for littlelemon project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.shortcuts import redirect
from rest_framework.authtoken.views import obtain_auth_token
from django.conf import settings
from reservation import views

urlpatterns = [
    # Admin panel
    path('admin/', admin.site.urls),

    # Reservation app URLs
    path('reservation/', include('reservation.urls')),

    # Redirect root to reservation
    path('', lambda request: redirect('reservation/', permanent=False)),

    # Token-based authentication (DRF)
    path('api-token-auth/', obtain_auth_token),

    # User authentication URLs (login, logout, password reset, etc.)
    path('accounts/', include('django.contrib.auth.urls')),

    # Signup view for new user registration
    path('accounts/signup/', views.signup_view, name='signup'),
]

# Add Debug Toolbar when in DEBUG mode
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
