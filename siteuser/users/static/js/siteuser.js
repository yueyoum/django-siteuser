(function(window, $){
    $(function(){
        $('#siteuserLogin').click(function(e){
            console.log('xxclicked...');
            e.preventDefault();
            console.log('clicked...');
            var email, passwd, referer;
            email = $('#siteuserLoginEmail').val();
            passwd = $('#siteuserLoginPassword').val();
            email = strip(email);
            passwd = strip(passwd);

            if(email.length===0 || passwd.length===0) {
                make_warning('#siteuserLoginWarning', '请填写电子邮件和密码');
                return;
            }

            $.ajax(
                {
                    type: 'POST',
                    url: '/siteuser/login/',
                    data: {
                        email: email,
                        passwd: passwd,
                        csrfmiddlewaretoken: get_csrf()
                    },
                    dateType: 'json',
                    async: false,
                    success: function(data){
                        if(data.ok) {
                            referer = $('#siteuserLogin').attr('referer');
                            if(referer==="" || referer===undefined) {
                                window.location.reload();
                            } else {
                                window.location.href = referer;
                            }
                        }
                        else {
                            make_warning('#siteuserLoginWarning', data.msg);
                        }
                    },
                    error: function(XmlHttprequest, textStatus, errorThrown){
                        make_warning('#siteuserLoginWarning', '发生错误，请稍后再试');
                    }
                }
            );
        });

        // register 
        $('#siteuserRegister').click(function(e){
            e.preventDefault();
            var email, username, passwd, passwd2, _tmp_email, referer;
            email = $('#siteuserRegEmail').val();
            username = $('#siteuserRegUsername').val();
            passwd = $('#siteuserRegPassword').val();
            passwd2 = $('#siteuserRegPassword2').val();
            email = strip(email);
            username = strip(username);
            passwd = strip(passwd);
            passwd2 = strip(passwd2);

            _tmp_email = email.replace(/^.+@.+\..+$/, '');
            if(_tmp_email.length>0){
                make_warning('#siteuserRegisterWarning', '目测邮箱格式不正确啊');
                return;
            }

            if(email.length === 0 || username.length === 0 || passwd.length === 0 || passwd2.length === 0) {
                make_warning('#siteuserRegisterWarning', '请完整填写注册信息');
                return;
            }

            if(passwd != passwd2) {
                make_warning('#siteuserRegisterWarning', '两次密码不一致');
                return;
            }

            $.ajax(
                {
                    type: 'POST',
                    url: '/siteuser/register/',
                    data: {
                        email: email,
                        username: username,
                        passwd: passwd,
                        csrfmiddlewaretoken: get_csrf()
                    },
                    dateType: 'json',
                    async: false,
                    success: function(data){
                        if(data.ok) {
                            referer = $('#siteuserRegister').attr('referer');
                            if(referer==="" || referer===undefined) {
                                window.location.reload();
                            } else {
                                window.location.href = referer;
                            }
                        }
                        else {
                            make_warning('#siteuserRegisterWarning', data.msg);
                        }
                    },
                    error: function(XmlHttprequest, textStatus, errorThrown){
                        make_warning('#siteuserRegisterWarning', '发生错误，请稍后再试');
                    }
                }
            );
        });

        //logout
        $('#siteuserLogout').click(function(e){
            e.preventDefault();
            $.ajax(
                {
                    type: 'GET',
                    url: '/siteuser/logout/',
                    async: false,
                    success: function(data){
                        window.location.reload();
                    },
                    error: function(XmlHttprequest, textStatus, errorThrown){
                        window.location.reload();
                    }
                }
            );
        });

    });


    function strip(value){
        return value.replace(/(^\s+|\s+$)/, '');
    }

    function get_csrf(){
        return $('input[name=csrfmiddlewaretoken]').attr('value');
    }


    function make_warning(obj, text) {
        $(obj).text(text);
        $(obj).show(100);
    }

    // get notifies
    function get_notifies() {
        $.ajax(
            {
                type: 'GET',
                url: '/notifies',
                data: {},
                dateType: 'json',
                async: true,
                success: function(data){
                    if(data.length>0) {
                        var len = data.length >= 100 ? '99+' : data.length;
                        $('#notifya span').text(len);
                        var $ul = $('#notifya').next();
                        data.forEach(function(item){
                            var $li = $('<li class="link" />');
                            $li.append(item);
                            $li.appendTo($ul);
                        });
                        bind_noify_click_event();
                    }
                    else {
                    }
                },
                error: function(XmlHttprequest, textStatus, errorThrown){
                }
            }
        );
    }


    function bind_noify_click_event() {
        $('a.notifyme').click(function(){
            var nid = $(this).attr('noti-id');
            $.ajax(
                {
                    type: 'POST',
                    url: '/notify/confirm',
                    data: {
                        nid: nid,
                        csrfmiddlewaretoken: get_csrf()
                    },
                    dateType: 'json',
                    async: false,
                    success: function(data){
                        return true;
                    },
                    error: function(XmlHttprequest, textStatus, errorThrown){
                        return true;
                    }
                }
            );
        });
    }


})(window, jQuery);

