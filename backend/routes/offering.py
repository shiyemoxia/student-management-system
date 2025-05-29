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