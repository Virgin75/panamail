"""panamail URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include(('users.urls', 'users'), namespace='users')),
    path('contacts/', include(('contacts.urls', 'contacts'), namespace='contacts')),
    path('emails/', include(('emails.urls', 'emails'), namespace='emails')),
    path('campaigns/', include(('campaigns.urls', 'campaigns'), namespace='campaigns')),
    path('api/', include(('trackerapi.urls', 'trackerapi'), namespace='trackerapi')),
]
