# MyProject 项目规则（实际环境）

## 一、技术栈与版本

### 后端（Python/Django 单体 + Django REST Framework）
| 模块 | 版本 | 说明 |
| --- | --- | --- |
| Python | **3.14.7** | 虚拟环境路径：`Myprojectvenv/`，位于项目根目录 |
| Django | **6.1** | 入口：`manage.py`，ASGI/WSGI 配置在 `config/` |
| djangorestframework (DRF) | >= 3.16.0 | 默认 JSON 渲染，自定义 `custom_exception_handler` |
| djangorestframework-simplejwt | >= 5.5.0 | Access 2h / Refresh 7d，带 token 黑名单 + 自动轮换 |
| django-guardian | >= 2.4.0 | 对象级权限（RBAC 辅助） |
| django-cors-headers | >= 4.7.0 | 开发期 `CORS_ALLOW_ALL_ORIGINS=True` |
| django-filter | >= 25.1 | DRF 过滤后端 |
| drf-spectacular | >= 0.28.0 | API 文档：`/api/docs/`、`/api/redoc/`、`/api/schema/` |
| channels + channels-redis | >= 4.2.x | WebSocket 消息推送（Pub/Sub 模式） |
| celery + django-celery-beat + django-celery-results | >= 5.5.x | 异步/定时任务 |
| mysqlclient | **2.2.8** | MySQL 驱动（锁定版本，含 cp314 wheel） |
| django-redis / redis | >= 5.4.x | 缓存 + 会话 + Celery Broker |
| whitenoise | >= 6.9.0 | 静态文件服务（部署） |
| openai | >= 1.60.0 | AI 客户端（支持通过 AI_BASE_URL 切换内网/本地模型） |

### 数据库 / 缓存 / 消息队列
| 组件 | 版本 | 端口/DB | 凭据 | 说明 |
| --- | --- | --- | --- | --- |
| MySQL | **8.4**（Docker） | `127.0.0.1:3307` | `edwin / DCT@2019`，库：`myproject` | 避免与本机 3306 冲突；Docker `docker compose up -d` |
| Redis | 7.x（建议） | `localhost:6379` | `DCT2019` | db1=celery broker / db2=celery result / db3=缓存&业务 / db4=channels |

### 前端（Vue 3 + Vite）
| 模块 | 版本 | 说明 |
| --- | --- | --- |
| Vue | **3.4.38** | 组合式 API + `<script setup>` |
| Vite | **4.5.3** | 端口 **5173**，代理：`/api`、`/ws`、`/media`、`/admin`、`/static` → `http://127.0.0.1:8000` |
| vue-router | **4.3.3** | 动态路由 + 权限守卫 |
| Pinia | **2.1.7** | 状态管理（store 按领域拆分：user / app / permission / message） |
| Element Plus | **2.7.6** + `@element-plus/icons-vue` 2.3.1 | UI 组件库 |
| Axios | **1.6.8** | HTTP 请求（见 `src/utils/request.js`） |
| ECharts | **5.5.0** | 数据可视化 |
| js-cookie | **3.0.5** | 记住密码 token 持久化 |
| NProgress | **0.2.0** | 路由加载进度条 |
| sass | **1.62.1** | SCSS 样式（非 Tailwind） |
| @vitejs/plugin-vue | **4.6.2** | — |

### 项目布局 & 命名约定
```
MyProject/
├── config/                  # Django 工程配置（settings/urls/celery/asgi/wsgi）
├── app01/                   # 认证 & 用户（自定义 User 模型 AUTH_USER_MODEL='app01.User'）
├── system/                  # RBAC：Menu / Role / OperationLog / LoginLog
├── tasks/                   # Celery 异步 / 定时任务
├── messaging/               # Channels 消息中心（私信 + 广播 + 未读）
├── aihub/                   # AI 助手（AI_PROVIDER/AI_BASE_URL 可内网）
├── TaskManagement/          # 任务管理子系统（新增 app 模板）
├── frontend/                # Vue 3 前端
│   └── src/
│       ├── api/index.js     # **所有 API 接口统一放在此文件，按模块注释分隔**
│       ├── utils/request.js # Axios 封装（拦截器 + JWT + 进度条 + 错误提示）
│       ├── store/{user,app,permission,message}.js  # Pinia 领域 store
│       ├── layout/          # 主框架 Layout（Navbar / Sidebar / SidebarItem）
│       ├── router/          # 静态路由 + permission 守卫
│       ├── views/{login,dashboard,message,ai,profile,task,system/*}/index.vue
│       ├── styles/index.scss
│       ├── directives/permission.js
│       └── App.vue + main.js
├── logs/                    # Django/Operation/Celery 日志（concurrent_log_handler 轮转）
├── manage.py
├── requirements.txt
└── docker-compose.yml       # MySQL 8.4 容器
```

## 二、后端代码规范

### 1. App 创建模式
- 新业务模块 → **新建独立 Django App**（例如 `TaskManagement`），**严禁**将业务代码直接塞入 `app01` 或 `system`。
- 新建 App 三步：
  1. `python manage.py startapp <Name>`（首字母大写的业务名，如 `TaskManagement`）
  2. 在 `config/settings.py` 的 `INSTALLED_APPS` 中注册
  3. 在 `config/urls.py` 挂载路由：`path('api/<prefix>/', include('<App>.urls'))`，前缀使用小写短名（如 `task`）

### 2. 模型（models.py）
- **必须继承 `models.Model`**，业务通用字段约定：
  - `created_at = DateTimeField(auto_now_add=True, verbose_name='创建时间')`
  - `updated_at = DateTimeField(auto_now=True, verbose_name='更新时间')`
- 字段中文 `verbose_name` **必须写**。
- 枚举一律用 `models.IntegerChoices`（如 `User.Status`、`Menu.MenuType`）。
- 自定义表名：`class Meta: db_table = 'sys_xxx'`（系统表以 `sys_` 开头，任务表用 `task_`、消息表用 `msg_` 等前缀）。
- `default / choices / blank / null` 语义严格区分。
- **自定义用户模型**：`AUTH_USER_MODEL = 'app01.User'`，**跨 app 关联用户** 一律用 `settings.AUTH_USER_MODEL`，不要直接 import `app01.User`。
- 用户扩展字段：昵称、头像、手机、邮箱、性别、状态、`menu_mode`、`menu_collapsed`、`remember_token` 等都已在 `app01.User` 提供。

### 3. 序列化（serializers.py）
- DRF `serializers.ModelSerializer` 为主；请求/响应非持久化字段用普通 `serializers.Serializer`。
- 响应一律通过 `Response(ok(data))` / `Response(fail(msg))` 包裹（`system/utils.py` 提供），格式固定：
  ```json
  {"code": 200, "msg": "...", "success": true, "data": <任意>}
  ```
- 列表接口 `list` 覆盖时不要忘了包 `ok()`。

### 4. 视图（views.py）
- 首选 **`viewsets.ModelViewSet` + mixins**，REST 风格。
- 权限类：
  - 默认 `[IsAuthenticated, HasPermission]`，设置属性 `permission_required = 'app:action'`（例如 `'system:menu'`）。
  - `HasPermission` 来自 `system.permissions`；超管自动放行；普通用户走 Role 关联 Menu + Django 权限。
- 自定义业务动作：`@action(detail=..., methods=['GET/POST/...'], url_path='xxx')`，返回用 `ok()`/`fail()`。
- 日志/统计/报表接口：在 ViewSet 中用 `@action` 暴露，URL 前缀按 `config/urls.py` 规则。
- **禁止**修改 `app01` / `system` 中已稳定的核心 ViewSet 行为，除非你确认修改全局不影响其他模块。

### 5. URL 路由（urls.py）
- 每个 App 内独立一个 `urls.py`，使用 `DefaultRouter` 或手动列表。
- 新接口路径命名：**小写下划线 + 层级一致**（与前端 `api/index.js` 对齐）：
  - CRUD：`GET/POST /prefix/plural`，`GET/PUT/DELETE /prefix/plural/{id}`
  - 动作：`POST /prefix/plural/{id}/submit_approval`、`/approve`、`/reject`、`/update_progress`、`/verify`…
  - 统计：`GET /prefix/stats/summary`、`/by_person`、`/performance_summary`

### 6. Admin 定制（admin.py）
- 密码修改：在 `UserChangeForm.fieldsets` 里使用 `new_password = CharField(widget=PasswordInput, required=False)`，在 `save_model` 里用 `obj.set_password(cleaned_data['new_password'])` 写入（参考 `app01/admin.py`）。
- 不要直接在 `fieldsets` 引用原始 `password` 字段。

### 7. 全局约定（settings / 安全）
- **时区**：`Asia/Shanghai`，`USE_TZ=True`，`LANGUAGE_CODE='zh-hans'`。
- **字符集**：MySQL 强制 `utf8mb4`，Redis RESP2 协议（兼容 < 6.0）。
- **JWT**：请求头 `Authorization: Bearer <access_token>`；刷新、黑名单机制已启用。
- **AI**：`AI_PROVIDER/AI_BASE_URL/AI_API_KEY/AI_MODEL/AI_TIMEOUT/AI_MAX_RETRIES` 全部用 `os.environ.get` 读取，**内网环境** 通过设置 `AI_BASE_URL` 指向公司模型网关或本地 Ollama 即可工作，代码已统一走 `aihub/client.py`。
- **日志**：`LOG_DIR = BASE_DIR / 'logs/'`，Windows 下使用 `concurrent_log_handler.ConcurrentRotatingFileHandler`（避免文件锁 PermissionError）；不要直接用标准库 `RotatingFileHandler`。

## 三、前端代码规范

### 1. 目录与命名
- **视图组件**：`src/views/<模块>/index.vue`（Dashboard、AI、Message 页面都沿用此模式），新建页面一律 `index.vue`。
- **子页/详情页**：同目录下 `dashboard.vue`、`detail.vue`、`category.vue` 等小驼峰（kebab-case）。
- **框架组件**（`layout/components/*.vue` 等）：PascalCase。
- **Pinia Store**：`src/store/<领域>.js`，**按领域拆分**（user / app / permission / message），新增领域就新增一个文件，不要往现有 store 里塞无关状态。
- **工具函数/API**：`camelCase`。

### 2. 风格：`<script setup>` + 组合式 API
- 所有新 `.vue` 文件**必须**用 `<script setup>`，不要用 Options API。
- 响应式数据：`ref` 优先；简单对象也可以用 `reactive`；计算属性 `computed`；副作用 `watch`/`watchEffect`/`onMounted`/`onActivated` 等生命周期。
- **循环依赖规避**：Pinia store 之间互相引用时，**不要在模块顶层 import**，应该在函数内部动态 `import('@/store/<xxx>')` 或延迟调用 `useXxxStore()`（参考 `user.logout()` 里对 permission store 的动态 import，避免循环依赖）。

### 3. Pinia 状态管理（关键习惯）
- **用户级偏好**（菜单布局 / 收起 / 主题）在 `appStore`，持久化用 `localStorage`，但**权威来源是用户表**（`app01.User.menu_mode`、`menu_collapsed`）。任何入口（登录 / 记住登录 / 拉取用户信息 / 路由守卫首次命中）都必须调用 `userStore.applyMenuPreferences(user)`，**覆盖掉设备 localStorage 残留值**。
- **消息未读数**：集中在 `useMessageStore().unreadCount`，提供 `fetchUnread()`。NavBar 徽标绑定它；消息页标记已读后要手动 `messageStore.fetchUnread()`，并保持 30s 轮询兜底。
- **主题**：`appStore.isDark` + `localStorage`，切换时同步 `document.documentElement.classList.toggle('dark')`，样式统一走 Element Plus CSS 变量（`--el-bg-color`、`--el-text-color-primary` 等），自定义全局覆盖用**非 scoped `<style>`**（如 `layout/index.vue` 的 `html.dark .layout-aside`）。
- **菜单重建**：切换左右/顶部布局时，`layout/index.vue` 根容器 `:key="appStore.menuMode"` 强制 Vue 重建组件树，消除左侧 DOM 残留。

### 4. HTTP 请求 & API 层
- **所有请求必须走** `frontend/src/utils/request.js` 导出的 axios 实例，不要直接 `import axios from 'axios'`。
  - baseURL 固定 `/api` → Vite 代理 / Nginx 转发到后端。
  - 自动 `Authorization: Bearer <token>`（从 userStore 读取）。
  - 自动 NProgress 进度条。
  - 自动错误弹窗（401 自动 logout + 跳登录页、403 无权限、500 内部错误、其余按业务 `res.msg` 显示）。
- **所有 API 函数集中放在** `frontend/src/api/index.js`，并按模块用 `// ===` 注释分隔（现有认证、系统、消息、AI、TaskManagement 五大块）。
  - 命名规范：`动词开头 + 小驼峰`：
    - 列表：`list<Xxx>s(params)`（如 `listTasks`、`listRoles`）
    - 详情：`get<Xxx>Detail(id)`（如 `getTaskDetail`）
    - 创建：`create<Xxx>(data)`（如 `createMenu`）
    - 更新：`update<Xxx>(id, data)`（如 `updateRole`）
    - 删除：`delete<Xxx>(id)` / `batchDelete<Xxx>s(data)`
    - 动作：`submitApproval`、`approveTask`、`rejectTask`、`updateTaskProgress`、`verifyTask`、`markMessageRead`…
    - 统计：`get<Xxx>Summary()`、`getTaskStatsByPerson()`、`getUnreadCount()`…
- **调用处**：所有异步调用必须包裹 `try/catch`，错误要么 `ElMessage.error`，要么静默忽略（如徽标拉取失败），严禁 `Unhandled Rejection`。

### 5. 动态路由 & 权限
- 静态路由（登录/404/403/仪表盘/个人中心）写死在 `router/index.js`。
- 用户动态菜单/路由来自后端 `/api/system/user-menus`，在 `router/permission.js` 守卫中调用 `permissionStore.generateRoutes()` + `router.addRoute` 注入 Layout 之下。
- 菜单权限由后端返回树决定，前端 `permissionStore.menus` 直接渲染；按钮级别用 `directives/permission.js` + `userStore.hasPermission('xxx:xxx')`。
- **新增页面必须同时**：① 在系统菜单表中维护 `path/component/icon/permission`；② 在用户角色中勾选关联菜单。

### 6. 样式（SCSS）
- **本项目使用 SCSS**，不要引入 Tailwind。
- 主题色/背景色**优先用 Element Plus CSS 变量**：`--el-bg-color`、`--el-bg-color-page`、`--el-text-color-primary`、`--el-border-color-lighter`，日间/夜间自动生效。
- 夜间模式需要跨组件全局覆盖的样式，必须放在**非 scoped** `<style lang="scss">` 里，选择器以 `html.dark` 开头。
- 菜单收缩徽标铃铛的对齐：`el-badge` 使用 `display: inline-flex; align-items: center` + `top: auto; bottom: -2px`；徽标外层 `pointer-events: none` 避免遮挡点击。

### 7. Element Plus 组件常用约定
- 多级 `el-sub-menu`：`:index` 若 `path` 为空，必须回退到 `String(item.id)` 保证唯一。
- 顶部菜单弹出的子菜单 `:teleported="false"`，渲染在 navbar 容器内，便于隔离定位。
- 穿梭框（Transfer）：负责人、参与人、审核人、用户选择等一律用 `el-transfer`，配合 filterable。
- 日期选择：任务日期统一 `DateTimeField`，前端 `el-date-picker type="datetime"`，`value-format="YYYY-MM-DD HH:mm:ss"`。
- 标签（Tag）区分任务状态/优先级/难度：各自对应不同颜色，保持与任务列表页一致。

## 四、API 响应结构（强约定）
所有 DRF 接口必须用 `system/utils.py` 的 `ok(data, msg, code)` / `fail(msg, code, data, err)` 包裹，前端 request.js 按此字段解析：
```ts
type ApiResponse<T> = {
  code: number        // 200 成功；401 未登录；403 无权限；其余业务错误
  msg: string
  success: boolean
  data?: T
}
```
前端 `.then(res => res.data)` 访问业务数据，下载接口需 `responseType: 'blob'`（request.js 会跳过 code 校验）。

## 五、安全与质量
- **XSS**：所有用户输入在入库后、渲染前依赖 Element Plus `v-text` / 模板插值默认转义；富文本场景必须用经过 `DOMPurify` 处理后再 `v-html`（目前没有富文本，请勿直接 `v-html` 用户数据）。
- **Token & 密钥**：JWT 存在 localStorage（`myproject_token` / `myproject_refresh`）；AI_KEY、DB 密码、Redis 密码等不得硬编码在前端；后端配置中 `os.environ.get('xxx', default)` 优先，默认值仅用于开发。
- **异步错误处理**：每个 `async function` 或 `await` 必须 `try/catch`；不要在 `onMounted/onActivated/watch` 回调中放未捕获的 async。
- **新 App 的审计**：创建新子系统（类似 TaskManagement）必须：
  1. 创建 Role + 菜单权限；
  2. 菜单权限格式：`<app_prefix>:<resource>`，例：`task:task_list`、`task:task_approve`；
  3. 角色编码建议业务前缀（例：`DQA_C38_TaskManagement_admin`、`DQA_C38_TaskManagement_users`），用户-角色**多对多**。
- **生产部署（Linux + Nginx）**：前端打包到 `dist/`，Nginx 既 serve 静态文件也反向代理 `/api`、`/ws`、`/admin`、`/media`、`/static` 到 Django/Gunicorn/Daphne；可参考 `deploymentprepare/` 下的 `nginx.conf` 与 `*.service`。Windows 部署对应 `deploymentprepare-windows/`。

## 六、启动命令速查
- 虚拟环境（Windows）：`Myprojectvenv\Scripts\activate.ps1`
- 启动后端：`python manage.py runserver 0.0.0.0:8000`（或 Daphne 支持 WebSocket）
- 启动前端：`cd frontend && npm run dev`（Vite 5173）
- MySQL 容器：`docker compose up -d`（先确保 Docker Desktop 运行）
- Redis：Windows 本机或容器；端口 6379、密码 `DCT2019`
- 数据库迁移：`python manage.py makemigrations <App>; python manage.py migrate`
- 收集静态：`python manage.py collectstatic`（部署）
- Celery：`celery -A config worker -l INFO -P solo`；Beat：`celery -A config beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler`
