# -*- coding: utf-8 -*-

import os

version_info = (0, 1, 0)
VERSION = __version__ = '.'.join( map(str, version_info) )

CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))
SITEUSER_TEMPLATE = os.path.join(CURRENT_PATH, 'templates')