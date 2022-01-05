# _*_ coding:utf-8 _*_
import os
import uuid
from datetime import datetime
from app import db
from . import admin
from flask import render_template, redirect, url_for, flash, session, request, g, abort,make_response,current_app
from app.admin.forms import LoginForm
from app.models import Admin,Adminlog,Oplog,Userlog,Area,User,Suggestion,Scenic,Travels
from werkzeug.utils import secure_filename
from sqlalchemy import or_ , and_
from functools import wraps

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