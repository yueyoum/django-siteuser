from django.conf.urls import patterns, include, url


urlpatterns = patterns('',
    url(r'', include('siteuser.urls')),
    url(r'', include('app.urls')),
)


from django.contrib.staticfiles.urls import staticfiles_urlpatterns
urlpatterns += staticfiles_urlpatterns()

# for test
from app.views import _test
urlpatterns += patterns('',
    url(r'^.+/?$', _test),
)