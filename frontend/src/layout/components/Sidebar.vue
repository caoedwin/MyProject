<template>
  <div class="sidebar">
    <div class="logo">
      <img v-if="!collapsed" src="@/assets/logo.svg" alt="logo" />
      <span v-if="!collapsed" class="logo-text">MyProject</span>
      <img v-else src="@/assets/logo.svg" alt="logo" class="logo-mini" />
    </div>
    <el-scrollbar>
      <el-menu
        :default-active="activeMenu"
        :collapse="collapsed"
        :collapse-transition="false"
        :background-color="menuBgColor"
        :text-color="menuTextColor"
        active-text-color="#409EFF"
        :unique-opened="true"
        router
      >
        <template v-for="item in menuItems" :key="item.path || item.id">
          <SidebarItem :item="item" :base-path="parentPath" />
        </template>
      </el-menu>
    </el-scrollbar>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { usePermissionStore } from '@/store/permission'
import { useAppStore } from '@/store/app'
import SidebarItem from './SidebarItem.vue'

const props = defineProps({
  collapsed: { type: Boolean, default: false },
  parentPath: { type: String, default: '' },
})

const route = useRoute()
const permissionStore = usePermissionStore()
const appStore = useAppStore()

const activeMenu = computed(() => route.path)

// 菜单颜色随主题切换
const menuBgColor = computed(() => appStore.isDark ? '#1d1e1f' : '#304156')
const menuTextColor = computed(() => appStore.isDark ? '#a3a6ad' : '#bfcbd9')

const menuItems = computed(() => {
  if (props.parentPath) {
    // 顶部模式下，只显示当前顶级菜单的子菜单
    const top = permissionStore.menus.find(m => m.path === props.parentPath)
    return top?.children || []
  }
  return permissionStore.menus
})
</script>

<style scoped lang="scss">
.sidebar {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.logo {
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #2b3a4d;
  color: #fff;
  img {
    width: 28px;
    height: 28px;
  }
  .logo-text {
    margin-left: 10px;
    font-size: 16px;
    font-weight: 600;
    white-space: nowrap;
  }
  .logo-mini {
    width: 28px;
    height: 28px;
  }
}

:deep(.el-menu) {
  border-right: none;
}
</style>

<style lang="scss">
/* 夜间模式覆盖（非 scoped） */
html.dark .logo {
  background: #141414;
}
</style>
