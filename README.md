# 学生信息管理系统

一个基于Python和Flask的学生信息管理系统，前端使用Vue.js和Bootstrap，数据库使用MySQL。

## 功能特点

- 学生管理：登记和管理学生基本信息
- 教师管理：登记和管理教师基本情况
- 课程管理：登记和管理课程基本情况
- 成绩管理：登记和管理学生课程成绩
- 授课管理：登记和管理教师授课安排
- 编码维护：管理系统中使用的各类编码

## 技术栈

- 后端：Python + Flask
- 前端：Vue.js + Bootstrap 5
- 数据库：MySQL

## 安装说明

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置数据库

1. 创建MySQL数据库
2. 在`backend/config.py`中修改数据库连接信息
3. 导入数据库模式

```bash
mysql -u username -p database_name < database/schema.sql
```

### 3. 运行应用

```bash
python -m backend.app
```

应用将在 http://localhost:5000 运行。

### 4. 初始登录信息

- 用户名：admin
- 密码：123456

## 项目结构

```
student_management_system/
├── backend/             # Python后端
│   ├── app.py           # 主应用文件
│   ├── config.py        # 配置文件
│   ├── models.py        # 数据模型
│   ├── routes/          # API路由
│   └── utils.py         # 工具函数
├── frontend/            # 前端
│   ├── css/             # 样式文件
│   ├── js/              # JavaScript文件
│   └── templates/       # HTML模板
├── database/            # 数据库脚本
│   └── schema.sql       # 数据库模式
├── requirements.txt     # Python依赖
└── README.md            # 项目说明
```

## 项目截图

暂无截图。

## 开发者

- 数据库课设小组 