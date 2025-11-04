# Deployment Guide

生产环境部署指南。

## 准备工作

### 1. 环境变量配置

创建生产环境的 `.env` 文件：

```bash
# 数据库（使用 PostgreSQL）
DATABASE_URL=postgresql://user:password@db-host:5432/ai_novel

# AI 提供商
OPENAI_API_KEY=your-production-openai-key
ANTHROPIC_API_KEY=your-production-anthropic-key

# CORS（设置为你的前端域名）
ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com

# 应用设置
APP_NAME=AI Novel Platform
DEBUG=false
```

### 2. 数据库设置

#### PostgreSQL
```bash
# 创建数据库
createdb ai_novel

# 运行迁移
cd backend
alembic upgrade head
```

### 3. 安全配置

- [ ] 使用强密码
- [ ] 启用 HTTPS
- [ ] 配置防火墙
- [ ] 限制数据库访问
- [ ] 定期更新依赖
- [ ] 配置备份策略

## 部署选项

### 选项 1: Docker Compose

最简单的部署方式：

```bash
# 克隆代码
git clone <repository-url>
cd write_novel

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件

# 使用 PostgreSQL 启动
docker-compose --profile postgres up -d

# 查看日志
docker-compose logs -f
```

#### 生产环境 docker-compose.yml
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: ai_novel
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - app-network
    restart: unless-stopped

  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/ai_novel
      DEBUG: false
    depends_on:
      - postgres
    networks:
      - app-network
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    networks:
      - app-network
    restart: unless-stopped

volumes:
  postgres_data:

networks:
  app-network:
    driver: bridge
```

### 选项 2: 云平台部署

#### AWS
- **Backend**: Elastic Beanstalk / ECS
- **Frontend**: S3 + CloudFront
- **Database**: RDS PostgreSQL
- **Cache**: ElastiCache Redis

#### Google Cloud Platform
- **Backend**: Cloud Run / GKE
- **Frontend**: Cloud Storage + Cloud CDN
- **Database**: Cloud SQL PostgreSQL
- **Cache**: Memorystore Redis

#### Azure
- **Backend**: App Service / AKS
- **Frontend**: Static Web Apps
- **Database**: Azure Database for PostgreSQL
- **Cache**: Azure Cache for Redis

### 选项 3: VPS 部署

#### 1. 安装依赖

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装 Python
sudo apt install python3.11 python3-pip python3-venv -y

# 安装 Node.js
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install nodejs -y

# 安装 PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# 安装 Nginx
sudo apt install nginx -y
```

#### 2. 部署后端

```bash
# 创建应用用户
sudo useradd -m -s /bin/bash ainovel

# 克隆代码
cd /opt
sudo git clone <repository-url> ainovel
sudo chown -R ainovel:ainovel /opt/ainovel

# 设置后端
cd /opt/ainovel/backend
sudo -u ainovel python3 -m venv .venv
sudo -u ainovel .venv/bin/pip install -r requirements.txt

# 配置环境变量
sudo -u ainovel cp .env.example .env
sudo -u ainovel nano .env

# 运行迁移
sudo -u ainovel .venv/bin/alembic upgrade head
```

#### 3. 配置 Systemd 服务

创建 `/etc/systemd/system/ainovel.service`:

```ini
[Unit]
Description=AI Novel Platform Backend
After=network.target postgresql.service

[Service]
Type=simple
User=ainovel
WorkingDirectory=/opt/ainovel/backend
Environment="PATH=/opt/ainovel/backend/.venv/bin"
ExecStart=/opt/ainovel/backend/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl daemon-reload
sudo systemctl enable ainovel
sudo systemctl start ainovel
sudo systemctl status ainovel
```

#### 4. 配置 Nginx

创建 `/etc/nginx/sites-available/ainovel`:

```nginx
upstream backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    # 前端
    location / {
        root /opt/ainovel/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # API
    location /api {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # API 文档
    location /docs {
        proxy_pass http://backend;
        proxy_set_header Host $host;
    }

    # 健康检查
    location /health {
        proxy_pass http://backend;
    }
}
```

启用站点：
```bash
sudo ln -s /etc/nginx/sites-available/ainovel /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 5. SSL 证书（Let's Encrypt）

```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx -y

# 获取证书
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

#### 6. 构建前端

```bash
cd /opt/ainovel/frontend
sudo -u ainovel npm install
sudo -u ainovel npm run build
```

## 监控和维护

### 1. 日志管理

```bash
# 查看应用日志
sudo journalctl -u ainovel -f

# 查看 Nginx 日志
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 2. 数据库备份

```bash
# 备份脚本
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/postgres"
mkdir -p $BACKUP_DIR

pg_dump ai_novel > $BACKUP_DIR/ai_novel_$DATE.sql
gzip $BACKUP_DIR/ai_novel_$DATE.sql

# 保留最近 7 天的备份
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete
```

设置 cron 任务：
```bash
# 每天凌晨 2 点备份
0 2 * * * /path/to/backup.sh
```

### 3. 性能监控

安装监控工具：
```bash
# htop - 系统监控
sudo apt install htop

# pg_stat_statements - PostgreSQL 查询监控
# 在 postgresql.conf 中启用
shared_preload_libraries = 'pg_stat_statements'
```

### 4. 更新部署

```bash
cd /opt/ainovel

# 拉取最新代码
sudo -u ainovel git pull

# 更新后端
cd backend
sudo -u ainovel .venv/bin/pip install -r requirements.txt
sudo -u ainovel .venv/bin/alembic upgrade head
sudo systemctl restart ainovel

# 更新前端
cd ../frontend
sudo -u ainovel npm install
sudo -u ainovel npm run build
```

## 故障排查

### 后端无法启动
```bash
# 检查日志
sudo journalctl -u ainovel -n 50

# 检查端口
sudo netstat -tlnp | grep 8000

# 检查数据库连接
sudo -u ainovel psql -d ai_novel
```

### 前端无法访问
```bash
# 检查 Nginx 配置
sudo nginx -t

# 检查 Nginx 日志
sudo tail -f /var/log/nginx/error.log

# 检查文件权限
ls -la /opt/ainovel/frontend/dist
```

### 数据库问题
```bash
# 检查 PostgreSQL 状态
sudo systemctl status postgresql

# 查看连接
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity;"

# 检查慢查询
sudo -u postgres psql -d ai_novel -c "SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"
```

## 安全最佳实践

- [ ] 使用环境变量管理敏感信息
- [ ] 启用 HTTPS
- [ ] 配置防火墙（UFW）
- [ ] 定期更新系统和依赖
- [ ] 实施速率限制
- [ ] 配置日志轮转
- [ ] 实施数据库备份
- [ ] 使用强密码策略
- [ ] 限制 SSH 访问
- [ ] 监控异常活动

## 性能优化

- [ ] 启用 Gzip 压缩
- [ ] 配置浏览器缓存
- [ ] 使用 CDN
- [ ] 优化数据库索引
- [ ] 配置 Redis 缓存
- [ ] 使用连接池
- [ ] 实施负载均衡
- [ ] 监控资源使用

## 成本估算

### 小型部署（< 1000 用户）
- VPS: $10-20/月
- 数据库: $10-15/月
- 总计: $20-35/月

### 中型部署（1000-10000 用户）
- 计算: $50-100/月
- 数据库: $30-50/月
- 缓存: $20-30/月
- CDN: $10-20/月
- 总计: $110-200/月

### 大型部署（> 10000 用户）
- 需要定制方案
- 考虑负载均衡、多区域部署
- 预算: $500+/月
