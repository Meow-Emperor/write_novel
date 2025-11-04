# AI Novel Platform - 更新说明

## 问题修复

### 1. Docker Compose 500 错误修复

**问题原因：**
- SQLite数据库路径配置不当，容器内无法正确访问数据库文件
- 缺少数据库初始化步骤
- 数据库表未正确创建

**修复方案：**
- 更新 `docker-compose.yml`：
  - 数据库URL改为: `sqlite:////app/data/ai_novel.db` (使用绝对路径)
  - 添加健康检查
  - 添加SECRET_KEY环境变量
- 应用启动时自动创建所有数据库表 (`app/main.py`)
- 添加 `init_db.py` 脚本用于手动初始化数据库

### 2. 缺失功能实现

#### 2.1 角色管理 (Character Management)

**后端实现：**
- 新增模型：`app/models/character.py`
- 新增Schema：`app/schemas/character.py`
- 完整CRUD API：`app/api/characters.py`
  - GET `/api/characters/` - 列表（支持按novel_id筛选）
  - GET `/api/characters/{id}` - 详情
  - POST `/api/characters/` - 创建
  - PUT `/api/characters/{id}` - 更新
  - DELETE `/api/characters/{id}` - 删除

**字段：**
- name (名称)
- role (角色类型：主角、反派、配角等)
- description (描述)
- personality (性格)
- background (背景故事)
- appearance (外貌)
- relationships (关系)

#### 2.2 情节架构 (Plot Structure)

**后端实现：**
- 新增模型：`app/models/plot.py`
- 新增Schema：`app/schemas/plot.py`
- 完整CRUD API：`app/api/plots.py`
  - GET `/api/plots/` - 列表（支持按novel_id筛选）
  - GET `/api/plots/{id}` - 详情
  - POST `/api/plots/` - 创建
  - PUT `/api/plots/{id}` - 更新
  - DELETE `/api/plots/{id}` - 删除

**字段：**
- title (标题)
- description (描述)
- plot_type (类型：主线、支线、转折等)
- order (顺序)
- status (状态：计划中、进行中、已完成)
- notes (备注)

#### 2.3 章节蓝图 (Chapter Blueprint)

**后端实现：**
- 新增模型：`app/models/chapter.py`
- 新增Schema：`app/schemas/chapter.py`
- 完整CRUD API：`app/api/chapters.py`
  - GET `/api/chapters/` - 列表（支持按novel_id筛选）
  - GET `/api/chapters/{id}` - 详情
  - POST `/api/chapters/` - 创建
  - PUT `/api/chapters/{id}` - 更新
  - DELETE `/api/chapters/{id}` - 删除

**字段：**
- title (标题)
- chapter_number (章节号)
- summary (摘要)
- content (内容)
- word_count (字数)
- status (状态：草稿、进行中、已完成、已发布)
- notes (备注)

#### 2.4 世界观设定 (World Settings)

**已有实现：**
- 模型：`app/models/world.py`
- API需要在 `app/api/worlds.py` 中完善（当前仅有占位符）

#### 2.5 AI 内容生成增强

**新增AI功能端点：**

1. **角色生成** - POST `/api/ai/generate-character`
   - 根据角色类型和特征自动生成详细的角色档案
   - 包含：姓名、外貌、性格、背景、动机、角色弧线

2. **情节生成** - POST `/api/ai/generate-plot`
   - 自动生成主线/支线情节大纲
   - 可选长度：短/中/长
   - 包含：冲突、关键情节点、角色参与、高潮解决

3. **章节大纲生成** - POST `/api/ai/generate-chapter-outline`
   - 基于前面章节生成新章节大纲
   - 包含：开场、关键事件、角色发展、情节推进、悬念设置

4. **内容扩展** - POST `/api/ai/expand-content`
   - 扩展简短内容片段
   - 支持风格：简洁、详细、戏剧化
   - 添加描述、情感、对话、感官细节

**更新的Schema：** `app/schemas/ai.py`

### 3. 后台管理系统

#### 3.1 管理员系统

**后端实现：**
- 新增模型：`app/models/admin.py`
- 新增Schema：`app/schemas/admin.py`
- 新增认证模块：`app/core/security.py`
  - JWT令牌认证
  - 密码哈希（bcrypt）
- 管理员API：`app/api/admin.py`

**功能端点：**

**认证：**
- POST `/api/admin/login` - 登录获取token
- POST `/api/admin/register` - 注册管理员（首个自动为超级管理员）
- GET `/api/admin/me` - 获取当前管理员信息

**管理员管理：**
- GET `/api/admin/admins` - 列表（需超级管理员）
- PUT `/api/admin/admins/{id}` - 更新
- DELETE `/api/admin/admins/{id}` - 删除（需超级管理员）

**数据管理：**
- GET `/api/admin/stats` - 平台统计数据
- GET `/api/admin/novels` - 小说列表（管理员视图）

**权限系统：**
- `is_superuser` - 超级管理员标志
- `is_active` - 账号激活状态
- Token认证中间件

#### 3.2 前端管理后台

**新增页面：**

1. **登录页面** - `frontend/src/views/AdminLogin.vue`
   - 用户名/密码登录
   - Token存储到localStorage

2. **管理后台** - `frontend/src/views/Admin.vue`
   - 侧边栏导航菜单
   - 三大功能模块：
     - **仪表盘**：显示平台统计数据（小说总数、各状态数量）
     - **小说管理**：查看、删除小说
     - **管理员管理**：添加、编辑、删除管理员

**路由更新：**
- `/admin/login` - 登录页
- `/admin` - 管理后台（需认证）

**请求拦截器：**
- 自动为 `/admin` API添加Authorization头
- 从localStorage读取admin_token

## 数据库架构更新

### 新增表：

1. **admins** - 管理员表
   - id, username, email, hashed_password
   - full_name, is_active, is_superuser
   - created_at, updated_at, last_login

2. **characters** - 角色表
   - id, novel_id (外键)
   - name, role, description
   - personality, background, appearance, relationships
   - created_at, updated_at

3. **plots** - 情节表
   - id, novel_id (外键)
   - title, description, plot_type
   - order, status, notes
   - created_at, updated_at

4. **chapters** - 章节表
   - id, novel_id (外键)
   - title, chapter_number, summary
   - content, word_count, status, notes
   - created_at, updated_at

### 关系更新：

**Novel模型新增关系：**
```python
characters = relationship("Character", back_populates="novel", cascade="all, delete-orphan")
plots = relationship("Plot", back_populates="novel", cascade="all, delete-orphan")
chapters = relationship("Chapter", back_populates="novel", cascade="all, delete-orphan")
```

## 配置更新

### 环境变量新增：

```bash
# Security
SECRET_KEY=your-secret-key-change-in-production-please-make-it-secure-and-random
```

### Docker Compose 更新：

- DATABASE_URL使用绝对路径
- 添加SECRET_KEY环境变量
- 添加健康检查
- volume映射确保数据持久化

## 安装和运行

### 方式1：使用安装脚本

```bash
chmod +x setup.sh
./setup.sh
```

### 方式2：手动安装

**后端：**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python init_db.py
uvicorn app.main:app --reload
```

**前端：**
```bash
cd frontend
npm install
npm run dev
```

### 方式3：Docker Compose

```bash
docker compose up -d
```

注意：首次运行Docker需要等待镜像构建完成。

## 使用说明

### 创建首个管理员

首个管理员可以直接注册（自动成为超级管理员）：

```bash
curl -X POST http://localhost:8000/api/admin/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@example.com",
    "password": "admin123",
    "full_name": "Admin User"
  }'
```

或访问 http://localhost:5173/admin/login 后使用此账号登录。

### 管理后台访问

1. 访问：http://localhost:5173/admin/login
2. 使用管理员账号登录
3. 进入管理后台

### API使用示例

**创建小说：**
```bash
curl -X POST http://localhost:8000/api/novels/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "测试小说",
    "author": "作者",
    "genre": "奇幻",
    "description": "这是一个测试小说"
  }'
```

**AI生成角色：**
```bash
curl -X POST http://localhost:8000/api/ai/generate-character \
  -H "Content-Type: application/json" \
  -d '{
    "novel_id": "your-novel-id",
    "character_role": "protagonist",
    "character_traits": "勇敢、聪明、有正义感"
  }'
```

## API文档

启动后端后，访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 技术栈

### 后端
- FastAPI
- SQLAlchemy
- Pydantic
- JWT认证 (python-jose)
- 密码哈希 (passlib + bcrypt)
- OpenAI / Anthropic API集成

### 前端
- Vue 3 + TypeScript
- Element Plus UI
- Vue Router
- Axios
- Pinia (状态管理)

### 数据库
- SQLite (默认)
- PostgreSQL (可选)

## 下一步开发建议

1. **完善前端页面**：
   - 角色管理界面
   - 情节架构可视化
   - 章节编辑器增强
   - 世界观设定界面

2. **增强AI功能**：
   - 对话生成
   - 场景描述生成
   - 写作建议
   - 风格分析

3. **用户系统**：
   - 普通用户注册登录
   - 作品权限管理
   - 协作写作功能

4. **数据分析**：
   - 写作统计
   - 进度追踪
   - 词频分析

5. **导入导出**：
   - 导出为EPUB/PDF
   - 从Word导入
   - Markdown支持

## 故障排除

### Docker构建失败

如遇到网络问题，可以尝试：
1. 使用国内镜像源
2. 或直接使用本地安装（setup.sh）

### 数据库初始化失败

手动初始化：
```bash
cd backend
source venv/bin/activate
python init_db.py
```

### 端口占用

修改端口：
- 后端：`docker-compose.yml` 中的 `8000:8000`
- 前端：`docker-compose.yml` 中的 `5173:5173`

## 版本信息

- 版本：v2.0.0
- 更新日期：2024
- 主要变更：完整功能实现 + 管理后台
