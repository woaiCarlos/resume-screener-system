#!/bin/bash
# 智能简历筛选系统 - 启动脚本

cd "$(dirname "$0")"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖（如需要）
pip install -q -r requirements.txt 2>/dev/null

# 数据库迁移
python manage.py migrate --no-input 2>/dev/null

# 创建超级管理员（如果不存在）
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('✅ 管理员账户已创建: admin / admin123')
else:
    print('ℹ️  管理员账户已存在')
" 2>/dev/null

# 启动服务
echo ""
echo "========================================="
echo "📍 访问地址: http://127.0.0.1:8000"
echo "📍 管理后台: http://127.0.0.1:8000/admin"
echo "📍 用户登录: http://127.0.0.1:8000/login"
echo "📍 职位投递: http://127.0.0.1:8000/positions"
echo "========================================="
echo ""
python manage.py runserver 0.0.0.0:8000
