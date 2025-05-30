from flask import Flask, render_template, send_from_directory, json
from flask_cors import CORS
import os
from decimal import Decimal

# 导入配置和路由蓝图
from .config import SECRET_KEY, DEBUG, SESSION_TYPE
from .routes.auth import auth_bp
from .routes.student import student_bp
from .routes.teacher import teacher_bp
from .routes.course import course_bp
from .routes.offering import offering_bp
from .routes.score import score_bp

# 自定义JSON编码器，支持Decimal类型
class CustomJSONEncoder(json.JSONEncoder):
    """自定义JSON编码器
    
    Flask默认的JSON编码器不能处理Decimal类型，我们需要将其转换为float类型
    以便前端能够正确处理数值数据，特别是成绩和学分等
    """
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)  # 将Decimal类型转换为float类型
        return super().default(obj)  # 其他类型使用默认转换

# 创建Flask应用实例
app = Flask(
    __name__, 
    static_folder='../frontend',  # 设置静态文件目录为frontend
    template_folder='../frontend/templates'  # 设置模板文件目录
)

# 应用配置
app.config['SECRET_KEY'] = SECRET_KEY  # 设置密钥，用于会话加密
app.config['DEBUG'] = DEBUG  # 设置调试模式
app.config['SESSION_TYPE'] = SESSION_TYPE  # 设置会话类型
app.json_encoder = CustomJSONEncoder  # 使用自定义JSON编码器

# 启用CORS（跨域资源共享）以允许前端发送请求
CORS(app, supports_credentials=True)  # supports_credentials=True 允许跨域请求携带Cookie

# 注册蓝图，每个蓝图代表一组相关功能的路由
app.register_blueprint(auth_bp, url_prefix='/api/auth')  # 认证相关路由
app.register_blueprint(student_bp, url_prefix='/api/student')  # 学生相关路由
app.register_blueprint(teacher_bp, url_prefix='/api/teacher')  # 教师相关路由
app.register_blueprint(course_bp, url_prefix='/api/course')  # 课程相关路由
app.register_blueprint(offering_bp, url_prefix='/api/offering')  # 授课安排相关路由
app.register_blueprint(score_bp, url_prefix='/api/score')  # 成绩相关路由

# 前端路由处理
@app.route('/')
def index():
    """首页路由
    
    返回前端应用的入口页面
    """
    return render_template('index.html')

@app.route('/<path:path>')
def static_file(path):
    """静态文件服务
    
    处理所有其他路由，返回相应的静态文件
    用于提供前端资源如JS、CSS、图片等
    """
    return send_from_directory('../frontend', path)

# 应用入口
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # 在所有网络接口上运行应用，端口为5000 