from flask import Blueprint, request, jsonify, session
from ..models import CourseOffering, Course, Teacher, Score
from ..utils import login_required, admin_required, teacher_required

# 创建授课安排相关的蓝图
offering_bp = Blueprint('offering', __name__)

@offering_bp.route('/', methods=['GET'])
@login_required
def get_offerings():
    """获取授课安排列表
    
    获取所有授课安排信息的分页列表，支持按课程名称、教师名称等搜索
    如果是学生用户，将只返回与该学生相关的授课安排
    
    URL参数:
        page: 页码，默认为1
        search: 搜索关键词，可选
        
    返回:
        {
            offerings: [授课安排对象列表],
            total: 授课安排总数,
            page: 当前页码
        }
    
    权限要求:
        需要登录，学生用户只能查看已选课程的授课安排
    """
    # 获取页码和搜索参数
    page = int(request.args.get('page', 1))
    search = request.args.get('search', None)
    
    # 实例化授课安排模型
    offering_model = CourseOffering()
    
    # 根据角色区分处理
    if session.get('role') == 'student':
        # 如果是学生用户，只返回与该学生相关的授课安排
        student_id = session.get('related_id')
        
        # 查询学生已选课程
        score_model = Score()
        scores = score_model.get_student_scores(student_id)
        
        # 从成绩记录中提取授课安排信息
        offerings = []
        for score in scores:
            offering = offering_model.get_offering_by_id(score['offering_id'])
            if offering:
                # 添加成绩信息到授课安排对象
                offering['score'] = score['score']
                offering['status'] = score['status']
                offerings.append(offering)
        
        return jsonify({
            'offerings': offerings,
            'total': len(offerings),
            'page': 1
        })
    else:
        # 管理员或教师可以查看所有授课安排
        offerings, total = offering_model.get_all_offerings(page=page, search=search)
        
        # 返回授课安排列表、总数和页码
        return jsonify({
            'offerings': offerings,
            'total': total,
            'page': page
        })

@offering_bp.route('/<int:offering_id>', methods=['GET'])
@login_required
def get_offering(offering_id):
    """获取单个授课安排信息
    
    根据授课安排ID获取特定授课安排的详细信息
    
    URL参数:
        offering_id: 授课安排ID
        
    返回:
        成功: {offering: 授课安排对象}
        失败: {error: '错误信息'}, 状态码
    
    权限要求:
        需要登录，学生用户只能查看已选课程的授课安排
    """
    # 实例化授课安排模型并获取特定授课安排
    offering_model = CourseOffering()
    offering = offering_model.get_offering_by_id(offering_id)
    
    if not offering:
        # 未找到授课安排
        return jsonify({'error': '授课安排不存在'}), 404
        
    # 检查学生权限
    if session.get('role') == 'student':
        student_id = session.get('related_id')
        
        # 查询学生是否已选该授课安排
        score_model = Score()
        scores = score_model.get_student_scores(student_id)
        
        offering_ids = [score['offering_id'] for score in scores]
        if offering_id not in offering_ids:
            return jsonify({'error': '您没有权限查看未选课程的授课安排'}), 403
    
    # 找到授课安排，返回授课安排信息
    return jsonify({'offering': offering})

@offering_bp.route('/', methods=['POST'])
@admin_required
def add_offering():
    """添加新授课安排
    
    创建新的授课安排记录，将课程与教师关联起来
    
    请求体:
        course_id: 课程ID
        teacher_id: 教师ID
        semester: 学期（如'春季'、'秋季'）
        year: 学年（如'2023-2024'）
        以及其他可选字段
        
    返回:
        成功: {success: true, message: '授课安排添加成功'}
        失败: {error: '错误信息'}, 状态码
    
    权限要求:
        需要管理员权限
    """
    # 获取请求中的JSON数据
    data = request.get_json()
    
    # 验证必填字段
    required_fields = ['course_id', 'teacher_id', 'semester', 'year']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'error': f'字段 {field} 不能为空'}), 400
    
    # 实例化授课安排模型并添加授课安排
    offering_model = CourseOffering()
    result = offering_model.add_offering(data)
    
    if result:
        # 添加成功
        return jsonify({'success': True, 'message': '授课安排添加成功'})
    else:
        # 添加失败
        return jsonify({'error': '授课安排添加失败'}), 500

@offering_bp.route('/<int:offering_id>', methods=['PUT'])
@admin_required
def update_offering(offering_id):
    """更新授课安排信息
    
    根据授课安排ID更新授课安排信息
    
    URL参数:
        offering_id: 授课安排ID
        
    请求体:
        course_id: 课程ID
        teacher_id: 教师ID
        semester: 学期
        year: 学年
        以及其他字段
        
    返回:
        成功: {success: true, message: '授课安排信息更新成功'}
        失败: {error: '错误信息'}, 状态码
    
    权限要求:
        需要管理员权限
    """
    # 获取请求中的JSON数据
    data = request.get_json()
    
    # 验证必填字段
    required_fields = ['course_id', 'teacher_id', 'semester', 'year']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'error': f'字段 {field} 不能为空'}), 400
    
    # 实例化授课安排模型并更新授课安排信息
    offering_model = CourseOffering()
    result = offering_model.update_offering(offering_id, data)
    
    if result:
        # 更新成功
        return jsonify({'success': True, 'message': '授课安排信息更新成功'})
    else:
        # 更新失败
        return jsonify({'error': '授课安排信息更新失败'}), 500

@offering_bp.route('/<int:offering_id>', methods=['DELETE'])
@admin_required
def delete_offering(offering_id):
    """删除授课安排
    
    根据授课安排ID删除授课安排记录
    
    URL参数:
        offering_id: 授课安排ID
        
    返回:
        成功: {success: true, message: '授课安排删除成功'}
        失败: {error: '错误信息'}, 状态码
    
    权限要求:
        需要管理员权限
    """
    # 实例化授课安排模型并删除授课安排
    offering_model = CourseOffering()
    result = offering_model.delete_offering(offering_id)
    
    if result:
        # 删除成功
        return jsonify({'success': True, 'message': '授课安排删除成功'})
    else:
        # 删除失败
        return jsonify({'error': '授课安排删除失败'}), 500 