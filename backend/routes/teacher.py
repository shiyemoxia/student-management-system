from flask import Blueprint, request, jsonify, session
from ..models import Teacher, Title, College
from ..utils import login_required, admin_required, teacher_required

# 创建教师相关的蓝图
teacher_bp = Blueprint('teacher', __name__)

@teacher_bp.route('/', methods=['GET'])
@login_required
def get_teachers():
    """获取教师列表
    
    获取所有教师信息的分页列表，支持按名称或教师号搜索
    
    URL参数:
        page: 页码，默认为1
        search: 搜索关键词，可选
        
    返回:
        成功: {
            teachers: [教师对象列表],
            total: 教师总数,
            page: 当前页码
        }
        失败: {error: '错误信息'}, 状态码
    
    权限要求:
        需要登录，学生用户无权访问
    """
    # 检查权限：学生无权访问教师列表
    if session.get('role') == 'student':
        return jsonify({'error': '学生无权查看教师列表'}), 403
        
    # 获取页码和搜索参数
    page = int(request.args.get('page', 1))
    search = request.args.get('search', None)
    
    # 实例化教师模型并获取教师列表
    teacher_model = Teacher()
    teachers, total = teacher_model.get_all_teachers(page=page, search=search)
    
    # 返回教师列表、总数和页码
    return jsonify({
        'teachers': teachers,
        'total': total,
        'page': page
    })

@teacher_bp.route('/<int:teacher_id>', methods=['GET'])
@login_required
def get_teacher(teacher_id):
    """获取单个教师信息
    
    根据教师ID获取特定教师的详细信息
    
    URL参数:
        teacher_id: 教师ID
        
    返回:
        成功: {teacher: 教师对象}
        失败: {error: '错误信息'}, 状态码
    
    权限要求:
        需要登录，学生用户无权访问
    """
    # 检查权限：学生无权访问教师详情
    if session.get('role') == 'student':
        return jsonify({'error': '学生无权查看教师详情'}), 403
        
    # 实例化教师模型并获取特定教师
    teacher_model = Teacher()
    teacher = teacher_model.get_teacher_by_id(teacher_id)
    
    if teacher:
        # 找到教师，返回教师信息
        return jsonify({'teacher': teacher})
    else:
        # 未找到教师
        return jsonify({'error': '教师不存在'}), 404

@teacher_bp.route('/', methods=['POST'])
@admin_required
def add_teacher():
    """添加新教师
    
    创建新的教师记录
    
    请求体:
        teacher_no: 教师工号
        name: 姓名
        gender: 性别
        college_id: 所属学院ID
        以及其他可选字段
        
    返回:
        成功: {success: true, message: '教师添加成功'}
        失败: {error: '错误信息'}, 状态码
    
    权限要求:
        需要管理员权限
    """
    # 获取请求中的JSON数据
    data = request.get_json()
    
    # 验证必填字段
    required_fields = ['teacher_no', 'name', 'gender', 'college_id']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'error': f'字段 {field} 不能为空'}), 400
    
    # 实例化教师模型并添加教师
    teacher_model = Teacher()
    result = teacher_model.add_teacher(data)
    
    if result:
        # 添加成功
        return jsonify({'success': True, 'message': '教师添加成功'})
    else:
        # 添加失败
        return jsonify({'error': '教师添加失败'}), 500

@teacher_bp.route('/<int:teacher_id>', methods=['PUT'])
@admin_required
def update_teacher(teacher_id):
    """更新教师信息
    
    根据教师ID更新教师信息
    
    URL参数:
        teacher_id: 教师ID
        
    请求体:
        teacher_no: 教师工号
        name: 姓名
        gender: 性别
        college_id: 所属学院ID
        以及其他字段
        
    返回:
        成功: {success: true, message: '教师信息更新成功'}
        失败: {error: '错误信息'}, 状态码
    
    权限要求:
        需要管理员权限
    """
    # 获取请求中的JSON数据
    data = request.get_json()
    
    # 验证必填字段
    required_fields = ['teacher_no', 'name', 'gender', 'college_id']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'error': f'字段 {field} 不能为空'}), 400
    
    # 实例化教师模型并更新教师信息
    teacher_model = Teacher()
    result = teacher_model.update_teacher(teacher_id, data)
    
    if result:
        # 更新成功
        return jsonify({'success': True, 'message': '教师信息更新成功'})
    else:
        # 更新失败
        return jsonify({'error': '教师信息更新失败'}), 500

@teacher_bp.route('/<int:teacher_id>', methods=['DELETE'])
@admin_required
def delete_teacher(teacher_id):
    """删除教师
    
    根据教师ID删除教师记录
    
    URL参数:
        teacher_id: 教师ID
        
    返回:
        成功: {success: true, message: '教师删除成功'}
        失败: {error: '错误信息'}, 状态码
    
    权限要求:
        需要管理员权限
    """
    # 实例化教师模型并删除教师
    teacher_model = Teacher()
    result = teacher_model.delete_teacher(teacher_id)
    
    if result:
        # 删除成功
        return jsonify({'success': True, 'message': '教师删除成功'})
    else:
        # 删除失败
        return jsonify({'error': '教师删除失败'}), 500

@teacher_bp.route('/title', methods=['GET'])
@login_required
def get_titles():
    """获取职称列表
    
    获取所有职称的列表，用于教师信息表单中的选择
    
    返回:
        {titles: [职称对象列表]}
    
    权限要求:
        需要登录，学生用户无权访问
    """
    # 检查权限：学生无权访问职称列表
    if session.get('role') == 'student':
        return jsonify({'error': '学生无权查看职称列表'}), 403
        
    # 实例化职称模型并获取职称列表
    title_model = Title()
    titles = title_model.get_all_titles()
    
    return jsonify({'titles': titles}) 