# 本地开发环境配置指南

## 问题诊断

您遇到的错误 `Unknown server host 'db' (11001)` 是因为 Django 设置中数据库主机配置为 `'db'`（Docker 服务名），但在本地运行 `python manage.py runserver` 时，系统无法解析该主机名。

## 解决方案

已更新 `Mall_Backend/settings.py`，现在支持通过环境变量配置数据库和 Redis 连接。默认值已设为本地开发环境（localhost）。

### 方法一：使用 Docker 运行所有服务（推荐）

```bash
# 使用开发配置启动所有服务
docker-compose -f docker-compose.dev.yml up
```

这将启动：
- MySQL 数据库 (localhost:3307)
- Redis (localhost:6379)
- Django 后端 (localhost:8000，支持热更新)
- Vue 前端 (localhost:5173，支持热更新)

### 方法二：本地运行 Django，使用 Docker 运行数据库和 Redis

1. **启动数据库和 Redis**：
   ```bash
   docker-compose -f docker-compose.dev.yml up db redis
   ```

2. **设置环境变量**（Windows PowerShell）：
   ```powershell
   $env:DATABASE_HOST="localhost"
   $env:DATABASE_PORT="3307"
   $env:REDIS_HOST="localhost"
   $env:DEBUG="True"
   ```

3. **安装 Python 依赖**：
   ```bash
   pip install -r requirements.txt
   ```

4. **运行 Django**：
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

### 方法三：完全本地运行（需要安装 MySQL 和 Redis）

1. **安装并启动 MySQL**：
   - 下载安装 MySQL 8.0
   - 创建数据库：`CREATE DATABASE shop_db;`
   - 创建用户：`CREATE USER 'root'@'localhost' IDENTIFIED BY 'root';`
   - 授权：`GRANT ALL PRIVILEGES ON shop_db.* TO 'root'@'localhost';`

2. **安装并启动 Redis**：
   - 下载安装 Redis for Windows
   - 或使用 WSL 中的 Redis

3. **设置环境变量**（可选，使用默认值）：
   - 默认数据库：`localhost:3306`, 用户/密码：`root/root`
   - 默认 Redis：`localhost:6379`
   - 默认 DEBUG：`True`

4. **运行 Django**：
   ```bash
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py runserver
   ```

## 环境变量参考

| 变量名 | 默认值 | 描述 |
|--------|--------|------|
| DEBUG | True | 调试模式 |
| DATABASE_HOST | 127.0.0.1 | 数据库主机 |
| DATABASE_PORT | 3306 | 数据库端口 |
| DATABASE_NAME | shop_db | 数据库名 |
| DATABASE_USER | root | 数据库用户 |
| DATABASE_PASSWORD | root | 数据库密码 |
| REDIS_HOST | 127.0.0.1 | Redis 主机 |
| REDIS_PORT | 6379 | Redis 端口 |

## 验证配置

运行以下命令测试配置是否正确：

```bash
# 检查 Django 配置
python manage.py check

# 测试数据库连接（确保数据库服务已启动）
python manage.py dbshell
```

## 常见问题

### 1. MySQL 连接失败
- 检查 MySQL 服务是否运行
- 确认数据库 `shop_db` 是否存在
- 检查用户名/密码是否正确

### 2. Redis 连接失败
- 检查 Redis 服务是否运行
- 如果是 Docker Redis，确保端口映射正确

### 3. 跨域问题（CORS）
- 前端运行在 `http://localhost:5173`
- 后端已配置允许该来源
- 如果使用其他端口，请添加到 `CORS_ALLOWED_ORIGINS`

### 4. 媒体文件无法访问
- 开发服务器自动服务媒体文件
- 确保 `media` 目录存在且可写

## 生产部署提醒

生产环境请务必：
1. 设置 `DEBUG=False`
2. 使用强密码替换默认数据库密码
3. 配置正确的 `ALLOWED_HOSTS`
4. 使用 `python manage.py collectstatic` 收集静态文件