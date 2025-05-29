# 学生学籍管理系统

一个基于Python Flask的学生学籍管理系统，前端采用Vue.js和Bootstrap，后端使用MySQL数据库。

## 功能模块

- **学生管理**：添加、编辑、查看和删除学生信息
- **教师管理**：管理教师基本信息及职称
- **课程管理**：课程的增删改查功能
- **授课管理**：教师授课安排管理
- **成绩管理**：学生成绩录入、查看和统计

## 技术栈

- **前端**：Vue.js + Bootstrap 5
- **后端**：Python Flask
- **数据库**：MySQL

## 开发环境配置

### 安装依赖
```bash
pip install -r requirements.txt
```

### 配置数据库
1. 创建MySQL数据库
2. 修改`backend/config.py`中的数据库连接参数
3. 运行`python create_tables.py`初始化数据库

### 运行应用
```bash
python run.py
```

## 系统账号
- **管理员账号**：admin
- **密码**：123456

## 更新历史

### v2.0
- 优化授课管理查看功能
- 重构成绩管理模块
- 改进添加成绩用户体验

### v1.0
- 初始版本发布
- 实现基础功能模块

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