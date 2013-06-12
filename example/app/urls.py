# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
    url(r'^$', views.home, name="home"),
    url(r'^account/login/?$', views.login, name="login"),
    url(r'^account/register/?$', views.register, name="register"),
)