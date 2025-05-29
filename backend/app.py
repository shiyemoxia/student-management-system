from flask import Flask, render_template, send_from_directory, json
from flask_cors import CORS
import os
from decimal import Decimal

from .config import SECRET_KEY, DEBUG, SESSION_TYPE
from .routes.auth import auth_bp
from .routes.student import student_bp
from .routes.teacher import teacher_bp
from .routes.course import course_bp
from .routes.offering import offering_bp
from .routes.score import score_bp

# 自定义JSON编码器，支持Decimal类型
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

app = Flask(
    __name__, 
    static_folder='../frontend',
    template_folder='../frontend/templates'
)

# 配置
app.config['SECRET_KEY'] = SECRET_KEY
app.config['DEBUG'] = DEBUG
app.config['SESSION_TYPE'] = SESSION_TYPE
app.json_encoder = CustomJSONEncoder  # 使用自定义JSON编码器

# 允许跨域
CORS(app, supports_credentials=True)

# 注册蓝图
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(student_bp, url_prefix='/api/student')
app.register_blueprint(teacher_bp, url_prefix='/api/teacher')
app.register_blueprint(course_bp, url_prefix='/api/course')
app.register_blueprint(offering_bp, url_prefix='/api/offering')
app.register_blueprint(score_bp, url_prefix='/api/score')

# 前端路由
@app.route('/')
def index():
    """首页"""
    return render_template('index.html')

@app.route('/<path:path>')
def static_file(path):
    """静态文件"""
    return send_from_directory('../frontend', path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 