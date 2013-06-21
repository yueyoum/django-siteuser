# -*- coding: utf-8 -*-

from celery import task

from siteuser.functional import send_html_mail as _send_mail

@task
def send_mail(to, subject, context):
    _send_mail(to, subject, context)
