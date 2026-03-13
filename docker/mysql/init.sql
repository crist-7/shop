-- 创建应用数据库用户并授权
CREATE USER IF NOT EXISTS 'shop_user'@'%' IDENTIFIED BY 'shop_password';
GRANT ALL PRIVILEGES ON shop_db.* TO 'shop_user'@'%';
GRANT ALL PRIVILEGES ON *.* TO 'shop_user'@'%' WITH GRANT OPTION;
FLUSH PRIVILEGES;

-- 设置字符集
ALTER DATABASE shop_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;