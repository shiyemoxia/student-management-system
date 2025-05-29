import pymysql

# 数据库连接配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'student_management',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def create_tables():
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        print("创建学院表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS college (
                college_id INT PRIMARY KEY AUTO_INCREMENT,
                college_name VARCHAR(50) NOT NULL,
                college_code VARCHAR(20) NOT NULL UNIQUE
            )
        """)
        
        print("创建班级表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS class (
                class_id INT PRIMARY KEY AUTO_INCREMENT,
                class_name VARCHAR(50) NOT NULL,
                class_code VARCHAR(20) NOT NULL UNIQUE,
                college_id INT NOT NULL,
                admission_year INT NOT NULL,
                FOREIGN KEY (college_id) REFERENCES college(college_id)
            )
        """)
        
        print("创建职称表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS title (
                title_id INT PRIMARY KEY AUTO_INCREMENT,
                title_name VARCHAR(20) NOT NULL,
                title_code VARCHAR(10) NOT NULL UNIQUE
            )
        """)
        
        print("创建课程类型表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS course_type (
                type_id INT PRIMARY KEY AUTO_INCREMENT,
                type_name VARCHAR(20) NOT NULL,
                type_code VARCHAR(10) NOT NULL UNIQUE
            )
        """)
        
        print("创建学生表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS student (
                student_id INT PRIMARY KEY AUTO_INCREMENT,
                student_no VARCHAR(20) NOT NULL UNIQUE,
                name VARCHAR(20) NOT NULL,
                gender ENUM('男', '女') NOT NULL,
                birth_date DATE,
                id_card VARCHAR(18),
                enrollment_date DATE NOT NULL,
                class_id INT NOT NULL,
                address VARCHAR(100),
                phone VARCHAR(20),
                email VARCHAR(50),
                status ENUM('在读', '休学', '退学', '毕业') DEFAULT '在读',
                FOREIGN KEY (class_id) REFERENCES class(class_id)
            )
        """)
        
        print("创建教师表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS teacher (
                teacher_id INT PRIMARY KEY AUTO_INCREMENT,
                teacher_no VARCHAR(20) NOT NULL UNIQUE,
                name VARCHAR(20) NOT NULL,
                gender ENUM('男', '女') NOT NULL,
                birth_date DATE,
                title_id INT,
                college_id INT NOT NULL,
                phone VARCHAR(20),
                email VARCHAR(50),
                FOREIGN KEY (title_id) REFERENCES title(title_id),
                FOREIGN KEY (college_id) REFERENCES college(college_id)
            )
        """)
        
        print("创建课程表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS course (
                course_id INT PRIMARY KEY AUTO_INCREMENT,
                course_code VARCHAR(20) NOT NULL UNIQUE,
                course_name VARCHAR(50) NOT NULL,
                credit DECIMAL(3,1) NOT NULL,
                hours INT NOT NULL,
                type_id INT NOT NULL,
                college_id INT NOT NULL,
                FOREIGN KEY (type_id) REFERENCES course_type(type_id),
                FOREIGN KEY (college_id) REFERENCES college(college_id)
            )
        """)
        
        print("创建开课表（授课安排）...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS course_offering (
                offering_id INT PRIMARY KEY AUTO_INCREMENT,
                course_id INT NOT NULL,
                teacher_id INT NOT NULL,
                semester VARCHAR(20) NOT NULL,
                year INT NOT NULL,
                classroom VARCHAR(50),
                class_time VARCHAR(50),
                FOREIGN KEY (course_id) REFERENCES course(course_id),
                FOREIGN KEY (teacher_id) REFERENCES teacher(teacher_id)
            )
        """)
        
        print("创建学生选课和成绩表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS student_course (
                sc_id INT PRIMARY KEY AUTO_INCREMENT,
                student_id INT NOT NULL,
                offering_id INT NOT NULL,
                score DECIMAL(5,2),
                status ENUM('选课中', '已修完', '已取消') DEFAULT '选课中',
                FOREIGN KEY (student_id) REFERENCES student(student_id),
                FOREIGN KEY (offering_id) REFERENCES course_offering(offering_id),
                UNIQUE KEY (student_id, offering_id)
            )
        """)
        
        print("创建用户表（用于系统登录）...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user (
                user_id INT PRIMARY KEY AUTO_INCREMENT,
                username VARCHAR(50) NOT NULL UNIQUE,
                password VARCHAR(100) NOT NULL,
                role ENUM('admin', 'teacher', 'student') NOT NULL,
                related_id INT,
                status TINYINT DEFAULT 1
            )
        """)
        
        # 插入初始数据
        print("插入初始数据...")
        
        # 清空现有数据（如果需要重新初始化）
        cursor.execute("DELETE FROM user WHERE role != 'admin'")
        cursor.execute("DELETE FROM student_course")
        cursor.execute("DELETE FROM course_offering")
        cursor.execute("DELETE FROM student")
        cursor.execute("DELETE FROM course")
        cursor.execute("DELETE FROM teacher")
        cursor.execute("DELETE FROM class")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        cursor.execute("TRUNCATE TABLE college")
        cursor.execute("TRUNCATE TABLE title")
        cursor.execute("TRUNCATE TABLE course_type")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        
        # 学院数据
        print("插入学院数据...")
        cursor.execute("""
            INSERT INTO college (college_name, college_code) VALUES 
            ('计算机科学与技术学院', 'CS'),
            ('数学学院', 'MATH'),
            ('物理学院', 'PHYS')
        """)
        
        # 获取学院ID以便后续使用
        cursor.execute("SELECT college_id, college_code FROM college")
        colleges = cursor.fetchall()
        college_ids = {college['college_code']: college['college_id'] for college in colleges}
        
        # 职称数据
        print("插入职称数据...")
        cursor.execute("""
            INSERT INTO title (title_name, title_code) VALUES 
            ('教授', 'PROF'),
            ('副教授', 'ASSO_PROF'),
            ('讲师', 'LECT')
        """)
        
        # 获取职称ID以便后续使用
        cursor.execute("SELECT title_id, title_code FROM title")
        titles = cursor.fetchall()
        title_ids = {title['title_code']: title['title_id'] for title in titles}
        
        # 课程类型数据
        print("插入课程类型数据...")
        cursor.execute("""
            INSERT INTO course_type (type_name, type_code) VALUES 
            ('必修课', 'REQ'),
            ('选修课', 'ELEC'),
            ('公共课', 'GEN')
        """)
        
        # 获取课程类型ID以便后续使用
        cursor.execute("SELECT type_id, type_code FROM course_type")
        course_types = cursor.fetchall()
        type_ids = {ct['type_code']: ct['type_id'] for ct in course_types}
        
        # 班级数据
        print("插入班级数据...")
        class_data = [
            ('计算机科学与技术1班', 'CS2021-1', college_ids['CS'], 2021),
            ('计算机科学与技术2班', 'CS2021-2', college_ids['CS'], 2021),
            ('软件工程1班', 'CS2022-1', college_ids['CS'], 2022),
            ('数学1班', 'MATH2021-1', college_ids['MATH'], 2021),
            ('应用物理1班', 'PHYS2022-1', college_ids['PHYS'], 2022)
        ]
        cursor.executemany("""
            INSERT INTO class (class_name, class_code, college_id, admission_year) 
            VALUES (%s, %s, %s, %s)
        """, class_data)
        
        # 获取班级ID以便后续使用
        cursor.execute("SELECT class_id, class_code FROM class")
        classes = cursor.fetchall()
        class_ids = {cls['class_code']: cls['class_id'] for cls in classes}
        
        # 教师数据
        print("插入教师数据...")
        teacher_data = [
            ('T2001', '张教授', '男', '1975-05-15', title_ids['PROF'], college_ids['CS'], '13800138001', 'zhang@example.com'),
            ('T2002', '李副教授', '女', '1980-08-22', title_ids['ASSO_PROF'], college_ids['CS'], '13800138002', 'li@example.com'),
            ('T2003', '王讲师', '男', '1985-03-10', title_ids['LECT'], college_ids['MATH'], '13800138003', 'wang@example.com'),
            ('T2004', '刘教授', '女', '1972-11-18', title_ids['PROF'], college_ids['PHYS'], '13800138004', 'liu@example.com')
        ]
        cursor.executemany("""
            INSERT INTO teacher (teacher_no, name, gender, birth_date, title_id, college_id, phone, email) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, teacher_data)
        
        # 获取教师ID以便后续使用
        cursor.execute("SELECT teacher_id, teacher_no FROM teacher")
        teachers = cursor.fetchall()
        teacher_ids = {t['teacher_no']: t['teacher_id'] for t in teachers}
        
        # 课程数据
        print("插入课程数据...")
        course_data = [
            ('CS101', '计算机导论', 3.0, 48, type_ids['REQ'], college_ids['CS']),
            ('CS201', '数据结构', 4.0, 64, type_ids['REQ'], college_ids['CS']),
            ('CS301', '操作系统', 4.0, 64, type_ids['REQ'], college_ids['CS']),
            ('CS401', '人工智能', 3.0, 48, type_ids['ELEC'], college_ids['CS']),
            ('MATH101', '高等数学', 5.0, 80, type_ids['REQ'], college_ids['MATH']),
            ('PHY101', '大学物理', 4.0, 64, type_ids['GEN'], college_ids['PHYS'])
        ]
        cursor.executemany("""
            INSERT INTO course (course_code, course_name, credit, hours, type_id, college_id) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """, course_data)
        
        # 获取课程ID以便后续使用
        cursor.execute("SELECT course_id, course_code FROM course")
        courses = cursor.fetchall()
        course_ids = {c['course_code']: c['course_id'] for c in courses}
        
        # 开课数据
        print("插入开课数据...")
        offering_data = [
            (course_ids['CS101'], teacher_ids['T2001'], '春季', 2023, 'A101', '周一 08:00-10:00'),
            (course_ids['CS201'], teacher_ids['T2002'], '春季', 2023, 'A102', '周二 10:00-12:00'),
            (course_ids['MATH101'], teacher_ids['T2003'], '春季', 2023, 'B201', '周三 14:00-16:00'),
            (course_ids['PHY101'], teacher_ids['T2004'], '春季', 2023, 'C301', '周四 16:00-18:00')
        ]
        cursor.executemany("""
            INSERT INTO course_offering (course_id, teacher_id, semester, year, classroom, class_time) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """, offering_data)
        
        # 获取开课ID以便后续使用
        cursor.execute("SELECT offering_id FROM course_offering")
        offerings = cursor.fetchall()
        offering_ids = [o['offering_id'] for o in offerings]
        
        # 学生数据
        print("插入学生数据...")
        student_data = [
            ('S20210101', '张三', '男', '2000-01-15', '110101200001150011', '2021-09-01', class_ids['CS2021-1'], '北京市海淀区', '13900139001', 'zhangsan@example.com'),
            ('S20210102', '李四', '女', '2000-05-20', '110101200005200022', '2021-09-01', class_ids['CS2021-1'], '北京市朝阳区', '13900139002', 'lisi@example.com'),
            ('S20210201', '王五', '男', '2000-08-10', '110101200008100033', '2021-09-01', class_ids['CS2021-2'], '上海市浦东新区', '13900139003', 'wangwu@example.com'),
            ('S20220101', '赵六', '女', '2001-03-25', '110101200103250044', '2022-09-01', class_ids['CS2022-1'], '广州市天河区', '13900139004', 'zhaoliu@example.com'),
            ('S20210301', '钱七', '男', '2000-11-30', '110101200011300055', '2021-09-01', class_ids['MATH2021-1'], '深圳市南山区', '13900139005', 'qianqi@example.com')
        ]
        cursor.executemany("""
            INSERT INTO student (student_no, name, gender, birth_date, id_card, enrollment_date, class_id, address, phone, email) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, student_data)
        
        # 获取学生ID以便后续使用
        cursor.execute("SELECT student_id, student_no FROM student")
        students = cursor.fetchall()
        student_ids = {s['student_no']: s['student_id'] for s in students}
        
        # 学生选课和成绩数据
        print("插入选课和成绩数据...")
        sc_data = [
            (student_ids['S20210101'], offering_ids[0], 85.5, '已修完'),
            (student_ids['S20210101'], offering_ids[1], 92.0, '已修完'),
            (student_ids['S20210101'], offering_ids[2], 78.5, '已修完'),
            (student_ids['S20210102'], offering_ids[0], 88.0, '已修完'),
            (student_ids['S20210102'], offering_ids[2], 90.5, '已修完'),
            (student_ids['S20210201'], offering_ids[1], 82.0, '已修完'),
            (student_ids['S20220101'], offering_ids[3], None, '选课中')
        ]
        cursor.executemany("""
            INSERT INTO student_course (student_id, offering_id, score, status) 
            VALUES (%s, %s, %s, %s)
        """, sc_data)
        
        # 插入用户账户（除了管理员账户）
        print("插入用户账户...")
        # 为学生创建账户
        for student_no, student_id in student_ids.items():
            cursor.execute("""
                INSERT INTO user (username, password, role, related_id) 
                VALUES (%s, %s, %s, %s)
            """, (student_no, '123456', 'student', student_id))
        
        # 为教师创建账户
        for teacher_no, teacher_id in teacher_ids.items():
            cursor.execute("""
                INSERT INTO user (username, password, role, related_id) 
                VALUES (%s, %s, %s, %s)
            """, (teacher_no, '123456', 'teacher', teacher_id))
        
        # 确保管理员账户存在
        cursor.execute("SELECT COUNT(*) as count FROM user WHERE username = 'admin'")
        admin_exists = cursor.fetchone()['count']
        if admin_exists == 0:
            cursor.execute("""
                INSERT INTO user (username, password, role) VALUES 
                ('admin', '123456', 'admin')
            """)
        
        # 提交事务
        conn.commit()
        print("数据库初始化完成！")
        
    except Exception as e:
        conn.rollback()
        print(f"数据库初始化失败: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    create_tables() 