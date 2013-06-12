# -*- coding: utf-8 -*-
import re
import json
import hashlib
from functools import wraps

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from socialoauth import SocialSites, SocialAPIError, SocialSitesConfigError


from siteuser.users.models import InnerUser, SiteUser, SocialUser
from siteuser.settings import (
    MAX_EMAIL_LENGTH,
    MAX_USERNAME_LENGTH,
    SOCIALOAUTH_SITES,
    SOCIAL_LOGIN_DONE_REDIRECT_URL,
    SOCIAL_LOGIN_ERROR_REDIRECT_URL,
)


# 注册，登录，退出等都通过弹出窗口和 ajax 的方式进行

EMAIL_PATTERN = re.compile('^.+@.+\..+$')

class InnerAccoutError(Exception):
    pass

def inner_accout_guard(func):
    @wraps(func)
    def deco(request, *args, **kwargs):
        if request.method != 'POST':
            ret_data = {
                'ok': False,
                'msg': '禁止此操作'
            }
            return HttpResponse(json.dumps(ret_data), mimetype='application/json')
        if request.siteuser:
            ret_data = {
                'ok': False,
                'msg': '你已经登录'
            }
            return HttpResponse(json.dumps(ret_data), mimetype='application/json')

        try:
            func(request, *args, **kwargs)
        except InnerAccoutError as e:
            ret_data = {
                'ok': False,
                'msg': str(e)
            }
            return HttpResponse(json.dumps(ret_data), mimetype='application/json')

        return HttpResponse(json.dumps({'ok': True}), mimetype='application/json')
    return deco



@inner_accout_guard
def login(request):
    email = request.POST.get('email', None)
    passwd = request.POST.get('passwd', None)

    if not email or not passwd:
        raise InnerAccoutError('请填写email和密码')

    try:
        user = InnerUser.objects.get(email=email)
    except InnerUser.DoesNotExist:
        raise InnerAccoutError('此用户不存在')

    if user.passwd != hashlib.sha1(passwd).hexdigest():
        raise InnerAccoutError('密码错误')

    # done
    request.session['uid'] = user.user.id


@inner_accout_guard
def register(request):
    email = request.POST.get('email', None)
    username = request.POST.get('username', None)
    passwd = request.POST.get('passwd', None)

    if not email or not username or not passwd:
        raise InnerAccoutError('请完整填写注册信息')

    if len(email) > MAX_EMAIL_LENGTH:
        raise InnerAccoutError('电子邮件地址太长')

    if EMAIL_PATTERN.search(email) is None:
        raise InnerAccoutError('电子邮件格式不正确')

    if InnerUser.objects.filter(email=email).exists():
        raise InnerAccoutError('此电子邮件已被占用')

    if len(username) > MAX_USERNAME_LENGTH:
        raise InnerAccoutError('用户名太长')

    if SiteUser.objects.filter(username=username).exists():
        raise InnerAccoutError('用户名已存在')

    passwd = hashlib.sha1(passwd).hexdigest()
    user = InnerUser.objects.create(email=email, passwd=passwd, username=username)
    request.session['uid'] = user.id

    # finish


def logout(request):
    try:
        del request.session['uid']
    except:
        pass

    return HttpResponse('', mimetype='application/json')


def account_settings(request):
    if not request.siteuser:
        return HttpResponseRedirect('/')
    return render_to_response('account_settings.html', context_instance=RequestContext(request))


def social_login_callback(request, sitename):
    code = request.GET.get('code', None)
    if not code:
        return HttpResponseRedirect(SOCIAL_LOGIN_ERROR_REDIRECT_URL)
    
    socialsites = SocialSites(SOCIALOAUTH_SITES)
    try:
        site = socialsites.get_site_object_by_name(sitename)
        site.get_access_token(code)
    except(SocialSitesConfigError, SocialAPIError):
        return HttpResponseRedirect(SOCIAL_LOGIN_ERROR_REDIRECT_URL)
    
    try:
        user = SocialUser.objects.get(site_uid=site.uid, site_name=site.site_name)
        SiteUser.objects.filter(id=user.id).update(username=site.username, avatar_url=site.avatar)
    except SocialUser.DoesNotExist:
        user = SocialUser.objects.create(
            site_uid=site.uid,
            site_name=site.site_name,
            username=site.name,
            avatar_url=site.avatar
        )
        
    # set uid in session, then this user will be auto login
    request.session['uid'] = user.user.id
    return HttpResponseRedirect(SOCIAL_LOGIN_DONE_REDIRECT_URL)
