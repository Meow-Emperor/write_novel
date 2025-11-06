# 项目优化迁移指南

## 概述

本次优化参考了 [arboris-novel](https://github.com/Meow-Emperor/arboris-novel) 项目，实现了完整的多用户小说创作平台功能。

## 主要变更

### 1. 数据模型重构

#### 新增模型
- **User**: 用户系统，支持多用户隔离
- **LLMConfig**: 用户自定义 LLM 配置
- **UserDailyRequest**: 用户每日请求配额管理
- **UsageMetric**: 系统使用统计
- **Prompt**: 可配置的 AI 提示词模板
- **SystemConfig**: 系统级配置项
- **NovelBlueprint**: 小说蓝图（风格、基调、概要）
- **NovelConversation**: 灵感模式对话记录
- **CharacterRelationship**: 角色关系管理
- **ChapterVersion**: 章节多版本管理
- **ChapterEvaluation**: 章节评估系统

#### 模型变更
- **Novel**:
  - 新增 `user_id` 外键（多用户支持）
  - 新增 `initial_prompt` 字段
  - 关联 `blueprint`、`conversations`、`relationships_`

- **Character**:
  - 改用自增 ID
  - 新增 `identity`、`goals`、`abilities`、`position` 字段
  - 新增 `extra` JSON 字段用于扩展

- **Chapter**:
  - 改用自增 ID
  - 新增 `outline`、`real_summary` 字段
  - 新增 `selected_version_id` 指向选中版本
  - 关联 `versions`、`evaluations`

- **Plot**: 改用自增 ID，保留原有字段
- **WorldSetting**: 改用自增 ID，移除 `unique` 约束

### 2. 核心功能新增

#### 用户认证系统
- JWT Token 认证
- 密码 bcrypt 哈希
- 用户注册/登录
- 管理员权限控制

#### API 路由
- `POST /auth/register` - 用户注册
- `POST /auth/login` - 用户登录
- `GET /users/me` - 获取当前用户信息
- `GET /users/` - 用户列表（管理员）
- `POST /users/` - 创建用户（管理员）
- `PUT /users/{id}` - 更新用户（管理员）
- `DELETE /users/{id}` - 删除用户（管理员）

#### Prompt 管理
- `GET /prompts/` - 提示词列表
- `GET /prompts/{id}` - 获取提示词
- `GET /prompts/name/{name}` - 按名称获取
- `POST /prompts/` - 创建提示词（管理员）
- `PUT /prompts/{id}` - 更新提示词（管理员）
- `DELETE /prompts/{id}` - 删除提示词（管理员）

#### 章节多版本管理
- 每个章节可生成多个版本
- 用户可选择最佳版本
- 支持版本评估和反馈

#### 灵感模式（对话式创作）
- 通过对话引导快速搭建小说雏形
- 自动生成世界观、角色、情节、章节大纲

### 3. 配置变更

#### 新增环境变量
```bash
# Security
ACCESS_TOKEN_EXPIRE_MINUTES=1440  # Token 过期时间（分钟）

# Admin
ADMIN_DEFAULT_USERNAME=admin      # 默认管理员用户名
ADMIN_DEFAULT_PASSWORD=admin123   # 默认管理员密码
ALLOW_USER_REGISTRATION=false     # 是否允许用户注册

# Quota
DAILY_REQUEST_LIMIT=100           # 每日请求限制
```

### 4. 依赖更新

```txt
pydantic[email]==2.5.0           # 邮箱验证支持
passlib[bcrypt]==1.7.4           # bcrypt 密码哈希
```

## 迁移步骤

### 1. 备份数据（如需要）
```bash
# 备份现有数据库
cp backend/ai_novel.db backend/ai_novel.db.backup
```

### 2. 更新环境变量
```bash
# 编辑 .env 文件，添加新配置
nano .env
```

必填项：
```bash
SECRET_KEY=your-very-secure-random-key-at-least-32-characters-long
ADMIN_DEFAULT_USERNAME=admin
ADMIN_DEFAULT_PASSWORD=your-secure-password
```

### 3. 安装依赖
```bash
cd backend
pip install -r requirements.txt
```

### 4. 初始化数据库
```bash
# 删除旧数据库（如不需要保留）
rm ai_novel.db

# 初始化新数据库
python init_db.py
```

输出示例：
```
正在创建数据库表...
数据库表创建完成！
正在创建默认管理员用户: admin
管理员用户创建成功！用户名: admin

数据库初始化完成！
管理员账号: admin
管理员密码: admin123

⚠️  请在生产环境中修改默认密码！
```

### 5. 启动服务
```bash
# 开发模式
uvicorn app.main:app --reload

# 生产模式
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 6. 测试 API
```bash
# 登录获取 Token
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# 使用 Token 访问受保护接口
curl -X GET http://localhost:8000/users/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## API 文档

启动服务后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 核心功能对比

| 功能 | 原项目 | 优化后 |
|------|--------|--------|
| 用户系统 | ❌ | ✅ 多用户隔离 |
| 认证授权 | ❌ | ✅ JWT Token |
| 配额管理 | ❌ | ✅ 每日请求限制 |
| Prompt 管理 | ❌ | ✅ 后台可配置 |
| 章节多版本 | ❌ | ✅ 支持多版本对比 |
| 灵感模式 | ❌ | ✅ 对话式创作 |
| 评估系统 | ❌ | ✅ 章节评分反馈 |
| 角色关系 | ❌ | ✅ 独立关系表 |
| 蓝图系统 | ❌ | ✅ 结构化创作流程 |

## 注意事项

### 安全性
1. **生产环境必须修改默认密码**
2. **SECRET_KEY 必须使用强随机字符串**
3. **建议关闭用户注册功能**（`ALLOW_USER_REGISTRATION=false`）

### 性能
1. 章节多版本会增加存储空间
2. 建议定期清理无用版本
3. 大量用户场景建议使用 PostgreSQL

### 兼容性
1. 旧数据无法直接迁移（数据结构变化较大）
2. 前端需要适配新的 API 接口
3. 所有 API 需要 Token 认证

## 下一步计划

### 前端适配
- [ ] 实现登录/注册页面
- [ ] 添加 Token 管理
- [ ] 适配新的 API 接口
- [ ] 实现灵感模式 UI
- [ ] 实现章节多版本选择
- [ ] 实现 Prompt 管理界面（管理员）

### 功能增强
- [ ] 邮件验证
- [ ] 密码重置
- [ ] 用户头像
- [ ] 导出小说
- [ ] 协作编辑

## 问题排查

### 数据库初始化失败
```bash
# 检查 SECRET_KEY 是否配置
echo $SECRET_KEY

# 查看详细错误
python init_db.py
```

### Token 认证失败
- 检查 Token 是否过期
- 检查 Authorization Header 格式：`Bearer <token>`
- 检查 SECRET_KEY 是否一致

### 导入错误
```bash
# 重新安装依赖
pip install -r requirements.txt --force-reinstall
```

## 参考资源

- [arboris-novel 项目](https://github.com/Meow-Emperor/arboris-novel)
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 文档](https://docs.sqlalchemy.org/en/20/)
- [JWT 认证最佳实践](https://jwt.io/introduction)
