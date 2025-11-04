# Contributing Guide

感谢你考虑为 AI Novel Platform 做出贡献！

## 开发流程

### 1. 设置开发环境

```bash
# 克隆仓库
git clone <repository-url>
cd write_novel

# 配置环境变量
cp .env.example .env
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# 编辑 .env 文件，填入你的配置
```

### 2. 后端开发

```bash
cd backend

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 运行数据库迁移
alembic upgrade head

# 启动开发服务器
uvicorn app.main:app --reload
```

### 3. 前端开发

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 4. 运行测试

```bash
# 后端测试
cd backend
pytest

# 生成覆盖率报告
pytest --cov=app --cov-report=html
```

## 代码规范

### Python (后端)

- 使用 Python 3.11+
- 遵循 PEP 8 代码风格
- 使用类型注解
- 所有新功能必须包含测试
- 使用 `from __future__ import annotations`

### TypeScript (前端)

- 使用 TypeScript strict mode
- 使用 Vue 3 Composition API
- 遵循 Vue 风格指南
- 组件命名使用 PascalCase

## 提交规范

使用语义化提交信息：

```
feat: 添加新功能
fix: 修复 bug
docs: 文档更新
style: 代码格式化
refactor: 代码重构
test: 添加测试
chore: 构建或工具更新
```

示例：
```
feat: add character relationship management
fix: resolve novel deletion cascade issue
docs: update API documentation
```

## 数据库迁移

创建新的数据库迁移：

```bash
cd backend
alembic revision --autogenerate -m "描述变更"
alembic upgrade head
```

## API 开发

1. 在 `backend/app/api/` 创建路由文件
2. 在 `backend/app/models/` 创建数据模型
3. 在 `backend/app/schemas/` 创建 Pydantic 模型
4. 在 `backend/app/services/` 添加业务逻辑
5. 添加单元测试和集成测试
6. 更新 API 文档

## 前端开发

1. 在 `frontend/src/views/` 创建页面组件
2. 在 `frontend/src/stores/` 创建 Pinia store
3. 在 `frontend/src/types/` 定义 TypeScript 类型
4. 在 `frontend/src/router/index.ts` 添加路由
5. 使用 Element Plus 组件库

## Pull Request 流程

1. Fork 仓库并创建特性分支
2. 进行开发并确保所有测试通过
3. 提交清晰的 commit 信息
4. 创建 Pull Request，描述你的更改
5. 等待代码审查

## 需要帮助？

如有问题，请在 Issue 中提问或联系维护者。
