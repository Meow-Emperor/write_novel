# 快速启动指南

## 🚀 一键启动（推荐）

### Windows用户

双击运行 `start.bat` 文件，或在命令行中执行：

```bash
start.bat
```

### Linux/Mac用户

```bash
chmod +x start.sh
./start.sh
```

### 访问应用

启动成功后，访问：
- **前端应用**: http://localhost:5173
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs

---

## 📋 前置要求

### 必需
- **Docker Desktop** (Windows/Mac) 或 **Docker Engine** (Linux)
- **Docker Compose**

### 可选
- OpenAI API Key（如需使用OpenAI）
- Anthropic API Key（如需使用Claude）

---

## 🔧 配置说明

### 1. 数据库配置

**默认使用SQLite**（无需额外配置）：
- 数据库文件：`backend/ai_novel.db`
- 自动创建，开箱即用

**可选使用PostgreSQL**：

```bash
# 启动PostgreSQL服务
docker-compose --profile postgres up -d

# 修改backend/.env文件
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/ai_novel
```

### 2. AI API配置（可选）

编辑项目根目录的 `.env` 文件：

```env
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
```

如果不配置API Key，AI功能将无法使用，但其他功能正常。

---

## 📦 Docker命令

### 启动服务

```bash
# 使用SQLite（默认）
docker-compose up -d

# 使用PostgreSQL
docker-compose --profile postgres up -d
```

### 查看日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 停止服务

```bash
docker-compose down
```

### 重启服务

```bash
docker-compose restart
```

### 重新构建

```bash
docker-compose up -d --build
```

---

## 🛠️ 手动启动（不使用Docker）

### 后端启动

```bash
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
copy .env.example .env
# 编辑.env文件

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 前端启动

```bash
cd frontend

# 安装依赖
npm install

# 配置环境变量
copy .env.example .env

# 启动开发服务器
npm run dev
```

---

## 🗄️ 数据库选择

### SQLite（默认，推荐用于开发和小规模使用）

**优点**：
- ✅ 无需额外安装
- ✅ 零配置
- ✅ 文件存储，易于备份
- ✅ 适合单用户或小规模使用

**配置**：
```env
DATABASE_URL=sqlite:///./ai_novel.db
```

### PostgreSQL（推荐用于生产环境）

**优点**：
- ✅ 更好的并发性能
- ✅ 更强大的查询功能
- ✅ 适合多用户和大规模使用

**配置**：
```env
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/ai_novel
```

**启动PostgreSQL**：
```bash
docker-compose --profile postgres up -d
```

---

## 🔍 故障排查

### 端口被占用

如果端口5173或8000被占用，修改 `docker-compose.yml`：

```yaml
services:
  backend:
    ports:
      - "8001:8000"  # 改为8001
  frontend:
    ports:
      - "5174:5173"  # 改为5174
```

### Docker启动失败

```bash
# 查看详细日志
docker-compose logs

# 重新构建
docker-compose up -d --build

# 清理并重启
docker-compose down -v
docker-compose up -d
```

### 数据库连接失败

**SQLite**：
- 检查 `backend/ai_novel.db` 文件是否可写
- 确保 `DATABASE_URL=sqlite:///./ai_novel.db`

**PostgreSQL**：
- 确保PostgreSQL服务已启动
- 检查连接字符串是否正确
- 使用 `docker-compose logs postgres` 查看日志

### AI功能不可用

- 检查 `.env` 文件中的API Key是否正确
- 确认API Key有足够的配额
- 查看后端日志：`docker-compose logs backend`

---

## 📊 数据备份

### SQLite备份

```bash
# 复制数据库文件
cp backend/ai_novel.db backend/ai_novel.db.backup
```

### PostgreSQL备份

```bash
# 导出数据
docker-compose exec postgres pg_dump -U postgres ai_novel > backup.sql

# 恢复数据
docker-compose exec -T postgres psql -U postgres ai_novel < backup.sql
```

---

## 🎯 下一步

1. ✅ 启动服务
2. 📝 访问 http://localhost:5173
3. 🎨 创建你的第一部小说
4. 🤖 配置AI API Key（可选）
5. 📖 开始创作！

---

## 💡 提示

- **首次启动**可能需要几分钟下载Docker镜像
- **SQLite**适合个人使用和开发测试
- **PostgreSQL**适合生产环境和多用户场景
- **AI功能**是可选的，不影响其他功能使用
- 数据存储在Docker volume中，停止容器不会丢失数据

---

## 📞 获取帮助

如遇问题，请查看：
- 项目README: `README.md`
- 后端文档: `backend/README.md`
- 前端文档: `frontend/README.md`
- 实施总结: `.claude/specs/ai-novel-writing-platform/implementation-summary.md`
