-- 创建数据库
CREATE DATABASE IF NOT EXISTS student_management;
USE student_management;

-- 学院表
CREATE TABLE IF NOT EXISTS college (
    college_id INT PRIMARY KEY AUTO_INCREMENT,
    college_name VARCHAR(50) NOT NULL,
    college_code VARCHAR(20) NOT NULL UNIQUE
);

-- 班级表
CREATE TABLE IF NOT EXISTS class (
    class_id INT PRIMARY KEY AUTO_INCREMENT,
    class_name VARCHAR(50) NOT NULL,
    class_code VARCHAR(20) NOT NULL UNIQUE,
    college_id INT NOT NULL,
    admission_year INT NOT NULL,
    FOREIGN KEY (college_id) REFERENCES college(college_id)
);

-- 职称表
CREATE TABLE IF NOT EXISTS title (
    title_id INT PRIMARY KEY AUTO_INCREMENT,
    title_name VARCHAR(20) NOT NULL,
    title_code VARCHAR(10) NOT NULL UNIQUE
);

-- 课程类型表
CREATE TABLE IF NOT EXISTS course_type (
    type_id INT PRIMARY KEY AUTO_INCREMENT,
    type_name VARCHAR(20) NOT NULL,
    type_code VARCHAR(10) NOT NULL UNIQUE
);

-- 学生表
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
);

-- 教师表
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
);

-- 课程表
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
);

-- 开课表（授课安排）
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
);

-- 学生选课和成绩表
CREATE TABLE IF NOT EXISTS student_course (
    sc_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    offering_id INT NOT NULL,
    score DECIMAL(5,2),
    status ENUM('选课中', '已修完', '已取消') DEFAULT '选课中',
    FOREIGN KEY (student_id) REFERENCES student(student_id),
    FOREIGN KEY (offering_id) REFERENCES course_offering(offering_id),
    UNIQUE KEY (student_id, offering_id)
);

-- 用户表（用于系统登录）
CREATE TABLE IF NOT EXISTS user (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL,
    role ENUM('admin', 'teacher', 'student') NOT NULL,
    related_id INT,  -- 关联到教师ID或学生ID
    status TINYINT DEFAULT 1 -- 1:启用 0:禁用
);

-- 插入一些初始数据
INSERT INTO college (college_name, college_code) VALUES 
('计算机科学与技术学院', 'CS'),
('数学学院', 'MATH'),
('物理学院', 'PHYS');

INSERT INTO title (title_name, title_code) VALUES 
('教授', 'PROF'),
('副教授', 'ASSO_PROF'),
('讲师', 'LECT');

INSERT INTO course_type (type_name, type_code) VALUES 
('必修课', 'REQ'),
('选修课', 'ELEC'),
('公共课', 'GEN');

-- 插入管理员账户
INSERT INTO user (username, password, role) VALUES 
('admin', '123456', 'admin'); 