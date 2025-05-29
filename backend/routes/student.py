from flask import Blueprint, request, jsonify
from ..models import Student, Class, College
from ..utils import login_required, admin_required

student_bp = Blueprint('student', __name__)

@student_bp.route('/', methods=['GET'])
@login_required
def get_students():
    """获取学生列表"""
    page = int(request.args.get('page', 1))
    search = request.args.get('search', None)
    
    student_model = Student()
    students, total = student_model.get_all_students(page=page, search=search)
    
    return jsonify({
        'students': students,
        'total': total,
        'page': page
    })

@student_bp.route('/<int:student_id>', methods=['GET'])
@login_required
def get_student(student_id):
    """获取单个学生信息"""
    student_model = Student()
    student = student_model.get_student_by_id(student_id)
    
    if student:
        return jsonify({'student': student})
    else:
        return jsonify({'error': '学生不存在'}), 404

@student_bp.route('/', methods=['POST'])
@admin_required
def add_student():
    """添加新学生"""
    data = request.get_json()
    
    # 验证必填字段
    required_fields = ['student_no', 'name', 'gender', 'enrollment_date', 'class_id']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'error': f'字段 {field} 不能为空'}), 400
    
    student_model = Student()
    result = student_model.add_student(data)
    
    if result:
        return jsonify({'success': True, 'message': '学生添加成功'})
    else:
        return jsonify({'error': '学生添加失败'}), 500

@student_bp.route('/<int:student_id>', methods=['PUT'])
@admin_required
def update_student(student_id):
    """更新学生信息"""
    data = request.get_json()
    
    # 验证必填字段
    required_fields = ['student_no', 'name', 'gender', 'enrollment_date', 'class_id']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'error': f'字段 {field} 不能为空'}), 400
    
    student_model = Student()
    result = student_model.update_student(student_id, data)
    
    if result:
        return jsonify({'success': True, 'message': '学生信息更新成功'})
    else:
        return jsonify({'error': '学生信息更新失败'}), 500

@student_bp.route('/<int:student_id>', methods=['DELETE'])
@admin_required
def delete_student(student_id):
    """删除学生"""
    student_model = Student()
    result = student_model.delete_student(student_id)
    
    if result:
        return jsonify({'success': True, 'message': '学生删除成功'})
    else:
        return jsonify({'error': '学生删除失败'}), 500

@student_bp.route('/class', methods=['GET'])
@login_required
def get_classes():
    """获取班级列表"""
    class_model = Class()
    classes = class_model.get_all_classes()
    
    return jsonify({'classes': classes})

@student_bp.route('/college', methods=['GET'])
@login_required
def get_colleges():
    """获取学院列表"""
    college_model = College()
    colleges = college_model.get_all_colleges()
    
    return jsonify({'colleges': colleges}) 