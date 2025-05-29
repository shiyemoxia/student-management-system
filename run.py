from backend.app import app

if __name__ == '__main__':
    print("学生信息管理系统启动中...")
    print("请访问 http://localhost:5000 使用系统")
    print("初始登录信息：")
    print("  用户名: admin")
    print("  密码: 123456")
    app.run(host='0.0.0.0', port=5000, debug=True) 