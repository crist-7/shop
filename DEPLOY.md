# Docker 部署指南

## 项目概述
这是一个 Django + Vue3 前后端分离项目，使用 Docker Compose 进行容器化部署。

## 包含的服务
1. **前端** (Vue3): 端口 80
2. **后端** (Django + Gunicorn): 端口 8000
3. **数据库** (MySQL 8): 端口 3306
4. **缓存** (Redis): 端口 6379

## 快速开始

### 前提条件
1. 安装 Docker Desktop（Windows/Mac）或 Docker Engine（Linux）
2. 安装 Docker Compose（通常包含在 Docker Desktop 中）

### 部署步骤

#### 第1步：打开终端（命令行）
在项目根目录（有 docker-compose.yml 文件的目录）打开终端。

#### 第2步：启动所有服务
运行以下命令：

```bash
docker-compose up -d
```

这将会：
- 下载所有需要的镜像（MySQL, Redis, Nginx, Python, Node.js）
- 构建前端和后端的 Docker 镜像
- 启动所有容器在后台运行

#### 第3步：查看服务状态
运行以下命令查看容器是否正常运行：

```bash
docker-compose ps
```

你应该看到4个服务都是 "Up" 状态。

#### 第4步：访问应用
1. **前端页面**: 打开浏览器访问 http://localhost
2. **后端API**: 访问 http://localhost:8000/api/
3. **管理后台**（如果有）: 访问 http://localhost:8000/admin/

#### 第5步：查看日志
如果遇到问题，查看日志：

```bash
# 查看所有服务的日志
docker-compose logs

# 查看特定服务的日志
docker-compose logs backend
docker-compose logs frontend
docker-compose logs db
```

### 常用命令

```bash
# 停止所有服务
docker-compose down

# 停止并删除所有数据（数据库数据也会被删除）
docker-compose down -v

# 重新构建镜像并启动（修改代码后需要）
docker-compose up -d --build

# 进入后端容器执行命令（如创建超级用户）
docker-compose exec backend python manage.py createsuperuser

# 查看容器资源使用情况
docker-compose stats
```

## 配置文件说明

### 1. Docker 配置文件
- `Mall_Frontend/Dockerfile` - 前端构建配置
- `Dockerfile.backend` - 后端构建配置
- `docker-compose.yml` - 服务编排配置

### 2. Nginx 配置
- `docker/nginx/nginx.conf` - Nginx 反向代理配置
  - `/` → 前端页面
  - `/api/` → 后端 API
  - `/media/` → 媒体文件

### 3. 数据库初始化
- `docker/mysql/init.sql` - MySQL 初始化脚本

### 4. 启动脚本
- `docker/scripts/start.sh` - 后端启动脚本，自动配置数据库连接

## 注意事项

1. **首次启动**：第一次启动时会自动创建数据库表（执行 migrate）
2. **数据库数据持久化**：数据库数据保存在 Docker volume 中，删除容器不会丢失数据
3. **媒体文件**：上传的文件保存在 `./media` 目录中
4. **端口冲突**：如果本地已有服务占用 80、8000、3306、6379 端口，请修改 `docker-compose.yml` 中的端口映射
5. **生产环境**：本配置适用于开发和毕业设计演示，生产环境需要：
   - 修改 Django SECRET_KEY
   - 设置正确的 ALLOWED_HOSTS
   - 配置 HTTPS
   - 使用更安全的数据库密码

## 故障排除

### 1. 前端访问不到后端 API
检查 Nginx 配置是否正确代理到后端容器，查看日志：
```bash
docker-compose logs frontend
```

### 2. 数据库连接失败
确保数据库容器已启动：
```bash
docker-compose logs db
```

### 3. 构建失败
清除缓存重新构建：
```bash
docker-compose build --no-cache
```

## 联系方式
如有问题，请参考 Docker 和 Docker Compose 官方文档，或联系项目负责人。