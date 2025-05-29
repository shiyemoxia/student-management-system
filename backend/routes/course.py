from flask import Blueprint, request, jsonify
from ..models import Course, CourseType, College
from ..utils import login_required, admin_required, teacher_required

course_bp = Blueprint('course', __name__)

@course_bp.route('/', methods=['GET'])
@login_required
def get_courses():
    """获取课程列表"""
    page = int(request.args.get('page', 1))
    search = request.args.get('search', None)
    
    course_model = Course()
    courses, total = course_model.get_all_courses(page=page, search=search)
    
    return jsonify({
        'courses': courses,
        'total': total,
        'page': page
    })

@course_bp.route('/<int:course_id>', methods=['GET'])
@login_required
def get_course(course_id):
    """获取单个课程信息"""
    course_model = Course()
    course = course_model.get_course_by_id(course_id)
    
    if course:
        return jsonify({'course': course})
    else:
        return jsonify({'error': '课程不存在'}), 404

@course_bp.route('/', methods=['POST'])
@admin_required
def add_course():
    """添加新课程"""
    data = request.get_json()
    
    # 验证必填字段
    required_fields = ['course_code', 'course_name', 'credit', 'hours', 'type_id', 'college_id']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'error': f'字段 {field} 不能为空'}), 400
    
    course_model = Course()
    result = course_model.add_course(data)
    
    if result:
        return jsonify({'success': True, 'message': '课程添加成功'})
    else:
        return jsonify({'error': '课程添加失败'}), 500

@course_bp.route('/<int:course_id>', methods=['PUT'])
@admin_required
def update_course(course_id):
    """更新课程信息"""
    data = request.get_json()
    
    # 验证必填字段
    required_fields = ['course_code', 'course_name', 'credit', 'hours', 'type_id', 'college_id']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'error': f'字段 {field} 不能为空'}), 400
    
    course_model = Course()
    result = course_model.update_course(course_id, data)
    
    if result:
        return jsonify({'success': True, 'message': '课程信息更新成功'})
    else:
        return jsonify({'error': '课程信息更新失败'}), 500

@course_bp.route('/<int:course_id>', methods=['DELETE'])
@admin_required
def delete_course(course_id):
    """删除课程"""
    course_model = Course()
    result = course_model.delete_course(course_id)
    
    if result:
        return jsonify({'success': True, 'message': '课程删除成功'})
    else:
        return jsonify({'error': '课程删除失败'}), 500

@course_bp.route('/type', methods=['GET'])
@login_required
def get_course_types():
    """获取课程类型列表"""
    course_type_model = CourseType()
    course_types = course_type_model.get_all_course_types()
    
    return jsonify({'course_types': course_types}) 