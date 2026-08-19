<template>
  <el-container class="layout-container" :key="appStore.menuMode">
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

    <!-- 顶部布局：top 菜单模式（无侧边栏，子菜单通过顶部导航下拉访问） -->
    <template v-else>
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
  </el-container>
</template>

<script setup>
import { useAppStore } from '@/store/app'
import Sidebar from './components/Sidebar.vue'
import Navbar from './components/Navbar.vue'

const appStore = useAppStore()
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
