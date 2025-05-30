import pymysql
from pymysql.cursors import DictCursor
from .config import DB_CONFIG

class Database:
    def __init__(self):
        self.conn = None
        self.cursor = None
        
    def connect(self):
        """连接数据库"""
        try:
            self.conn = pymysql.connect(
                host=DB_CONFIG['host'],
                user=DB_CONFIG['user'],
                password=DB_CONFIG['password'],
                database=DB_CONFIG['database'],
                charset=DB_CONFIG['charset'],
                cursorclass=DictCursor
            )
            self.cursor = self.conn.cursor()
            return True
        except Exception as e:
            print(f"数据库连接错误: {e}")
            return False
    
    def close(self):
        """关闭数据库连接"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
    
    def execute_query(self, sql, params=None):
        """执行查询语句"""
        result = None
        try:
            self.connect()
            self.cursor.execute(sql, params or ())
            result = self.cursor.fetchall()
        except Exception as e:
            print(f"查询执行错误: {e}")
        finally:
            self.close()
        return result
    
    def execute_one(self, sql, params=None):
        """执行查询语句并返回一条结果"""
        result = None
        try:
            self.connect()
            self.cursor.execute(sql, params or ())
            result = self.cursor.fetchone()
        except Exception as e:
            print(f"查询执行错误: {e}")
        finally:
            self.close()
        return result
    
    def execute_update(self, sql, params=None):
        """执行更新语句"""
        result = False
        try:
            self.connect()
            rows = self.cursor.execute(sql, params or ())
            self.conn.commit()
            result = rows
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            print(f"更新执行错误: {e}")
        finally:
            self.close()
        return result
    
    def execute_many(self, sql, params_list):
        """批量执行SQL语句"""
        result = False
        try:
            self.connect()
            rows = self.cursor.executemany(sql, params_list)
            self.conn.commit()
            result = rows
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            print(f"批量执行错误: {e}")
        finally:
            self.close()
        return result

# 用户模型
class User:
    def __init__(self):
        self.db = Database()
    
    def authenticate(self, username, password):
        """验证用户身份"""
        sql = "SELECT * FROM user WHERE username = %s AND password = %s AND status = 1"
        return self.db.execute_one(sql, (username, password))
    
    def get_user_by_id(self, user_id):
        """根据ID获取用户"""
        sql = "SELECT * FROM user WHERE user_id = %s"
        return self.db.execute_one(sql, (user_id,))
    
    def create_user(self, username, password, role, related_id=None):
        """创建新用户"""
        sql = "INSERT INTO user (username, password, role, related_id) VALUES (%s, %s, %s, %s)"
        return self.db.execute_update(sql, (username, password, role, related_id))

    def update_password(self, user_id, new_password):
        """更新用户密码
        
        参数:
            user_id (int): 用户ID
            new_password (str): 新密码
            
        返回:
            bool: 更新是否成功
        """
        sql = "UPDATE user SET password = %s WHERE user_id = %s"
        return self.db.execute_update(sql, (new_password, user_id))
    
    def check_password(self, user_id, password):
        """检查密码是否正确
        
        参数:
            user_id (int): 用户ID
            password (str): 要检查的密码
            
        返回:
            bool: 密码是否正确
        """
        sql = "SELECT * FROM user WHERE user_id = %s AND password = %s"
        user = self.db.execute_one(sql, (user_id, password))
        return user is not None
    
    def get_all_users(self):
        """获取所有用户
        
        返回:
            list: 所有用户的列表
        """
        sql = "SELECT * FROM user ORDER BY user_id"
        return self.db.execute_query(sql)

# 学生模型
class Student:
    def __init__(self):
        self.db = Database()
    
    def get_all_students(self, page=1, items_per_page=10, search=None):
        """获取所有学生"""
        offset = (page - 1) * items_per_page
        
        if search:
            sql = """
                SELECT s.*, c.class_name, co.college_name 
                FROM student s
                JOIN class c ON s.class_id = c.class_id
                JOIN college co ON c.college_id = co.college_id
                WHERE s.name LIKE %s OR s.student_no LIKE %s
                ORDER BY s.student_id
                LIMIT %s, %s
            """
            search_param = f"%{search}%"
            count_sql = """
                SELECT COUNT(*) as count 
                FROM student s
                WHERE s.name LIKE %s OR s.student_no LIKE %s
            """
            total = self.db.execute_one(count_sql, (search_param, search_param))
            return self.db.execute_query(sql, (search_param, search_param, offset, items_per_page)), total['count']
        else:
            sql = """
                SELECT s.*, c.class_name, co.college_name 
                FROM student s
                JOIN class c ON s.class_id = c.class_id
                JOIN college co ON c.college_id = co.college_id
                ORDER BY s.student_id
                LIMIT %s, %s
            """
            count_sql = "SELECT COUNT(*) as count FROM student"
            total = self.db.execute_one(count_sql)
            return self.db.execute_query(sql, (offset, items_per_page)), total['count']
    
    def get_student_by_id(self, student_id):
        """根据ID获取学生"""
        sql = """
            SELECT s.*, c.class_name, co.college_name 
            FROM student s
            JOIN class c ON s.class_id = c.class_id
            JOIN college co ON c.college_id = co.college_id
            WHERE s.student_id = %s
        """
        return self.db.execute_one(sql, (student_id,))
    
    def add_student(self, data):
        """添加学生"""
        sql = """
            INSERT INTO student 
            (student_no, name, gender, birth_date, id_card, enrollment_date, 
            class_id, address, phone, email) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            data['student_no'], data['name'], data['gender'], data['birth_date'], 
            data['id_card'], data['enrollment_date'], data['class_id'], 
            data['address'], data['phone'], data['email']
        )
        return self.db.execute_update(sql, params)
    
    def update_student(self, student_id, data):
        """更新学生信息"""
        sql = """
            UPDATE student 
            SET student_no = %s, name = %s, gender = %s, birth_date = %s, 
            id_card = %s, enrollment_date = %s, class_id = %s, 
            address = %s, phone = %s, email = %s, status = %s
            WHERE student_id = %s
        """
        params = (
            data['student_no'], data['name'], data['gender'], data['birth_date'], 
            data['id_card'], data['enrollment_date'], data['class_id'], 
            data['address'], data['phone'], data['email'], data['status'], student_id
        )
        return self.db.execute_update(sql, params)
    
    def delete_student(self, student_id):
        """删除学生"""
        sql = "DELETE FROM student WHERE student_id = %s"
        return self.db.execute_update(sql, (student_id,))

# 教师模型
class Teacher:
    def __init__(self):
        self.db = Database()
    
    def get_all_teachers(self, page=1, items_per_page=10, search=None):
        """获取所有教师"""
        offset = (page - 1) * items_per_page
        
        if search:
            sql = """
                SELECT t.*, c.college_name, tt.title_name 
                FROM teacher t
                JOIN college c ON t.college_id = c.college_id
                LEFT JOIN title tt ON t.title_id = tt.title_id
                WHERE t.name LIKE %s OR t.teacher_no LIKE %s
                ORDER BY t.teacher_id
                LIMIT %s, %s
            """
            search_param = f"%{search}%"
            count_sql = """
                SELECT COUNT(*) as count 
                FROM teacher t
                WHERE t.name LIKE %s OR t.teacher_no LIKE %s
            """
            total = self.db.execute_one(count_sql, (search_param, search_param))
            return self.db.execute_query(sql, (search_param, search_param, offset, items_per_page)), total['count']
        else:
            sql = """
                SELECT t.*, c.college_name, tt.title_name 
                FROM teacher t
                JOIN college c ON t.college_id = c.college_id
                LEFT JOIN title tt ON t.title_id = tt.title_id
                ORDER BY t.teacher_id
                LIMIT %s, %s
            """
            count_sql = "SELECT COUNT(*) as count FROM teacher"
            total = self.db.execute_one(count_sql)
            return self.db.execute_query(sql, (offset, items_per_page)), total['count']
    
    def get_teacher_by_id(self, teacher_id):
        """根据ID获取教师"""
        sql = """
            SELECT t.*, c.college_name, tt.title_name 
            FROM teacher t
            JOIN college c ON t.college_id = c.college_id
            LEFT JOIN title tt ON t.title_id = tt.title_id
            WHERE t.teacher_id = %s
        """
        return self.db.execute_one(sql, (teacher_id,))
    
    def add_teacher(self, data):
        """添加教师"""
        sql = """
            INSERT INTO teacher 
            (teacher_no, name, gender, birth_date, title_id, college_id, phone, email) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            data['teacher_no'], data['name'], data['gender'], data['birth_date'], 
            data['title_id'], data['college_id'], data['phone'], data['email']
        )
        return self.db.execute_update(sql, params)
    
    def update_teacher(self, teacher_id, data):
        """更新教师信息"""
        sql = """
            UPDATE teacher 
            SET teacher_no = %s, name = %s, gender = %s, birth_date = %s, 
            title_id = %s, college_id = %s, phone = %s, email = %s
            WHERE teacher_id = %s
        """
        params = (
            data['teacher_no'], data['name'], data['gender'], data['birth_date'], 
            data['title_id'], data['college_id'], data['phone'], data['email'], teacher_id
        )
        return self.db.execute_update(sql, params)
    
    def delete_teacher(self, teacher_id):
        """删除教师"""
        sql = "DELETE FROM teacher WHERE teacher_id = %s"
        return self.db.execute_update(sql, (teacher_id,))

# 课程模型
class Course:
    def __init__(self):
        self.db = Database()
    
    def get_all_courses(self, page=1, items_per_page=10, search=None):
        """获取所有课程"""
        offset = (page - 1) * items_per_page
        
        if search:
            sql = """
                SELECT c.*, ct.type_name, co.college_name 
                FROM course c
                JOIN course_type ct ON c.type_id = ct.type_id
                JOIN college co ON c.college_id = co.college_id
                WHERE c.course_name LIKE %s OR c.course_code LIKE %s
                ORDER BY c.course_id
                LIMIT %s, %s
            """
            search_param = f"%{search}%"
            count_sql = """
                SELECT COUNT(*) as count 
                FROM course c
                WHERE c.course_name LIKE %s OR c.course_code LIKE %s
            """
            total = self.db.execute_one(count_sql, (search_param, search_param))
            return self.db.execute_query(sql, (search_param, search_param, offset, items_per_page)), total['count']
        else:
            sql = """
                SELECT c.*, ct.type_name, co.college_name 
                FROM course c
                JOIN course_type ct ON c.type_id = ct.type_id
                JOIN college co ON c.college_id = co.college_id
                ORDER BY c.course_id
                LIMIT %s, %s
            """
            count_sql = "SELECT COUNT(*) as count FROM course"
            total = self.db.execute_one(count_sql)
            return self.db.execute_query(sql, (offset, items_per_page)), total['count']
    
    def get_course_by_id(self, course_id):
        """根据ID获取课程"""
        sql = """
            SELECT c.*, ct.type_name, co.college_name 
            FROM course c
            JOIN course_type ct ON c.type_id = ct.type_id
            JOIN college co ON c.college_id = co.college_id
            WHERE c.course_id = %s
        """
        return self.db.execute_one(sql, (course_id,))
    
    def add_course(self, data):
        """添加课程"""
        sql = """
            INSERT INTO course 
            (course_code, course_name, credit, hours, type_id, college_id) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (
            data['course_code'], data['course_name'], data['credit'], 
            data['hours'], data['type_id'], data['college_id']
        )
        return self.db.execute_update(sql, params)
    
    def update_course(self, course_id, data):
        """更新课程信息"""
        sql = """
            UPDATE course 
            SET course_code = %s, course_name = %s, credit = %s, 
            hours = %s, type_id = %s, college_id = %s
            WHERE course_id = %s
        """
        params = (
            data['course_code'], data['course_name'], data['credit'], 
            data['hours'], data['type_id'], data['college_id'], course_id
        )
        return self.db.execute_update(sql, params)
    
    def delete_course(self, course_id):
        """删除课程"""
        sql = "DELETE FROM course WHERE course_id = %s"
        return self.db.execute_update(sql, (course_id,))

# 班级模型
class Class:
    def __init__(self):
        self.db = Database()
    
    def get_all_classes(self):
        """获取所有班级"""
        sql = """
            SELECT c.*, co.college_name 
            FROM class c
            JOIN college co ON c.college_id = co.college_id
            ORDER BY c.class_id
        """
        return self.db.execute_query(sql)
    
    def get_class_by_id(self, class_id):
        """根据ID获取班级"""
        sql = """
            SELECT c.*, co.college_name 
            FROM class c
            JOIN college co ON c.college_id = co.college_id
            WHERE c.class_id = %s
        """
        return self.db.execute_one(sql, (class_id,))
        
    def add_class(self, data):
        """添加班级"""
        sql = """
            INSERT INTO class 
            (class_name, class_code, college_id, admission_year) 
            VALUES (%s, %s, %s, %s)
        """
        params = (
            data['class_name'], data['class_code'], 
            data['college_id'], data['admission_year']
        )
        return self.db.execute_update(sql, params)
    
    def update_class(self, class_id, data):
        """更新班级"""
        sql = """
            UPDATE class 
            SET class_name = %s, class_code = %s, 
            college_id = %s, admission_year = %s
            WHERE class_id = %s
        """
        params = (
            data['class_name'], data['class_code'], 
            data['college_id'], data['admission_year'], class_id
        )
        return self.db.execute_update(sql, params)
    
    def delete_class(self, class_id):
        """删除班级"""
        sql = "DELETE FROM class WHERE class_id = %s"
        return self.db.execute_update(sql, (class_id,))

# 学院模型
class College:
    def __init__(self):
        self.db = Database()
    
    def get_all_colleges(self):
        """获取所有学院"""
        sql = "SELECT * FROM college ORDER BY college_id"
        return self.db.execute_query(sql)
        
    def get_college_by_id(self, college_id):
        """根据ID获取学院"""
        sql = "SELECT * FROM college WHERE college_id = %s"
        return self.db.execute_one(sql, (college_id,))
        
    def add_college(self, data):
        """添加学院"""
        sql = """
            INSERT INTO college 
            (college_name, college_code) 
            VALUES (%s, %s)
        """
        params = (data['college_name'], data['college_code'])
        return self.db.execute_update(sql, params)
    
    def update_college(self, college_id, data):
        """更新学院"""
        sql = """
            UPDATE college 
            SET college_name = %s, college_code = %s
            WHERE college_id = %s
        """
        params = (data['college_name'], data['college_code'], college_id)
        return self.db.execute_update(sql, params)
    
    def delete_college(self, college_id):
        """删除学院"""
        sql = "DELETE FROM college WHERE college_id = %s"
        return self.db.execute_update(sql, (college_id,))

# 职称模型
class Title:
    def __init__(self):
        self.db = Database()
    
    def get_all_titles(self):
        """获取所有职称"""
        sql = "SELECT * FROM title ORDER BY title_id"
        return self.db.execute_query(sql)

# 课程类型模型
class CourseType:
    def __init__(self):
        self.db = Database()
    
    def get_all_course_types(self):
        """获取所有课程类型"""
        sql = "SELECT * FROM course_type ORDER BY type_id"
        return self.db.execute_query(sql)

# 授课安排模型
class CourseOffering:
    def __init__(self):
        self.db = Database()
    
    def get_all_offerings(self, page=1, items_per_page=10, search=None):
        """获取所有授课安排"""
        offset = (page - 1) * items_per_page
        
        if search:
            sql = """
                SELECT co.*, c.course_name, c.course_code, t.name as teacher_name 
                FROM course_offering co
                JOIN course c ON co.course_id = c.course_id
                JOIN teacher t ON co.teacher_id = t.teacher_id
                WHERE c.course_name LIKE %s OR t.name LIKE %s
                ORDER BY co.offering_id
                LIMIT %s, %s
            """
            search_param = f"%{search}%"
            count_sql = """
                SELECT COUNT(*) as count 
                FROM course_offering co
                JOIN course c ON co.course_id = c.course_id
                JOIN teacher t ON co.teacher_id = t.teacher_id
                WHERE c.course_name LIKE %s OR t.name LIKE %s
            """
            total = self.db.execute_one(count_sql, (search_param, search_param))
            return self.db.execute_query(sql, (search_param, search_param, offset, items_per_page)), total['count']
        else:
            sql = """
                SELECT co.*, c.course_name, c.course_code, t.name as teacher_name 
                FROM course_offering co
                JOIN course c ON co.course_id = c.course_id
                JOIN teacher t ON co.teacher_id = t.teacher_id
                ORDER BY co.offering_id
                LIMIT %s, %s
            """
            count_sql = "SELECT COUNT(*) as count FROM course_offering"
            total = self.db.execute_one(count_sql)
            return self.db.execute_query(sql, (offset, items_per_page)), total['count']
    
    def add_offering(self, data):
        """添加授课安排"""
        sql = """
            INSERT INTO course_offering 
            (course_id, teacher_id, semester, year, classroom, class_time) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (
            data['course_id'], data['teacher_id'], data['semester'], 
            data['year'], data['classroom'], data['class_time']
        )
        return self.db.execute_update(sql, params)
    
    def get_offering_by_id(self, offering_id):
        """根据ID获取授课安排"""
        sql = """
            SELECT co.*, c.course_name, c.course_code, t.name as teacher_name 
            FROM course_offering co
            JOIN course c ON co.course_id = c.course_id
            JOIN teacher t ON co.teacher_id = t.teacher_id
            WHERE co.offering_id = %s
        """
        return self.db.execute_one(sql, (offering_id,))
    
    def update_offering(self, offering_id, data):
        """更新授课安排"""
        sql = """
            UPDATE course_offering 
            SET course_id = %s, teacher_id = %s, semester = %s, 
            year = %s, classroom = %s, class_time = %s
            WHERE offering_id = %s
        """
        params = (
            data['course_id'], data['teacher_id'], data['semester'], 
            data['year'], data['classroom'], data['class_time'], offering_id
        )
        return self.db.execute_update(sql, params)
    
    def delete_offering(self, offering_id):
        """删除授课安排"""
        sql = "DELETE FROM course_offering WHERE offering_id = %s"
        return self.db.execute_update(sql, (offering_id,))

# 成绩模型
class Score:
    def __init__(self):
        self.db = Database()
    
    def get_student_scores(self, student_id):
        """获取学生的成绩"""
        sql = """
            SELECT sc.*, c.course_name, c.credit, t.name as teacher_name,
            co.semester, co.year
            FROM student_course sc
            JOIN course_offering co ON sc.offering_id = co.offering_id
            JOIN course c ON co.course_id = c.course_id
            JOIN teacher t ON co.teacher_id = t.teacher_id
            WHERE sc.student_id = %s
            ORDER BY co.year DESC, co.semester DESC
        """
        return self.db.execute_query(sql, (student_id,))
    
    def add_score(self, data):
        """添加成绩"""
        sql = """
            INSERT INTO student_course 
            (student_id, offering_id, score, status) 
            VALUES (%s, %s, %s, %s)
        """
        params = (data['student_id'], data['offering_id'], data['score'], data['status'])
        return self.db.execute_update(sql, params)
    
    def update_score(self, sc_id, score):
        """更新成绩"""
        sql = "UPDATE student_course SET score = %s, status = '已修完' WHERE sc_id = %s"
        return self.db.execute_update(sql, (score, sc_id))
        
    def update_score_with_status(self, sc_id, score, status):
        """更新成绩和状态"""
        sql = "UPDATE student_course SET score = %s, status = %s WHERE sc_id = %s"
        return self.db.execute_update(sql, (score, status, sc_id))
        
    def update_status(self, sc_id, status):
        """仅更新状态"""
        # 如果状态不是已修完，则清空成绩
        if status != '已修完':
            sql = "UPDATE student_course SET score = NULL, status = %s WHERE sc_id = %s"
        else:
            sql = "UPDATE student_course SET status = %s WHERE sc_id = %s"
        return self.db.execute_update(sql, (status, sc_id))
        
    def delete_score(self, sc_id):
        """删除成绩记录"""
        sql = "DELETE FROM student_course WHERE sc_id = %s"
        return self.db.execute_update(sql, (sc_id,)) 