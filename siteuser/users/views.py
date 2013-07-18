# -*- coding: utf-8 -*-
import re
import json
import hashlib
from functools import wraps

from django.core import signing
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template import loader, RequestContext
from django.views.generic import View


from siteuser.users.models import InnerUser, SiteUser, SocialUser
from siteuser.users.tasks import send_mail
from siteuser.settings import (
    USING_SOCIAL_LOGIN,
    MAX_EMAIL_LENGTH,
    MAX_USERNAME_LENGTH,
    SOCIALOAUTH_SITES,
    SOCIAL_LOGIN_DONE_REDIRECT_URL,
    SOCIAL_LOGIN_ERROR_REDIRECT_URL,
)
from siteuser.utils.load_user_define import user_defined_mixin

if USING_SOCIAL_LOGIN:
    from socialoauth import SocialSites, SocialAPIError, SocialSitesConfigError

# 注册，登录，退出等都通过 ajax 的方式进行

EMAIL_PATTERN = re.compile('^.+@.+\..+$')

class InnerAccoutError(Exception):
    pass

make_password = lambda passwd: hashlib.sha1(passwd).hexdigest()

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
    """用户可以自定义 SITEUSER_ACCOUNT_MIXIN 来覆盖这些配置"""
    login_template = 'siteuser/login.html'
    register_template = 'siteuser/register.html'
    reset_passwd_template = 'siteuser/reset_password.html'
    change_passwd_template = 'siteuser/change_password.html'

    # 用于生成重置密码链接的key,用于加密解密
    sign_key = 'siteuser_signkey'

    # 重置密码邮件的标题
    reset_passwd_email_title = u'重置密码'
    reset_passwd_email_template = 'siteuser/reset_password_email.html'

    # 多少小时后重置密码的链接失效
    reset_passwd_link_expired_in = 24

    # 在渲染这些模板的时候，如果你有额外的context需要传入，请重写这些方法
    def get_login_context(self, request):
        return {}

    def get_register_context(self, request):
        return {}

    def get_reset_passwd_context(self, request):
        return {}

    def get_change_passwd_context(self, request):
        return {}

    def get(self, request, *args, **kwargs):
        """使用此get方法的Class，必须制定这两个属性：
        self.tpl - 此view要渲染的模板名
        self.ctx_getter - 渲染模板是获取额外context的方法名
        """
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

    def _normalize_referer(self, request):
        referer = request.META.get('HTTP_REFERER', '/')
        if referer.endswith('done/'):
            referer = '/'
        return referer



class SiteUserLoginView(user_defined_mixin(), SiteUserMixIn, View):
    """登录"""
    def __init__(self, **kwargs):
        self.tpl = self.login_template
        self.ctx_getter = self.get_login_context
        super(SiteUserLoginView, self).__init__(**kwargs)

    def get_login_context(self, request):
        """注册和登录都是通过ajax进行的，这里渲染表单模板的时候传入referer，
        当ajax post返回成功标识的时候，js就到此referer的页面。
        以此来完成注册/登录完毕后自动回到上个页面
        """
        ctx = super(SiteUserLoginView, self).get_login_context(request)
        ctx['referer'] = self._normalize_referer(request)
        return ctx

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
    """注册"""
    def __init__(self, **kwargs):
        self.tpl = self.register_template
        self.ctx_getter = self.get_register_context
        super(SiteUserRegisterView, self).__init__(**kwargs)

    def get_register_context(self, request):
        ctx = super(SiteUserRegisterView, self).get_register_context(request)
        ctx['referer'] = self._normalize_referer(request)
        return ctx

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
            raise InnerAccoutError('用户名太长，不要超过{0}个字符'.format(MAX_USERNAME_LENGTH))

        if SiteUser.objects.filter(username=username).exists():
            raise InnerAccoutError('用户名已存在')

        passwd = make_password(passwd)
        user = InnerUser.objects.create(email=email, passwd=passwd, username=username)
        request.session['uid'] = user.user.id


class SiteUserResetPwStepOneView(user_defined_mixin(), SiteUserMixIn, View):
    """丢失密码重置第一步，填写注册时的电子邮件"""
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
        # 异步发送邮件
        body = unicode(body)
        send_mail.delay(email, self.reset_passwd_email_title, body)
        return HttpResponseRedirect(reverse('siteuser_reset_step1_done'))


class SiteUserResetPwStepOneDoneView(user_defined_mixin(), SiteUserMixIn, View):
    """发送重置邮件完成"""
    def __init__(self, **kwargs):
        self.tpl = self.reset_passwd_template
        self.ctx_getter = self.get_reset_passwd_context
        self.ctx = self._reset_passwd_default_ctx()
        self.ctx['step1_done'] = True
        super(SiteUserResetPwStepOneDoneView, self).__init__(**kwargs)


class SiteUserResetPwStepTwoView(user_defined_mixin(), SiteUserMixIn, View):
    """丢失密码重置第二步，填写新密码"""
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
        password = make_password(password)
        InnerUser.objects.filter(user_id=uid).update(passwd=password)
        return HttpResponseRedirect(reverse('siteuser_reset_step2_done'))


class SiteUserResetPwStepTwoDoneView(user_defined_mixin(), SiteUserMixIn, View):
    """重置完成"""
    def __init__(self, **kwargs):
        self.tpl = self.reset_passwd_template
        self.ctx_getter = self.get_reset_passwd_context
        self.ctx = self._reset_passwd_default_ctx()
        self.ctx['step2_done'] = True
        super(SiteUserResetPwStepTwoDoneView, self).__init__(**kwargs)


class SiteUserChangePwView(user_defined_mixin(), SiteUserMixIn, View):
    """已登录用户修改密码"""
    def render_to_response(self, request, **kwargs):
        ctx = self.get_change_passwd_context(request)
        ctx['done'] = False
        ctx.update(kwargs)
        return render_to_response(
            self.change_passwd_template,
            ctx,
            context_instance=RequestContext(request)
        )

    def get(self, request, *args, **kwargs):
        if not request.siteuser:
            return HttpResponseRedirect('/')
        if not request.siteuser.is_active or request.siteuser.is_social:
            return HttpResponseRedirect('/')
        return self.render_to_response(request)

    def post(self, request, *args, **kwargs):
        if not request.siteuser:
            return HttpResponseRedirect('/')
        if not request.siteuser.is_active or request.siteuser.is_social:
            return HttpResponseRedirect('/')

        password = request.POST.get('password', None)
        password1 = request.POST.get('password1', None)
        if not password or not password1:
            return self.render_to_response(request, error_msg='请填写新密码')
        if password != password1:
            return self.render_to_response(request, error_msg='两次密码不一致')
        password = make_password(password)
        if request.siteuser.inner_user.passwd == password:
            return self.render_to_response(request, error_msg='不能与旧密码相同')
        InnerUser.objects.filter(user_id=request.siteuser.id).update(passwd=password)
        # 清除登录状态
        try:
            del request.session['uid']
        except:
            pass

        return HttpResponseRedirect(reverse('siteuser_changepw_done'))


class SiteUserChangePwDoneView(user_defined_mixin(), SiteUserMixIn, View):
    """已登录用户修改密码成功"""
    def get(self, request, *args, **kwargs):
        if request.siteuser:
            return HttpResponseRedirect('/')
        ctx = self.get_change_passwd_context(request)
        ctx['done'] = True
        return render_to_response(
            self.change_passwd_template,
            ctx,
            context_instance=RequestContext(request)
        )


def logout(request):
    """登出，ajax请求，然后刷新页面"""
    try:
        del request.session['uid']
    except:
        pass

    return HttpResponse('', mimetype='application/json')



def social_login_callback(request, sitename):
    """第三方帐号OAuth认证登录，只有设置了USING_SOCIAL_LOGIN=True才会使用到此功能"""
    code = request.GET.get('code', None)
    if not code:
        return HttpResponseRedirect(SOCIAL_LOGIN_ERROR_REDIRECT_URL)

    socialsites = SocialSites(SOCIALOAUTH_SITES)
    try:
        site = socialsites.get_site_object_by_name(sitename)
        site.get_access_token(code)
    except(SocialSitesConfigError, SocialAPIError):
        return HttpResponseRedirect(SOCIAL_LOGIN_ERROR_REDIRECT_URL)

    # 首先根据site_name和site uid查找此用户是否已经在自身网站认证，
    # 如果查不到，表示这个用户第一次认证登陆，创建新用户记录
    # 如果查到，就跟新其用户名和头像
    try:
        user = SocialUser.objects.get(site_uid=site.uid, site_name=site.site_name)
        SiteUser.objects.filter(id=user.user.id).update(username=site.name, avatar_url=site.avatar)
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
