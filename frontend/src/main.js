import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

import App from './App.vue'
import router from './router'
import './router/permission'  // 路由守卫
import './styles/index.scss'
import { permissionDirective } from './directives/permission'
import { createWebSocket, closeWebSocket } from './utils/websocket'

const app = createApp(App)

// 注册所有 Element Plus 图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(createPinia())
app.use(router)
app.use(ElementPlus, { locale: zhCn })

// 自定义权限指令 v-permission="'system:user_add'"
app.directive('permission', permissionDirective)

app.mount('#app')
