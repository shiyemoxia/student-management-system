from flask import Blueprint, request, jsonify, session
from ..models import User
from ..utils import hash_password, login_required, admin_required

# 创建认证相关的蓝图
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录
    
    处理用户的登录请求，验证用户名和密码
    如果验证成功，将用户信息存储在会话中，并返回成功响应
    如果验证失败，返回错误响应
    
    请求参数:
        username: 用户名
        password: 密码
        
    返回:
        成功: {success: true, user: {user_id, username, role}}
        失败: {error: '错误信息'}, 状态码
    """
    # 获取请求中的JSON数据
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    # 验证用户名和密码是否提供
    if not username or not password:
        return jsonify({'error': '用户名和密码不能为空'}), 400
    
    # 实例化用户模型并验证用户身份
    user_model = User()
    user = user_model.authenticate(username, password)
    
    if user:
        # 身份验证成功，将用户信息存储在会话中
        session['user_id'] = user['user_id']  # 用户ID
        session['username'] = user['username']  # 用户名
        session['role'] = user['role']  # 用户角色（admin/teacher/student）
        session['related_id'] = user['related_id']  # 关联ID（如学生ID或教师ID）
        
        # 返回成功响应和用户信息
        return jsonify({
            'success': True,
            'user': {
                'user_id': user['user_id'],
                'username': user['username'],
                'role': user['role']
            }
        })
    else:
        # 身份验证失败
        return jsonify({'error': '用户名或密码错误'}), 401

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """用户登出
    
    清除用户会话，完成用户注销
    
    返回:
        {success: true} - 表示成功注销
    """
    # 清除会话中的所有数据
    session.clear()
    return jsonify({'success': True})

@auth_bp.route('/check_auth', methods=['GET'])
def check_auth():
    """检查用户是否已登录
    
    验证当前会话中是否包含用户信息
    用于前端验证用户登录状态，保持用户会话
    
    返回:
        已登录: {authenticated: true, user: {user_id, username, role}}
        未登录: {authenticated: false}
    """
    if 'user_id' in session:
        # 用户已登录，返回认证成功和用户信息
        return jsonify({
            'authenticated': True,
            'user': {
                'user_id': session['user_id'],
                'username': session['username'],
                'role': session['role']
            }
        })
    else:
        # 用户未登录，返回认证失败的JSON响应
        return jsonify({'authenticated': False}) 