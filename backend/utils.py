import hashlib
import functools
from flask import session, redirect, url_for, jsonify

def hash_password(password):
    """对密码进行哈希处理"""
    return hashlib.md5(password.encode()).hexdigest()

def login_required(f):
    """登录验证装饰器"""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """管理员权限验证装饰器"""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        if session.get('role') != 'admin':
            return jsonify({'error': '无权限访问'}), 403
        return f(*args, **kwargs)
    return decorated_function

def teacher_required(f):
    """教师权限验证装饰器"""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        if session.get('role') not in ['admin', 'teacher']:
            return jsonify({'error': '无权限访问'}), 403
        return f(*args, **kwargs)
    return decorated_function

def format_date(date_str):
    """格式化日期字符串"""
    if not date_str:
        return None
    return date_str

def paginate(items, page, per_page):
    """分页函数"""
    page = int(page)
    start = (page - 1) * per_page
    end = start + per_page
    
    return items[start:end] 