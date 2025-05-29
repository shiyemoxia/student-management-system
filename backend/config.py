import os

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',  # 修改为你的MySQL密码
    'database': 'student_management',
    'charset': 'utf8mb4',
    'cursorclass': 'pymysql.cursors.DictCursor'
}

# Flask应用配置
SECRET_KEY = os.urandom(24)
DEBUG = True
SESSION_TYPE = 'filesystem'

# 分页配置
ITEMS_PER_PAGE = 10 