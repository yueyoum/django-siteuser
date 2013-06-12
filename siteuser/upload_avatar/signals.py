# -*- coding: utf-8 -*-

from django.dispatch import Signal

avatar_upload_done = Signal(providing_args=['uid', 'avatar_name'])
avatar_crop_done = Signal(providing_args=['uid', 'avatar_name'])