# -*- coding: utf-8 -*-

from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext

from siteuser.users.models import SiteUser
from siteuser import settings as siteuser_settings

if siteuser_settings.USING_SOCIAL_LOGIN:
    from socialoauth import SocialSites

def home(request):
    if siteuser_settings.USING_SOCIAL_LOGIN:
        socialsites = SocialSites(settings.SOCIALOAUTH_SITES)

    def _make_user_info(u):
        info = {}
        info['id'] = u.id
        info['social'] = u.is_social
        
        if siteuser_settings.USING_SOCIAL_LOGIN and info['social']:
            info['social'] = socialsites.get_site_object_by_name(u.social_user.site_name).site_name_zh
            
        info['username'] = u.username
        info['avatar'] = u.avatar
        info['current'] = request.siteuser and request.siteuser.id == u.id
        return info

    all_users = SiteUser.objects.all()
    users = map(_make_user_info, all_users)
    
    return render_to_response(
        'home.html',
        {
            'users': users,
        },
        context_instance = RequestContext(request)
    )

def account_settings(request):
    return render_to_response(
        'account_settings.html', context_instance=RequestContext(request)
    )