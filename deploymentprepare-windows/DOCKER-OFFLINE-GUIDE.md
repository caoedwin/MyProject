# Docker 离线部署完整指南

> **场景**：目标 Windows 服务器无外网，且已安装其他版本 MySQL/Redis（端口冲突需用 Docker 隔离）

---

## 一、在有网机器上准备（开发机）

### 1.1 安装 Docker Desktop（如有网机器没装）

从 https://www.docker.com/products/docker-desktop 下载安装。

### 1.2 拉取所需镜像

打开 PowerShell 执行：

```powershell
# 拉取 MySQL 8.4
docker pull mysql:8.4

# 拉取 Redis 7（必须 6.0+，WebSocket 需要 HELLO 命令）
docker pull redis:7-alpine

# 验证
docker images
# 应看到：
# REPOSITORY   TAG          IMAGE ID       CREATED        SIZE
# mysql        8.4          xxxxxxxxxxxx   xx ago         xxxMB
# redis        7-alpine     xxxxxxxxxxxx   xx ago         xxxMB
```

### 1.3 导出镜像为 tar 文件

```powershell
# 创建导出目录
mkdir C:\docker-images -Force

# 导出镜像（注意：文件较大，MySQL 约 600MB，Redis 约 40MB）
docker save -o C:\docker-images\mysql-8.4.tar mysql:8.4
docker save -o C:\docker-images\redis-7.tar redis:7-alpine

# 验证文件
dir C:\docker-images\*.tar
```

### 1.4 下载 Docker Desktop 离线安装包

从 https://www.docker.com/products/docker-desktop 下载 Windows 版安装包：
- 文件名类似：`Docker Desktop Installer.exe`
- 大小约 500MB-1GB

**注意**：Docker Desktop 依赖 WSL2 或 Hyper-V，服务器需要支持虚拟化。

---

## 二、在无网服务器上安装 Docker

### 2.1 前置条件检查

#### 2.1.1 检查虚拟化支持

```powershell
# 检查 CPU 虚拟化是否启用
Get-ComputerInfo -Property "HyperV*"

# 或检查系统信息
systeminfo | findstr /i "Hyper-V"
```

输出应显示：
- `Hyper-V Requirements: A hypervisor has been detected...`（已启用）
- 或 `VM Monitor Mode Extensions: Yes`

#### 2.1.2 启用 WSL2（推荐）

```powershell
# 检查 WSL 是否已安装
wsl --status

# 如未安装，启用 WSL 功能（需要重启）
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

# 重启电脑
shutdown /r /t 0
```

重启后，如有 WSL2 内核更新包（`wsl_update_x64.msi`），双击安装。

#### 2.1.3 启用 Hyper-V（备选，如 WSL2 不可用）

```powershell
# 以管理员身份运行
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All
# 重启电脑
shutdown /r /t 0
```

### 2.2 安装 Docker Desktop

1. 双击 `Docker Desktop Installer.exe`
2. 安装选项：
   - ✅ Use WSL 2 instead of Hyper-V（推荐）
   - ❌ 不勾选 "Add shortcut to desktop"（可选）
3. 等待安装完成
4. 重启电脑（如提示）

### 2.3 配置 Docker（无网环境关键设置）

#### 2.3.1 启动 Docker Desktop

1. 启动 Docker Desktop
2. 等待右下角 Docker 图标变为绿色（稳定运行）

#### 2.3.2 配置国内镜像源（可选，无网环境跳过）

如服务器完全无网，跳过此步。无网环境下 Docker 无法拉取镜像，只能通过 `docker load` 导入。

#### 2.3.3 配置数据存储位置（可选，C 盘空间紧张时）

默认 Docker 数据存在 `C:\Users\<用户>\AppData\Local\Docker\wsl\`，如需迁移：

```powershell
# 1. 停止 Docker
Stop-Service com.docker.service

# 2. 导出 docker-desktop-data 到其他盘
wsl --export docker-desktop-data D:\docker-data\docker-desktop-data.tar

# 3. 注销原有数据
wsl --unregister docker-desktop-data

# 4. 重新导入到新位置
wsl --import docker-desktop-data D:\docker-data\ D:\docker-data\docker-desktop-data.tar

# 5. 启动 Docker
Start-Service com.docker.service
```

### 2.4 验证 Docker 安装

```powershell
docker version
docker info
```

应看到 Client 和 Server 信息，无报错。

---

## 三、导入 Docker 镜像（无网环境关键步骤）

### 3.1 传输镜像文件

将开发机上的 `C:\docker-images\mysql-8.4.tar` 和 `redis-7.tar` 拷贝到服务器，例如：
- `D:\docker-images\mysql-8.4.tar`
- `D:\docker-images\redis-7.tar`

### 3.2 导入镜像

```powershell
# 导入 MySQL 8.4
docker load -i D:\docker-images\mysql-8.4.tar

# 导入 Redis 7
docker load -i D:\docker-images\redis-7.tar
```

导入过程会显示每层解压进度，耗时约 1-3 分钟。

### 3.3 验证镜像

```powershell
docker images
```

应看到：
```
REPOSITORY   TAG         IMAGE ID       CREATED        SIZE
mysql        8.4         xxxxxxxxxxxx   xx ago         xxxMB
redis        7-alpine    xxxxxxxxxxxx   xx ago         xxxMB
```

---

## 四、启动 MySQL + Redis 容器

### 4.1 使用 docker-compose 启动（推荐）

#### 4.1.1 准备 compose 文件

将项目中的 [docker-compose.prod.yml](file:///c:/djangoproject/MyProject/deploymentprepare-windows/docker-compose.prod.yml) 拷贝到服务器，例如 `D:\myproject-docker\docker-compose.yml`。

#### 4.1.2 关键配置说明

```yaml
services:
  mysql84:
    image: mysql:8.4              # 使用已导入的镜像
    container_name: myproject_mysql84
    restart: unless-stopped       # 开机自启
    ports:
      - "3307:3306"               # 宿主机 3307 -> 容器 3306
                                    # 避免与服务器已有的 MySQL 3306 冲突
    environment:
      MYSQL_ROOT_PASSWORD: "DCT@2019"   # root 密码，建议修改
      MYSQL_DATABASE: "myproject"       # 自动创建数据库
      MYSQL_USER: "edwin"               # 应用用户
      MYSQL_PASSWORD: "DCT@2019"        # 应用密码，建议修改
      TZ: "Asia/Shanghai"
    command:
      --character-set-server=utf8mb4
      --collation-server=utf8mb4_unicode_ci
      --mysql-native-password=ON
      --max_connections=200
      --innodb_buffer_pool_size=512M
    volumes:
      - mysql84_data:/var/lib/mysql    # 数据持久化
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost", "-uroot", "-pDCT@2019"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: myproject_redis
    restart: unless-stopped
    ports:
      - "6379:6379"               # 如服务器已有 Redis 6379，改为 "6380:6379"
    command: redis-server --requirepass DCT@2019 --appendonly yes
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "-a", "DCT@2019", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  mysql84_data:
    name: myproject_mysql84_data
  redis_data:
    name: myproject_redis_data
```

#### 4.1.3 端口冲突处理

**如服务器已有 MySQL 占用 3306**：
- compose 中已用 3307，不冲突 ✅

**如服务器已有 Redis 占用 6379**：
```yaml
redis:
  ports:
    - "6380:6379"    # 改为 6380
```
同时修改 `config\settings.py`：
```python
REDIS_PORT = 6380
```

#### 4.1.4 启动容器

```powershell
cd D:\myproject-docker
docker compose up -d
```

#### 4.1.5 验证容器状态

```powershell
# 查看运行中的容器
docker ps

# 应看到：
# CONTAINER ID   IMAGE          STATUS         PORTS                    NAMES
# xxxxxxxxxxxx   mysql:8.4      Up 30 seconds  0.0.0.0:3307->3306/tcp   myproject_mysql84
# xxxxxxxxxxxx   redis:7-alpine Up 30 seconds  0.0.0.0:6379->6379/tcp   myproject_redis

# 查看日志（排错用）
docker logs myproject_mysql84
docker logs myproject_redis

# 测试 MySQL 连接
docker exec myproject_mysql84 mysql -uroot -pDCT@2019 -e "SHOW DATABASES;"

# 测试 Redis 连接
docker exec myproject_redis redis-cli -a DCT2019 ping
# 应返回: PONG
```

### 4.2 手动启动（备选，不用 compose）

```powershell
# 启动 MySQL
docker run -d ^
  --name myproject_mysql84 ^
  --restart unless-stopped ^
  -p 3307:3306 ^
  -e MYSQL_ROOT_PASSWORD=DCT@2019 ^
  -e MYSQL_DATABASE=myproject ^
  -e MYSQL_USER=edwin ^
  -e MYSQL_PASSWORD=DCT@2019 ^
  -e TZ=Asia/Shanghai ^
  -v myproject_mysql84_data:/var/lib/mysql ^
  mysql:8.4 ^
  --character-set-server=utf8mb4 ^
  --collation-server=utf8mb4_unicode_ci ^
  --mysql-native-password=ON

# 启动 Redis
docker run -d ^
  --name myproject_redis ^
  --restart unless-stopped ^
  -p 6379:6379 ^
  -v myproject_redis_data:/data ^
  redis:7-alpine ^
  redis-server --requirepass DCT2019 --appendonly yes
```

---

## 五、配置 Docker 开机自启

### 5.1 Docker Desktop 设置

1. 右键 Docker Desktop 托盘图标
2. Settings → General
3. ✅ 勾选 "Start Docker Desktop when you log in"
4. ✅ 勾选 "Use the WSL 2 based engine"
5. Apply & Restart

### 5.2 容器自启

docker-compose.prod.yml 中已配置 `restart: unless-stopped`，Docker 启动后容器会自动启动。

手动管理：
```powershell
# 停止所有容器
docker compose down

# 启动所有容器
docker compose up -d

# 重启某个容器
docker restart myproject_mysql84
docker restart myproject_redis
```

---

## 六、数据持久化与备份

### 6.1 数据存储位置

Docker 数据卷默认存储在 WSL2 虚拟磁盘中：
- 路径：`\\wsl$\docker-desktop-data\version-pack-data\community\docker\volumes\`

如需查看：
```powershell
docker volume inspect myproject_mysql84_data
```

### 6.2 备份数据库

使用项目提供的脚本：
```powershell
cd C:\app\MyProject\deploymentprepare-windows
.\08-backup-database.bat
```

或手动执行：
```powershell
docker exec myproject_mysql84 mysqldump -uroot -pDCT@2019 ^
  --databases myproject ^
  --single-transaction ^
  --routines ^
  --triggers ^
  --events > D:\backups\myproject_%date:~0,4%%date:~5,2%%date:~8,2%.sql
```

### 6.3 备份 Docker 数据卷（整机迁移用）

```powershell
# 备份 MySQL 数据卷
docker run --rm -v myproject_mysql84_data:/data -v D:\backups:/backup ^
  alpine tar czf /backup/mysql_data.tar.gz -C /data .

# 恢复 MySQL 数据卷
docker run --rm -v myproject_mysql84_data:/data -v D:\backups:/backup ^
  alpine tar xzf /backup/mysql_data.tar.gz -C /data
```

---

## 七、常见问题

### Q1：Docker Desktop 无法启动

**症状**：Docker Desktop 一直转圈，或报 WSL2 错误

**解决**：
1. 检查 WSL2 是否正确安装：
   ```powershell
   wsl --list --verbose
   # 应看到 docker-desktop 和 docker-desktop-data
   ```
2. 如未安装，下载 WSL2 内核更新：
   - https://wslstorestorage.blob.core.windows.net/wslblob/wsl_update_x64.msi
   - 双击安装后重启
3. 设置 WSL2 为默认：
   ```powershell
   wsl --set-default-version 2
   ```

### Q2：docker compose 命令不存在

**Docker Desktop 较新版本已内置 compose**，如提示命令不存在：

```powershell
# 方式1：使用新版语法
docker compose up -d        # 注意无连字符

# 方式2：如需旧版 docker-compose
# 在有网机器下载：https://github.com/docker/compose/releases
# 下载 docker-compose-Windows-x86_64.exe
# 重命名为 docker-compose.exe 放到 C:\Windows\
```

### Q3：容器启动后立即退出

**查看日志**：
```powershell
docker logs myproject_mysql84
docker logs myproject_redis
```

**常见原因**：
- 端口冲突：检查 `netstat -ano | findstr :3307`
- 数据卷损坏：`docker volume rm myproject_mysql84_data` 后重建
- 内存不足：Docker Desktop 默认 2GB，改为 4GB+（Settings → Resources）

### Q4：MySQL 连接被拒绝

**检查清单**：
1. 容器是否运行：`docker ps | findstr mysql`
2. 端口是否映射：`docker port myproject_mysql84`
3. 防火墙是否放行：`netsh advfirewall firewall add rule name="MySQL" dir=in action=allow protocol=TCP localport=3307`
4. 用户权限：`docker exec myproject_mysql84 mysql -uroot -pDCT@2019 -e "SELECT user,host FROM mysql.user;"`

### Q5：Redis 版本不兼容 WebSocket

**现象**：WebSocket 连接报 "unknown command 'HELLO'"

**原因**：Redis 版本 < 6.0

**解决**：
1. 检查版本：`docker exec myproject_redis redis-cli INFO server | findstr redis_version`
2. 必须使用 redis:7-alpine（已在 compose 中配置）
3. 如使用旧版 Redis，修改 `config\settings.py` 的 `CHANNEL_LAYERS`：
   ```python
   CHANNEL_LAYERS = {
       'default': {
           'BACKEND': 'channels_redis.core.RedisChannelLayer',
           'CONFIG': {
               'hosts': [(REDIS_HOST, REDIS_PORT)],
               'password': REDIS_PASSWORD,
               'protocol': 2,  # 强制使用 RESP2 协议
           },
       },
   }
   ```

### Q6：如何完全卸载 Docker 中的 MySQL/Redis

```powershell
# 停止并删除容器
docker compose down

# 删除数据卷（谨慎！会删除所有数据）
docker volume rm myproject_mysql84_data
docker volume rm myproject_redis_data

# 删除镜像（如需释放空间）
docker rmi mysql:8.4
docker rmi redis:7-alpine
```

---

## 八、完整部署流程速查

```powershell
# ===== 在有网开发机执行 =====
docker pull mysql:8.4
docker pull redis:7-alpine
docker save -o C:\docker-images\mysql-8.4.tar mysql:8.4
docker save -o C:\docker-images\redis-7.tar redis:7-alpine
# 拷贝 mysql-8.4.tar、redis-7.tar、Docker Desktop Installer.exe 到服务器

# ===== 在无网服务器执行 =====
# 1. 安装 Docker Desktop（双击安装包）
# 2. 导入镜像
docker load -i D:\docker-images\mysql-8.4.tar
docker load -i D:\docker-images\redis-7.tar

# 3. 启动容器
cd C:\app\MyProject\deploymentprepare-windows
docker compose -f docker-compose.prod.yml up -d

# 4. 验证
docker ps
docker exec myproject_mysql84 mysql -uroot -pDCT@2019 -e "SHOW DATABASES;"
docker exec myproject_redis redis-cli -a DCT2019 ping

# 5. 继续执行项目部署
.\04-init-mysql.bat
.\05-migrate.bat
.\10-install-nssm-services.bat
```
