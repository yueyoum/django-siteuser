from django.conf import settings

from siteuser.users.urls import urlpatterns
from siteuser.upload_avatar.urls import urlpatterns as upurls
from siteuser.notify.urls import urlpatterns as nourls

siteuser_url_table = {
    'siteuser.upload_avatar': upurls,
    'siteuser.notify': nourls,
}

for app in settings.INSTALLED_APPS:
    if app in siteuser_url_table:
        urlpatterns += siteuser_url_table[app]
