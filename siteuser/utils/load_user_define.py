# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

class UserNotDefined(object):pass

def user_defined_mixin():
    mixin = getattr(settings, 'SITEUSER_ACCOUNT_MIXIN', UserNotDefined)
    if mixin is UserNotDefined:
        raise ImproperlyConfigured("No Settings For SITEUSER_ACCOUNT_MIXIN")
    if mixin is object:
        raise ImproperlyConfigured("Invalid SITEUSER_ACCOUNT_MIXIN")
    if isinstance(mixin, type):
        return mixin

    _module, _class = mixin.rsplit('.', 1)
    m = __import__(_module, fromlist=['.'])
    return getattr(m, _class)