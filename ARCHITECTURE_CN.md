# AI小说写作平台 - 架构文档

## 项目概述

这是一个基于AI的智能小说创作平台，提供世界观设定、角色管理、情节架构和AI辅助写作等功能。项目采用前后端分离架构，后端使用FastAPI，前端使用Vue 3 + TypeScript。

## 技术架构

### 后端架构 (FastAPI + SQLAlchemy)

#### 核心模块

1. **应用入口** (`backend/app/main.py`)
   - FastAPI应用初始化
   - CORS中间件配置
   - 路由注册
   - 数据库表创建

2. **核心配置** (`backend/app/core/`)
   - `config.py`: 应用配置管理，从环境变量加载配置
   - `database.py`: 数据库连接和会话管理

3. **数据模型** (`backend/app/models/`)
   - `novel.py`: 小说模型和状态枚举
   - `world.py`: 世界观设定模型
   - 使用SQLAlchemy ORM定义表结构

4. **数据传输对象** (`backend/app/schemas/`)
   - `novel.py`: 小说的请求/响应模式
   - `ai.py`: AI服务的请求/响应模式
   - 使用Pydantic进行数据验证

5. **业务服务** (`backend/app/services/`)
   - `ai_service.py`: AI内容生成服务
     - 支持OpenAI (GPT-4, GPT-3.5)
     - 支持Anthropic (Claude)
     - 支持自定义API
     - 智能上下文构建

6. **API路由** (`backend/app/api/`)
   - `novels.py`: 小说CRUD接口
   - `ai.py`: AI内容生成接口
   - `characters.py`: 角色管理接口（占位符）
   - `worlds.py`: 世界观设定接口（占位符）
   - `plots.py`: 情节结构接口（占位符）
   - `chapters.py`: 章节管理接口（占位符）

#### 数据库设计

**小说表 (novels)**
- id: 唯一标识符 (UUID)
- title: 标题
- author: 作者
- genre: 类型/流派
- description: 简介
- status: 状态 (DRAFT/IN_PROGRESS/COMPLETED/PUBLISHED)
- created_at: 创建时间
- updated_at: 更新时间

**世界观设定表 (world_settings)**
- id: 唯一标识符 (UUID)
- novel_id: 关联小说ID (外键，一对一关系)
- era: 时代背景
- locations: 地点列表 (JSON)
- rules: 世界规则 (JSON)
- culture: 文化设定 (JSON)
- created_at: 创建时间

### 前端架构 (Vue 3 + TypeScript)

#### 核心模块

1. **应用入口** (`frontend/src/main.ts`)
   - Vue应用创建
   - 插件注册（Pinia、Router、Element Plus）
   - 全局配置

2. **路由配置** (`frontend/src/router/`)
   - 页面路由定义
   - 导航守卫（待实现）
   - 路由懒加载

3. **状态管理** (`frontend/src/stores/`)
   - `novel.ts`: 小说状态管理
     - 小说列表、当前小说
     - CRUD操作
     - 加载状态和错误处理
   - `ai.ts`: AI服务状态管理
     - AI配置管理
     - 内容生成
     - 错误处理

4. **类型定义** (`frontend/src/types/`)
   - `novel.ts`: 小说相关类型
   - `plot.ts`: 情节结构类型
   - TypeScript接口定义

5. **工具函数** (`frontend/src/utils/`)
   - `autosave.ts`: 自动保存管理器
     - 定时自动保存
     - 手动保存
     - 可配置保存间隔

6. **页面视图** (`frontend/src/views/`)
   - `Home.vue`: 首页
   - `NovelList.vue`: 小说列表页
   - `NovelDetail.vue`: 小说详情页
   - `CharacterManagement.vue`: 角色管理页（待完善）
   - `PlotStructure.vue`: 情节结构页（待完善）
   - `WorldSettings.vue`: 世界观设定页（待完善）
   - `ChapterBlueprint.vue`: 章节蓝图页（待完善）
   - `ContentEditor.vue`: 内容编辑器页（待完善）

## 核心功能流程

### 1. 小说管理流程

```
用户操作 → Vue组件 → Pinia Store → Axios → 后端API → 数据库
                ↓
           UI更新 ← Store状态更新 ← 响应数据
```

### 2. AI内容生成流程

```
用户提示词 → AI Store → 后端AI接口 → AIService
                                        ↓
                                    选择提供商
                                        ↓
                        OpenAI / Anthropic / 自定义API
                                        ↓
                                    构建上下文
                                        ↓
                                    生成内容
                                        ↓
                                返回结果 → 前端展示
```

### 3. 数据流向

```
前端组件
    ↓
Pinia Store (状态管理)
    ↓
Axios (HTTP客户端)
    ↓
FastAPI路由 (API接口)
    ↓
Service层 (业务逻辑)
    ↓
SQLAlchemy (ORM)
    ↓
数据库 (SQLite/PostgreSQL)
```

## 代码规范

### Python后端

1. **文件组织**
   - 每个文件顶部添加模块说明文档字符串
   - 类和函数使用docstring注释
   - 类型注解使用`from __future__ import annotations`

2. **注释风格**
   ```python
   """
   模块说明
   详细描述模块功能
   """
   
   class MyClass:
       """类说明"""
       
       def my_method(self, param: str) -> str:
           """
           方法说明
           
           Args:
               param: 参数说明
               
           Returns:
               返回值说明
           """
   ```

3. **命名规范**
   - 类名：大驼峰 (PascalCase)
   - 函数/变量：下划线 (snake_case)
   - 常量：全大写下划线 (UPPER_SNAKE_CASE)

### TypeScript前端

1. **文件组织**
   - 每个文件顶部添加JSDoc注释
   - 接口和类型添加说明注释
   - 重要函数添加JSDoc注释

2. **注释风格**
   ```typescript
   /**
    * 模块说明
    * 详细描述模块功能
    */
   
   /**
    * 接口说明
    */
   export interface MyInterface {
     field: string  // 字段说明
   }
   
   /**
    * 函数说明
    * @param param 参数说明
    * @returns 返回值说明
    */
   function myFunction(param: string): string {
     // 实现
   }
   ```

3. **命名规范**
   - 类型/接口：大驼峰 (PascalCase)
   - 函数/变量：小驼峰 (camelCase)
   - 常量：全大写下划线 (UPPER_SNAKE_CASE)
   - 组件：大驼峰 (PascalCase)

## 配置说明

### 环境变量配置

后端环境变量 (`.env`):
```bash
# 数据库配置
DATABASE_URL=sqlite:///./ai_novel.db

# AI服务配置
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
CUSTOM_API_URL=your_custom_api_url
CUSTOM_API_KEY=your_custom_key

# CORS配置
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# 应用配置
APP_NAME=AI Novel Platform
DEBUG=true
```

### Docker配置

使用Docker Compose可以快速启动整个应用栈：

```yaml
services:
  backend:   # FastAPI后端服务
  frontend:  # Vue前端服务
  postgres:  # PostgreSQL数据库（可选）
```

## 开发工作流

### 添加新功能

1. **后端API开发**
   ```bash
   # 1. 创建数据模型
   backend/app/models/your_model.py
   
   # 2. 创建Pydantic模式
   backend/app/schemas/your_schema.py
   
   # 3. 创建API路由
   backend/app/api/your_router.py
   
   # 4. 生成数据库迁移
   cd backend
   alembic revision --autogenerate -m "add your feature"
   alembic upgrade head
   
   # 5. 在main.py中注册路由
   ```

2. **前端功能开发**
   ```bash
   # 1. 创建类型定义
   frontend/src/types/your_type.ts
   
   # 2. 创建Pinia Store
   frontend/src/stores/your_store.ts
   
   # 3. 创建Vue组件
   frontend/src/views/YourView.vue
   
   # 4. 配置路由
   frontend/src/router/index.ts
   ```

### 测试流程

1. **后端测试**
   ```bash
   cd backend
   pytest  # 运行单元测试
   ```

2. **前端测试**
   ```bash
   cd frontend
   npm run test  # 运行测试
   npm run build # 构建生产版本
   ```

## 安全考虑

1. **API密钥管理**
   - 使用环境变量存储敏感信息
   - 永远不要提交`.env`文件到Git
   - 生产环境使用密钥管理服务

2. **输入验证**
   - 后端使用Pydantic进行数据验证
   - 前端使用TypeScript类型检查
   - SQL注入防护（ORM自动处理）

3. **CORS配置**
   - 开发环境允许本地域名
   - 生产环境严格限制允许的源

## 性能优化

1. **后端优化**
   - 使用异步IO (async/await)
   - 数据库连接池
   - 适当的索引设计

2. **前端优化**
   - 路由懒加载
   - 组件按需加载
   - 自动保存防抖

## 待完善功能

- [ ] 角色管理系统完整实现
- [ ] 情节架构工具
- [ ] 章节管理与版本控制
- [ ] 富文本编辑器集成
- [ ] 用户认证与授权
- [ ] 多用户协作
- [ ] 导出功能（PDF、EPUB等）
- [ ] 数据备份和恢复

## 贡献指南

1. Fork本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 许可证

MIT License
