# ============================================================
# 离线部署打包清单
# 在有网的开发机上准备这些文件，打包后拷贝到无网服务器
# ============================================================

## 1. 项目代码
- 整个 MyProject 文件夹（除以下目录外）
  - 排除：Myprojectvenv/（虚拟环境太大，单独打包）
  - 排除：node_modules/（前端依赖，单独打包）
  - 排除：__pycache__/
  - 排除：.git/
  - 排除：Test/

## 2. 虚拟环境（Myprojectvenv）
- 方式A：直接打包整个 Myprojectvenv 文件夹（约 200-400MB）
  - 注意：目标服务器的 Python 版本必须与开发机一致
  - 拷贝后需修改 Scripts/activate.bat 中的路径
- 方式B（推荐）：用 02-download-pip-packages.bat 下载依赖
  - 在目标服务器新建虚拟环境后离线安装
  - 见下方"离线安装步骤"

## 3. 前端构建产物（frontend/dist）
- 方式A：在有网机器执行 npm run build，拷贝 dist/ 目录
- 方式B：拷贝整个 frontend/（含 node_modules）到服务器构建
- 推荐：方式A，体积更小

## 4. Docker 镜像（如使用 Docker 部署 MySQL/Redis）
- 在有网机器拉取镜像并导出:
  docker pull mysql:8.4
  docker pull redis:7-alpine
  docker save -o mysql-8.4.tar mysql:8.4
  docker save -o redis-7.tar redis:7-alpine
- 在目标服务器加载:
  docker load -i mysql-8.4.tar
  docker load -i redis-7.tar

## 5. 离线安装包
- Python 3.11/3.12 安装包 (python.org 下载)
  - https://www.python.org/downloads/windows/
- Redis for Windows (如不用 Docker)
  - https://github.com/tporadowski/redis/releases
- Nginx for Windows
  - http://nginx.org/en/download.html
- NSSM (注册 Windows 服务)
  - https://nssm.cc/release/nssm-2.24.zip
- Node.js LTS (如需在服务器构建前端)
  - https://nodejs.org/

## 6. 数据库备份（从开发机迁移数据）
- 执行 08-backup-database.bat 生成 .sql 文件
- 或直接拷贝 Docker 数据卷（不推荐，版本敏感）

# ============================================================
# 离线安装步骤（按顺序执行）
# ============================================================

1. 安装 Python 3.11/3.12
2. 创建虚拟环境: python -m venv Myprojectvenv
3. 执行 02-download-pip-packages.bat 下载依赖（在有网机器）
4. 执行 03-install-python-deps.bat 离线安装依赖
5. 启动 Docker MySQL + Redis (docker compose -f docker-compose.prod.yml up -d)
   - 或安装 Redis for Windows 原生版
6. 执行 04-init-mysql.bat 初始化数据库
7. 执行 05-migrate.bat 执行迁移
8. 执行 06-start-services.bat 启动服务（测试用）
   - 或执行 10-install-nssm-services.bat 注册为服务（生产用）
9. 配置 Nginx 反向代理（可选，生产推荐）
