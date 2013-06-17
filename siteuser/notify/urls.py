# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from siteuser.notify import views

urlpatterns = patterns('',
    url(r'^notifies.json/$', views.notifies_json),
    url(r'^notifies/$', views.get_notifies, name="siteuser_nofities"),
    url(r'^notify/confirm/(?P<notify_id>\d+)/$', views.notify_confirm, name='siteuser_notify_confirm')
)