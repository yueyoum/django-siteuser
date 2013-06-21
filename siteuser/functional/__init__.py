# -*- coding: utf-8 -*-

from django.conf import settings
from siteuser.functional.mail import send_mail

SITEUSER_EMAIL = settings.SITEUSER_EMAIL

def send_html_mail(to, subject, content):
    send_mail(
        SITEUSER_EMAIL['smtp_host'],
        SITEUSER_EMAIL['smtp_port'],
        SITEUSER_EMAIL['username'],
        SITEUSER_EMAIL['password'],
        SITEUSER_EMAIL['from'],
        to,
        subject,
        content,
        'html',
        SITEUSER_EMAIL['display_from']
    )
