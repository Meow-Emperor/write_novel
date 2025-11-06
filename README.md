# AI 小说创作平台（中文文档）

基于 FastAPI + Vue3 + Pinia + Element Plus 的 AI 小说创作平台，提供“我的小说、角色管理、情节架构、章节蓝图、世界观设定、内容编辑”等完整创作链路，并集成多家大模型（OpenAI / Anthropic / 自定义接口）。

![Status](https://img.shields.io/badge/status-ready-brightgreen)
![Version](https://img.shields.io/badge/version-2.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## 功能亮点

- 核心创作
  - 小说管理：创建/编辑/删除、列表与详情
  - 情节架构：主线/支线/反转等情节的规划与排序
  - 章节蓝图：章节大纲/状态/字数/备注管理
  - 世界观设定：时代/规则/地点/文化结构化存储
  - 内容编辑：章节内容写作、支持自动保存
- AI 能力（可在前端直接使用）
  - AI 生成角色档案（自动结构化填充表单）
  - AI 生成情节（支持“预览后编辑”或“直接创建”）
  - AI 生成章节大纲（支持“预览后编辑”或“直接创建”）
  - AI 生成/增强世界观（自动解析 json 片段回填）
  - AI 扩写选中文本（内容编辑器中一键替换）
- 灵感模式
  - 对话式引导快速搭建雏形：创建小说 → 世界观 → 主线情节 → 核心角色 → 第1章大纲
  - 既可新建也可对“已有小说”快速完善
- 管理与体验
  - 管理后台：管理员注册/登录、平台统计
  - 现代化 UI、响应式布局、前端错误处理
  - 丰富日志与健康检查、CORS、限流（可选）

## 快速开始

### 环境要求
- Node.js 18+
- Python 3.10/3.11/3.12（建议，默认 SQLite）

### 方式 A：Docker Compose（推荐）

默认不启用缓存（Redis），一条命令即可启动：

```bash
docker compose up -d
```

打开：
- 前端：http://localhost:5173
- 后端：http://localhost:8000
- API 文档：http://localhost:8000/docs

启用缓存（Redis）有两种方式：

方式一：使用 profile（先开启开关）
```bash
echo AI_CACHE_ENABLED=true >> .env
docker compose --profile cache up -d
```

方式二：使用覆盖文件（无需改 .env）
```bash
docker compose -f docker-compose.yml -f docker-compose.cache.yml up -d
```

说明：未启动或连接失败时，后端会自动降级为“无缓存模式”，AI 功能不受影响。

### 方式 B：源码运行（前后端分开）

后端（FastAPI）：
```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
python init_db.py    # 初始化数据库（SQLite）
uvicorn app.main:app --reload
```

前端（Vite + Vue3）：
```bash
cd frontend
npm install
npm run dev
```

访问：
- 前端：http://localhost:5173
- 后端：http://localhost:8000
- API 文档：http://localhost:8000/docs

## 环境变量说明

后端（.env）常用项：
- DATABASE_URL（默认 SQLite：sqlite:///./ai_novel.db）
- SECRET_KEY（必填，32+ 位随机字符串）
- OPENAI_API_KEY / ANTHROPIC_API_KEY（可选）
- ALLOWED_ORIGINS（默认 http://localhost:5173,http://localhost:3000）
- APP_NAME / DEBUG
- AI_CACHE_ENABLED（默认 false）
- REDIS_HOST / REDIS_PORT（默认 localhost / 6379；Docker 下为 redis / 6379）

前端（frontend/.env）：
- VITE_API_BASE_URL（默认 http://localhost:8000；Docker 下由 Vite 代理转发 /api 到 backend 容器）

## 前端使用指引

- 首页 → AI 配置：选择 Provider、Base URL（自定义时）、API Key、Model、Temperature（创意度）
- 我的小说：创建/编辑作品，点击卡片进入“小说详情”
- 小说详情页：提供直达入口（章节蓝图/角色/情节/世界观/内容编辑）
- 角色管理：点击“AI 生成角色”自动填充表单（外貌/性格/背景/关系）
- 情节架构：点击“AI 生成情节”，可选择“预览并编辑”或“直接创建”
- 章节蓝图：点击“AI 生成章节大纲”，同样支持“预览/直接创建”
- 世界观设定：点击“AI 生成世界观”，可选整体或单项（时代/规则/地点/文化）
- 内容编辑：选择文本 → “AI 扩写选中内容”，自动替换选区
- 灵感模式：
  - 首页卡片“灵感模式”，或小说详情的“AI 快速完善”按钮
  - 新建或快速搭建现有小说的基础雏形

## 常见问题（FAQ）

1) 连接 Redis 报错（Error 111/Connection refused）
- 已内置容错。未启动 Redis 时，AI 功能自动降级为无缓存模式，不影响使用；如需缓存，启用 Docker 的 `redis` 服务并设置 AI_CACHE_ENABLED=true。

2) Python 安装依赖失败（例如 psycopg2-binary/asyncpg）
- 本项目默认使用 SQLite，不依赖 PostgreSQL。如果你不使用 Postgres，可忽略相关包；或考虑使用 Python 3.10/3.11/3.12 环境。

3) 前端无法请求后端
- 开发模式下，Vite 代理将 `/api` 转发到后端；生产模式请设置 `VITE_API_BASE_URL` 或在反向代理层配置。

## API 速览

启动后端后访问 Swagger：
http://localhost:8000/docs

部分接口：
- `GET /api/novels` 列表 | `POST /api/novels` 创建 | `GET /api/novels/{id}` 详情
- 角色：`GET/POST/PUT/DELETE /api/characters`
- 情节：`GET/POST/PUT/DELETE /api/plots`
- 章节：`GET/POST/PUT/DELETE /api/chapters`
- 世界观：`GET/POST/PUT/DELETE /api/worlds`，按小说查询 `GET /api/worlds/novel/{novel_id}`
- AI：
  - `POST /api/ai/generate` 通用生成（支持 temperature）
  - `POST /api/ai/generate-character` 角色档案
  - `POST /api/ai/generate-plot` 情节大纲
  - `POST /api/ai/generate-chapter-outline` 章节大纲
  - `POST /api/ai/expand-content` 扩写片段
  - `POST /api/ai/generate-world` 世界观

## 目录结构

```
backend/
  app/
    api/           # FastAPI 路由
    core/          # 配置/数据库/日志
    models/        # SQLAlchemy 模型
    schemas/       # Pydantic 模型
    services/      # 业务服务（AI 等）
    main.py        # 应用入口
  requirements.txt

frontend/
  src/
    router/        # 路由
    stores/        # Pinia store
    types/         # TypeScript 类型
    utils/         # 工具
    views/         # 页面视图
    main.ts        # 入口
  package.json

docker-compose.yml               # 默认：不启用缓存
docker-compose.cache.yml         # 覆盖：启用缓存（结合 -f 使用）
```

## 许可协议

本项目基于 MIT License 开源。
