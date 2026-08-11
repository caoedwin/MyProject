-- ============================================================
-- MyProject 数据库初始化脚本
-- 在 MySQL 服务器上执行: mysql -u root -p < mysql_setup.sql
-- ============================================================

-- 创建数据库
CREATE DATABASE IF NOT EXISTS myproject
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

-- 创建应用用户 (替换密码为生产环境强密码)
CREATE USER IF NOT EXISTS 'myproject_user'@'127.0.0.1' IDENTIFIED BY 'CHANGE_ME_STRONG_PASSWORD';
CREATE USER IF NOT EXISTS 'myproject_user'@'localhost' IDENTIFIED BY 'CHANGE_ME_STRONG_PASSWORD';

-- 授权
GRANT ALL PRIVILEGES ON myproject.* TO 'myproject_user'@'127.0.0.1';
GRANT ALL PRIVILEGES ON myproject.* TO 'myproject_user'@'localhost';
FLUSH PRIVILEGES;

-- 切换数据库
USE myproject;

-- 权限说明:
-- myproject_user 用于 Django 应用连接, 仅需 DML 权限
-- 如果需要读写分离, 可以创建只读账号:
-- CREATE USER 'myproject_readonly'@'127.0.0.1' IDENTIFIED BY 'readonly_password';
-- GRANT SELECT ON myproject.* TO 'myproject_readonly'@'127.0.0.1';
