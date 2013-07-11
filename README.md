# Django-siteuser

集成用户注册，登录，上传头像，第三方登录等功能。此项目的目标是当建立新站点的时候，不再重头写用户系统。


## 注意

*   项目中的js依赖jQuery，所以请确保你的站点引入了jQuery
*   只实现了第三方帐号登录，并没有实现一个本地帐号绑定多个社交帐号的功能。
*   siteuser并没有使用Django自带的User系统。


## 功能

*   注册，登录
*   登录用户修改密码
*   忘记密码时重置密码
*   上传头像 （带有剪裁预览功能）
*   第三方帐号登录
*   消息通知


## 如何使用

#### 安装

```bash
pip install django-siteuser
```

同时会安装此项目的依赖：

*   [socialoauth](https://github.com/yueyoum/social-oauth) - 第三方登录
*   [django-celery](https://github.com/celery/django-celery) - 异步发送邮件



####  在你的模板中引入必要的js文件

```html
<script type="text/javascript" src="{{ STATIC_URL }}js/jquery.js"></script>
<script type="text/javascript" src="{{ STATIC_URL }}js/siteuser.js"></script>
```


#### 设置settings.py文件

*   首先设置 [django-celery](https://github.com/celery/django-celery)

*   将 `siteuser` 加入到 `INSTALLED_APPS` 中
    ```python
    INSTALLED_APPS = (
        # ...
        'djcelery',
        'siteuser.users',
        'siteuser.upload_avatar',
        'siteuser.notify',
    )
    ```

    `siteuser.users` 为 **必须添加** 的app，另外两个一个用于上传头像，一个是简单的通知系统，**可以不添加**


*   将 `siteuser.SITEUSER_TEMPLATE` 加入 `TEMPLATE_DIRS`

    **注意**： 这里不是字符串，所以你需要在`settings.py` 文件中 先 `import siteuser`


*   将 `'siteuser.context_processors.social_sites'` 加入 `TEMPLATE_CONTEXT_PROCESSORS`
*   将 `'siteuser.middleware.User'` 加入 `MIDDLEWARE_CLASSES`
*   将 `url(r'', include('siteuser.urls'))` 加入到项目的 `urls.py` 
*   `AVATAR_DIR` - 告诉siteuser将上传的头像放置到哪个位置
*   `USING_SOCIAL_LOGIN` 是否开启第三方帐号登录功能。**若不设置，默认为 False**
*   `SOCIALOAUTH_SITES` - 仅在 `USING_SOCIAL_LOGIN`为True的情况下需要设置。第三方登录所需的配置。[见socialoauth文档](https://github.com/yueyoum/social-oauth/blob/master/doc.md#-settingspy)
*   `SITEUSER_EXTEND_MODEL`
    不设置此项，example一样可以运行，但实际项目中，肯定会根据项目本身来设定用户字段.
    默认的字段请查看 [SiteUser](/siteuser/users/models.py#L108).
    
    支持两种方式来扩展SiteUser字段
    *   直接在`settings.py`中定义
    
        ```python
        # project settings.py
        from django.db import models
        class SITEUSER_EXTEND_MODEL(models.Model):
            # some fields...
            class Meta:
                abstract = True
        ```

    *   将此model的定义写在其他文件中，然后在settings.py中指定。

    
    `example`使用的第二种，具体可以查看`example`项目.

*   `SITEUSER_ACCOUNT_MIXIN`
    siteuser 提供了登录，注册的template，但只是登录，注册form的模板，
    并且siteuser不知道如何将这个form模板嵌入到你的站点中，以及不知道在渲染模板的时候还要传入什么额外的context，
    所以你需要在自己定义这个设置。
    
    与 `SITEUSER_EXTEND_MODEL` 一样，同样有两种方法定义，
    *   直接在 `settings.py` 中定义
    
        ```python
        class SITEUSER_ACCOUNT_MIXIN(object):
            login_template = 'login.html'           # 你项目的登录页面模板
            register_template = 'register.html'     # 你项目的注册页面模板
            reset_passwd_template = 'reset_password.html'   # 忘记密码的重置密码模板
            change_passwd_template = 'change_password.html' # 登录用户修改密码的模板
            reset_passwd_email_title = u'重置密码'    # 重置密码发送电子邮件的标题
            reset_passwd_link_expired_in = 24        # 重置密码链接多少小时后失效
            
            def get_login_context(self, request):
                return {}
                
            def get_register_context(self, request):
                return {}
        ```
        
        这两个方法正如其名，request是django传递给view的request，你在这里返回需要传递到模板中的context即可
        在这里查看默认的 [SiteUserMixIn](/siteuser/users/views.py#L73)
        
    *   第二中方法是将此Mixin定义在一个文件中，然后在settings.py中指定
    
    `example`使用的第二种，具体可以查看`example`项目.


*   `SITEUSER_EMAIL`

    siteuser自己写了发邮件的方法，所以也没使用Django自己的EMAI设置
    所以你需要设置`SITEUSER_EMAIL`, 见 [local_settings.py.example](/example/example/local_settings.py.example)

    其中需要说明的是 `display_from` 这个设置，
    如果你没有自己架设SMTP SERVER，也没有购买发送邮件的服务，
    而是直接在gmail, 163, sohu等email提供商那儿免费申请了个邮箱，
    那么你的邮箱肯定是 name@gmail.com这种形式的。
    这时候如果你想在别人的收件箱里显示 `abc@def.com` 
    那么就把 `display_from` 设置成此值。如果不设置，那么默认就是`from`


#### 模板

你需要自己完成 login.html, register.html, account_settings.html 模板。（名字可以自己取，只要在代码中
等对应起来就行），你只需要干一件事情，就是在你的模板的 `include` 相应的siteuser模板即可。

比如 login.html 中在你定义的位置 `{% include 'siteuser/login.html' %}`,

account_settings.html 中 `{% include 'siteuser/upload_avatar.html' %}`

具体可以参考`example`项目

做完上面的设置后， `python manage.py validate` 检测无误后，syncdb，runserver 就可以测试注册，登录，头像，第三方登录
