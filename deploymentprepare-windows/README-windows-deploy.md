# MyProject Windows 无外网部署指南

> **目标环境**：Windows Server 2016+ / Windows 10/11，无外网
> **部署方式**：Docker MySQL/Redis + Python 原生 + Nginx + NSSM 服务
>
> **重要文档**：
> - [FRONTEND-BACKEND-DEPLOYMENT.md](file:///c:/djangoproject/MyProject/deploymentprepare-windows/FRONTEND-BACKEND-DEPLOYMENT.md) — 前后端分离部署详解（Vite 打包、Nginx 同源配置、跨域方案）
> - [DOCKER-OFFLINE-GUIDE.md](file:///c:/djangoproject/MyProject/deploymentprepare-windows/DOCKER-OFFLINE-GUIDE.md) — Docker 离线安装、镜像导出导入详细步骤
> - [NO-DOCKER-MULTIVERSION-GUIDE.md](file:///c:/djangoproject/MyProject/deploymentprepare-windows/NO-DOCKER-MULTIVERSION-GUIDE.md) — 无 Docker 多版本共存部署（服务器已有 MySQL/Redis/Python）
> - [PACKAGE-CHECKLIST.md](file:///c:/djangoproject/MyProject/deploymentprepare-windows/PACKAGE-CHECKLIST.md) — 离线打包清单
>
> **部署前必读**：
> - 如服务器**无 Docker**或希望**不依赖 Docker**，请阅读 [NO-DOCKER-MULTIVERSION-GUIDE.md](file:///c:/djangoproject/MyProject/deploymentprepare-windows/NO-DOCKER-MULTIVERSION-GUIDE.md)
> - 如服务器已有 MySQL/Redis，本项目通过 **不同端口 + 不同服务名** 隔离运行（MySQL 用 3307，Redis 用 6380）
> - 如你对 **Vite 打包、前后端如何结合部署、跨域处理** 有疑问，请阅读 [FRONTEND-BACKEND-DEPLOYMENT.md](file:///c:/djangoproject/MyProject/deploymentprepare-windows/FRONTEND-BACKEND-DEPLOYMENT.md)

---

## 一、环境规划

### 1.1 端口规划

| 服务        | 端口  | 说明              |
| ----------- | ----- | ----------------- |
| Nginx       | 80    | 对外访问入口      |
| Django      | 8000  | 后端应用（内网）  |
| Daphne      | 8001  | WebSocket（内网） |
| MySQL       | 3307  | 数据库（内网）    |
| Redis       | 6379  | 缓存/消息（内网） |

### 1.2 目录结构（推荐）

```
C:\app\MyProject\               # 项目根目录
├── config\                     # Django 配置
├── app01\                      # 认证模块
├── system\                     # RBAC 模块
├── messaging\                  # 消息推送
├── aihub\                      # AI 模块
├── frontend\dist\              # 前端构建产物
├── staticfiles\                # 收集的静态文件
├── media\                      # 用户上传
├── logs\                       # 运行日志
├── Myprojectvenv\              # Python 虚拟环境
├── deploymentprepare-windows\  # 本部署目录
├── requirements.txt
└── manage.py
```

---

## 二、前置准备（在有网机器上）

### 2.1 下载 Python 离线安装包

1. 访问 https://www.python.org/downloads/windows/
2. 下载 Python 3.11.x 或 3.12.x 64位安装包（如 `python-3.12.7-amd64.exe`）

### 2.2 下载 Redis for Windows（可选，如不用 Docker）

- 推荐：使用 Docker 版（见 2.4）
- 原生版：https://github.com/tporadowski/redis/releases （下载 `.msi` 或 `.zip`）
- **版本要求**：Redis 6.0+（WebSocket 需要 HELLO 命令支持）

### 2.3 下载 Nginx for Windows

- http://nginx.org/en/download.html
- 下载 Stable version，如 `nginx-1.26.1.zip`

### 2.4 下载 Docker 镜像（推荐用 Docker 跑 MySQL + Redis）

**详细步骤见 [DOCKER-OFFLINE-GUIDE.md](file:///c:/djangoproject/MyProject/deploymentprepare-windows/DOCKER-OFFLINE-GUIDE.md)**

简要步骤：

```powershell
# 在有网机器上拉取并导出
docker pull mysql:8.4
docker pull redis:7-alpine
docker save -o C:\docker-images\mysql-8.4.tar mysql:8.4
docker save -o C:\docker-images\redis-7.tar redis:7-alpine
```

同时下载 Docker Desktop 离线安装包：https://www.docker.com/products/docker-desktop

将 `mysql-8.4.tar`、`redis-7.tar`、`Docker Desktop Installer.exe` 拷贝到服务器。

**服务器端 Docker 安装 + 镜像导入**：详见 [DOCKER-OFFLINE-GUIDE.md](file:///c:/djangoproject/MyProject/deploymentprepare-windows/DOCKER-OFFLINE-GUIDE.md) 第二、三节

### 2.5 下载 Python 依赖包

在有网机器的项目根目录执行：

```powershell
cd deploymentprepare-windows
.\02-download-pip-packages.bat
```

生成 `pip_packages\` 目录，包含所有依赖的 `.whl` 文件。

### 2.6 下载 NSSM（注册 Windows 服务用）

- https://nssm.cc/release/nssm-2.24.zip
- 解压后将 `win64\nssm.exe` 拷贝到 `deploymentprepare-windows\`

### 2.7 构建前端（在有网机器上）

```powershell
cd frontend
npm install
npm run build
```

生成 `frontend\dist\` 目录，连同 `frontend` 一起拷贝到服务器。

### 2.8 打包项目

需要拷贝到服务器的文件：

| 文件/目录                      | 说明                       |
| ------------------------------ | -------------------------- |
| `MyProject\` (整个项目)        | 排除 `node_modules`、`.git`、`__pycache__` |
| `deploymentprepare-windows\`   | 部署脚本                   |
| `pip_packages\`                | Python 离线依赖            |
| `python-3.12.x-amd64.exe`      | Python 安装包              |
| `nginx-1.26.x.zip`             | Nginx                      |
| `nssm.exe`                     | 服务注册工具               |
| `mysql-8.4.tar`                | MySQL Docker 镜像          |
| `redis-7.tar`                  | Redis Docker 镜像          |

---

## 三、服务器安装（无网环境）

### 3.1 安装 Python

1. 双击 `python-3.12.x-amd64.exe`
2. **重要**：勾选 "Add Python to PATH"
3. 选择 "Install for all users"
4. 安装路径建议：`C:\Python312\`

验证：
```powershell
python --version
pip --version
```

### 3.2 创建虚拟环境

```powershell
cd C:\app\MyProject
python -m venv Myprojectvenv
```

### 3.3 离线安装 Python 依赖

```powershell
cd deploymentprepare-windows
.\03-install-python-deps.bat
```

或手动执行：
```powershell
..\Myprojectvenv\Scripts\activate
pip install --no-index --find-links=pip_packages\ -r ..\requirements.txt
```

### 3.4 安装 Docker Desktop（如服务器有 Docker）

如服务器已有 Docker，跳过。否则：
- 从 https://www.docker.com/products/docker-desktop 下载（需联网）
- **无网环境推荐**：直接用 Windows 原生 Redis + MySQL，不用 Docker

### 3.5 加载 Docker 镜像（如使用 Docker）

```powershell
docker load -i mysql-8.4.tar
docker load -i redis-7.tar
```

启动 MySQL 和 Redis：
```powershell
cd deploymentprepare-windows
docker compose -f docker-compose.prod.yml up -d
```

验证：
```powershell
docker ps
# 应看到 myproject_mysql84 和 myproject_redis 两个容器
```

### 3.6 安装 Redis 原生版（如不用 Docker）

1. 解压 Redis `.zip` 到 `C:\Redis\`
2. 修改 `redis.windows.conf`：
   ```
   requirepass DCT@2019
   bind 127.0.0.1
   port 6379
   ```
3. 注册为服务：
   ```powershell
   redis-server --service-install redis.windows.conf --service-name Redis
   net start Redis
   ```

### 3.7 初始化数据库

```powershell
cd deploymentprepare-windows
.\04-init-mysql.bat
```

### 3.8 执行数据库迁移

```powershell
.\05-migrate.bat
```

### 3.9 创建超级用户

```powershell
cd C:\app\MyProject
Myprojectvenv\Scripts\activate
python manage.py createsuperuser
```

### 3.10 收集静态文件

```powershell
python manage.py collectstatic --noinput
```

---

## 四、服务启动

### 4.1 方式A：命令行启动（测试用）

```powershell
cd deploymentprepare-windows
.\06-start-services.bat
```

会启动 3 个命令行窗口：Django、Daphne、Celery。

### 4.2 方式B：注册为 Windows 服务（生产推荐）

**前置**：将 `nssm.exe` 放到 `deploymentprepare-windows\` 目录

以管理员身份运行：
```powershell
.\10-install-nssm-services.bat
```

注册后可通过 `services.msc` 管理服务，或命令行：
```powershell
net start MyProject-Django
net start MyProject-Daphne
net start MyProject-Celery

net stop MyProject-Django
net stop MyProject-Daphne
net stop MyProject-Celery
```

### 4.3 方式C：设置开机自启

NSSM 注册的服务默认为 `SERVICE_AUTO_START`，开机自动启动。

---

## 五、Nginx 配置（生产推荐）

> 💡 如需更详细的前后端部署说明（Vite 打包、SPA 配置、跨域方案等），请阅读 [FRONTEND-BACKEND-DEPLOYMENT.md](file:///c:/djangoproject/MyProject/deploymentprepare-windows/FRONTEND-BACKEND-DEPLOYMENT.md)

### 5.1 安装 Nginx

解压 `nginx-1.26.x.zip` 到 `C:\nginx\`

### 5.2 配置反向代理

1. 编辑 `C:\nginx\conf\nginx.conf`
2. 在 `http` 块内 include 项目配置：
   ```nginx
   http {
       include       mime.types;
       default_type  application/octet-stream;
       sendfile      on;
       keepalive_timeout  65;

       include C:/app/MyProject/deploymentprepare-windows/nginx.conf;
   }
   ```

3. 修改 `nginx.conf` 中的路径为实际部署路径

### 5.3 启动 Nginx

```powershell
cd C:\nginx
start nginx
```

注册为服务（用 NSSM）：
```powershell
nssm install Nginx C:\nginx\nginx.exe
nssm set Nginx AppDirectory C:\nginx
nssm set Nginx Start SERVICE_AUTO_START
net start Nginx
```

---

## 六、数据备份与恢复

### 6.1 备份

```powershell
cd deploymentprepare-windows
.\08-backup-database.bat
```

备份文件保存在 `backups\` 目录，文件名格式：`myproject_YYYYMMDD_HHMMSS.sql`

### 6.2 恢复

```powershell
.\09-restore-database.bat backups\myproject_20260811_120000.sql
```

### 6.3 定时备份（Windows 任务计划）

1. 打开"任务计划程序"
2. 创建基本任务
3. 触发器：每天凌晨 2:00
4. 操作：启动程序 `C:\app\MyProject\deploymentprepare-windows\08-backup-database.bat`
5. 起始位置：`C:\app\MyProject\deploymentprepare-windows\`

---

## 七、常见问题

### Q1：MySQL Workbench 能连接 Docker 里的 MySQL 吗？

**可以**。Docker MySQL 已映射端口到宿主机：

| 配置项 | 值           |
| ------ | ------------ |
| Host   | `127.0.0.1`  |
| Port   | `3307`       |
| User   | `root` 或 `edwin` |
| Password | `DCT@2019` |

在 MySQL Workbench 中新建连接，填入上述信息即可。

### Q2：WebSocket 连接失败

1. 确认 Redis 已启动且版本 >= 6.0
2. 确认 Daphne 服务已启动（端口 8001）
3. 检查 `config\settings.py` 中 `CHANNEL_LAYERS` 配置
4. 查看日志：`logs\daphne.log`

### Q3：CSRF 验证失败

在 `config\settings.py` 的 `CSRF_TRUSTED_ORIGINS` 中添加访问地址：
```python
CSRF_TRUSTED_ORIGINS = [
    'http://你的服务器IP',
    'http://你的域名',
]
```

### Q4：静态文件 404

1. 执行 `python manage.py collectstatic --noinput`
2. 检查 Nginx 配置中的 `alias` 路径是否正确
3. 如不用 Nginx，Django dev 模式会自动提供静态文件

### Q5：虚拟环境路径变了怎么办

如果项目从 `C:\djangoproject\MyProject` 移到 `C:\app\MyProject`：

```powershell
# 删除旧虚拟环境
rmdir /s /q Myprojectvenv

# 重新创建
python -m venv Myprojectvenv

# 重新安装依赖（离线）
Myprojectvenv\Scripts\activate
pip install --no-index --find-links=deploymentprepare-windows\pip_packages\ -r requirements.txt
```

### Q6：如何修改数据库密码

1. 修改 MySQL：
   ```sql
   ALTER USER 'edwin'@'%' IDENTIFIED BY '新密码';
   FLUSH PRIVILEGES;
   ```

2. 修改 `config\settings.py`：
   ```python
   DATABASES = {
       'default': {
           'PASSWORD': '新密码',
           ...
       }
   }
   ```

3. 重启 Django 服务

---

## 八、部署检查清单

部署完成后，逐项检查：

- [ ] Python 3.11/3.12 已安装
- [ ] 虚拟环境已创建并激活
- [ ] Python 依赖已安装
- [ ] MySQL 已启动（Docker 或原生）
- [ ] Redis 已启动（版本 >= 6.0）
- [ ] 数据库已初始化（04-init-mysql.bat）
- [ ] 数据库迁移已执行（05-migrate.bat）
- [ ] 静态文件已收集
- [ ] 超级用户已创建
- [ ] Django 服务已启动（端口 8000）
- [ ] Daphne 服务已启动（端口 8001）
- [ ] Celery 服务已启动
- [ ] Nginx 已配置并启动
- [ ] 防火墙已放行 80 端口
- [ ] 访问 http://服务器IP/ 能正常显示
- [ ] 能登录 Django Admin
- [ ] WebSocket 连接正常（消息中心有实时推送）
