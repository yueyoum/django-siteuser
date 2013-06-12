# Django-siteuser

集成用户注册，登录，上传头像，第三方登录等功能。此项目的目标是当建立新站点的时候，不再重头写用户系统。

<table>
<tr><td>更新时间</td><td>状态</td></tr>
<tr><td>2013-06-12</td><td>开发中</td></tr>
</table>

## 注意

*   项目中的js依赖jQuery，所以请确保你的站点引入了jQuery
*   项目依赖于 ![socialoauth](https://github.com/yueyoum/social-oauth)
*   只实现了第三方帐号登录，并没有实现一个本地帐号绑定多个社交帐号的功能。
*   siteuser并没有使用Django自带的User系统，所以`login_required`不可用，请使用`login_needed`。
    `from siteuser.decorators import login_needed`。
*   也正因为siteuser并没有与Django自身结合的太深，所以在去除掉一些Django特性后（ORM, Signals），
此项目很容易移植到tornado, flask, bottle等各种框架中


## 功能

*   注册，登录
*   上传头像 （带有剪裁预览功能）
*   第三方帐号登录

## TODO

*   重置密码
*   站内信/消息通知

## 如何使用

*   引入必要的js文件
    ```html
    <script type="text/javascript" src="{{ STATIC_URL }}js/siteuser.js"></script>
    ```

*   将 `siteuser` 加入到 `INSTALLED_APPS` 中
    ```python
    INSTALLED_APPS = (
        # ...
        'siteuser.users',
        'siteuser.upload_avatar',
    )
    ```

*   将 `siteuser.context_processors.social_sites` 加入 `TEMPLATE_CONTEXT_PROCESSORS`
*   将 `siteuser.middleware.User` 加入 `MIDDLEWARE_CLASSES`
*   将 `url(r'', include('siteuser.urls'))` 加入到项目的 `urls.py` 
*   `AVATAR_DIR` - 告诉siteuser将上传的头像放置到哪个位置
*   `SOCIALOAUTH_SITES` - 第三方登录所需的配置。![见socialoauth文档](https://github.com/yueyoum/social-oauth/blob/master/doc.md#-settingspy)
*   `SITEUSER_EXTEND_MODEL`
    不设置此项，example一样可以运行，但实际项目中，肯定会根据项目本身来设定用户字段.
    默认的字段请查看 ![SiteUser](/siteuser/users/models.py).
    
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


最后还要做的是： siteuser 提供了登录，注册的template，但只是登录，注册form的模板，
并且siteuser不知道如何将这个form模板嵌入到你的站点中，以及不知道在渲染模板的时候还要传入什么额外的context，
所以你需要在自己的项目`views.py`中写对应的方法，在`urls.py`添加对应的url，并且完成对应的模板。

看起来工作量很大，其实最简单的情况下，你只用添加几行代码。
url需要注意的是 不要用 `siteuser` 作为你定义的url开头。
`view.py`中的方法很简单，基本上只用 `render_to_response`，
而模板也只用 `{% include 'siteuser/login.html' %}`即可。（如果是注册，则`include 'siteuser/register.html'`）

具体可以参考`example`项目

做完上面的设置后， `python manage.py validate` 检测无误后，syncdb，runserver 就可以测试注册，登录，头像，第三方登录
