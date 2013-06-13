# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

from siteuser.users import views

urlpatterns = patterns('',
    url(r'account/login/$', views.SiteUserLoginView.as_view(), name='siteuser_login'),
    url(r'account/register/$', views.SiteUserRegisterView.as_view(), name='siteuser_register'),
    url(r'account/logout/$', views.logout, name='siteuser_logout'),
    url(r'account/oauth/(?P<sitename>\w+)/?$', views.social_login_callback),
)
