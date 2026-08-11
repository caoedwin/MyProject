import { defineStore } from 'pinia'
import { ref } from 'vue'
import { RouterView } from 'vue-router'
import { getUserMenus } from '@/api'

export const usePermissionStore = defineStore('permission', () => {
  // 后端返回的菜单树（用于动态路由生成）
  const menus = ref([])
  // 已添加的动态路由
  const dynamicRoutes = ref([])
  // 是否已加载
  const loaded = ref(false)

  // 拉取菜单 + 生成路由
  async function generateRoutes() {
    const res = await getUserMenus()
    menus.value = res.data.menus || []
    const userStore = useUserStore()
    userStore.setPermissions(res.data.permissions || [])
    const routes = buildRoutes(menus.value)
    loaded.value = true
    return routes
  }

  function reset() {
    menus.value = []
    dynamicRoutes.value = []
    loaded.value = false
  }

  return { menus, dynamicRoutes, loaded, generateRoutes, reset }
})

// 把后端菜单树转换为 vue-router 路由
function buildRoutes(menus) {
  // 使用 Vite 的 import.meta.glob 静态收集所有视图组件
  const modules = import.meta.glob('@/views/**/*.vue')

  function resolveComponent(component) {
    if (!component) return RouterView  // 目录类型使用 RouterView 渲染子路由
    // component 格式如 'system/user/index' -> '/src/views/system/user/index.vue'
    const path = `/src/views/${component}.vue`
    return modules[path] || undefined
  }

  function traverse(nodes) {
    const routes = []
    for (const node of nodes) {
      const route = {
        path: node.path,
        name: node.path?.replace(/\//g, '-').slice(1) || `menu-${node.id}`,
        meta: {
          title: node.name,
          icon: node.icon,
          permission: node.permission,
          menuType: node.menu_type,
          visible: node.is_visible,
        },
      }
      if (node.component) {
        route.component = resolveComponent(node.component)
      } else if (node.children && node.children.length > 0) {
        // 目录类型：使用 RouterView 以便渲染子路由
        route.component = RouterView
      }
      // 目录类型：带 children + 重定向到第一个子节点
      if (node.children && node.children.length > 0) {
        route.children = traverse(node.children)
        if (node.redirect) {
          route.redirect = node.redirect
        } else if (route.children[0]) {
          route.redirect = route.children[0].path
        }
      }
      routes.push(route)
    }
    return routes
  }

  return traverse(menus)
}

// 在 store 内部使用其他 store
import { useUserStore } from '@/store/user'
