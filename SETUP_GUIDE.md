# AI 小说创作平台 - 快速启动指南

## ✨ 项目简介

AI 驱动的智能小说创作平台，提供完整的小说创作工具链，包括：
- 📚 小说管理
- 🎨 世界观设定
- 👤 角色管理
- 📈 情节架构
- ✍️ AI 辅助写作

## 🚀 快速启动

### 方式一：本地开发（推荐）

#### 1. 启动后端服务

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 运行数据库迁移
alembic upgrade head

# 启动后端服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端服务将运行在：http://localhost:8000
API 文档：http://localhost:8000/docs

#### 2. 启动前端服务

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端应用将运行在：http://localhost:5173

### 方式二：Docker 部署

```bash
# 启动所有服务（SQLite 模式）
docker-compose up -d

# 启动所有服务（PostgreSQL 模式）
docker-compose --profile postgres up -d
```

访问地址：
- 前端：http://localhost:5173
- 后端 API：http://localhost:8000
- API 文档：http://localhost:8000/docs

## 🎯 功能特性

### 已实现功能
- ✅ 用户友好的界面设计
- ✅ 小说创建、编辑、删除
- ✅ 多状态管理（草稿、进行中、已完成、已发布）
- ✅ 多类型支持（奇幻、科幻、现代、历史等）
- ✅ 响应式设计，支持移动端
- ✅ 统一的导航系统
- ✅ 美观的卡片式布局
- ✅ AI 配置管理

### 即将推出
- 🚧 角色管理系统
- 🚧 情节架构工具
- 🚧 世界观设定
- 🚧 章节管理
- 🚧 AI 内容生成
- 🚧 自动保存功能

## 🎨 界面亮点

1. **渐变主题色**：采用紫色渐变主题，现代时尚
2. **响应式布局**：完美支持桌面和移动设备
3. **直观导航**：顶部导航栏，快速访问各功能
4. **卡片式展示**：美观的卡片布局，信息清晰
5. **动画效果**：流畅的过渡和悬停效果
6. **图标系统**：丰富的图标提升用户体验

## 🛠 技术栈

### 后端
- FastAPI - 现代化 Python Web 框架
- SQLAlchemy - ORM 数据库工具
- Alembic - 数据库迁移管理
- Pydantic - 数据验证
- SQLite/PostgreSQL - 数据库

### 前端
- Vue 3 - 渐进式 JavaScript 框架
- TypeScript - 类型安全
- Element Plus - UI 组件库
- Pinia - 状态管理
- Vite - 构建工具

## 📝 使用指南

### 创建第一部小说

1. 访问 http://localhost:5173
2. 点击"开始创作"或"创建新小说"
3. 填写小说信息：
   - 标题（必填）
   - 作者
   - 类型（奇幻、科幻等）
   - 状态
   - 简介
4. 点击"保存"完成创建

### 管理小说

- **查看列表**：在小说列表页面查看所有作品
- **编辑小说**：点击卡片右上角的"..."菜单，选择"编辑"
- **删除小说**：点击"..."菜单，选择"删除"
- **查看详情**：点击小说卡片进入详情页

### 配置 AI

1. 点击右上角的设置图标
2. 选择 AI 提供商（OpenAI、Anthropic 或自定义）
3. 输入 API Key
4. 选择模型名称
5. 点击"保存配置"

## 🔒 安全注意事项

⚠️ **重要**：
- 永远不要将 `.env` 文件提交到版本控制
- API 密钥应保密，定期轮换
- 生产环境中限制 CORS 允许的源

## 📞 获取帮助

如遇到问题：
1. 检查控制台日志
2. 查看 API 文档：http://localhost:8000/docs
3. 确保后端和前端服务都在运行
4. 检查数据库迁移是否成功

## 📄 许可证

MIT License

---

**享受创作的乐趣！** ✨
