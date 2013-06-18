(function(window, $){
    $(function(){
        $('#siteuserLogin').click(function(e){
            e.preventDefault();
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
                    url: '/account/login/',
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
                    url: '/account/register/',
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
                    url: '/account/logout/',
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
        
        get_notifies();

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
                url: '/notifies.json/',
                data: {},
                dateType: 'json',
                async: true,
                success: function(data){
                    if(data.length>0) {
                        var len = data.length > 10 ? '9+' : data.length;
                        $('#siteuserNotify').text(len);
                        var $ul = $('<ul/>');
                        $ul.attr('id', 'siteusernotifyul');
                        data.forEach(function(item){
                            var $li = $('<li/>');
                            $li.append(item);
                            $li.appendTo($ul);
                        });
                        $('#siteuserNotify').after($ul);
                        bind_notify_click_event();
                    }
                    else {
                        $('#siteuserNotify').text(0);
                    }
                },
                error: function(XmlHttprequest, textStatus, errorThrown){
                }
            }
        );
    }

    function bind_notify_click_event() {
        $('#siteusernotifyul>li>a:odd').click(function(){
            $(this).parent().hide();
        });
    }

})(window, jQuery);

