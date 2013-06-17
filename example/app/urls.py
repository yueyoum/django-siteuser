# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
    url(r'^$', views.home, name="home"),
    url(r'^account/settings/?$', views.account_settings, name="account_settings"),
    url(r'^.+/?$', views._test),
)