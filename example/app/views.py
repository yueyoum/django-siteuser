# -*- coding: utf-8 -*-

from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext

from socialoauth import SocialSites
from siteuser.users.models import SiteUser


def home(request):
    def _make_user_info(u):
        info = {}
        info['id'] = u.id
        info['social'] = u.is_social
        
        if info['social']:
            info['social'] = socialsites.get_site_object_by_name(u.social_user.site_name).site_name_zh
            
        info['username'] = u.username
        info['avatar'] = u.avatar
        info['current'] = request.siteuser and request.siteuser.id == u.id
        return info
    
    socialsites = SocialSites(settings.SOCIALOAUTH_SITES)
    all_users = SiteUser.objects.all()
    users = map(_make_user_info, all_users)
    
    return render_to_response(
        'home.html',
        {
            'users': users,
        },
        context_instance = RequestContext(request)
    )


def login(request):
    return render_to_response(
        'login.html', context_instance=RequestContext(request)
    )

def register(request):
    return render_to_response(
        'register.html', context_instance=RequestContext(request)
    )