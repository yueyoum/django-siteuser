# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

from siteuser.users import views

urlpatterns = patterns('',
    url(r'account/login/?$', views.login),
    url(r'account/register/?$', views.register),
    url(r'account/logout/?$', views.logout),
    url(r'account/settings/?$', views.account_settings),
    url(r'account/oauth/(?P<sitename>\w+)/?$', views.social_login_callback),
)
