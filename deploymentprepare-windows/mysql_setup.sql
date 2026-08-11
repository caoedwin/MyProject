-- ============================================================
-- MyProject 数据库初始化脚本 (Windows)
-- 适用于: Docker MySQL 或 Windows 原生 MySQL
-- ============================================================

-- 创建数据库
CREATE DATABASE IF NOT EXISTS myproject
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

-- 创建应用用户
CREATE USER IF NOT EXISTS 'edwin'@'%' IDENTIFIED BY 'DCT@2019';
CREATE USER IF NOT EXISTS 'edwin'@'127.0.0.1' IDENTIFIED BY 'DCT@2019';
CREATE USER IF NOT EXISTS 'edwin'@'localhost' IDENTIFIED BY 'DCT@2019';

-- 授权
GRANT ALL PRIVILEGES ON myproject.* TO 'edwin'@'%';
GRANT ALL PRIVILEGES ON myproject.* TO 'edwin'@'127.0.0.1';
GRANT ALL PRIVILEGES ON myproject.* TO 'edwin'@'localhost';
FLUSH PRIVILEGES;

-- 说明:
-- 1. 'edwin'@'%' 允许从任意主机连接（Docker 场景需要）
-- 2. 生产环境建议改为具体 IP 或仅限 localhost
-- 3. 密码 DCT@2019 请改为强密码
