# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

from siteuser.users import views
from siteuser.settings import USING_SOCIAL_LOGIN

urlpatterns = patterns('',
    url(r'^account/login/$', views.SiteUserLoginView.as_view(), name='siteuser_login'),
    url(r'^account/register/$', views.SiteUserRegisterView.as_view(), name='siteuser_register'),

    # 丢失密码，重置第一步，填写注册邮件
    url(r'^account/resetpw/step1/$', views.SiteUserResetPwStepOneView.as_view(), name='siteuser_reset_step1'),
    url(r'^account/resetpw/step1/done/$', views.SiteUserResetPwStepOneDoneView.as_view(), name='siteuser_reset_step1_done'),

    # 第二布，重置密码。token是django.core.signing模块生成的带时间戳的加密字符串
    url(r'^account/resetpw/step2/done/$', views.SiteUserResetPwStepTwoDoneView.as_view(), name='siteuser_reset_step2_done'),
    url(r'^account/resetpw/step2/(?P<token>.+)/$', views.SiteUserResetPwStepTwoView.as_view(), name='siteuser_reset_step2'),

    # 登录用户修改密码
    url(r'^account/changepw/$', views.SiteUserChangePwView.as_view(), name='siteuser_changepw'),
    url(r'^account/changepw/done/$', views.SiteUserChangePwDoneView.as_view(), name='siteuser_changepw_done'),

    # 以上关于密码管理的url只能有本网站注册用户才能访问，第三方帐号不需要此功能


    url(r'^account/logout/$', views.logout, name='siteuser_logout'),
)


# 只有设置 USING_SOCIAL_LOGIN = True 的情况下，才会开启第三方登录功能
if USING_SOCIAL_LOGIN:
    urlpatterns += patterns('',
        url(r'^account/oauth/(?P<sitename>\w+)/?$', views.social_login_callback),
    )
