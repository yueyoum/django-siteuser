# -*- coding: utf-8 -*-
import os
from django.conf import settings

### 第三方帐号登录 - 配置见soicaloauth文档和例子
SOCIALOAUTH_SITES = settings.SOCIALOAUTH_SITES

### 头像目录 - 需要在项目的settings.py中设置
AVATAR_DIR = settings.AVATAR_DIR

# 上传的原始图片目录, 默认和头像目录相同
AVATAR_UPLOAD_DIR = getattr(settings, 'AVATAR_UPLOAD_DIR', AVATAR_DIR)

# 默认头像的文件名，需要将其放入AVATAR_DIR 头像目录
DEFAULT_AVATAR = getattr(settings, 'DEFAULT_AVATAR', 'default_avatar.png')

if not os.path.isdir(AVATAR_DIR):
    os.mkdir(AVATAR_DIR)
if not os.path.isdir(AVATAR_UPLOAD_DIR):
    os.mkdir(AVATAR_UPLOAD_DIR)

# 头像url的前缀
AVATAR_URL_PREFIX = getattr(settings, 'AVATAR_URL_PREFIX', '/static/avatar/')

# 原始上传的图片url前缀，用于在裁剪选择区域显示原始图片
AVATAR_UPLOAD_URL_PREFIX = getattr(settings, 'AVATAR_UPLOAD_URL_PREFIX', AVATAR_URL_PREFIX)

# 最大可上传图片大小 MB
AVATAR_UPLOAD_MAX_SIZE =  getattr(settings, 'AVATAR_UPLOAD_MAX_SIZE', 5)

# 剪裁后的大小 px
AVATAR_RESIZE_SIZE = getattr(settings, 'AVATAR_RESIZE_SIZE', 50)

# 头像处理完毕后保存的格式和质量， 格式还可以是 jpep, gif
AVATAR_SAVE_FORMAT = getattr(settings, 'AVATAR_SAVE_FORMAT', 'png')
AVATAR_SAVE_QUALITY = getattr(settings, 'AVATAR_SAVE_QUALITY', 90)

# 处理完头像后是否删除原始的上传图片
AVATAR_DELETE_ORIGINAL_AFTER_CROP = getattr(settings, 'AVATAR_DELETE_ORIGINAL_AFTER_CROP', True)


# 注册用户的电子邮件最大长度
MAX_EMAIL_LENGTH = getattr(settings, 'MAX_EMAIL_LENGTH', 128)

# 注册用户的用户名最大长度
MAX_USERNAME_LENGTH = getattr(settings, 'MAX_USERNAME_LENGTH', 12)


# 第三方帐号授权成功后跳转的URL
SOCIAL_LOGIN_DONE_REDIRECT_URL = getattr(settings, 'SOCIAL_LOGIN_DONE_REDIRECT_URL', '/')
# 授权失败后跳转的URL
SOCIAL_LOGIN_ERROR_REDIRECT_URL = getattr(settings, 'SOCIAL_LOGIN_ERROR_REDIRECT_URL', '/')