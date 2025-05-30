import hashlib
import functools
from flask import session, redirect, url_for, jsonify

def hash_password(password):
    """对密码进行哈希处理
    
    使用MD5算法对密码进行单向加密，提高安全性
    实际生产环境应使用更安全的算法如bcrypt或Argon2
    
    参数:
        password (str): 原始密码字符串
    
    返回:
        str: 经过哈希处理的密码字符串
    """
    return hashlib.md5(password.encode()).hexdigest()

def login_required(f):
    """登录验证装饰器
    
    用于保护需要登录才能访问的路由
    如果用户未登录，将重定向到登录页面
    
    参数:
        f (function): 被装饰的视图函数
    
    返回:
        function: 包含登录检查的新函数
    """
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """管理员权限验证装饰器
    
    用于保护只有管理员才能访问的路由
    如果用户未登录或不是管理员，将返回错误信息
    
    参数:
        f (function): 被装饰的视图函数
    
    返回:
        function: 包含权限检查的新函数
    """
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        if session.get('role') != 'admin':
            return jsonify({'error': '无权限访问'}), 403
        return f(*args, **kwargs)
    return decorated_function

def teacher_required(f):
    """教师权限验证装饰器
    
    用于保护只有教师或管理员才能访问的路由
    如果用户未登录或既不是教师也不是管理员，将返回错误信息
    
    参数:
        f (function): 被装饰的视图函数
    
    返回:
        function: 包含权限检查的新函数
    """
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        if session.get('role') not in ['admin', 'teacher']:
            return jsonify({'error': '无权限访问'}), 403
        return f(*args, **kwargs)
    return decorated_function

def student_self_required(f):
    """学生自身信息访问权限验证装饰器
    
    用于保护学生只能访问自己的信息的路由
    如果是学生角色，则只能访问自己的信息
    如果是管理员或教师，则可以访问所有学生信息
    
    参数:
        f (function): 被装饰的视图函数
        
    返回:
        function: 包含权限检查的新函数
    """
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
            
        # 如果是管理员或教师，允许访问
        if session.get('role') in ['admin', 'teacher']:
            return f(*args, **kwargs)
            
        # 如果是学生，只能访问自己的信息
        if session.get('role') == 'student':
            # 获取URL中的student_id参数
            student_id = kwargs.get('student_id')
            # 如果没有提供student_id或者不是查看自己的信息，则拒绝访问
            if not student_id or int(student_id) != session.get('related_id'):
                return jsonify({'error': '您只能查看自己的信息'}), 403
                
        return f(*args, **kwargs)
    return decorated_function

def format_date(date_str):
    """格式化日期字符串
    
    处理从数据库返回的日期字符串
    
    参数:
        date_str (str): 原始日期字符串
    
    返回:
        str or None: 格式化后的日期字符串，若输入为空则返回None
    """
    if not date_str:
        return None
    return date_str

def paginate(items, page, per_page):
    """分页函数
    
    将列表按指定的页码和每页数量进行分页处理
    
    参数:
        items (list): 要分页的项目列表
        page (int): 页码，从1开始
        per_page (int): 每页包含的项目数
    
    返回:
        list: 指定页的项目子集
    """
    page = int(page)
    start = (page - 1) * per_page
    end = start + per_page
    
    return items[start:end] 