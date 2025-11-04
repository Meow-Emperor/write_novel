# Performance Optimization Guide

本文档描述了项目中实施的性能优化和最佳实践。

## 后端优化

### 1. 数据库优化

#### 索引
在关键字段上添加了索引以提高查询性能：
- `novels.title` - 用于搜索和排序
- `novels.author` - 用于按作者筛选
- `novels.genre` - 用于按类型筛选
- `novels.status` - 用于按状态筛选
- `novels.created_at` - 用于时间排序

#### 连接池配置
```python
pool_size=10          # 基础连接池大小
max_overflow=20       # 额外连接数
pool_timeout=30       # 连接超时时间
pool_recycle=3600     # 连接回收时间
```

#### 查询优化
- 使用 `order_by()` 优化列表查询
- 实现分页（skip/limit）减少数据传输
- 使用 `pool_pre_ping` 验证连接有效性

### 2. 缓存策略

#### 内存缓存
使用 `CacheManager` 进行简单的内存缓存：
```python
from app.core.cache import cache

# 缓存数据
cache.set("key", data, ttl=300)

# 获取缓存
cached_data = cache.get("key")
```

#### 生产环境建议
- 使用 Redis 作为分布式缓存
- 缓存频繁访问的数据（小说列表、AI配置）
- 实现缓存失效策略

### 3. API 速率限制

使用 SlowAPI 限制请求频率：
```python
@limiter.limit("10/minute")
async def endpoint(request: Request):
    pass
```

### 4. 日志优化

- 开发环境：详细日志到控制台
- 生产环境：INFO级别日志到文件
- 使用异步日志避免阻塞

### 5. 数据库会话管理

- 使用依赖注入管理数据库会话
- 自动关闭会话防止连接泄漏
- 错误时自动回滚事务

## 前端优化

### 1. 代码分割

使用 Vue Router 的懒加载：
```typescript
component: () => import('@/views/NovelDetail.vue')
```

### 2. API 请求优化

#### 统一请求处理
使用 axios 实例配置：
- 统一 baseURL
- 全局超时设置（60秒）
- 统一错误处理
- 请求/响应拦截器

#### 错误处理
使用 composables 统一处理错误：
```typescript
import { useErrorHandler } from '@/composables/useErrorHandler'

const { handleError, handleSuccess } = useErrorHandler()
```

### 3. 状态管理

- 使用 Pinia 进行状态管理
- 缓存已加载的数据
- 避免重复请求

### 4. 加载状态

使用 `useLoading` composable：
```typescript
const { loading, withLoading } = useLoading()
await withLoading(() => fetchData())
```

### 5. 自动保存

实现自动保存管理器：
- 30秒自动保存间隔
- 防止数据丢失
- 可配置保存频率

## Docker 优化

### 1. 镜像优化

#### 后端
- 使用 `python:3.11-slim` 减小镜像大小
- 多阶段构建（如需要）
- 清理 apt 缓存

#### 前端
- 使用 `node:20-alpine` 减小镜像大小
- npm 缓存优化

### 2. 健康检查

- 后端：检查 `/health` 端点
- 前端：检查服务可用性
- 合理的检查间隔和超时

### 3. 资源限制

在生产环境使用 docker-compose 限制资源：
```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
```

## 监控建议

### 1. 性能监控

- 使用 APM 工具（如 New Relic, DataDog）
- 监控 API 响应时间
- 跟踪数据库查询性能

### 2. 错误监控

- 集成 Sentry 进行错误跟踪
- 日志聚合（ELK Stack）
- 实时告警

### 3. 关键指标

- API 响应时间
- 数据库查询时间
- 错误率
- 请求速率
- 内存使用
- CPU 使用

## 扩展性

### 水平扩展

1. **无状态设计**
   - API 服务器无状态
   - 会话存储在 Redis

2. **负载均衡**
   - 使用 Nginx 或云负载均衡器
   - 健康检查配置

3. **数据库扩展**
   - 读写分离
   - 数据库复制
   - 连接池优化

### 垂直扩展

- 增加服务器资源
- 优化数据库配置
- 调整连接池大小

## 最佳实践清单

- [ ] 数据库字段添加适当索引
- [ ] 实现查询分页
- [ ] 使用连接池
- [ ] 实现缓存策略
- [ ] 添加 API 速率限制
- [ ] 实现日志记录
- [ ] 添加健康检查端点
- [ ] 使用环境变量配置
- [ ] 实现错误处理
- [ ] 编写单元测试
- [ ] 优化 Docker 镜像
- [ ] 配置监控和告警
- [ ] 使用 CDN（生产环境）
- [ ] 启用 GZIP 压缩
- [ ] 实现数据备份策略

## 未来优化计划

1. **Redis 集成**
   - 分布式缓存
   - 会话存储
   - 任务队列

2. **WebSocket**
   - 实时更新
   - 多用户协作

3. **异步任务**
   - Celery 集成
   - 后台任务处理

4. **CDN**
   - 静态资源加速
   - 图片优化

5. **数据库优化**
   - 查询优化
   - 索引优化
   - 分区策略
