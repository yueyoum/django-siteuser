# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from siteuser.notify import views

urlpatterns = patterns('',
    # ajax 获取通知
    url(r'^notifies.json/$', views.notifies_json),
    # 普通页面浏览获取通知
    url(r'^notifies/$', views.get_notifies, name="siteuser_nofities"),

    # 点击一个通知，ajax是在url后面加 ?js_ajax=1
    url(r'^notify/confirm/(?P<notify_id>\d+)/$', views.notify_confirm, name='siteuser_notify_confirm')
)