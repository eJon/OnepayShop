# -*- coding: utf-8 -*-
__author__ = 'wog'

import inspect

from flask import request, current_app, session
from flask_wtf import Form
from wtforms import validators, StringField, SelectField, DateField,\
    PasswordField, SubmitField, BooleanField, Field, IntegerField,\
    TextField, TextAreaField, FloatField
from flask_security.forms import LoginForm, ConfirmRegisterForm, NextFormMixin, ValidatorMixin,\
    ResetPasswordForm, ForgotPasswordForm, email_required, email_validator, valid_user_email, password_required,\
    password_length, ChangePasswordForm
from flask_security.utils import get_message
from werkzeug.local import LocalProxy



_datastore = LocalProxy(lambda: current_app.extensions['security'].datastore)

not_null = u"不能为空"
data_err = u"格式错误或含有非法字符"


class RegisterFormMixin():
    def to_dict(form):
        def is_field_and_user_attr(member):
            return isinstance(member, Field) and \
                hasattr(_datastore.user_model, member.name)

        fields = inspect.getmembers(form, is_field_and_user_attr)
        return dict((key, value.data) for key, value in fields)

class EqualTo(ValidatorMixin, validators.EqualTo):
    pass


class PasswordConfirmFormMixin():
    password_confirm = PasswordField(
        u"重复密码",
        validators=[EqualTo('password', message=u"两次密码不相同")])


class LoginForms(LoginForm, NextFormMixin):
    email = StringField(u"邮箱",
        validators=[validators.DataRequired(not_null), validators.Email(data_err)])
    password = PasswordField(u"密码",
        validators=[validators.DataRequired(not_null),
                    validators.Length(min=6, max=32, message=data_err)]
    )
    remember = BooleanField('记住我')
    submit = SubmitField(u"登录")

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        if not self.next.data:
            self.next.data = request.args.get('next', '')
        self.remember.default = True#config_value('DEFAULT_REMEMBER_ME')

class RegisterForm(ConfirmRegisterForm, PasswordConfirmFormMixin,NextFormMixin):
    name = StringField(u"用户名",
        validators=[validators.DataRequired(not_null),
            validators.Length(min=3, max=16, message=data_err)])
    email = StringField(u"邮箱",
        validators=[validators.DataRequired(not_null), validators.Email(data_err)])
    password = PasswordField(u"密码",
        validators=[validators.DataRequired(not_null),
                    validators.Length(min=6, max=32, message=data_err)]
    )
    submit = SubmitField(u"注册")

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)

        if not self.next.data:
            self.next.data = request.args.get('next', '')
        if request.args.get("invitor"):
            session['invitor'] = request.args.get("invitor")
    def validate(self):
        if not super(RegisterForm, self).validate():
            return False
        #将邮箱转换成小写
        self.email.data = self.email.data.lower()
        user = _datastore.find_user(email=self.email.data)

        if user is not None:
            if user.active:
                self.email.errors.append(u"邮箱已经有人用了")
                return False
            else:
                user.delete_instance()

        if _datastore.find_user(name=self.name.data) is not None:
            self.name.errors.append(u"用户名已经有人用了")
            return False
        return True

class ForgotForm(ForgotPasswordForm):
    user = None
    email = StringField(
        u"邮箱地址",
        validators=[email_required, email_validator, valid_user_email])

class ChangeForm(ChangePasswordForm):
    """The default change password form"""
    password = PasswordField(
        u"旧密码",
        validators=[password_required])
    new_password = PasswordField(
        u"新密码",
        validators=[password_required, password_length])

    new_password_confirm = PasswordField(
        u"确认新密码",
        validators=[EqualTo('new_password', message='RETYPE_PASSWORD_MISMATCH')])

    #submit = SubmitField('<button type="submit" class="btn btn-success">123</button>')

class ResetForm(ResetPasswordForm):
    """The default change password form"""
    password = PasswordField(
        u"新密码",
        validators=[password_required, password_length])

    password_confirm = PasswordField(
        u"确认新密码",
        validators=[EqualTo('password', message='RETYPE_PASSWORD_MISMATCH')])
    def __init__(self, *args, **kwargs):
        super(ResetPasswordForm, self).__init__(*args, **kwargs)

