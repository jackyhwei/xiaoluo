from django.contrib.auth.models import User
from django.db import connection, models
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render
import json
import logging
from django.urls import reverse
from django.views import View
from django.contrib import auth
from ..omengine.utils.uuid_generator import generate
from omserver.model.model import CSysConfigModel
import os

from omserver.config.sys_config import g_config_dir, g_config_path, g_sys_code

logger = logging.getLogger(__name__)


# g_config_dir = os.path.dirname(os.path.abspath(__file__))
# g_config_path = os.path.join(g_config_dir, 'default_config.json')
# g_sys_code = "adminSettings"


def auth_sys_user_create():
    user = User.object.create_superuser(username='jacky',password='123456', email='jacky@rg4.net', is_superuse=1, is_active=1)

def auth_create_user():
    with connection.cursor() as cursor:
        cursor.execute("INSERT INTO auth_user (username, password) VALUES ('newuser', 'password')")

def auth_user_count():
    return User.objects.all()

def auth_update_user(user_id, **kwargs):
    user = User.objects.get(pk=user_id)
    for key, value in kwargs.items():
        setattr(user, key, value)
    user.save()

def auth_delete_user(user_id):
    user = User.objects.get(pk=user_id)
    user.delete()

def auth_is_authenticated(request):
    # 如果登陆了,结果为布尔值Ture,否则为False
    return request.user.is_authenticated

# 我们如果不指定这里的url,就不会跳转到我们制作的登陆页面.
# @login_required(login_url='/login/')  局部配置 
# @login_required                        全局配置
# 配置文件：LOGIN_URL = '/login/'
# 配置文件中修改,会让全局的@login_required影响下的视图函数/类全都跳转向一个页面

def auth_check_password(request):
    return request.user.check_password("原密码")

@login_required
def auth_change_password(request):
    request.user.set_password("新密码")
    request.user.save()

@login_required
def set_password(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        '''校验原密码是否正确 自定加密并检验'''
        is_right = request.user.check_password(old_password)
        if is_right:
            request.user.set_password(new_password)  # 修改密码
            request.user.save()  # 保存数据
    return render(request, 'set_password.html')

'''自动清除Cookie与Session'''
@login_required
def logout(request):
    request.session.flush()
    auth.logout(request)  # 自动清楚cookie和Session

    # 退出成功，重定向到登录界面
    return render(request, "login.html", None)

from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def login(request):
    print(f"request.user.is_authenticated={request.user.is_authenticated}")  # True表示存在此用户，
    print(f"request.user={request.user}")  # 没有登录显示：AnonymousUser匿名用户    登录显示登录的用户对象数据
    print(f"request.user.is_superuser={request.user.is_superuser}")

    '''
    用户登录成功之后执行Auth.login 该方法返回当前登录用户对象  admin
    用户没有登录成功没有执行Auth.login 该方法返回匿名用户对象  AnonymousUser
    '''
    
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        user_id = 0

        logger.debug(f"username={username}, email={email}, password={password}, user_id={user_id}")

        # if not User.objects.filter(username=username):
        #     message = "用户不存在"
        #     return render(request, "login.html", locals())
        try:
            user = User.objects.get(email=email)
            user_id = user.id
            username = user.username
            logger.debug(f"username={username}, email={email}, password={password}, user_id={user_id}")
        except User.DoesNotExist:
            message = "用户不存在"
            logger.warn(f"user {username} does not exist")
            return render(request, "login.html", locals())
            # target= reverse('omserver.login')
            # return redirect(target, locals())

        user = auth.authenticate(username=username, password=password)
        if not user:
            message = "密码错误或账号被禁用"
            return render(request, "login.html", locals())
            # target= reverse('omserver/login')
            # return redirect(target, locals())

        # 登录成功
        auth.login(request, user)

        # 向session中添加额外信息
        request.session["is_login"] = True
        request.session["user_name"] = user.username
        request.session["user_id"] = user_id

        logger.debug(f"username={username}, email={email}, password={password}, user_id={user_id}")

        # 检查是否已经有sysconfig
        default_sys_config_json = "{}"
        cfg = CSysConfigModel.objects.filter(code=g_sys_code, user_id=user_id).first()
        if cfg == None:
            logger.debug("=> save default sys config to db")
            print("\n\n[sys_config] config_path=%s\n\n" %(g_config_path))

            with open(g_config_path, 'r', encoding='utf-8') as f:
                default_sys_config_json = json.load(f)
                print("\n\nsys_config_json=%s\n\n" %(default_sys_config_json))

            sys_config_model = CSysConfigModel(code=g_sys_code, config=json.dumps(default_sys_config_json), user_id=user_id)
            sys_config_model.save()
        else:
            default_sys_config_json = json.loads(cfg.config)

        request.session["cfg"] = json.dumps(default_sys_config_json)

        # 登录完成，重定向到主页
        # return render(request, "index.html", locals())
        target= reverse('omserver/index')
        return redirect(target, locals())
    else:
        # GET
        for i in request.session.keys():
            print(f"{i}:{request.session[i]}")

        return render(request, "login.html", locals())

def login_face(request):
    return render(request,'login_face.html')

def user_pwd(request):
    if request.method == "POST":
        # POST
        email = request.POST.get('email')
        password = request.POST.get('password')

        logger.debug(f"change password request, email={email}, password={password}")

        if User.objects.filter(email=email):
            message = "邮箱已注册，开始重置密码"
            context = {"message": message, "email": email}
            return render(request, "recover-password.html", context)
        else:
            message = "无效的邮箱ID"
            return render(request, "forgot-password.html")

    else:
        return render(request, "user_pwd.html")

# def register(request):
#     User.objects.create(username='Like', password=123, email='120@qq.com')    # 这里创建的是普通用户 不能登录管理员系统
#     return HttpResponse('注册成功！！！')

def forgotpassword(request):
    if request.method == "POST":
        email = request.POST.get('email')

        logger.debug(f"forgot password: email={email}")

        # check inputs
        if email == "":
            message = "无效输入"
            # return render(request, "recover-password.html", locals())
            target= reverse('omserver/fogotpassword', locals())
            return redirect(target)

        # check whether account exists
        try:
            user = User.objects.get(email=email)
            username = user.username
            logger.debug(f"username={username}, email={email}")
        except User.DoesNotExist:
            message = "用户不存在"
            target= reverse('omserver/forgotpassword', locals())
            return redirect(target)

        context = {"email": email}
        # target= reverse('omserver/recoverpassword')
        # return redirect(target, context)
        return render(request, "recover-password.html", context)

    else:
        return render(request, "forgot-password.html")

def recoverpassword(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        authcode = request.POST.get('authcode')

        logger.debug(f"recover password request, email={email}, password={password}, authcode={authcode}")

        # check inputs
        if email == "" or password == "" or authcode == "":
            message = "无效输入"
            return render(request, "recover-password.html", locals())

        # check whether account exists
        try:
            user = User.objects.get(email=email)
            username = user.username
            logger.debug(f"username={username}, email={email}, password={password}")
        except User.DoesNotExist:
            message = "用户不存在"
            return render(request, "login.html", locals())
        
        # if authcode != user.authcode:
        #     message = "验证码错误"
        #     return render(request, "recover-password.html", locals())
        if authcode != "OddMeta":
            message = "验证码错误"
            return render(request, "recover-password.html", locals())
        
        # save new password to db
        user.set_password(password)
        user.save()

        # login with new password
        auth.login(request, user)

        # 向session中添加额外信息
        request.session["is_login"] = True
        request.session["user_name"] = user.username

        # redirect to index
        logger.debug("redirecting to index.html")
        #return render(request, "index.html", locals())
        target= reverse('omserver/index')
        return redirect(target)
    else:
        logger.warn("invalid access to recover password page, jump to login.html")
        return render(request, "recover-password.html")

def register(request):
    if request.method == "POST":
        # POST
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')

        # FIXME 要想办法把auth_user表里的username改成non-unique，然后以email为unique

        # if User.objects.filter(username=username):
        #     message = "用户已存在"
        #     return render(request, "register.html", locals())

        if User.objects.filter(email=email):
            message = "邮箱已注册，请使用找回密码功能"
            return render(request, "register.html", locals())
        
        if (username == "" or username == None):
            try:
                n = email.index('@')
                username = email.split('@')[0]
                logger.debug(f"try prefix name of the email addr, username: {username}")
                if User.objects.filter(username=username):
                    # 想办法让用户自己进系统后可以改username
                    username = generate()
                    logger.debug(f"use randon guid as username: {username}")
            except ValueError:
                logger.error("invalid email address, can not find character @")
                message = "无效的邮箱地址"
                return render(request, "register.html", locals())

        # user = User.objects.create(username=username, password=password, email=email)    # 这里创建的是普通用户 不能登录管理员系统
        user = User.objects.create_user(username=username,password=password, email=email, is_superuser=False, is_active=True)

        if not user:
            message = "服务器错误"
            return render(request, "register.html", locals())

        auth.login(request, user)

        # 向session中添加额外信息
        request.session["is_login"] = True
        request.session["user_name"] = user.username

        # 重定向到主页
        user_id = user.pk
        # 使用redirect并添加查询参数
        redirect_url = 'index.html?user_id={}'.format(user_id)
        return redirect(redirect_url)
        # return render(request, "register.html", locals())
    else:
        # GET
        for i in request.session.keys():
            print(f"{i}:{request.session[i]}")
        return render(request, "register.html", locals())
