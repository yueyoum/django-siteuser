# -*- coding: utf-8 -*-
import smtplib
from email.mime.text import MIMEText


def send_mail(host, port, username, password, mail_from, mail_to, mail_subject, mail_content, mail_type, display_from=None):
    if isinstance(mail_content, unicode):
        mail_content = mail_content.encode('utf-8')
    content = MIMEText(mail_content, mail_type, 'utf-8')
    content['From'] = display_from or mail_from
    if isinstance(mail_to, (list, tuple)):
        content['To'] = ', '.join(mail_to)
    else:
        content['To'] = mail_to
    content['Subject'] = mail_subject

    s = smtplib.SMTP()
    s.connect(host, port)
    s.login(username, password)
    s.sendmail(mail_from, mail_to, content.as_string())
    s.quit()
