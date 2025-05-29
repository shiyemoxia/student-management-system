from flask import Blueprint, request, jsonify, session
from ..models import Score, Student, CourseOffering
from ..utils import login_required, admin_required, teacher_required

score_bp = Blueprint('score', __name__)

@score_bp.route('/<int:student_id>', methods=['GET'])
@login_required
def get_student_scores(student_id):
    """获取学生成绩"""
    # 检查权限：只有管理员、教师或学生本人可以查看
    if session.get('role') == 'student' and session.get('related_id') != student_id:
        return jsonify({'error': '无权限查看其他学生成绩'}), 403
    
    score_model = Score()
    scores = score_model.get_student_scores(student_id)
    
    return jsonify({'scores': scores})

@score_bp.route('/', methods=['POST'])
@teacher_required
def add_score():
    """添加成绩"""
    data = request.get_json()
    
    # 验证必填字段
    required_fields = ['student_id', 'offering_id', 'status']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'字段 {field} 不能为空'}), 400
    
    # 如果状态为已修完，必须有成绩
    if data['status'] == '已修完':
        if 'score' not in data or data['score'] is None:
            return jsonify({'error': '已修完状态必须填写成绩'}), 400
        
        # 验证分数范围
        score = data['score']
        if isinstance(score, (int, float)) and (score < 0 or score > 100):
            return jsonify({'error': '成绩必须在0-100之间'}), 400
    else:
        # 如果不是已修完状态，成绩设为None
        data['score'] = None
    
    score_model = Score()
    result = score_model.add_score(data)
    
    if result:
        return jsonify({'success': True, 'message': '成绩添加成功'})
    else:
        return jsonify({'error': '成绩添加失败'}), 500

@score_bp.route('/<int:sc_id>', methods=['PUT'])
@teacher_required
def update_score(sc_id):
    """更新成绩"""
    data = request.get_json()
    
    # 验证数据
    if 'score' in data and data['score'] is not None:
        score = data['score']
        if isinstance(score, (int, float)) and (score < 0 or score > 100):
            return jsonify({'error': '成绩必须在0-100之间'}), 400
    
    # 如果提供了状态
    if 'status' in data:
        if data['status'] == '已修完' and ('score' not in data or data['score'] is None):
            return jsonify({'error': '已修完状态必须填写成绩'}), 400
        
        score_model = Score()
        if 'score' in data:
            result = score_model.update_score_with_status(sc_id, data['score'], data['status'])
        else:
            result = score_model.update_status(sc_id, data['status'])
    else:
        # 仅更新成绩
        score_model = Score()
        result = score_model.update_score(sc_id, data['score'])
    
    if result:
        return jsonify({'success': True, 'message': '成绩更新成功'})
    else:
        return jsonify({'error': '成绩更新失败'}), 500

@score_bp.route('/<int:sc_id>', methods=['DELETE'])
@teacher_required
def delete_score(sc_id):
    """删除成绩记录"""
    score_model = Score()
    result = score_model.delete_score(sc_id)
    
    if result:
        return jsonify({'success': True, 'message': '成绩记录删除成功'})
    else:
        return jsonify({'error': '成绩记录删除失败'}), 500 