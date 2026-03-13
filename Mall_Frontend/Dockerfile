# 构建阶段：使用 Node 镜像打包 Vue 项目
FROM node:20-alpine AS build-stage
ENV NODE_ENV=development

# 设置工作目录
WORKDIR /app

# 复制 package.json 和 package-lock.json
COPY package*.json ./

# 安装依赖
RUN npm install --registry=https://registry.npm.taobao.org

# 复制源代码
COPY . .

# 修改 API 基础 URL 为相对路径（适配 Docker 部署）
RUN sed -i "s|baseURL: 'http://127.0.0.1:8000/api'|baseURL: '/api'|" src/utils/request.ts

# 构建生产版本
RUN npm run build

# 生产阶段：使用 Nginx 镜像
FROM nginx:alpine AS production-stage
ENV NODE_ENV=production

# 复制构建产物到 Nginx 的静态文件目录
COPY --from=build-stage /app/dist /usr/share/nginx/html

# 复制自定义 Nginx 配置（如果有）
# 注意：在 docker-compose.yml 中通过 volumes 挂载配置，这里不需要复制
# COPY nginx.conf /etc/nginx/nginx.conf

# 暴露 80 端口
EXPOSE 80

# 启动 Nginx
CMD ["nginx", "-g", "daemon off;"]