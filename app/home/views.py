# _*_ coding: utf-8 _*_
from . import home
from app import db
from app.home.forms import LoginForm,RegisterForm,SuggetionForm
from app.models import User ,Area,Scenic,Travels,Collect,Suggestion,Userlog
from flask import render_template, url_for, redirect, flash, session, request
from werkzeug.security import generate_password_hash
from sqlalchemy import and_
from functools import wraps

def user_login(f):
    """
    登录装饰器
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("home.login"))
        return f(*args, **kwargs)

    return decorated_function

@home.route("/login/", methods=["GET", "POST"])
def login():
    """
    登录
    """
    form = LoginForm()              # 实例化LoginForm类
    if form.validate_on_submit():   # 如果提交
        data = form.data            # 接收表单数据
        # 判断用户名和密码是否匹配
        user = User.query.filter_by(email=data["email"]).first()    # 获取用户信息
        if not user :
            flash("邮箱不存在！", "err")           # 输出错误信息
            return redirect(url_for("home.login")) # 调回登录页
        if not user.check_pwd(data["pwd"]):     # 调用check_pwd()方法，检测用户名密码是否匹配
            flash("密码错误！", "err")           # 输出错误信息
            return redirect(url_for("home.login")) # 调回登录页

        session["user_id"] = user.id                # 将user_id写入session, 后面用户判断用户是否登录
        # 将用户登录信息写入Userlog表
        userlog = Userlog(
            user_id=user.id,
            ip=request.remote_addr
        )
        db.session.add(userlog) # 存入数据
        db.session.commit()     # 提交数据
        return redirect(url_for("home.index")) # 登录成功，跳转到首页
    return render_template("home/login.html", form=form) # 渲染登录页面模板

@home.route("/register/", methods=["GET", "POST"])
def register():
    """
    注册功能
    """
    form = RegisterForm()           # 导入注册表单
    if form.validate_on_submit():   # 提交注册表单
        data = form.data            # 接收表单数据
        # 为User类属性赋值
        user = User(
            username = data["username"],            # 用户名
            email = data["email"],                  # 邮箱
            pwd = generate_password_hash(data["pwd"]),# 对密码加密
        )
        db.session.add(user) # 添加数据
        db.session.commit()  # 提交数据
        flash("注册成功！", "ok") # 使用flask存储成功信息
    return render_template("home/register.html", form=form) # 渲染模板

@home.route("/logout/")
def logout():
    """
    退出登录
    """
    # 重定向到home模块下的登录。
    session.pop("user_id", None)
    return redirect(url_for('home.login'))    


@home.route("/")
def index():
    """
    首页
    """
    area = Area.query.all() # 获取所有城市
    hot_area = Area.query.filter_by(is_recommended = 1).limit(2).all() # 获取热门城市
    scenic = Scenic.query.filter_by(is_hot = 1).all() # 热门景区
    return render_template('home/index.html',area=area,hot_area=hot_area,scenic=scenic) # 渲染模板

@home.route("/info/<int:id>/")
def info(id=None):  # id 为景区ID
    """
    详情页
    """
    scenic = Scenic.query.get_or_404(int(id)) # 根据景区ID获取景区数据，如果不存在返回404
    user_id = session.get('user_id',None)    # 获取用户ID,判断用户是否登录
    if user_id :                              # 如果已经登录
        count = Collect.query.filter_by(      # 根据用户ID和景区ID判断用户是否已经收藏该景区
            user_id =int(user_id),
            scenic_id=int(id)
        ).count()
    else :                                    # 用户未登录状态
        user_id = 0
        count = 0    
    return render_template('home/info.html',scenic=scenic,user_id=user_id,count=count)   # 渲染模板

@home.route("/about/")
def about():
    """
    关于我们
    """
    return render_template('home/about.html')

@home.route("/contact/",methods=["GET", "POST"])
def contact():
    """
    联系我们
    """
    form = SuggetionForm()              # 实例化SuggestionForm类
    if form.validate_on_submit():       # 判断用户是否提交表单
        data = form.data                # 接收用户提交的数据
        # 为属性赋值
        suggestion = Suggestion(
            name = data["name"],
            email=data["email"],
            content = data["content"],
        )
        db.session.add(suggestion)       # 添加数据
        db.session.commit()              # 提交数据
        flash("发送成功！", "ok")        # 用flask存储发送成功消息
        form.content.data = ''           # 设置内容为空
    return render_template('home/contact.html',form=form) # 渲染模板，并传递表单数据