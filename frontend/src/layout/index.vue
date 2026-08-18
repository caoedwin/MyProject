<template>
  <el-container class="layout-container">
    <!-- 左侧布局：side 菜单模式 -->
    <template v-if="appStore.menuMode === 'side'">
      <el-aside :width="appStore.menuCollapsed ? '64px' : '220px'" class="layout-aside">
        <Sidebar :collapsed="appStore.menuCollapsed" />
      </el-aside>
      <el-container>
        <el-header class="layout-header">
          <Navbar />
        </el-header>
        <el-main class="layout-main">
          <router-view v-slot="{ Component }">
            <transition name="fade" mode="out-in">
              <keep-alive>
                <component :is="Component" />
              </keep-alive>
            </transition>
          </router-view>
        </el-main>
      </el-container>
    </template>

    <!-- 顶部布局：top 菜单模式 -->
    <template v-else>
      <el-container>
        <el-header class="layout-header">
          <Navbar />
        </el-header>
        <el-container>
          <el-aside width="220px" class="layout-aside" v-if="showTopSidebar">
            <Sidebar :collapsed="false" :parent-path="activeTopMenu" />
          </el-aside>
          <el-main class="layout-main">
            <router-view v-slot="{ Component }">
              <transition name="fade" mode="out-in">
                <keep-alive>
                  <component :is="Component" />
                </keep-alive>
              </transition>
            </router-view>
          </el-main>
        </el-container>
      </el-container>
    </template>
  </el-container>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAppStore } from '@/store/app'
import { usePermissionStore } from '@/store/permission'
import Sidebar from './components/Sidebar.vue'
import Navbar from './components/Navbar.vue'

const route = useRoute()
const appStore = useAppStore()
const permissionStore = usePermissionStore()

// 顶部菜单模式下，当前激活的顶级菜单
const activeTopMenu = ref('')

const topMenus = computed(() => permissionStore.menus)

// 顶部模式下，当前顶级菜单是否有子菜单（无子菜单则隐藏侧边栏，让主区域占满）
const showTopSidebar = computed(() => {
  if (!activeTopMenu.value) return false
  const top = topMenus.value.find(m => m.path === activeTopMenu.value)
  return !!(top && top.children && top.children.length > 0)
})

// 根据当前路由计算激活的顶级菜单
watch(() => route.path, (path) => {
  if (appStore.menuMode === 'top') {
    const matched = path.split('/').filter(Boolean)
    if (matched.length > 0) {
      activeTopMenu.value = `/${matched[0]}`
    }
  }
}, { immediate: true })
</script>

<style scoped lang="scss">
.layout-container {
  height: 100vh;
}

.layout-aside {
  background: #304156;
  transition: width 0.28s;
  overflow: hidden;
}

.layout-header {
  background: var(--el-bg-color);
  border-bottom: 1px solid var(--el-border-color-lighter);
  padding: 0 15px;
  height: 50px;
  line-height: 50px;
  display: flex;
  align-items: center;
  overflow: visible;
}

.layout-main {
  padding: 16px;
  background: var(--el-bg-color-page);
  overflow-y: auto;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>

<style lang="scss">
/* 夜间模式覆盖（非 scoped，确保选择器不受 Vue 作用域影响） */
html.dark .layout-aside {
  background: #1d1e1f;
}
</style>
