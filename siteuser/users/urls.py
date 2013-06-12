# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

from siteuser.users import views

urlpatterns = patterns('',
    url(r'siteuser/login/$', views.login, name='siteuser_login'),
    url(r'siteuser/register/$', views.register, name='siteuser_register'),
    url(r'siteuser/logout/$', views.logout, name='siteuser_logout'),
    url(r'account/oauth/(?P<sitename>\w+)/?$', views.social_login_callback),
)
