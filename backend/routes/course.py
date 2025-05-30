from flask import Blueprint, request, jsonify, session
from ..models import Course, CourseType, College, Score
from ..utils import login_required, admin_required, teacher_required

# 创建课程相关的蓝图
course_bp = Blueprint('course', __name__)

@course_bp.route('/', methods=['GET'])
@login_required
def get_courses():
    """获取课程列表
    
    获取所有课程信息的分页列表，支持按课程名称或代码搜索
    如果是学生用户，将只返回与该学生相关的课程
    
    URL参数:
        page: 页码，默认为1
        search: 搜索关键词，可选
        
    返回:
        {
            courses: [课程对象列表],
            total: 课程总数,
            page: 当前页码
        }
    
    权限要求:
        需要登录，学生用户仅能查看已选课程
    """
    # 获取页码和搜索参数
    page = int(request.args.get('page', 1))
    search = request.args.get('search', None)
    
    # 实例化课程模型
    course_model = Course()
    
    # 根据角色区分处理
    if session.get('role') == 'student':
        # 如果是学生用户，只返回与该学生相关的课程
        student_id = session.get('related_id')
        
        # 查询学生已选课程
        score_model = Score()
        scores = score_model.get_student_scores(student_id)
        
        # 从成绩记录中提取课程信息
        courses = []
        for score in scores:
            course = course_model.get_course_by_id(score['course_id'])
            if course:
                # 添加成绩信息到课程对象
                course['score'] = score['score']
                course['status'] = score['status']
                courses.append(course)
        
        return jsonify({
            'courses': courses,
            'total': len(courses),
            'page': 1
        })
    else:
        # 管理员或教师可以查看所有课程
        courses, total = course_model.get_all_courses(page=page, search=search)
        
        # 返回课程列表、总数和页码
        return jsonify({
            'courses': courses,
            'total': total,
            'page': page
        })

@course_bp.route('/<int:course_id>', methods=['GET'])
@login_required
def get_course(course_id):
    """获取单个课程信息
    
    根据课程ID获取特定课程的详细信息
    
    URL参数:
        course_id: 课程ID
        
    返回:
        成功: {course: 课程对象}
        失败: {error: '错误信息'}, 状态码
    
    权限要求:
        需要登录，学生用户只能查看已选课程
    """
    # 实例化课程模型并获取特定课程
    course_model = Course()
    course = course_model.get_course_by_id(course_id)
    
    if not course:
        # 未找到课程
        return jsonify({'error': '课程不存在'}), 404
        
    # 检查学生权限
    if session.get('role') == 'student':
        student_id = session.get('related_id')
        
        # 查询学生是否已选该课程
        score_model = Score()
        scores = score_model.get_student_scores(student_id)
        
        course_ids = [score['course_id'] for score in scores]
        if course_id not in course_ids:
            return jsonify({'error': '您没有权限查看未选修的课程信息'}), 403
    
    # 找到课程，返回课程信息
    return jsonify({'course': course})

@course_bp.route('/', methods=['POST'])
@admin_required
def add_course():
    """添加新课程
    
    创建新的课程记录
    
    请求体:
        course_code: 课程代码
        course_name: 课程名称
        credit: 学分
        hours: 学时
        type_id: 课程类型ID
        college_id: 所属学院ID
        以及其他可选字段
        
    返回:
        成功: {success: true, message: '课程添加成功'}
        失败: {error: '错误信息'}, 状态码
    
    权限要求:
        需要管理员权限
    """
    # 获取请求中的JSON数据
    data = request.get_json()
    
    # 验证必填字段
    required_fields = ['course_code', 'course_name', 'credit', 'hours', 'type_id', 'college_id']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'error': f'字段 {field} 不能为空'}), 400
    
    # 实例化课程模型并添加课程
    course_model = Course()
    result = course_model.add_course(data)
    
    if result:
        # 添加成功
        return jsonify({'success': True, 'message': '课程添加成功'})
    else:
        # 添加失败
        return jsonify({'error': '课程添加失败'}), 500

@course_bp.route('/<int:course_id>', methods=['PUT'])
@admin_required
def update_course(course_id):
    """更新课程信息
    
    根据课程ID更新课程信息
    
    URL参数:
        course_id: 课程ID
        
    请求体:
        course_code: 课程代码
        course_name: 课程名称
        credit: 学分
        hours: 学时
        type_id: 课程类型ID
        college_id: 所属学院ID
        以及其他字段
        
    返回:
        成功: {success: true, message: '课程信息更新成功'}
        失败: {error: '错误信息'}, 状态码
    
    权限要求:
        需要管理员权限
    """
    # 获取请求中的JSON数据
    data = request.get_json()
    
    # 验证必填字段
    required_fields = ['course_code', 'course_name', 'credit', 'hours', 'type_id', 'college_id']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'error': f'字段 {field} 不能为空'}), 400
    
    # 实例化课程模型并更新课程信息
    course_model = Course()
    result = course_model.update_course(course_id, data)
    
    if result:
        # 更新成功
        return jsonify({'success': True, 'message': '课程信息更新成功'})
    else:
        # 更新失败
        return jsonify({'error': '课程信息更新失败'}), 500

@course_bp.route('/<int:course_id>', methods=['DELETE'])
@admin_required
def delete_course(course_id):
    """删除课程
    
    根据课程ID删除课程记录
    
    URL参数:
        course_id: 课程ID
        
    返回:
        成功: {success: true, message: '课程删除成功'}
        失败: {error: '错误信息'}, 状态码
    
    权限要求:
        需要管理员权限
    """
    # 实例化课程模型并删除课程
    course_model = Course()
    result = course_model.delete_course(course_id)
    
    if result:
        # 删除成功
        return jsonify({'success': True, 'message': '课程删除成功'})
    else:
        # 删除失败
        return jsonify({'error': '课程删除失败'}), 500

@course_bp.route('/type', methods=['GET'])
@login_required
def get_course_types():
    """获取课程类型列表
    
    获取所有课程类型的列表，用于课程信息表单中的选择
    
    返回:
        {course_types: [课程类型对象列表]}
    
    权限要求:
        需要登录，学生用户无权访问
    """
    # 检查权限：学生无权访问课程类型列表
    if session.get('role') == 'student':
        return jsonify({'error': '学生无权查看课程类型列表'}), 403
        
    # 实例化课程类型模型并获取类型列表
    course_type_model = CourseType()
    course_types = course_type_model.get_all_course_types()
    
    return jsonify({'course_types': course_types}) 