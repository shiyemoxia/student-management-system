from flask import Blueprint, request, jsonify
from ..models import CourseOffering, Course, Teacher
from ..utils import login_required, admin_required, teacher_required

offering_bp = Blueprint('offering', __name__)

@offering_bp.route('/', methods=['GET'])
@login_required
def get_offerings():
    """获取授课安排列表"""
    page = int(request.args.get('page', 1))
    search = request.args.get('search', None)
    
    offering_model = CourseOffering()
    offerings, total = offering_model.get_all_offerings(page=page, search=search)
    
    return jsonify({
        'offerings': offerings,
        'total': total,
        'page': page
    })

@offering_bp.route('/<int:offering_id>', methods=['GET'])
@login_required
def get_offering(offering_id):
    """获取单个授课安排信息"""
    offering_model = CourseOffering()
    offering = offering_model.get_offering_by_id(offering_id)
    
    if offering:
        return jsonify({'offering': offering})
    else:
        return jsonify({'error': '授课安排不存在'}), 404

@offering_bp.route('/', methods=['POST'])
@admin_required
def add_offering():
    """添加新授课安排"""
    data = request.get_json()
    
    # 验证必填字段
    required_fields = ['course_id', 'teacher_id', 'semester', 'year']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'error': f'字段 {field} 不能为空'}), 400
    
    offering_model = CourseOffering()
    result = offering_model.add_offering(data)
    
    if result:
        return jsonify({'success': True, 'message': '授课安排添加成功'})
    else:
        return jsonify({'error': '授课安排添加失败'}), 500

@offering_bp.route('/<int:offering_id>', methods=['PUT'])
@admin_required
def update_offering(offering_id):
    """更新授课安排信息"""
    data = request.get_json()
    
    # 验证必填字段
    required_fields = ['course_id', 'teacher_id', 'semester', 'year']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'error': f'字段 {field} 不能为空'}), 400
    
    offering_model = CourseOffering()
    result = offering_model.update_offering(offering_id, data)
    
    if result:
        return jsonify({'success': True, 'message': '授课安排信息更新成功'})
    else:
        return jsonify({'error': '授课安排信息更新失败'}), 500

@offering_bp.route('/<int:offering_id>', methods=['DELETE'])
@admin_required
def delete_offering(offering_id):
    """删除授课安排"""
    offering_model = CourseOffering()
    result = offering_model.delete_offering(offering_id)
    
    if result:
        return jsonify({'success': True, 'message': '授课安排删除成功'})
    else:
        return jsonify({'error': '授课安排删除失败'}), 500 