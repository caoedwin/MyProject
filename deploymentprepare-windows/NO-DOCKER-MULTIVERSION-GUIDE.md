# 无 Docker 多版本共存离线部署指南

> **场景**：Windows 服务器无外网，且已安装其他版本的 MySQL、Redis、Python
> **目标**：在不影响现有服务的前提下，并孪安装第二套版本供 MyProject 使用
> **核心思路**：不同安装目录 + 不同端口 + 不同服务名

---

## 一、版本规划

### 1.1 现有服务 vs 新装服务

| 服务    | 现有版本（假设） | 现有端口 | 新装版本 | 新端口 | 新服务名             |
| ------- | ---------------- | -------- | -------- | ------ | -------------------- |
| MySQL   | 5.7 / 8.0        | 3306     | 8.4      | 3307   | MySQL84              |
| Redis   | 3.x / 5.x        | 6379     | 7.x      | 6380   | Redis7               |
| Python  | 3.8 / 3.9        | -        | 3.12     | -      | (独立目录 + venv)    |

### 1.2 安装目录规划

```
C:\Program Files\MySQL\MySQL Server 8.4\     # 新版 MySQL
C:\Redis7\                                    # 新版 Redis
C:\Python312\                                 # 新版 Python（全局）
C:\app\MyProject\Myprojectvenv\               # 项目虚拟环境（独立隔离）
```

> **关键**：MySQL、Redis 必须装到**不同目录**，端口、服务名**不能与现有冲突**。

---

## 二、在有网机器上准备安装包

### 2.1 下载 MySQL 8.4 离线安装包

1. 访问 https://dev.mysql.com/downloads/mysql/
2. 选择 **MySQL Community Server 8.4.x**
3. 操作系统选 **Microsoft Windows**
4. 下载 **mysql-8.4.x-winx64.zip**（免安装版，推荐）
   - 或下载 **MSI Installer**（mysql-installer-community-8.4.x.msi）

### 2.2 下载 Redis 7 for Windows 离线包

Redis 官方不支持 Windows，需用社区移植版：

1. 访问 https://github.com/tporadowski/redis/releases
2. 下载 **Redis-x64-7.x.x.zip**（推荐 7.0+）
   - 或下载 **Redis-x64-7.x.x.msi**

> **版本要求**：**必须 6.0+**，否则 WebSocket 的 HELLO 命令会失败。
> 推荐 7.x 版本。

### 2.3 下载 Python 3.12 离线安装包

1. 访问 https://www.python.org/downloads/windows/
2. 下载 **Python 3.12.x - Windows installer (64-bit)**
   - 文件名：`python-3.12.x-amd64.exe`

### 2.4 下载 Python 依赖（离线 wheel 包）

在有网机器执行：

```powershell
# 假设已安装 Python 3.12
cd C:\djangoproject\MyProject\deploymentprepare-windows
.\02-download-pip-packages.bat
```

生成 `pip_packages\` 目录，包含所有 `.whl` 文件。

### 2.5 下载 Nginx for Windows

- http://nginx.org/en/download.html
- 下载 Stable version，如 `nginx-1.26.1.zip`

### 2.6 下载 NSSM（注册 Windows 服务）

- https://nssm.cc/release/nssm-2.24.zip
- 解压后取 `win64\nssm.exe`

### 2.7 打包清单

| 文件                                 | 用途                |
| ------------------------------------ | ------------------- |
| `mysql-8.4.x-winx64.zip`             | MySQL 8.4 免安装版  |
| `Redis-x64-7.x.x.zip`                | Redis 7             |
| `python-3.12.x-amd64.exe`            | Python 3.12         |
| `pip_packages\`                      | Python 离线依赖     |
| `nginx-1.26.x.zip`                   | Nginx               |
| `nssm.exe`                           | 服务注册工具        |
| `MyProject\`（整个项目）             | 项目代码            |

---

## 三、安装 Python 3.12（多版本共存）

### 3.1 安装 Python 3.12

1. 双击 `python-3.12.x-amd64.exe`
2. **关键选项**：
   - ❌ **不要勾选** "Add Python 3.12 to PATH"（避免影响现有 Python）
   - ✅ 勾选 "Install for all users"
   - 安装路径：**`C:\Python312\`**（不与现有 Python 冲突）
3. 完成安装

### 3.2 验证多版本共存

```powershell
# 现有 Python（通过 PATH）
python --version
# 例如输出: Python 3.9.x

# 新装 Python 3.12（用完整路径）
C:\Python312\python.exe --version
# 输出: Python 3.12.x
```

### 3.3 创建项目虚拟环境（隔离依赖）

```powershell
cd C:\app\MyProject

# 用 Python 3.12 创建虚拟环境（不影响系统 Python）
C:\Python312\python.exe -m venv Myprojectvenv

# 激活虚拟环境
Myprojectvenv\Scripts\activate

# 验证 Python 版本
python --version
# 输出: Python 3.12.x
```

### 3.4 离线安装 Python 依赖

```powershell
# 确保虚拟环境已激活
cd C:\app\MyProject\deploymentprepare-windows
pip install --no-index --find-links=pip_packages\ -r ..\requirements.txt
```

验证：
```powershell
pip list
# 应看到 Django、daphne、channels、channels-redis 等
```

---

## 四、安装 MySQL 8.4（多版本共存）

### 4.1 方式A：免安装版（推荐，可控性强）

#### 4.1.1 解压

```powershell
# 解压到独立目录（不与现有 MySQL 冲突）
Expand-Archive C:\downloads\mysql-8.4.x-winx64.zip -DestinationPath "C:\Program Files\MySQL\"
Rename-Item "C:\Program Files\MySQL\mysql-8.4.x-winx64" "MySQL Server 8.4"
```

最终路径：`C:\Program Files\MySQL\MySQL Server 8.4\`

#### 4.1.2 创建 my.ini 配置文件

在 `C:\Program Files\MySQL\MySQL Server 8.4\` 下新建 `my.ini`：

```ini
[mysqld]
# 基本配置
basedir=C:/Program Files/MySQL/MySQL Server 8.4
datadir=C:/Program Files/MySQL/MySQL Server 8.4/data
port=3307                              # 关键：用 3307，避开现有 3306
socket=C:/Program Files/MySQL/MySQL Server 8.4/mysql.sock
pid-file=C:/Program Files/MySQL/MySQL Server 8.4/mysql.pid

# 字符集
character-set-server=utf8mb4
collation-server=utf8mb4_unicode_ci

# 认证（兼容旧客户端）
mysql_native_password=ON

# 连接数
max_connections=200
innodb_buffer_pool_size=512M

# 日志
log-error=C:/Program Files/MySQL/MySQL Server 8.4/logs/error.log
slow_query_log=1
slow_query_log_file=C:/Program Files/MySQL/MySQL Server 8.4/logs/slow.log
long_query_time=2

# 时区
default-time-zone='+08:00'

[client]
port=3307
default-character-set=utf8mb4

[mysql]
default-character-set=utf8mb4
```

#### 4.1.3 创建日志目录

```powershell
mkdir "C:\Program Files\MySQL\MySQL Server 8.4\logs" -Force
mkdir "C:\Program Files\MySQL\MySQL Server 8.4\data" -Force
```

#### 4.1.4 初始化数据目录

```powershell
cd "C:\Program Files\MySQL\MySQL Server 8.4\bin"

# 初始化（注意临时密码输出，务必记录！）
.\mysqld --defaults-file="C:\Program Files\MySQL\MySQL Server 8.4\my.ini" --initialize --console
```

**重要**：控制台会输出临时 root 密码，类似：
```
A temporary password is generated for root@localhost: xxxxxxxxxxxx
```
**务必保存此密码**，首次登录需要。

#### 4.1.5 注册为 Windows 服务

```powershell
# 管理员权限运行
cd "C:\Program Files\MySQL\MySQL Server 8.4\bin"

# 安装服务，服务名 MySQL84（不与现有 MySQL 冲突）
.\mysqld --install MySQL84 --defaults-file="C:\Program Files\MySQL\MySQL Server 8.4\my.ini"

# 启动服务
net start MySQL84
```

#### 4.1.6 修改 root 密码 + 创建应用数据库

```powershell
# 用临时密码登录（端口 3307）
.\mysql -uroot -P 3307 -p
# 输入临时密码
```

执行 SQL：
```sql
-- 修改 root 密码
ALTER USER 'root'@'localhost' IDENTIFIED BY 'DCT@2019';

-- 创建数据库
CREATE DATABASE myproject CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建应用用户（允许从本机连接）
CREATE USER 'edwin'@'localhost' IDENTIFIED BY 'DCT@2019';
CREATE USER 'edwin'@'127.0.0.1' IDENTIFIED BY 'DCT@2019';
GRANT ALL PRIVILEGES ON myproject.* TO 'edwin'@'localhost';
GRANT ALL PRIVILEGES ON myproject.* TO 'edwin'@'127.0.0.1';
FLUSH PRIVILEGES;

EXIT;
```

#### 4.1.7 验证

```powershell
# 用新密码登录
"C:\Program Files\MySQL\MySQL Server 8.4\bin\mysql.exe" -uedwin -P 3307 -pDCT@2019 -e "SHOW DATABASES;"
# 应看到 myproject 数据库
```

### 4.2 方式B：MSI 安装版

1. 双击 `mysql-installer-community-8.4.x.msi`
2. 选择 "Custom" 安装类型
3. 选择 MySQL Server 8.4
4. **关键配置**：
   - 安装路径：`C:\Program Files\MySQL\MySQL Server 8.4\`
   - 数据路径：`C:\ProgramData\MySQL\MySQL Server 8.4\`
   - **Type and Networking**：
     - Config Type: Development Computer
     - **Port: 3307**（改为 3307）
     - **Windows Service Name: MySQL84**（改名）
   - Authentication: Use Strong Password Encryption
   - 设置 root 密码
5. 完成安装后，按 4.1.6 步骤创建数据库和用户

### 4.3 多版本 MySQL 共存验证

```powershell
# 查看所有 MySQL 服务
Get-Service | Where-Object {$_.Name -like "*MySQL*"}
# 应看到：
# MySQL   (现有，端口 3306)
# MySQL84 (新装，端口 3307)

# 分别连接测试
mysql -uroot -P 3306 -p       # 现有 MySQL
"C:\Program Files\MySQL\MySQL Server 8.4\bin\mysql.exe" -uroot -P 3307 -p  # 新装 MySQL
```

---

## 五、安装 Redis 7（多版本共存）

### 5.1 方式A：免安装版（推荐）

#### 5.1.1 解压

```powershell
# 解压到独立目录
Expand-Archive C:\Downloads\Redis-x64-7.x.x.zip -DestinationPath C:\Redis7
```

#### 5.1.2 修改配置文件

编辑 `C:\Redis7\redis.windows.conf`：

```conf
# 网络
port 6380                              # 关键：用 6380，避开现有 6379
bind 127.0.0.1
protected-mode yes

# 密码
requirepass DCT@2019

# 内存
maxmemory 256mb
maxmemory-policy allkeys-lru

# 持久化
appendonly yes
appendfilename "appendonly.aof"
appendfsync everysec

# 日志
logfile "C:/Redis7/redis.log"

# 数据目录
dir C:/Redis7/data/
```

创建数据目录：
```powershell
mkdir C:\Redis7\data -Force
```

#### 5.1.3 注册为 Windows 服务

```powershell
# 管理员权限运行
cd C:\Redis7

# 安装服务，服务名 Redis7（不与现有 Redis 冲突）
.\redis-server.exe --service-install redis.windows.conf --service-name Redis7

# 启动服务
net start Redis7
```

#### 5.1.4 验证

```powershell
# 连接测试（端口 6380）
.\redis-cli.exe -p 6380 -a DCT@2019 ping
# 应输出: PONG

# 查看版本
.\redis-cli.exe -p 6380 -a DCT@2019 INFO server | findstr redis_version
# 应输出: redis_version:7.x.x
```

### 5.2 方式B：MSI 安装版

1. 双击 `Redis-x64-7.x.x.msi`
2. **关键配置**：
   - 安装路径：`C:\Redis7\`
   - **Port: 6380**（改为 6380）
   - **Add to PATH: ❌ 不勾选**（避免与现有 redis-cli 冲突）
   - **Service Name: Redis7**（改名）
   - 设置密码：`DCT@2019`
3. 完成安装

### 5.3 多版本 Redis 共存验证

```powershell
# 查看所有 Redis 服务
Get-Service | Where-Object {$_.Name -like "*Redis*"}
# 应看到：
# Redis   (现有，端口 6379)
# Redis7  (新装，端口 6380)

# 分别连接测试
redis-cli -p 6379 ping                 # 现有 Redis
"C:\Redis7\redis-cli.exe" -p 6380 -a DCT@2019 ping  # 新装 Redis
```

---

## 六、配置项目连接新服务

### 6.1 修改 Django settings.py

编辑 `C:\app\MyProject\config\settings.py`，确保使用新端口：

```python
# MySQL 配置（端口 3307）
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'myproject',
        'USER': 'edwin',
        'PASSWORD': 'DCT@2019',
        'HOST': '127.0.0.1',
        'PORT': '3307',  # 新装 MySQL 端口
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    }
}

# Redis 配置（端口 6380）
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6380      # 新装 Redis 端口
REDIS_PASSWORD = 'DCT@2019'

# Channels（WebSocket）
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [f'redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/4'],
        },
    },
}

# Celery
CELERY_BROKER_URL = f'redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/1'
CELERY_RESULT_BACKEND = f'redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/2'
```

### 6.2 验证连接

```powershell
cd C:\app\MyProject
Myprojectvenv\Scripts\activate

# 测试 Django 能否连接 MySQL
python manage.py dbshell
# 能进入 mysql 提示符即成功，输入 exit 退出

# 测试 Redis 连接
python -c "import redis; r = redis.Redis(host='127.0.0.1', port=6380, password='DCT@2019'); print(r.ping())"
# 应输出: True
```

---

## 七、初始化数据库 + 启动服务

### 7.1 执行数据库迁移

```powershell
cd C:\app\MyProject
Myprojectvenv\Scripts\activate

python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

### 7.2 启动服务（命令行测试）

```powershell
# 启动 Django（端口 8000）
start "MyProject-Django" cmd /k "cd C:\app\MyProject && Myprojectvenv\Scripts\activate && python manage.py runserver 0.0.0.0:8000"

# 启动 Daphne（WebSocket，端口 8001）
start "MyProject-Daphne" cmd /k "cd C:\app\MyProject && Myprojectvenv\Scripts\activate && daphne -b 0.0.0.0 -p 8001 config.asgi:application"

# 启动 Celery
start "MyProject-Celery" cmd /k "cd C:\app\MyProject && Myprojectvenv\Scripts\activate && celery -A config worker -l info"
```

验证：
- 访问 http://localhost:8000/ → Django 首页
- 访问 http://localhost:8000/admin/ → Django Admin
- 浏览器控制台 WebSocket 应连接成功（无 1006 错误）

### 7.3 注册为 Windows 服务（生产推荐）

**前置**：将 `nssm.exe` 放到 `C:\app\MyProject\deploymentprepare-windows\`

以管理员身份运行：
```powershell
cd C:\app\MyProject\deploymentprepare-windows
.\10-install-nssm-services.bat
```

注册后：
```powershell
net start MyProject-Django
net start MyProject-Daphne
net start MyProject-Celery
```

### 7.4 配置 Nginx 反向代理（可选）

参考 [nginx.conf](file:///c:/djangoproject/MyProject/deploymentprepare-windows/nginx.conf)，修改路径为实际部署路径。

---

## 八、服务管理速查

### 8.1 多版本服务列表

| 服务名             | 类型    | 端口  | 启动方式                |
| ------------------ | ------- | ----- | ----------------------- |
| MySQL (现有)       | 自动    | 3306  | 系统服务，开机自启      |
| **MySQL84** (新装) | 自动    | 3307  | 系统服务，开机自启      |
| Redis (现有)       | 自动    | 6379  | 系统服务，开机自启      |
| **Redis7** (新装)  | 自动    | 6380  | 系统服务，开机自启      |
| **MyProject-Django** | 自动  | 8000  | NSSM 注册，开机自启     |
| **MyProject-Daphne** | 自动  | 8001  | NSSM 注册，开机自启     |
| **MyProject-Celery** | 自动  | -     | NSSM 注册，开机自启     |
| Nginx (可选)       | 自动    | 80    | NSSM 注册，开机自启     |

### 8.2 常用管理命令

```powershell
# 启动 MyProject 相关服务
net start MySQL84
net start Redis7
net start MyProject-Django
net start MyProject-Daphne
net start MyProject-Celery

# 停止 MyProject 相关服务
net stop MyProject-Celery
net stop MyProject-Daphne
net stop MyProject-Django
net stop Redis7
net stop MySQL84

# 查看服务状态
Get-Service MySQL84, Redis7, MyProject-Django, MyProject-Daphne, MyProject-Celery

# services.msc 图形化管理
services.msc
```

---

## 九、数据备份与恢复

### 9.1 备份（使用新装 MySQL 客户端）

```powershell
# 设置 PATH 临时指向新 MySQL
$env:PATH = "C:\Program Files\MySQL\MySQL Server 8.4\bin;" + $env:PATH

# 备份
mysqldump -h127.0.0.1 -P3307 -uroot -pDCT@2019 ^
  --databases myproject ^
  --single-transaction ^
  --routines ^
  --triggers ^
  --events > D:\backups\myproject_%date:~0,4%%date:~5,2%%date:~8,2%.sql
```

### 9.2 恢复

```powershell
$env:PATH = "C:\Program Files\MySQL\MySQL Server 8.4\bin;" + $env:PATH
mysql -h127.0.0.1 -P3307 -uroot -pDCT@2019 < D:\backups\myproject_20260811.sql
```

### 9.3 使用项目脚本

直接使用 [08-backup-database.bat](file:///c:/djangoproject/MyProject/deploymentprepare-windows/08-backup-database.bat) 和 [09-restore-database.bat](file:///c:/djangoproject/MyProject/deploymentprepare-windows/09-restore-database.bat)，脚本已内置端口 3307 配置。

---

## 十、常见问题

### Q1：MySQL 服务启动失败

**排查步骤**：

1. 查看错误日志：
   ```powershell
   type "C:\Program Files\MySQL\MySQL Server 8.4\logs\error.log"
   ```

2. 常见原因：
   - **端口 3307 被占用**：`netstat -ano | findstr :3307`
   - **data 目录权限不足**：右键 data 目录 → 属性 → 安全 → 添加 SYSTEM 完全控制
   - **my.ini 路径错误**：检查 basedir、datadir 路径
   - **数据目录未初始化**：执行 4.1.4 步骤

3. 手动启动查看报错：
   ```powershell
   cd "C:\Program Files\MySQL\MySQL Server 8.4\bin"
   .\mysqld --defaults-file="..\my.ini" --console
   ```

### Q2：Redis 服务启动失败

**排查步骤**：

1. 查看日志：
   ```powershell
   type C:\Redis7\redis.log
   ```

2. 常见原因：
   - **端口 6380 被占用**：`netstat -ano | findstr :6380`
   - **配置文件路径错误**：检查 conf 中所有路径
   - **data 目录不存在**：`mkdir C:\Redis7\data -Force`

3. 手动启动查看报错：
   ```powershell
   cd C:\Redis7
   .\redis-server.exe redis.windows.conf
   ```

### Q3：Django 连不上 MySQL

**检查清单**：

1. MySQL 服务是否运行：
   ```powershell
   Get-Service MySQL84
   ```

2. 端口是否监听：
   ```powershell
   netstat -ano | findstr :3307
   # 应看到 LISTENING 状态
   ```

3. 防火墙是否放行（如需远程访问）：
   ```powershell
   netsh advfirewall firewall add rule name="MySQL84" dir=in action=allow protocol=TCP localport=3307
   ```

4. 用户权限：
   ```powershell
   "C:\Program Files\MySQL\MySQL Server 8.4\bin\mysql.exe" -uroot -P 3307 -pDCT@2019 -e "SELECT user,host FROM mysql.user;"
   ```

### Q4：WebSocket 报 "unknown command 'HELLO'"

**原因**：连到了旧版 Redis（6379，< 6.0）

**解决**：

1. 确认 `config\settings.py` 中 `REDIS_PORT = 6380`（不是 6379）
2. 确认 Redis 7 服务已启动：
   ```powershell
   Get-Service Redis7
   ```
3. 测试连接：
   ```powershell
   "C:\Redis7\redis-cli.exe" -p 6380 -a DCT@2019 INFO server | findstr redis_version
   # 应输出: redis_version:7.x.x
   ```

### Q5：虚拟环境用错 Python 版本

**症状**：虚拟环境中 `python --version` 显示旧版本

**解决**：

```powershell
# 删除虚拟环境重建
rmdir /s /q C:\app\MyProject\Myprojectvenv
cd C:\app\MyProject
C:\Python312\python.exe -m venv Myprojectvenv
Myprojectvenv\Scripts\activate
python --version
# 应输出: Python 3.12.x

# 重新离线安装依赖
pip install --no-index --find-links=deploymentprepare-windows\pip_packages\ -r requirements.txt
```

### Q6：如何查看现有 MySQL/Redis 占用的端口

```powershell
# 查看所有监听端口
netstat -ano | findstr "LISTENING"

# 查看 MySQL 服务配置
Get-WmiObject Win32_Service | Where-Object {$_.Name -like "*MySQL*"} | Select-Object Name, PathName

# 查看 Redis 服务配置
Get-WmiObject Win32_Service | Where-Object {$_.Name -like "*Redis*"} | Select-Object Name, PathName
```

### Q7：如何卸载新装的服务

```powershell
# 卸载 MySQL84
net stop MySQL84
"C:\Program Files\MySQL\MySQL Server 8.4\bin\mysqld.exe" --remove MySQL84

# 卸载 Redis7
net stop Redis7
"C:\Redis7\redis-server.exe" --service-uninstall --service-name Redis7

# 卸载 MyProject 服务
cd C:\app\MyProject\deploymentprepare-windows
.\11-uninstall-nssm-services.bat
```

### Q8：MySQL Workbench 连接新 MySQL

在 MySQL Workbench 新建连接：

| 配置项   | 值                    |
| -------- | --------------------- |
| Hostname | `127.0.0.1`           |
| Port     | **`3307`**            |
| Username | `root` 或 `edwin`     |
| Password | `DCT@2019`            |

---

## 十一、部署检查清单

部署完成后逐项检查：

- [ ] Python 3.12 已安装到 `C:\Python312\`
- [ ] 虚拟环境已创建（`Myprojectvenv`），`python --version` 显示 3.12
- [ ] Python 依赖已离线安装
- [ ] MySQL 8.4 已安装到独立目录，端口 3307
- [ ] MySQL84 服务已启动，开机自启
- [ ] myproject 数据库已创建，edwin 用户已授权
- [ ] Redis 7 已安装到 `C:\Redis7\`，端口 6380
- [ ] Redis7 服务已启动，开机自启
- [ ] `config\settings.py` 已配置新端口（3307、6380）
- [ ] Django 能连接 MySQL（`python manage.py dbshell`）
- [ ] Redis 能连接（`redis-cli -p 6380 -a DCT@2019 ping`）
- [ ] 数据库迁移已执行（`python manage.py migrate`）
- [ ] 静态文件已收集（`python manage.py collectstatic`）
- [ ] 超级用户已创建
- [ ] MyProject 服务已注册（NSSM）
- [ ] 访问 http://localhost:8000/ 正常
- [ ] 访问 http://localhost:8000/admin/ 能登录
- [ ] WebSocket 连接正常（浏览器控制台无 1006 错误）
- [ ] 现有 MySQL/Redis 服务不受影响

---

## 十二、完整部署流程速查

```powershell
# ===== 在有网开发机准备 =====
# 1. 下载安装包
#    - mysql-8.4.x-winx64.zip
#    - Redis-x64-7.x.x.zip
#    - python-3.12.x-amd64.exe
#    - nginx-1.26.x.zip
#    - nssm.exe

# 2. 下载 Python 依赖
cd C:\djangoproject\MyProject\deploymentprepare-windows
.\02-download-pip-packages.bat

# 3. 打包所有文件拷贝到服务器

# ===== 在无网服务器执行 =====
# 4. 安装 Python 3.12 到 C:\Python312\（不加 PATH）
# 5. 解压 MySQL 到 C:\Program Files\MySQL\MySQL Server 8.4\
# 6. 解压 Redis 到 C:\Redis7\

# 7. 配置 MySQL（端口 3307，服务名 MySQL84）
#    - 创建 my.ini
#    - 初始化数据目录
#    - 注册服务
#    - 创建数据库和用户

# 8. 配置 Redis（端口 6380，服务名 Redis7）
#    - 修改 redis.windows.conf
#    - 注册服务

# 9. 创建 Python 虚拟环境
cd C:\app\MyProject
C:\Python312\python.exe -m venv Myprojectvenv
Myprojectvenv\Scripts\activate

# 10. 离线安装依赖
pip install --no-index --find-links=deploymentprepare-windows\pip_packages\ -r requirements.txt

# 11. 修改 settings.py（端口 3307、6380）

# 12. 迁移数据库
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser

# 13. 注册 MyProject 服务
.\deploymentprepare-windows\10-install-nssm-services.bat

# 14. 启动服务
net start MySQL84
net start Redis7
net start MyProject-Django
net start MyProject-Daphne
net start MyProject-Celery

# 15. 验证
#    访问 http://localhost:8000/admin/
#    WebSocket 连接正常
```
