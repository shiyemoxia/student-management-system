from flask import Blueprint, request, jsonify, session
from ..models import Score, Student, CourseOffering
from ..utils import login_required, admin_required, teacher_required

# 创建成绩相关的蓝图
score_bp = Blueprint('score', __name__)

@score_bp.route('/<int:student_id>', methods=['GET'])
@login_required
def get_student_scores(student_id):
    """获取学生成绩
    
    根据学生ID获取该学生的所有课程成绩
    包含权限验证，确保只有管理员、教师或学生本人可以查看成绩
    
    URL参数:
        student_id: 学生ID
        
    返回:
        成功: {scores: [成绩对象列表]}
        失败: {error: '错误信息'}, 状态码
    
    权限要求:
        需要登录，且只有管理员、教师或学生本人可以查看
    """
    # 检查权限：只有管理员、教师或学生本人可以查看
    if session.get('role') == 'student' and session.get('related_id') != student_id:
        return jsonify({'error': '无权限查看其他学生成绩'}), 403
    
    # 实例化成绩模型并获取学生成绩
    score_model = Score()
    scores = score_model.get_student_scores(student_id)
    
    return jsonify({'scores': scores})

@score_bp.route('/', methods=['POST'])
@teacher_required
def add_score():
    """添加成绩
    
    为学生添加课程成绩记录
    
    请求体:
        student_id: 学生ID
        offering_id: 授课安排ID
        status: 状态（如'已修完'、'在修'等）
        score: 成绩分数（如果状态为'已修完'，则必须提供）
        
    返回:
        成功: {success: true, message: '成绩添加成功'}
        失败: {error: '错误信息'}, 状态码
    
    权限要求:
        需要教师或管理员权限
    """
    # 获取请求中的JSON数据
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
    
    # 实例化成绩模型并添加成绩
    score_model = Score()
    result = score_model.add_score(data)
    
    if result:
        # 添加成功
        return jsonify({'success': True, 'message': '成绩添加成功'})
    else:
        # 添加失败
        return jsonify({'error': '成绩添加失败'}), 500

@score_bp.route('/<int:sc_id>', methods=['PUT'])
@teacher_required
def update_score(sc_id):
    """更新成绩
    
    根据成绩ID更新成绩信息，可更新成绩分数和/或状态
    
    URL参数:
        sc_id: 成绩ID
        
    请求体:
        score: 成绩分数，可选
        status: 状态，可选（如'已修完'、'在修'等）
        
    返回:
        成功: {success: true, message: '成绩更新成功'}
        失败: {error: '错误信息'}, 状态码
    
    权限要求:
        需要教师或管理员权限
    """
    # 获取请求中的JSON数据
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
        
        # 实例化成绩模型
        score_model = Score()
        
        if 'score' in data:
            # 同时更新成绩和状态
            result = score_model.update_score_with_status(sc_id, data['score'], data['status'])
        else:
            # 仅更新状态
            result = score_model.update_status(sc_id, data['status'])
    else:
        # 仅更新成绩
        score_model = Score()
        result = score_model.update_score(sc_id, data['score'])
    
    if result:
        # 更新成功
        return jsonify({'success': True, 'message': '成绩更新成功'})
    else:
        # 更新失败
        return jsonify({'error': '成绩更新失败'}), 500

@score_bp.route('/<int:sc_id>', methods=['DELETE'])
@teacher_required
def delete_score(sc_id):
    """删除成绩记录
    
    根据成绩ID删除成绩记录
    
    URL参数:
        sc_id: 成绩ID
        
    返回:
        成功: {success: true, message: '成绩记录删除成功'}
        失败: {error: '错误信息'}, 状态码
    
    权限要求:
        需要教师或管理员权限
    """
    # 实例化成绩模型并删除成绩记录
    score_model = Score()
    result = score_model.delete_score(sc_id)
    
    if result:
        # 删除成功
        return jsonify({'success': True, 'message': '成绩记录删除成功'})
    else:
        # 删除失败
        return jsonify({'error': '成绩记录删除失败'}), 500 