from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('user.urls')),
    # path('user/', include('django.contrib.auth.urls')),
    path('accounts/', include('allauth.urls')),
    path('', include('darts.urls')),
]

'''
Note that you do not necessarily need the URLs provided by django.contrib.auth.urls.
Instead of the URLs login, logout, and password_change (among others),
you can use the URLs provided by allauth: account_login, account_logout, account_set_password…
'''