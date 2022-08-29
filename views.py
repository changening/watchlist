from flask import render_template, request, url_for, redirect, flash
from flask_login import login_user, login_required, logout_user, current_user

from . import app, db
from .models import User, Movie


# 处理表单数据
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if not current_user.is_authenticated:  # 如果当前用户未认证
            return redirect(url_for('index'))  # 重定向到主页
        # 获取表单数据
        title = request.form.get('title')
        year = request.form.get('year')
        # 验证数据
        if not title or not year or len(year) > 4 or len(title) > 60 or int(year) < 1900:
            flash('Invalid input') # 显示错误提示
            return redirect(url_for('index')) # 重定向回主页
        # 保存表单数据到数据库
        movie = Movie(title=title, year=year) # 创建记录
        db.session.add(movie) # 添加到数据库
        db.session.commit()   # 提交数据会话
        return redirect(url_for('index')) # 重定向回主页

    movies = Movie.query.all()
    return render_template('index.html', movies=movies)


# 编辑电影条目
@app.route('/movie/edit/<int:movie_id>', methods=['GET', 'POST'])
@login_required  # 登录保护
def edit(movie_id):
    # 使用了get_or_404()方法，它会返回对应主键的记录，如果没有找到，则返回404错误响应
    movie = Movie.query.get_or_404(movie_id)
    if request.method == 'POST':
        # 获取表单数据
        title = request.form.get('title')
        year = request.form.get('year')
        # 验证数据
        if not title or not year or len(year) > 4 or len(title) > 60 or nt(year) < 1900:
            flash('Invalid input') # 显示错误提示
            return redirect(url_for('edit', movie_id=movie_id)) # 重定向回对应的编辑页面
        # 保存表单数据到数据库
        movie.title = title # 更新标题
        movie.year = year   # 更新年份
        db.session.commit()   # 提交数据会话
        return redirect(url_for('index')) # 重定向回主页

    return render_template('index.html', movie=movie)


# 删除电影条目
@app.route('/movie/delote/<int:movie_id>', methods=['POST']) # 限定只接受POST请求
@login_required  # 登录保护
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id) # 获取电影记录
    db.session.delete(movie)
    db.session.commit()
    flash('Item deleted.')
    return redirect(url_for('index')) # 重定向回主页


# 用户登录试图函数，并判断密码是否正确
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('Invalid input.')
            return redirect(url_for('login'))

        user = User.query.first()

        if username == user.username and user.validate_password(password): # 验证用户名和密码是否一致
            login_user(user) # 登入用户
            flash('login success.')
            return redirect(url_for('index'))   # 重定向到主页
        flash('Invalid username or password.')  # 如果验证失败，显示错误消息
        return redirect(url_for('login'))       # 重定向回登录页面

    return render_template('login.html')


# 登出
@app.route('/logout')
@login_required # 用于视图保护
def logout():
    logout_user() # 登出用户
    flash('goodbye.')
    return redirect(url_for('index'))


# 设置用户名字
@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        name = request.form['name']

        if not name or len(name) > 20:
            flash('Invalid input.')
            return redirect(url_for('settings'))

        current_user.name = name
        db.session.commit()
        flash('Settings updated.')
        return redirect(url_for('index'))

    return render_template('settings.html')