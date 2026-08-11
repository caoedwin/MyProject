# ============================================================
# MySQL 8.4 Docker 容器 - 启动与使用说明
# ============================================================

## 一、启动 Docker Desktop
先确保 Docker Desktop 已启动（任务栏图标为运行状态）。

## 二、启动 MySQL 8.4 容器

```powershell
cd C:\djangoproject\MyProject
docker compose up -d
```

首次启动会自动拉取 mysql:8.4 镜像（约 600MB），需要等待 1-2 分钟。

## 三、验证容器状态

```powershell
# 查看容器运行状态
docker ps

# 查看启动日志
docker logs myproject_mysql84

# 连接到容器内的 MySQL 验证版本
docker exec -it myproject_mysql84 mysql -uedwin -pDCT@2019 -e "SELECT VERSION();"
```

应输出类似：`8.4.x`。

## 四、连接信息（供 Django 配置使用）

| 项目        | 值             |
|------------|----------------|
| Host       | 127.0.0.1      |
| Port       | 3307           |
| Database   | myproject      |
| User       | edwin          |
| Password   | DCT@2019       |
| Root密码    | DCT@2019       |

## 五、Django settings.py 已自动配置为连接此容器

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'myproject',
        'USER': 'edwin',
        'PASSWORD': 'DCT@2019',
        'HOST': '127.0.0.1',
        'PORT': '3307',   # 注意：容器暴露的端口是 3307
    }
}
```

## 六、常用命令

```powershell
# 停止容器（数据保留）
docker compose stop

# 启动已停止的容器
docker compose start

# 重启容器
docker compose restart

# 查看实时日志
docker logs -f myproject_mysql84

# 进入 MySQL 命令行
docker exec -it myproject_mysql84 mysql -uedwin -pDCT@2019 myproject

# 备份数据库
docker exec myproject_mysql84 mysqldump -uedwin -pDCT@2019 myproject > backup.sql

# 恢复数据库
docker exec -i myproject_mysql84 mysql -uedwin -pDCT@2019 myproject < backup.sql

# 完全删除容器（保留数据卷）
docker compose down

# 完全删除容器 + 数据（⚠️慎用，会丢失所有数据）
docker compose down -v
```

## 七、数据存储位置

数据持久化在 Docker 命名卷 `myproject_mysql84_data` 中。
查看卷位置：
```powershell
docker volume inspect myproject_mysql84_data
```

## 八、与旧 MySQL 8.0 的隔离

- **端口隔离**：新容器用 3307，旧 MySQL 用 3306，互不冲突
- **服务隔离**：容器独立运行，与本机 MySQL 服务无关
- **数据隔离**：容器有自己的数据卷，不访问本机 MySQL 数据目录
- **配置隔离**：容器内 MySQL 配置完全独立

你的旧项目（Django 2.1.7 + MySQL 8.0）完全不受影响。

## 九、停止/启动容器不影响旧项目

停止 Docker 容器后，旧 MySQL 8.0 服务照常运行。
