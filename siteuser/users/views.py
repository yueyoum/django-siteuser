# -*- coding: utf-8 -*-
import re
import json
import hashlib
from functools import wraps

from django.conf import settings
from django.core import signing
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template import loader, RequestContext
from django.views.generic import View

from socialoauth import SocialSites, SocialAPIError, SocialSitesConfigError

from siteuser.users.models import InnerUser, SiteUser, SocialUser
from siteuser.functional import send_mail_convenient
from siteuser.settings import (
    MAX_EMAIL_LENGTH,
    MAX_USERNAME_LENGTH,
    SOCIALOAUTH_SITES,
    SOCIAL_LOGIN_DONE_REDIRECT_URL,
    SOCIAL_LOGIN_ERROR_REDIRECT_URL,
)


# 注册，登录，退出等都通过 ajax 的方式进行

EMAIL_PATTERN = re.compile('^.+@.+\..+$')

class InnerAccoutError(Exception):
    pass


def inner_account_ajax_guard(func):
    @wraps(func)
    def deco(self, request, *args, **kwargs):
        dump = lambda d: HttpResponse(json.dumps(d), mimetype='application/json')
        if request.siteuser:
            return dump({'ok': False, 'msg': '你已登录'})

        try:
            func(self, request, *args, **kwargs)
        except InnerAccoutError as e:
            return dump({'ok': False, 'msg': str(e)})

        return dump({'ok': True})
    return deco

def inner_account_http_guard(func):
    @wraps(func)
    def deco(self, request, *args, **kwargs):
        if request.siteuser:
            return HttpResponseRedirect('/')
        try:
            return func(self, request, *args, **kwargs)
        except InnerAccoutError as e:
            ctx = self.ctx_getter(request)
            ctx.update(getattr(self, 'ctx', {}))
            ctx.update({'error_msg': e})
            return render_to_response(
                self.tpl,
                ctx,
                context_instance=RequestContext(request)
            )
    return deco


class SiteUserMixIn(object):
    login_template = 'siteuser/login.html'
    register_template = 'siteuser/register.html'
    reset_passwd_template = 'siteuser/reset_password.html'
    sign_key = 'siteuser_signkey'
    reset_passwd_email_title = u'重置密码'
    reset_passwd_email_template = 'siteuser/reset_password_email.html'
    reset_passwd_link_expired_in = 24   # 多少小时后重置密码的链接失效

    def get_login_context(self, request):
        return {}

    def get_register_context(self, request):
        return {}

    def get_reset_passwd_context(self, request):
        return {}

    def get(self, request, *args, **kwargs):
        if request.siteuser:
            return HttpResponseRedirect('/')
        ctx = self.ctx_getter(request)
        ctx.update(getattr(self, 'ctx', {}))
        return render_to_response(
            self.tpl,
            ctx,
            context_instance=RequestContext(request)
        )

    def _reset_passwd_default_ctx(self):
        return {
            'step1': False,
            'step1_done': False,
            'step2': False,
            'step2_done': False,
            'expired': False,
        }


class UserNotDefined(object):pass

def user_defined_mixin():
    mixin = getattr(settings, 'SITEUSER_ACCOUNT_MIXIN', UserNotDefined)
    if mixin is object:
        raise AttributeError("Invalid SITEUSER_ACCOUNT_MIXIN")
    if isinstance(mixin, type):
        return mixin
    
    _module, _class = mixin.rsplit('.', 1)
    m = __import__(_module, fromlist=['.'])
    return getattr(m, _class)


class SiteUserLoginView(user_defined_mixin(), SiteUserMixIn, View):
    def __init__(self, **kwargs):
        self.tpl = self.login_template
        self.ctx_getter = self.get_login_context
        super(SiteUserLoginView, self).__init__(**kwargs)

    @inner_account_ajax_guard
    def post(self, request, *args, **kwargs):
        email = request.POST.get('email', None)
        passwd = request.POST.get('passwd', None)

        if not email or not passwd:
            raise InnerAccoutError('请填写email和密码')

        try:
            user = InnerUser.objects.get(email=email)
        except InnerUser.DoesNotExist:
            raise InnerAccoutError('用户不存在')

        if user.passwd != hashlib.sha1(passwd).hexdigest():
            raise InnerAccoutError('密码错误')

        request.session['uid'] = user.user.id


class SiteUserRegisterView(user_defined_mixin(), SiteUserMixIn, View):
    def __init__(self, **kwargs):
        self.tpl = self.register_template
        self.ctx_getter = self.get_register_context
        super(SiteUserRegisterView, self).__init__(**kwargs)

    @inner_account_ajax_guard
    def post(self, request, *args, **kwargs):
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
        request.session['uid'] = user.user.id


class SiteUserResetPwStepOneView(user_defined_mixin(), SiteUserMixIn, View):
    def __init__(self, **kwargs):
        self.tpl = self.reset_passwd_template
        self.ctx_getter = self.get_reset_passwd_context
        self.ctx = self._reset_passwd_default_ctx()
        self.ctx['step1'] = True
        super(SiteUserResetPwStepOneView, self).__init__(**kwargs)

    @inner_account_http_guard
    def post(self, request, *args, **kwargs):
        email = request.POST.get('email', None)
        if not email:
            raise InnerAccoutError('请填写电子邮件')
        if EMAIL_PATTERN.search(email) is None:
            raise InnerAccoutError('电子邮件格式不正确')
        try:
            user = InnerUser.objects.get(email=email)
        except InnerUser.DoesNotExist:
            raise InnerAccoutError('请填写您注册时的电子邮件地址')

        token = signing.dumps(user.user.id, key=self.sign_key)
        link = reverse('siteuser_reset_step2', kwargs={'token': token})
        link = request.build_absolute_uri(link)
        context = {
            'hour': self.reset_passwd_link_expired_in,
            'link': link
        }
        body = loader.render_to_string(self.reset_passwd_email_template, context)
        # TODO 异步发送邮件
        body = unicode(body)
        send_mail_convenient(email, self.reset_passwd_email_title, body)
        return HttpResponseRedirect(reverse('siteuser_reset_step1_done'))


class SiteUserResetPwStepOneDoneView(user_defined_mixin(), SiteUserMixIn, View):
    def __init__(self, **kwargs):
        self.tpl = self.reset_passwd_template
        self.ctx_getter = self.get_reset_passwd_context
        self.ctx = self._reset_passwd_default_ctx()
        self.ctx['step1_done'] = True
        super(SiteUserResetPwStepOneDoneView, self).__init__(**kwargs)


class SiteUserResetPwStepTwoView(user_defined_mixin(), SiteUserMixIn, View):
    def __init__(self, **kwargs):
        self.tpl = self.reset_passwd_template
        self.ctx_getter = self.get_reset_passwd_context
        self.ctx = self._reset_passwd_default_ctx()
        self.ctx['step2'] = True
        super(SiteUserResetPwStepTwoView, self).__init__(**kwargs)

    def get(self, request, *args, **kwargs):
        token = kwargs['token']
        try:
            self.uid = signing.loads(token, key=self.sign_key, max_age=self.reset_passwd_link_expired_in*3600)
        except signing.SignatureExpired:
            # 通过context来控制到底显示表单还是过期信息
            self.ctx['expired'] = True
        except signing.BadSignature:
            raise Http404
        return super(SiteUserResetPwStepTwoView, self).get(request, *args, **kwargs)


    @inner_account_http_guard
    def post(self, request, *args, **kwargs):
        password = request.POST.get('password', None)
        password1 = request.POST.get('password1', None)
        if not password or not password1:
            raise InnerAccoutError('请填写密码')
        if password != password1:
            raise InnerAccoutError('两次密码不一致')
        uid = signing.loads(kwargs['token'], key=self.sign_key)
        password = hashlib.sha1(password).hexdigest()
        InnerUser.objects.filter(user_id=uid).update(passwd=password)
        return HttpResponseRedirect(reverse('siteuser_reset_step2_done'))


class SiteUserResetPwStepTwoDoneView(user_defined_mixin(), SiteUserMixIn, View):
    def __init__(self, **kwargs):
        self.tpl = self.reset_passwd_template
        self.ctx_getter = self.get_reset_passwd_context
        self.ctx = self._reset_passwd_default_ctx()
        self.ctx['step2_done'] = True
        super(SiteUserResetPwStepTwoDoneView, self).__init__(**kwargs)




def logout(request):
    try:
        del request.session['uid']
    except:
        pass

    return HttpResponse('', mimetype='application/json')



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
        SiteUser.objects.filter(id=user.id).update(username=site.name, avatar_url=site.avatar)
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
