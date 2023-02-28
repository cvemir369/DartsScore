from django.contrib import admin
from django.urls import path, include

# Static files serve
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView

# Allauth custom urls
from allauth.utils import importlib
from allauth.account.views import login, logout, signup
from allauth.socialaccount import providers

providers_urlpatterns = []

for provider in providers.registry.get_list():
    prov_mod = importlib.import_module(provider.get_package() + '.urls')
    providers_urlpatterns += getattr(prov_mod, 'urlpatterns', [])


urlpatterns = [
    path(
        "favicon.ico",
        RedirectView.as_view(url=staticfiles_storage.url("images/favicon.ico")),
    ),
    path('admin/', admin.site.urls),
    path('accounts/', include('user.urls')),
    path('accounts/signup/', signup, name="account_signup"),
    path('accounts/login/', login, name="account_login"),
    path('accounts/logout/', logout, name="account_logout"),
    path('accounts/', include(providers_urlpatterns)),
    # path('user/', include('django.contrib.auth.urls')),
    # path('accounts/', include('allauth.urls')),
    path('', include('darts.urls')), # disable this line for initial makemigrations
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

'''
Note that you do not necessarily need the URLs provided by django.contrib.auth.urls.
Instead of the URLs login, logout, and password_change (among others),
you can use the URLs provided by allauth: account_login, account_logout, account_set_password…
'''