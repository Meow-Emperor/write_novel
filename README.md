# ✨ AI 小说创作平台

AI驱动的智能小说创作平台，提供完整的创作工具链，包括小说管理、世界观设定、角色管理、情节架构和AI辅助写作。

![Status](https://img.shields.io/badge/status-ready-brightgreen)
![Version](https://img.shields.io/badge/version-2.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## 🎯 特色功能

### 核心功能
- 📚 **小说管理** - 创建、编辑、管理你的小说作品
- 👥 **角色管理** - 详细的角色档案，包括外貌、性格、背景、关系等
- 📖 **章节蓝图** - 章节规划、大纲、内容编写和管理
- 🎭 **情节架构** - 主线、支线情节的规划和追踪
- 🌍 **世界观设定** - 构建完整的世界观体系

### AI 智能助手
- 🤖 **AI角色生成** - 根据角色类型自动生成完整角色档案
- 📝 **AI情节生成** - 智能创建主线/支线情节大纲
- 📋 **AI章节大纲** - 基于上下文生成章节大纲
- ✨ **AI内容扩展** - 扩展简短内容为详细描述
- 🎨 **多风格支持** - 简洁、详细、戏剧化等多种写作风格

### 管理后台
- 🔐 **管理员系统** - 完整的管理员认证和权限管理
- 📊 **数据统计** - 平台数据概览和统计分析
- 👨‍💼 **用户管理** - 管理员账号的创建、编辑、删除
- 📚 **内容管理** - 小说内容的审核和管理

### 技术特性
- 🎨 **美观UI** - 现代化的渐变设计和流畅动画
- 📱 **响应式** - 完美支持桌面和移动设备
- 🚀 **高性能** - 优化的数据库索引和缓存策略
- 🔒 **安全** - JWT认证、密码加密、完善的数据验证
- 🔌 **AI集成** - 支持 OpenAI、Anthropic 等多个AI提供商

## 🚀 快速开始

### 📋 环境要求

- Python 3.9+
- Node.js 18+
- Git

### 🔧 安装步骤

#### 方法 1：一键安装（推荐）

```bash
git clone <repository-url>
cd write_novel
chmod +x setup.sh
./setup.sh
```

#### 方法 2：Docker Compose

```bash
docker compose up -d
```

访问:
- 前端: http://localhost:5173
- 后端: http://localhost:8000
- API文档: http://localhost:8000/docs
- 管理后台: http://localhost:5173/admin

#### 方法 3：手动安装

**启动后端**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python init_db.py  # 初始化数据库
uvicorn app.main:app --reload
```

**启动前端**
```bash
cd frontend
npm install
npm run dev
```

**访问应用**
- 前端: http://localhost:5173
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

## 📖 使用指南

### 创建管理员账号

首次运行时，需要创建管理员账号（首个账号自动成为超级管理员）：

**方法 1：API创建**
```bash
curl -X POST http://localhost:8000/api/admin/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@example.com",
    "password": "admin123",
    "full_name": "系统管理员"
  }'
```

**方法 2：通过注册页面**
访问 http://localhost:5173/admin/login 使用上述凭据登录

### 管理后台功能

登录后台后，可以使用以下功能：

1. **仪表盘** - 查看平台统计数据
   - 小说总数及各状态统计
   - 管理员数量

2. **小说管理** - 管理所有小说
   - 查看所有小说列表
   - 删除小说

3. **管理员管理** - 管理管理员账号（需超级管理员权限）
   - 创建新管理员
   - 编辑管理员信息
   - 删除管理员账号
   - 设置超级管理员权限

### 使用 AI 功能

平台提供多种 AI 辅助创作功能：

**1. 生成角色档案**
```bash
curl -X POST http://localhost:8000/api/ai/generate-character \
  -H "Content-Type: application/json" \
  -d '{
    "novel_id": "your-novel-id",
    "character_role": "protagonist",
    "character_traits": "勇敢、聪明、富有正义感"
  }'
```

**2. 生成情节大纲**
```bash
curl -X POST http://localhost:8000/api/ai/generate-plot \
  -H "Content-Type: application/json" \
  -d '{
    "novel_id": "your-novel-id",
    "plot_type": "main",
    "plot_length": "medium"
  }'
```

**3. 生成章节大纲**
```bash
curl -X POST http://localhost:8000/api/ai/generate-chapter-outline \
  -H "Content-Type: application/json" \
  -d '{
    "novel_id": "your-novel-id",
    "chapter_number": 1,
    "chapter_theme": "主角觉醒"
  }'
```

**4. 扩展内容**
```bash
curl -X POST http://localhost:8000/api/ai/expand-content \
  -H "Content-Type: application/json" \
  -d '{
    "novel_id": "your-novel-id",
    "chapter_id": "your-chapter-id",
    "content_snippet": "他走进了黑暗的森林",
    "expansion_style": "detailed"
  }'
```

详细的使用说明请参阅：
- [UPDATES.md](UPDATES.md) - 功能更新详情
- [API文档](http://localhost:8000/docs) - 完整API参考

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
