from flask import Blueprint, request, jsonify
from ..models import Teacher, Title, College
from ..utils import login_required, admin_required

teacher_bp = Blueprint('teacher', __name__)

@teacher_bp.route('/', methods=['GET'])
@login_required
def get_teachers():
    """获取教师列表"""
    page = int(request.args.get('page', 1))
    search = request.args.get('search', None)
    
    teacher_model = Teacher()
    teachers, total = teacher_model.get_all_teachers(page=page, search=search)
    
    return jsonify({
        'teachers': teachers,
        'total': total,
        'page': page
    })

@teacher_bp.route('/<int:teacher_id>', methods=['GET'])
@login_required
def get_teacher(teacher_id):
    """获取单个教师信息"""
    teacher_model = Teacher()
    teacher = teacher_model.get_teacher_by_id(teacher_id)
    
    if teacher:
        return jsonify({'teacher': teacher})
    else:
        return jsonify({'error': '教师不存在'}), 404

@teacher_bp.route('/', methods=['POST'])
@admin_required
def add_teacher():
    """添加新教师"""
    data = request.get_json()
    
    # 验证必填字段
    required_fields = ['teacher_no', 'name', 'gender', 'college_id']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'error': f'字段 {field} 不能为空'}), 400
    
    teacher_model = Teacher()
    result = teacher_model.add_teacher(data)
    
    if result:
        return jsonify({'success': True, 'message': '教师添加成功'})
    else:
        return jsonify({'error': '教师添加失败'}), 500

@teacher_bp.route('/<int:teacher_id>', methods=['PUT'])
@admin_required
def update_teacher(teacher_id):
    """更新教师信息"""
    data = request.get_json()
    
    # 验证必填字段
    required_fields = ['teacher_no', 'name', 'gender', 'college_id']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'error': f'字段 {field} 不能为空'}), 400
    
    teacher_model = Teacher()
    result = teacher_model.update_teacher(teacher_id, data)
    
    if result:
        return jsonify({'success': True, 'message': '教师信息更新成功'})
    else:
        return jsonify({'error': '教师信息更新失败'}), 500

@teacher_bp.route('/<int:teacher_id>', methods=['DELETE'])
@admin_required
def delete_teacher(teacher_id):
    """删除教师"""
    teacher_model = Teacher()
    result = teacher_model.delete_teacher(teacher_id)
    
    if result:
        return jsonify({'success': True, 'message': '教师删除成功'})
    else:
        return jsonify({'error': '教师删除失败'}), 500

@teacher_bp.route('/title', methods=['GET'])
@login_required
def get_titles():
    """获取职称列表"""
    title_model = Title()
    titles = title_model.get_all_titles()
    
    return jsonify({'titles': titles}) 