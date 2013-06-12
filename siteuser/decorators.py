# -*- coding: utf-8 -*-
from functools import wraps

from django.http import HttpResponseRedirect
from django.http import Http404

def login_needed(login_url=None):
    def deco(func):
        @wraps(func)
        def wrap(request, *args, **kwargs):
            if not request.siteuser:
                # No login
                if login_url:
                    return HttpResponseRedirect(login_url)
                raise Http404

            return func(request, *args, **kwargs)
        return wrap