# _*_ coding:utf-8 _*_
import os
import uuid
from datetime import datetime
from app import db
from . import admin
from flask import render_template, redirect, url_for, flash, session, request, g, abort,make_response,current_app
from app.admin.forms import LoginForm,PwdForm,AreaForm,ScenicForm,TravelsForm
from app.models import Admin,Adminlog,Oplog,Userlog,Area,User,Suggestion,Scenic,Travels
from werkzeug.utils import secure_filename
from sqlalchemy import or_ , and_
from functools import wraps


def admin_login(f):
    """
    登录装饰器
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "admin" not in session:
            return redirect(url_for("admin.login", next=request.url))
        return f(*args, **kwargs)

    return decorated_function

def addOplog(reason):
    oplog = Oplog(
        admin_id=session["admin_id"],
        ip=request.remote_addr,
        reason=reason
    )
    db.session.add(oplog)
    db.session.commit()

def gen_rnd_filename():
    return datetime.now().strftime("%Y%m%d%H%M%S") + str(uuid.uuid4().hex)

def change_filename(filename):
    """
    修改文件名称
    """
    fileinfo = os.path.splitext(filename)
    filename =  gen_rnd_filename() + fileinfo[-1]
    return filename


@admin.route("/")
@admin_login
def index():
    return render_template("admin/index.html")

@admin.route("/login/", methods=["GET", "POST"])
def login():
    """
    登录功能
    """
    form = LoginForm()   # 实例化登录表单
    if form.validate_on_submit():   # 验证提交表单
        data = form.data    # 接收数据
        admin = Admin.query.filter_by(name=data["account"]).first() # 查找Admin表数据
        # 密码错误时，check_pwd返回false,则此时not check_pwd(data["pwd"])为真。
        if not admin.check_pwd(data["pwd"]):
            flash("密码错误!", "err")   # 闪存错误信息
            return redirect(url_for("admin.login")) # 跳转到后台登录页
        # 如果是正确的，就要定义session的会话进行保存。
        session["admin"] = data["account"]  # 存入session
        session["admin_id"] = admin.id # 存入session
        # 创建数据
        adminlog = Adminlog(
            admin_id=admin.id,
            ip=request.remote_addr,
        )
        db.session.add(adminlog) # 添加数据
        db.session.commit() # 提交数据
        return redirect(url_for("admin.index")) # 返回后台主页

    return render_template("admin/login.html",form=form)    

@admin.route('/logout/')
@admin_login
def logout():
    """
    后台注销登录
    """
    session.pop("admin", None)
    session.pop("admin_id", None)
    return redirect(url_for("admin.login"))

@admin.route('/pwd/',methods=["GET","POST"])
@admin_login
def pwd():
    """
    后台密码修改
    """
    form = PwdForm()
    if form.validate_on_submit():
        data = form.data
        admin = Admin.query.filter_by(name=session["admin"]).first()
        from werkzeug.security import generate_password_hash
        admin.pwd = generate_password_hash(data["new_pwd"])
        db.session.add(admin)
        db.session.commit()
        flash("修改密码成功，请重新登录！", "ok")
        return redirect(url_for('admin.logout'))
    return render_template("admin/pwd.html", form=form)


'''
会员的增删查改
'''
@admin.route("/user/list/", methods=["GET"])
@admin_login
def user_list():
    """
    会员列表
    """
    page = request.args.get('page', 1, type=int) # 获取page参数值 
    keyword = request.args.get('keyword', '', type=str)

    if keyword:
        # 根据姓名或者邮箱查询
        filters = or_(User.username == keyword, User.email == keyword)
        page_data = User.query.filter(filters).order_by(
            User.addtime.desc()
        ).paginate(page=page, per_page=5)
    else:
        page_data = User.query.order_by(
            User.addtime.desc()
        ).paginate(page=page, per_page=5)

    return render_template("admin/user_list.html", page_data=page_data)

@admin.route("/user/view/<int:id>/", methods=["GET"])
@admin_login
def user_view(id=None):
    """
    查看会员详情
    """
    from_page = request.args.get('fp')
    if not from_page:
        from_page = 1
    user = User.query.get_or_404(int(id))
    return render_template("admin/user_view.html", user=user, from_page=from_page)

@admin.route("/user/del/<int:id>/", methods=["GET"])
@admin_login
def user_del(id=None):
    """
    删除会员
    """
    page = request.args.get('page',1,type=int)
    user = User.query.get_or_404(int(id))
    db.session.delete(user)
    db.session.commit()
    addOplog("删除会员"+user.name)  # 添加日志
    flash("删除会员成功！", "ok")
    return redirect(url_for('admin.user_list', page=page))

'''意见的收集'''

@admin.route("/suggestion_list/list/", methods=["GET"])
@admin_login
def suggestion_list():
    """
    意见建议列表
    """
    page = request.args.get('page', 1, type=int) # 获取page参数值
    page_data = Suggestion.query.order_by(
        Suggestion.addtime.desc()
    ).paginate(page=page, per_page=5)
    return render_template("admin/suggestion_list.html", page_data=page_data)

@admin.route("/suggestion/del/<int:id>/", methods=["GET"])
@admin_login
def suggestion_del(id=None):
    """
    删除意见
    """
    page = request.args.get('page',1,type=int)
    suggestion = Suggestion.query.get_or_404(int(id))
    db.session.delete(suggestion)
    db.session.commit()
    addOplog("删除意见建议" )  # 添加日志
    flash("删除成功！", "ok")
    return redirect(url_for('admin.suggestion_list', page=page))

# 地区相关
@admin.route('/area/add/',methods=["GET","POST"])
@admin_login
def area_add():
    """
    添加地区
    """
    form = AreaForm()
    if form.validate_on_submit():
        data = form.data # 接收数据
        area = Area.query.filter_by(name=data["name"]).count()
        # 说明已经有这个地区了
        if area == 1:
            flash("地区已存在", "err")
            return redirect(url_for("admin.area_add"))
        area = Area(
            name=data["name"],     
            is_recommended = data['is_recommended'],
            introduction = data['introduction']
        )
        db.session.add(area)
        db.session.commit()
        addOplog("添加地区"+data["name"])  # 添加日志
        flash("地区添加成功", "ok")
        return redirect(url_for("admin.area_add"))
    return render_template("admin/area_add.html",form=form)

@admin.route("/area/edit/<int:id>", methods=["GET", "POST"])
@admin_login
def area_edit(id=None):
    """
    地区编辑
    """
    form = AreaForm()
    form.submit.label.text = "修改"
    area = Area.query.get_or_404(id)
    if request.method == "GET":
        form.name.data = area.name
        form.is_recommended.data = area.is_recommended
        form.introduction.data = area.introduction
    if form.validate_on_submit():
        data = form.data
        area_count = Area.query.filter_by(name=data["name"]).count()
        if area.name != data["name"] and area_count == 1:
            flash("地区已存在", "err")
            return redirect(url_for("admin.area_edit", id=area.id))
        area.name = data["name"]
        area.is_recommended = int(data["is_recommended"])
        area.introduction = data["introduction"]
        db.session.add(area)
        db.session.commit()
        flash("地区修改成功", "ok")
        return redirect(url_for("admin.area_edit", id=area.id))
    return render_template("admin/area_edit.html", form=form, area=area)

@admin.route("/area/list/", methods=["GET"])
@admin_login
def area_list():
    """
    标签列表
    """
    name = request.args.get('name',type=str)     # 获取name参数值
    page = request.args.get('page', 1, type=int) # 获取page参数值   
    if name: # 搜索功能
        page_data = Area.query.filter_by(name=name).order_by(
            Area.addtime.desc()
        ).paginate(page=page, per_page=5)
    else:   
        # 查找数据
        page_data = Area.query.order_by(
            Area.addtime.desc()
        ).paginate(page=page, per_page=5)
    return render_template("admin/area_list.html", page_data=page_data) # 渲染模板   


@admin.route("/area/del/<int:id>/", methods=["GET"])
@admin_login
def area_del(id=None):
    """
    标签删除
    """
    # filter_by在查不到或多个的时候并不会报错，get会报错。
    area = Area.query.filter_by(id=id).first_or_404()
    db.session.delete(area)
    db.session.commit()
    addOplog("删除地区"+area.name)  # 添加日志
    flash("地区<<{0}>>删除成功".format(area.name), "ok")
    return redirect(url_for("admin.area_list"))

