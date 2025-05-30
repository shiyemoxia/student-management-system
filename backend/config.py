import os

# 数据库配置
# 这些参数用于建立与MySQL数据库的连接
DB_CONFIG = {
    'host': 'localhost',  # 数据库服务器地址，本地开发环境通常为localhost
    'user': 'root',  # 数据库用户名
    'password': '123456',  # 数据库密码，实际部署时应使用环境变量或配置文件存储
    'database': 'student_management',  # 要连接的数据库名称
    'charset': 'utf8mb4',  # 字符集，utf8mb4支持完整的Unicode字符集，包括表情符号
    'cursorclass': 'pymysql.cursors.DictCursor'  # 使用字典形式的游标，查询结果以字典返回而非元组
}

# Flask应用配置
SECRET_KEY = os.urandom(24)  # 生成随机密钥，用于会话安全和CSRF保护
DEBUG = True  # 开启调试模式，生产环境应设为False
SESSION_TYPE = 'filesystem'  # 会话类型，使用文件系统存储会话数据

# 分页配置
ITEMS_PER_PAGE = 10  # 每页显示的条目数，用于列表页面的分页显示