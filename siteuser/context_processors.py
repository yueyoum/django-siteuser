# -*- coding: utf-8 -*-

from siteuser.utils import LazyList
from siteuser.settings import USING_SOCIAL_LOGIN, SOCIALOAUTH_SITES

if USING_SOCIAL_LOGIN:
    from socialoauth import SocialSites

# add 'siteuser.context_processors.social_sites' in TEMPLATE_CONTEXT_PROCESSORS
# then in template, you can get this sites via {% for s in social_sites %} ... {% endfor %}
# Don't worry about the performance,
# `social_sites` is a lazy object, it readly called just access the `social_sites`


def social_sites(request):
    def _social_sites():
        def make_site(site_class):
            s = socialsites.get_site_object_by_class(site_class)
            return {
                'site_name': s.site_name,
                'site_name_zh': s.site_name_zh,
                'authorize_url': s.authorize_url,
            }
        socialsites = SocialSites(SOCIALOAUTH_SITES)
        return [make_site(site_class) for site_class in socialsites.list_sites_class()]

    if SOCIALOAUTH_SITES:
        return {'social_sites': LazyList(_social_sites)}
    return {'social_sites': []}
