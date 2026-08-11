-- MySQL 8.4 容器初始化脚本
-- 仅在容器首次启动时执行（数据目录为空时）
-- 环境变量 MYSQL_DATABASE/MYSQL_USER/MYSQL_PASSWORD 已自动创建库和用户
-- 这里仅做权限补充和验证

-- 确保字符集
ALTER DATABASE myproject CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 授予 edwin 用户远程访问权限（容器内 % 通配）
GRANT ALL PRIVILEGES ON myproject.* TO 'edwin'@'%';
FLUSH PRIVILEGES;

-- 验证版本（输出到日志）
SELECT VERSION();
