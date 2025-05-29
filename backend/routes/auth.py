from flask import Blueprint, request, jsonify, session
from ..models import User
from ..utils import hash_password

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': '用户名和密码不能为空'}), 400
    
    user_model = User()
    user = user_model.authenticate(username, password)
    
    if user:
        session['user_id'] = user['user_id']
        session['username'] = user['username']
        session['role'] = user['role']
        session['related_id'] = user['related_id']
        
        return jsonify({
            'success': True,
            'user': {
                'user_id': user['user_id'],
                'username': user['username'],
                'role': user['role']
            }
        })
    else:
        return jsonify({'error': '用户名或密码错误'}), 401

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """用户登出"""
    session.clear()
    return jsonify({'success': True})

@auth_bp.route('/check_auth', methods=['GET'])
def check_auth():
    """检查用户是否已登录"""
    if 'user_id' in session:
        return jsonify({
            'authenticated': True,
            'user': {
                'user_id': session['user_id'],
                'username': session['username'],
                'role': session['role']
            }
        })
    else:
        return jsonify({'authenticated': False}) 