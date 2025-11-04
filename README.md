# AI Novel Platform

AI驱动的智能小说创作平台，支持世界观设定、角色管理、情节架构和AI辅助写作。

## 技术栈

### 后端
- **FastAPI** - 现代化的Python Web框架
- **SQLAlchemy** - ORM数据库工具
- **Alembic** - 数据库迁移管理
- **Pydantic** - 数据验证
- **SQLite/PostgreSQL** - 数据库

### 前端
- **Vue 3** - 渐进式JavaScript框架
- **TypeScript** - 类型安全
- **Element Plus** - UI组件库
- **Pinia** - 状态管理
- **Vite** - 构建工具

### AI集成
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude 3)
- 自定义API支持

## 快速开始

### 环境要求
- Python 3.9+
- Node.js 18+
- Docker & Docker Compose (可选)

### 本地开发

#### 1. 克隆仓库
```bash
git clone <repository-url>
cd write_novel
```

#### 2. 配置环境变量
```bash
# 复制环境变量模板
cp .env.example .env
cp backend/.env.example backend/.env

# 编辑 .env 文件，填入你的API密钥
# ⚠️ 警告：永远不要提交包含真实密钥的 .env 文件到Git！
```

#### 3. 启动后端
```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 运行数据库迁移
alembic upgrade head

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端API将运行在: http://localhost:8000

#### 4. 启动前端
```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端应用将运行在: http://localhost:5173

### Docker部署

```bash
# 启动所有服务（SQLite模式）
docker-compose up -d

# 启动所有服务（PostgreSQL模式）
docker-compose --profile postgres up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

访问:
- 前端: http://localhost:5173
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

## 项目结构

```
write_novel/
├── backend/
│   ├── app/
│   │   ├── api/          # API路由
│   │   ├── core/         # 核心配置
│   │   ├── models/       # 数据模型
│   │   ├── schemas/      # Pydantic验证模型
│   │   ├── services/     # 业务逻辑
│   │   └── main.py       # 应用入口
│   ├── alembic/          # 数据库迁移
│   ├── requirements.txt  # Python依赖
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── stores/       # Pinia状态管理
│   │   ├── types/        # TypeScript类型
│   │   ├── views/        # 页面视图
│   │   ├── router/       # 路由配置
│   │   └── main.ts       # 应用入口
│   ├── package.json      # npm依赖
│   └── Dockerfile
└── docker-compose.yml
```

## 核心功能

### 已实现
- ✅ 小说创建、编辑、删除
- ✅ 多AI提供商支持（OpenAI、Anthropic、自定义）
- ✅ 世界观设定数据模型
- ✅ 响应式前端界面
- ✅ 数据库迁移管理
- ✅ 日志记录系统
- ✅ API 速率限制
- ✅ 错误处理和验证
- ✅ 数据库连接池
- ✅ 单元测试框架
- ✅ 健康检查端点
- ✅ 前端错误处理
- ✅ 环境变量配置

### 规划中
- 🚧 角色管理系统
- 🚧 情节架构工具
- 🚧 章节管理与蓝图
- 🚧 智能内容编辑器
- 🚧 自动保存功能
- 🚧 用户认证与授权
- 🚧 Redis 缓存集成
- 🚧 WebSocket 实时更新

## API文档

启动后端后访问: http://localhost:8000/docs

主要接口:
- `GET /api/novels` - 获取小说列表
- `POST /api/novels` - 创建新小说
- `GET /api/novels/{id}` - 获取小说详情
- `PUT /api/novels/{id}` - 更新小说
- `DELETE /api/novels/{id}` - 删除小说
- `POST /api/ai/generate` - AI内容生成

## 数据库迁移

```bash
cd backend

# 创建新迁移
alembic revision --autogenerate -m "描述变更内容"

# 应用迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1

# 查看迁移历史
alembic history
```

## 安全注意事项

⚠️ **重要安全提示**:

1. **永远不要提交 `.env` 文件到Git**
   - 使用 `.env.example` 作为模板
   - `.env` 文件已被 `.gitignore` 排除

2. **API密钥管理**
   - 定期轮换API密钥
   - 使用环境变量而非硬编码
   - 生产环境使用密钥管理服务

3. **CORS配置**
   - 生产环境中限制允许的源
   - 当前配置仅适用于开发环境

## 开发指南

### 添加新的数据模型
1. 在 `backend/app/models/` 创建模型文件
2. 在 `backend/app/models/__init__.py` 导出
3. 创建对应的Pydantic schema在 `backend/app/schemas/`
4. 运行 `alembic revision --autogenerate -m "描述"`
5. 应用迁移 `alembic upgrade head`

### 添加新的API路由
1. 在 `backend/app/api/` 创建路由文件
2. 在 `backend/app/api/__init__.py` 导出
3. 在 `backend/app/main.py` 注册路由
4. 添加日志记录和错误处理
5. 编写单元测试

### 添加新的前端页面
1. 在 `frontend/src/views/` 创建Vue组件
2. 在 `frontend/src/router/index.ts` 添加路由
3. 如需状态管理，在 `frontend/src/stores/` 创建store
4. 使用 composables 处理错误和加载状态

### 运行测试
```bash
# 后端测试
cd backend
pytest

# 生成覆盖率报告
pytest --cov=app --cov-report=html

# 查看报告
open htmlcov/index.html
```

### 查看日志
```bash
# 开发环境日志输出到控制台
# 生产环境日志保存在 backend/logs/app.log
```

## 贡献

欢迎提交Issue和Pull Request!

## 许可证

MIT License
