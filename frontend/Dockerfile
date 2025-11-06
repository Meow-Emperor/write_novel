# Node.js 20 基础镜像
FROM node:20-alpine

# 设置工作目录
WORKDIR /app

# 复制 package 文件
COPY package*.json ./

# 安装依赖
RUN npm install

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 5173

# 健康检查（优先使用 IPv4 避免 ::1 回环导致的连接失败）
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://127.0.0.1:5173 || exit 1

# 启动命令（在 docker-compose.yml 中覆盖）
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
