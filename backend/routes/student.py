from flask import Blueprint, request, jsonify, session
from ..models import Student, Class, College
from ..utils import login_required, admin_required, student_self_required

# 创建学生相关的蓝图
student_bp = Blueprint('student', __name__)

@student_bp.route('/', methods=['GET'])
@login_required
def get_students():
    """获取学生列表
    
    获取所有学生信息的分页列表，支持按名称或学号搜索
    
    URL参数:
        page: 页码，默认为1
        search: 搜索关键词，可选
        
    返回:
        {
            students: [学生对象列表],
            total: 学生总数,
            page: 当前页码
        }
    
    权限要求:
        需要登录，学生用户将只看到自己的信息
    """
    # 获取页码和搜索参数
    page = int(request.args.get('page', 1))
    search = request.args.get('search', None)
    
    # 实例化学生模型并获取学生列表
    student_model = Student()
    
    # 根据角色区分处理
    if session.get('role') == 'student':
        # 如果是学生用户，只返回自己的信息
        student_id = session.get('related_id')
        student = student_model.get_student_by_id(student_id)
        
        if student:
            return jsonify({
                'students': [student],
                'total': 1,
                'page': 1
            })
        else:
            return jsonify({
                'students': [],
                'total': 0,
                'page': 1
            })
    else:
        # 管理员或教师可以查看所有学生
        students, total = student_model.get_all_students(page=page, search=search)
        
        # 返回学生列表、总数和页码
        return jsonify({
            'students': students,
            'total': total,
            'page': page
        })

@student_bp.route('/<int:student_id>', methods=['GET'])
@student_self_required
def get_student(student_id):
    """获取单个学生信息
    
    根据学生ID获取特定学生的详细信息
    
    URL参数:
        student_id: 学生ID
        
    返回:
        成功: {student: 学生对象}
        失败: {error: '错误信息'}, 状态码
    
    权限要求:
        学生只能查看自己的信息，管理员和教师可以查看所有学生信息
    """
    # 实例化学生模型并获取特定学生
    student_model = Student()
    student = student_model.get_student_by_id(student_id)
    
    if student:
        # 找到学生，返回学生信息
        return jsonify({'student': student})
    else:
        # 未找到学生
        return jsonify({'error': '学生不存在'}), 404

@student_bp.route('/', methods=['POST'])
@admin_required
def add_student():
    """添加新学生
    
    创建新的学生记录
    
    请求体:
        student_no: 学号
        name: 姓名
        gender: 性别
        enrollment_date: 入学日期
        class_id: 班级ID
        以及其他可选字段
        
    返回:
        成功: {success: true, message: '学生添加成功'}
        失败: {error: '错误信息'}, 状态码
    
    权限要求:
        需要管理员权限
    """
    # 获取请求中的JSON数据
    data = request.get_json()
    
    # 验证必填字段
    required_fields = ['student_no', 'name', 'gender', 'enrollment_date', 'class_id']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'error': f'字段 {field} 不能为空'}), 400
    
    # 实例化学生模型并添加学生
    student_model = Student()
    result = student_model.add_student(data)
    
    if result:
        # 添加成功
        return jsonify({'success': True, 'message': '学生添加成功'})
    else:
        # 添加失败
        return jsonify({'error': '学生添加失败'}), 500

@student_bp.route('/<int:student_id>', methods=['PUT'])
@admin_required
def update_student(student_id):
    """更新学生信息
    
    根据学生ID更新学生信息
    
    URL参数:
        student_id: 学生ID
        
    请求体:
        student_no: 学号
        name: 姓名
        gender: 性别
        enrollment_date: 入学日期
        class_id: 班级ID
        以及其他字段
        
    返回:
        成功: {success: true, message: '学生信息更新成功'}
        失败: {error: '错误信息'}, 状态码
    
    权限要求:
        需要管理员权限
    """
    # 获取请求中的JSON数据
    data = request.get_json()
    
    # 验证必填字段
    required_fields = ['student_no', 'name', 'gender', 'enrollment_date', 'class_id']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'error': f'字段 {field} 不能为空'}), 400
    
    # 实例化学生模型并更新学生信息
    student_model = Student()
    result = student_model.update_student(student_id, data)
    
    if result:
        # 更新成功
        return jsonify({'success': True, 'message': '学生信息更新成功'})
    else:
        # 更新失败
        return jsonify({'error': '学生信息更新失败'}), 500

@student_bp.route('/<int:student_id>', methods=['DELETE'])
@admin_required
def delete_student(student_id):
    """删除学生
    
    根据学生ID删除学生记录
    
    URL参数:
        student_id: 学生ID
        
    返回:
        成功: {success: true, message: '学生删除成功'}
        失败: {error: '错误信息'}, 状态码
    
    权限要求:
        需要管理员权限
    """
    # 实例化学生模型并删除学生
    student_model = Student()
    result = student_model.delete_student(student_id)
    
    if result:
        # 删除成功
        return jsonify({'success': True, 'message': '学生删除成功'})
    else:
        # 删除失败
        return jsonify({'error': '学生删除失败'}), 500

@student_bp.route('/class', methods=['GET'])
@login_required
def get_classes():
    """获取班级列表
    
    获取所有班级的列表，用于学生信息表单中的选择
    
    返回:
        {classes: [班级对象列表]}
    
    权限要求:
        需要登录
    """
    # 实例化班级模型并获取班级列表
    class_model = Class()
    classes = class_model.get_all_classes()
    
    return jsonify({'classes': classes})

@student_bp.route('/class/<int:class_id>', methods=['GET'])
@login_required
def get_class(class_id):
    """获取单个班级信息
    
    根据班级ID获取班级详细信息
    
    参数:
        class_id: 班级ID
        
    返回:
        {class: 班级对象}
    
    权限要求:
        需要登录
    """
    # 实例化班级模型并获取班级信息
    class_model = Class()
    class_info = class_model.get_class_by_id(class_id)
    
    if not class_info:
        return jsonify({'error': '班级不存在'}), 404
        
    return jsonify({'class': class_info})

@student_bp.route('/class', methods=['POST'])
@admin_required
def add_class():
    """添加班级
    
    添加新的班级信息
    
    请求体:
        class_name: 班级名称
        class_code: 班级代码
        college_id: 所属学院ID
        admission_year: 入学年份
        
    返回:
        成功: {success: true, message: '班级添加成功'}
        失败: {error: '错误信息'}, 状态码
    
    权限要求:
        需要管理员权限
    """
    # 获取请求数据
    data = request.get_json()
    
    # 验证必填字段
    required_fields = ['class_name', 'class_code', 'college_id', 'admission_year']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'error': f'缺少必填字段: {field}'}), 400
    
    # 验证数据类型
    try:
        data['college_id'] = int(data['college_id'])
        data['admission_year'] = int(data['admission_year'])
    except ValueError:
        return jsonify({'error': '学院ID和入学年份必须是整数'}), 400
    
    # 实例化班级模型并添加班级
    class_model = Class()
    try:
        class_model.add_class(data)
        return jsonify({'success': True, 'message': '班级添加成功'})
    except Exception as e:
        # 捕获数据库错误
        error_message = str(e)
        if 'Duplicate entry' in error_message and 'class_code' in error_message:
            return jsonify({'error': '班级代码已存在'}), 400
        return jsonify({'error': f'添加班级失败: {e}'}), 500

@student_bp.route('/class/<int:class_id>', methods=['PUT'])
@admin_required
def update_class(class_id):
    """更新班级信息
    
    更新指定班级的信息
    
    参数:
        class_id: 班级ID
        
    请求体:
        class_name: 班级名称
        class_code: 班级代码
        college_id: 所属学院ID
        admission_year: 入学年份
        
    返回:
        成功: {success: true, message: '班级更新成功'}
        失败: {error: '错误信息'}, 状态码
    
    权限要求:
        需要管理员权限
    """
    # 获取请求数据
    data = request.get_json()
    
    # 验证必填字段
    required_fields = ['class_name', 'class_code', 'college_id', 'admission_year']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'error': f'缺少必填字段: {field}'}), 400
    
    # 验证数据类型
    try:
        data['college_id'] = int(data['college_id'])
        data['admission_year'] = int(data['admission_year'])
    except ValueError:
        return jsonify({'error': '学院ID和入学年份必须是整数'}), 400
    
    # 实例化班级模型并更新班级
    class_model = Class()
    
    # 检查班级是否存在
    class_info = class_model.get_class_by_id(class_id)
    if not class_info:
        return jsonify({'error': '班级不存在'}), 404
    
    try:
        class_model.update_class(class_id, data)
        return jsonify({'success': True, 'message': '班级更新成功'})
    except Exception as e:
        # 捕获数据库错误
        error_message = str(e)
        if 'Duplicate entry' in error_message and 'class_code' in error_message:
            return jsonify({'error': '班级代码已存在'}), 400
        return jsonify({'error': f'更新班级失败: {e}'}), 500

@student_bp.route('/class/<int:class_id>', methods=['DELETE'])
@admin_required
def delete_class(class_id):
    """删除班级
    
    删除指定的班级
    
    参数:
        class_id: 班级ID
        
    返回:
        成功: {success: true, message: '班级删除成功'}
        失败: {error: '错误信息'}, 状态码
    
    权限要求:
        需要管理员权限
    """
    # 实例化班级模型
    class_model = Class()
    
    # 检查班级是否存在
    class_info = class_model.get_class_by_id(class_id)
    if not class_info:
        return jsonify({'error': '班级不存在'}), 404
    
    try:
        # 删除班级
        class_model.delete_class(class_id)
        return jsonify({'success': True, 'message': '班级删除成功'})
    except Exception as e:
        # 捕获数据库错误
        error_message = str(e)
        if 'foreign key constraint fails' in error_message.lower():
            return jsonify({'error': '无法删除班级，该班级下存在学生'}), 400
        return jsonify({'error': f'删除班级失败: {e}'}), 500

@student_bp.route('/college', methods=['GET'])
@login_required
def get_colleges():
    """获取学院列表
    
    获取所有学院的列表，用于表单中的选择
    
    返回:
        {colleges: [学院对象列表]}
    
    权限要求:
        需要登录
    """
    # 实例化学院模型并获取学院列表
    college_model = College()
    colleges = college_model.get_all_colleges()
    
    return jsonify({'colleges': colleges})

@student_bp.route('/college/<int:college_id>', methods=['GET'])
@login_required
def get_college(college_id):
    """获取单个学院信息
    
    根据学院ID获取学院详细信息
    
    参数:
        college_id: 学院ID
        
    返回:
        {college: 学院对象}
    
    权限要求:
        需要登录
    """
    # 实例化学院模型并获取学院信息
    college_model = College()
    college_info = college_model.get_college_by_id(college_id)
    
    if not college_info:
        return jsonify({'error': '学院不存在'}), 404
        
    return jsonify({'college': college_info})

@student_bp.route('/college', methods=['POST'])
@admin_required
def add_college():
    """添加学院
    
    添加新的学院信息
    
    请求体:
        college_name: 学院名称
        college_code: 学院代码
        
    返回:
        成功: {success: true, message: '学院添加成功'}
        失败: {error: '错误信息'}, 状态码
    
    权限要求:
        需要管理员权限
    """
    # 获取请求数据
    data = request.get_json()
    
    # 验证必填字段
    required_fields = ['college_name', 'college_code']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'error': f'缺少必填字段: {field}'}), 400
    
    # 实例化学院模型并添加学院
    college_model = College()
    try:
        college_model.add_college(data)
        return jsonify({'success': True, 'message': '学院添加成功'})
    except Exception as e:
        # 捕获数据库错误
        error_message = str(e)
        if 'Duplicate entry' in error_message and 'college_code' in error_message:
            return jsonify({'error': '学院代码已存在'}), 400
        return jsonify({'error': f'添加学院失败: {e}'}), 500

@student_bp.route('/college/<int:college_id>', methods=['PUT'])
@admin_required
def update_college(college_id):
    """更新学院信息
    
    更新指定学院的信息
    
    参数:
        college_id: 学院ID
        
    请求体:
        college_name: 学院名称
        college_code: 学院代码
        
    返回:
        成功: {success: true, message: '学院更新成功'}
        失败: {error: '错误信息'}, 状态码
    
    权限要求:
        需要管理员权限
    """
    # 获取请求数据
    data = request.get_json()
    
    # 验证必填字段
    required_fields = ['college_name', 'college_code']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'error': f'缺少必填字段: {field}'}), 400
    
    # 实例化学院模型并更新学院
    college_model = College()
    
    # 检查学院是否存在
    college_info = college_model.get_college_by_id(college_id)
    if not college_info:
        return jsonify({'error': '学院不存在'}), 404
    
    try:
        college_model.update_college(college_id, data)
        return jsonify({'success': True, 'message': '学院更新成功'})
    except Exception as e:
        # 捕获数据库错误
        error_message = str(e)
        if 'Duplicate entry' in error_message and 'college_code' in error_message:
            return jsonify({'error': '学院代码已存在'}), 400
        return jsonify({'error': f'更新学院失败: {e}'}), 500

@student_bp.route('/college/<int:college_id>', methods=['DELETE'])
@admin_required
def delete_college(college_id):
    """删除学院
    
    删除指定的学院
    
    参数:
        college_id: 学院ID
        
    返回:
        成功: {success: true, message: '学院删除成功'}
        失败: {error: '错误信息'}, 状态码
    
    权限要求:
        需要管理员权限
    """
    # 实例化学院模型
    college_model = College()
    
    # 检查学院是否存在
    college_info = college_model.get_college_by_id(college_id)
    if not college_info:
        return jsonify({'error': '学院不存在'}), 404
    
    try:
        # 删除学院
        college_model.delete_college(college_id)
        return jsonify({'success': True, 'message': '学院删除成功'})
    except Exception as e:
        # 捕获数据库错误
        error_message = str(e)
        if 'foreign key constraint fails' in error_message.lower():
            return jsonify({'error': '无法删除学院，该学院下存在班级或教师记录'}), 400
        return jsonify({'error': f'删除学院失败: {e}'}), 500 