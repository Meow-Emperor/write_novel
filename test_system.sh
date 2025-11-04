#!/bin/bash

# AI 小说平台系统测试脚本

echo "================================"
echo "  AI 小说创作平台 - 系统测试"
echo "================================"
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 测试后端
echo "🔍 测试后端服务..."
BACKEND_HEALTH=$(curl -s http://localhost:8000/health)
if echo "$BACKEND_HEALTH" | grep -q "healthy"; then
    echo -e "${GREEN}✅ 后端服务运行正常${NC}"
    echo "   地址: http://localhost:8000"
else
    echo -e "${RED}❌ 后端服务未运行${NC}"
    exit 1
fi

# 测试API
echo ""
echo "🔍 测试小说API..."
NOVELS_COUNT=$(curl -s http://localhost:8000/api/novels/ | python3 -c "import sys, json; print(len(json.load(sys.stdin)))" 2>/dev/null)
if [ ! -z "$NOVELS_COUNT" ]; then
    echo -e "${GREEN}✅ 小说API正常，当前有 $NOVELS_COUNT 部小说${NC}"
else
    echo -e "${RED}❌ 小说API异常${NC}"
fi

# 列出所有小说
echo ""
echo "📚 小说列表:"
curl -s http://localhost:8000/api/novels/ | python3 -c "
import sys, json
novels = json.load(sys.stdin)
if novels:
    for n in novels:
        status_icons = {'DRAFT': '📝', 'IN_PROGRESS': '⏳', 'COMPLETED': '✅', 'PUBLISHED': '📖'}
        genre_icons = {'fantasy': '🧙', 'sci-fi': '🚀', 'modern': '🏙️', 'historical': '📜'}
        print(f\"   {status_icons.get(n['status'], '❓')} {genre_icons.get(n['genre'], '📚')} {n['title']} - {n['author'] or '未知作者'}\")
else:
    print('   暂无小说')
"

# 测试数据库
echo ""
echo "🔍 测试数据库..."
if [ -f "backend/ai_novel.db" ]; then
    DB_SIZE=$(du -h backend/ai_novel.db | cut -f1)
    echo -e "${GREEN}✅ 数据库存在 (大小: $DB_SIZE)${NC}"
else
    echo -e "${RED}❌ 数据库文件未找到${NC}"
fi

# 检查前端构建
echo ""
echo "🔍 检查前端..."
if [ -d "frontend/node_modules" ]; then
    echo -e "${GREEN}✅ 前端依赖已安装${NC}"
else
    echo -e "${YELLOW}⚠️  前端依赖未安装${NC}"
fi

# API端点测试
echo ""
echo "🔍 测试API端点..."
endpoints=("/" "/health" "/api/novels/")
for endpoint in "${endpoints[@]}"; do
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:8000$endpoint")
    if [ "$STATUS" = "200" ] || [ "$STATUS" = "307" ]; then
        echo -e "   ${GREEN}✅${NC} $endpoint - HTTP $STATUS"
    else
        echo -e "   ${RED}❌${NC} $endpoint - HTTP $STATUS"
    fi
done

# 显示快速启动命令
echo ""
echo "================================"
echo "  ✨ 快速启动命令"
echo "================================"
echo ""
echo "启动后端:"
echo "  cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo ""
echo "启动前端:"
echo "  cd frontend && npm run dev"
echo ""
echo "访问地址:"
echo "  前端: http://localhost:5173"
echo "  后端: http://localhost:8000"
echo "  API文档: http://localhost:8000/docs"
echo ""
echo "================================"
