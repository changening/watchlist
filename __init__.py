import os
import sys

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


# SQLite URI 兼容配置
WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'   # 如果是 Windows 系统，使用三个斜线
else:
    prefix = 'sqlite:////'  # 否则使用四个斜线

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev' # 设置签名所需的密钥
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(os.path.dirname(app.root_path), 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭对模型修改的监控
# 在扩展类实例化前加载配置
db = SQLAlchemy(app)

login_manager = LoginManager(app)  # 实例化扩展类
# 初始化 Flask-Login
@login_manager.user_loader
def load_user(user_id):  # 创建用户加载回调函数，接受用户 ID 作为参数
    from .models import User
    user = User.query.get(int(user_id))  # 用 ID 作为 User 模型的主键查询对应的用户
    return user  # 返回用户对象

login_manager.login_view = 'login'


# 上下文处理函数
@app.context_processor
def inject_user():
    from .models import User
    user = User.query.first()
    return dict(user=user)

from . import views, errors, commands