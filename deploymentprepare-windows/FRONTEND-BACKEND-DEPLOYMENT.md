# 前后端分离部署指南

> 本文档详细说明 MyProject（Vue 3 + Vite 前端 + Django 后端）的生产部署方式。
> 涵盖：是否需要打包、如何处理跨域、Nginx 同源部署配置、以及完整的部署流程。

---

## 一、核心概念

### 1.1 开发环境 vs 生产环境

| 对比项 | 开发环境 (`npm run dev`) | 生产环境 (`npm run build` + Nginx) |
|---|---|---|
| **前端运行方式** | Vite Dev Server 运行在内存中 | 打包为静态文件 (HTML/CSS/JS) |
| **代理** | `vite.config.js` 中的 `server.proxy` 生效 | **完全不存在**，需要 Nginx 处理 |
| **HMR 热更新** | 支持 | 不支持 |
| **访问地址** | `http://localhost:5173` | `http://服务器IP/` (由 Nginx 托管) |
| **请求 `/api/xxx`** | Vite 代理转发到 Django | Nginx 直接转发到 Django |
| **性能** | 较慢（未压缩、未优化） | 快（压缩、Tree-shaking、CDN 可缓存） |

### 1.2 Vite vs Webpack（Vue CLI）

两者都需要 `npm run build` 生成 `dist/` 目录作为生产部署产物：

| | Vue CLI / Webpack | Vite（本项目使用） |
|---|---|---|
| 开发命令 | `npm run serve` | `npm run dev` |
| 打包命令 | `npm run build` | `npm run build`（底层用 Rollup） |
| 开发代理配置 | `vue.config.js` → `devServer.proxy` | `vite.config.js` → `server.proxy` |
| 打包产物 | `dist/` | `dist/`（结构相同，包含 `index.html` + 静态资源） |

**结论：Vite 和 Vue CLI 一样需要打包，命令都是 `npm run build`，产物都是 `dist/` 静态文件。**

---

## 二、跨域问题详解

### 2.1 什么是跨域

当浏览器从页面 A (`http://app.com`) 向不同源的服务器 B (`http://api.com`) 发送请求时，浏览器会自动拦截并要求服务器返回 CORS 头信息。这是浏览器的安全策略。

### 2.2 本项目的跨域处理状态

你的 Django 后端**已经配置了跨域支持**，位于 `config/settings.py`：

```python
# CORS 跨域配置（已启用）
CORS_ALLOW_ALL_ORIGINS = True          # 允许所有来源
CORS_ALLOW_CREDENTIALS = True          # 允许携带 Cookie
CORS_ALLOW_HEADERS = [
    'accept', 'accept-encoding', 'authorization', 'content-type',
    'dnt', 'origin', 'user-agent', 'x-csrftoken', 'x-requested-with',
    'x-remember-me', 'x-menu-mode',
]
CORS_EXPOSE_HEADERS = ['Content-Disposition', 'X-Total-Count']
```

且 `INSTALLED_APPS` 和 `MIDDLEWARE` 中已正确加载 `corsheaders`。

### 2.3 两种部署策略对比

#### 策略 A：同源部署（推荐 ⭐，零跨域）

```
浏览器
  │
  ▼
Nginx (:80) ─── 统一入口
  │
  ├── /            → 前端 SPA 静态文件 (frontend/dist/)
  ├── /api/        → 反代到 Django (127.0.0.1:8000)
  ├── /ws/         → 反代到 Daphne (127.0.0.1:8001)
  ├── /static/     → 反代到 Django 静态文件
  └── /media/      → 反代到 Django 媒体文件
```

- 前端代码中使用相对路径 `/api/xxx`（与开发时一致）
- 浏览器访问 `http://服务器IP/api/xxx`，Nginx 转发到 Django
- **不存在跨域问题**，前端完全不需要修改
- **生产环境最推荐**的方式

#### 策略 B：跨域部署（前后端不同域名/端口）

```
浏览器
  ├── 访问 http://app.com       (前端 dist，由 Nginx 托管)
  └── 请求 http://api.com/api   (Django 单独部署)
```

- 前端 `request.js` 的 `baseURL` 需要改为绝对地址 `http://api.com/api`
- Django 的 CORS 需要配置具体的 `CORS_ALLOWED_ORIGINS`（不要用 `*` 通配）
- 需要处理 Token/ Cookie 跨域共享
- 仅当前后端必须部署在不同服务器时使用

### 2.4 推荐策略：同源部署

**几乎所有生产环境都采用策略 A**。原因：
1. 零跨域问题，前端代码无需任何环境判断
2. 部署简单，所有流量通过 Nginx 统一管理
3. 便于 HTTPS 配置、负载均衡、SSL 证书管理
4. 便于前端性能优化（Gzip 压缩、CDN 缓存等）

---

## 三、完整部署流程（同源策略）

### 3.1 第一步：前端打包

```powershell
# 进入前端目录
cd C:\djangoproject\MyProject\frontend

# 安装依赖（首次或 package.json 变更后）
npm install

# 打包生成生产产物
npm run build
```

打包完成后，`frontend/dist/` 目录结构：

```
frontend/dist/
├── index.html              # 入口 HTML
├── assets/
│   ├── index-xxxx.js       # 业务代码（已压缩）
│   ├── element-plus-xxxx.js  # Element Plus（独立 chunk，便于缓存）
│   ├── echarts-xxxx.js     # ECharts（独立 chunk）
│   └── index-xxxx.css      # 样式文件
└── favicon.ico
```

### 3.2 第二步：Django 静态文件收集

```powershell
cd C:\djangoproject\MyProject

# 激活虚拟环境
Myprojectvenv\Scripts\activate

# 收集静态文件（admin 后台 + 自定义静态）
python manage.py collectstatic --noinput
```

### 3.3 第三步：启动后端服务

参考 `06-start-services.bat`，依次启动：

```powershell
# 终端 1：Django (端口 8000)
Myprojectvenv\Scripts\activate
python manage.py runserver 0.0.0.0:8000

# 终端 2：Daphne WebSocket (端口 8001)
Myprojectvenv\Scripts\activate
daphne -b 0.0.0.0 -p 8001 config.asgi:application

# 终端 3：Celery Worker
Myprojectvenv\Scripts\activate
celery -A config worker -l info
```

> 生产环境推荐用 NSSM 注册为 Windows 服务（详见 `README-windows-deploy.md` 第四章）

### 3.4 第四步：Nginx 配置（核心）

这是关键一步。Nginx 作为前端和后端的统一入口，实现同源部署。

#### 4.1 安装 Nginx

```powershell
# 解压 nginx-1.26.x.zip 到 C:\nginx\
# 目录结构：
C:\nginx\
├── nginx.exe
├── conf\
│   ├── nginx.conf          # 主配置
│   └── myproject.conf      # 本项目专用配置
└── ...
```

#### 4.2 配置 Nginx

编辑 `C:\nginx\conf\nginx.conf`，在 `http {}` 块内 include 项目配置：

```nginx
http {
    include       mime.types;
    default_type  application/octet-stream;
    sendfile      on;
    keepalive_timeout  65;

    # ============ 引入本项目配置 ============
    include C:/djangoproject/MyProject/deploymentprepare-windows/nginx.conf;
}
```

#### 4.3 本项目 Nginx 配置详解

> 完整配置文件见 `deploymentprepare-windows/nginx.conf`，部署时将其中所有 `__DEPLOY_ROOT__` 替换为实际路径（如 `C:/app/MyProject`）。

关键配置结构：

```nginx
# ---------- 后端服务上游 ----------
upstream myproject_django {
    server 127.0.0.1:8000;
}

upstream myproject_ws {
    server 127.0.0.1:8001;
}

server {
    listen 80;
    server_name _;
    client_max_body_size 50M;

    # ============ ① API 代理到 Django ============
    # 其他 location 必须写在 location / 之前，Nginx 按最长前缀匹配
    location /api/ {
        proxy_pass http://myproject_django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # ============ ② Django Admin 后台 ============
    location /admin/ {
        proxy_pass http://myproject_django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # ============ ③ WebSocket 代理 ============
    location /ws/ {
        proxy_pass http://myproject_ws;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 86400;
    }

    # ============ ④ 静态文件 ============
    location /static/ {
        alias __DEPLOY_ROOT__/staticfiles/;
        expires 30d;
        add_header Cache-Control "public";
        access_log off;
    }

    # ============ ⑤ 媒体文件 ============
    location /media/ {
        alias __DEPLOY_ROOT__/media/;
        expires 7d;
        add_header Cache-Control "public";
        access_log off;
    }

    # ============ ⑥ 前端 SPA（必须放在最后！） ============
    # 使用 root（非 alias）+ try_files，避免 Nginx "alias + try_files" 刷新 404 陷阱
    location / {
        root __DEPLOY_ROOT__/frontend/dist;
        try_files $uri $uri/ /index.html;
        index index.html;
    }

    # ============ 日志 ============
    access_log __DEPLOY_ROOT__/logs/nginx-access.log;
    error_log  __DEPLOY_ROOT__/logs/nginx-error.log;
}
```

#### 4.4 关键配置说明

**① `location /` — 前端 SPA**
- 使用 `root __DEPLOY_ROOT__/frontend/dist`（不是 `alias`），指向 `npm run build` 产物目录
- `try_files $uri $uri/ /index.html`：**SPA 核心配置**。当 Vue Router 使用 history 模式时（本项目默认），用户直接访问 `/message` 或刷新页面时，Nginx 找不到对应文件，会回退到 `index.html`，由 Vue Router 处理路由
- ⚠️ **为什么用 `root` 而不是 `alias`**：`alias` + `try_files` 在 Nginx 中有已知坑——fallback 内部重定向到 `/index.html` 时，基于 `alias` 的路径解析可能静默失败，导致刷新子路由 404。用 `root` 可以完全避免这个问题
- 这是传统 Django 模板渲染项目不需要、但 Vue/React SPA 必须有的配置

**② `location /api/` — API 代理**
- 将浏览器的 `/api/xxx` 请求转发给 Django
- 前端代码中的 `axios.create({ baseURL: '/api' })` 无需任何修改
- 与开发环境 `vite.config.js` 中的 `proxy` 效果完全一致

**③ `location /ws/` — WebSocket 代理**
- 代理 `/ws/notifications/` 到 Daphne (端口 8001)
- `proxy_http_version 1.1` 和 `Upgrade/Connection` 头是 WebSocket 必需的
- `proxy_read_timeout 86400` 保证长连接不被 Nginx 过早断开

**location 顺序的重要性**

Nginx 的 `location` 匹配规则是**最长前缀匹配优先**。上面配置中：
- `/api/` 比 `/` 长 → API 请求不会被前端规则拦截
- `/ws/` 比 `/` 长 → WebSocket 请求不会被前端规则拦截
- `/static/`、`/media/`、`/admin/` 同理
- 其他所有路径 → 前端 SPA 回退到 `index.html`

**所以 `location /` 必须放在最后**（或说其他规则必须写在它前面）。

#### 4.5 启动 Nginx

```powershell
cd C:\nginx
nginx.exe                    # 启动
nginx.exe -s reload          # 重新加载配置（不中断服务）
nginx.exe -s stop            # 停止
```

---

## 四、完整部署命令汇总

以下是从零到生产的完整命令序列：

```powershell
# ============= 1. 前端打包 =============
cd C:\__DEPLOY_ROOT__\frontend
npm install
npm run build
# 产物在 frontend/dist/

# ============= 2. Django 静态文件收集 =============
cd C:\__DEPLOY_ROOT__
Myprojectvenv\Scripts\activate
python manage.py collectstatic --noinput

# ============= 3. 启动后端服务 =============
# 终端 1：Django
python manage.py runserver 0.0.0.0:8000

# 终端 2：Daphne（WebSocket）
daphne -b 0.0.0.0 -p 8001 config.asgi:application

# 终端 3：Celery（异步任务）
celery -A config worker -l info

# ============= 4. 配置并启动 Nginx =============
# 1) 修改 deploymentprepare-windows/nginx.conf 中 __DEPLOY_ROOT__ 为实际路径（如 C:/app/MyProject）
# 2) 在 C:\nginx\conf\nginx.conf 的 http{} 块 include 该文件
# 3) 启动
cd C:\nginx
nginx.exe

# ============= 5. 验证 =============
# 浏览器访问：http://服务器IP/
# 应该看到登录页面（前端 SPA）
# 登录后功能完整正常
```

---

## 五、常见问题排查

### Q1：Nginx 配置中 `root` vs `alias` 的区别

两者都能用来托管静态文件，但路径解析逻辑不同：

- **`root`**（本项目 SPA 推荐用法）：`location /` + `root /path/to/dist` → 请求 `/index.html` 映射到文件 `/path/to/dist/index.html`；请求 `/assets/app.js` 映射到 `/path/to/dist/assets/app.js`
- **`alias`**：`location /` + `alias /path/to/dist/` → 请求 `/index.html` 映射到 `/path/to/dist/index.html`（与 root 结果相同）；但 `alias` + `try_files` 的 SPA fallback 在部分 Nginx 版本下会静默失败

**为什么本项目用 `root`**：
1. SPA history 模式必须配合 `try_files` 才能在刷新子路由时正常回退
2. `root` + `try_files` 组合稳定可靠；`alias` + `try_files` 存在已知陷阱
3. 对于深层路径如 `/assets/sub/app.js`，`root` 的路径拼接更直观

本项目其他 location（`/static/`、`/media/`）仍使用 `alias`，因为它们不需要 `try_files` 回退。

### Q2：刷新页面 404？

没有配置 `try_files $uri $uri/ /index.html`。SPA 使用 history 模式时，直接访问或刷新子路由（如 `/message`）会因为 Nginx 找不到物理文件而报 404。

### Q3：API 请求返回 HTML 页面？

`location /api/` 的代理规则没有写在 `location /` 前面，被前端规则拦截了。检查 location 顺序。

### Q4：WebSocket 连不上？

1. 确认 Daphne 已在 8001 端口启动
2. 确认 Nginx 的 `location /ws/` 配置包含 `proxy_http_version 1.1` 和 `Upgrade/Connection` 头
3. 检查 `proxy_read_timeout` 是否足够长（建议 86400 秒）

### Q5：静态资源 404？

1. 执行 `python manage.py collectstatic --noinput`
2. 检查 Nginx 中 `alias` 路径是否正确（注意末尾 `/`）
3. 确认目录存在且 Nginx 进程有读取权限

### Q6：前端打包后 `baseURL` 写错了？

你的项目 `request.js` 使用的是 `baseURL: '/api'`（相对路径），这是正确的。打包后浏览器请求 `http://服务器IP/api/xxx`，Nginx 会代理。**不需要改成绝对地址**。

### Q7：开发环境和生产环境的区别？

| 环境 | 谁处理 `/api/xxx` | 配置位置 |
|---|---|---|
| 开发 (`npm run dev`) | Vite Dev Server 代理 | `vite.config.js` → `server.proxy` |
| 生产 (Nginx) | Nginx 反向代理 | `nginx.conf` → `location /api/` |

两者对前端代码来说是透明的——前端始终用相对路径 `/api/xxx`，不需要区分环境。

---

## 六、HTTPS 配置（可选但推荐）

在 `nginx.conf` 的 `server` 块中添加 SSL：

```nginx
server {
    listen 80;
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate     C:/nginx/ssl/your-domain.crt;
    ssl_certificate_key C:/nginx/ssl/your-domain.key;

    # HTTP 自动跳转 HTTPS
    if ($server_port !~ 443) {
        return 301 https://$host$request_uri;
    }

    # ... 其余 location 配置同上
}
```

---

## 七、架构图总览

```
┌─────────────────────────────────────────────────┐
│                   浏览器 (客户端)                 │
│                                                   │
│  访问 http://your-server/                         │
│  请求路径：/  /api/  /ws/  /static/  /media/     │
└──────────────────────┬────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────┐
│                    Nginx (:80)                    │
│                                                   │
│  /           → frontend/dist/ (Vue SPA)           │
│  /api/       → proxy_pass Django (127.0.0.1:8000) │
│  /admin/     → proxy_pass Django Admin           │
│  /ws/        → proxy_pass Daphne (127.0.0.1:8001) │
│  /static/    → staticfiles/ (静态文件直读)        │
│  /media/     → media/ (用户上传直读)              │
└──────────┬──────────────┬──────────────┬─────────┘
           │              │              │
           ▼              ▼              ▼
    ┌──────────┐   ┌──────────┐   ┌──────────┐
    │ Django   │   │  Daphne  │   │  Celery  │
    │ :8000    │   │  :8001   │   │ Worker   │
    └────┬─────┘   └────┬─────┘   └──────────┘
         │              │
         ▼              ▼
    ┌──────────┐   ┌──────────┐
    │  MySQL   │   │  Redis   │
    │  :3306   │   │  :6379   │
    └──────────┘   └──────────┘
```

---

## 八、部署检查清单

- [ ] 前端 `npm run build` 成功，`frontend/dist/` 生成
- [ ] Django `collectstatic --noinput` 执行成功
- [ ] Django 在 8000 端口运行
- [ ] Daphne 在 8001 端口运行
- [ ] Celery Worker 正常运行
- [ ] Nginx 配置文件路径已改为实际部署路径
- [ ] Nginx 已启动 (`nginx.exe`)
- [ ] 浏览器访问 `http://服务器IP/` 看到登录页面
- [ ] 浏览器访问 `http://服务器IP/api/system/menus/` 返回 JSON
- [ ] 登录功能正常（Token 存储与发送）
- [ ] 刷新子路由页面不 404（SPA history 回退正常）
- [ ] WebSocket 连接正常（无控制台报错）
- [ ] 静态资源加载正常（F12 无 404）
- [ ] 防火墙已放行 80 端口
