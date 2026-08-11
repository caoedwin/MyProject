import { defineStore } from 'pinia'
import { ref } from 'vue'

// 应用全局设置（菜单布局 / 收起状态 / 主题等）
export const useAppStore = defineStore('app', () => {
  // 菜单布局：side=左侧 / top=顶部
  const menuMode = ref(localStorage.getItem('menu_mode') || 'side')
  // 菜单是否收起
  const menuCollapsed = ref(localStorage.getItem('menu_collapsed') === 'true')

  function setMenuMode(mode) {
    menuMode.value = mode
    localStorage.setItem('menu_mode', mode)
  }

  function toggleCollapse() {
    menuCollapsed.value = !menuCollapsed.value
    localStorage.setItem('menu_collapsed', String(menuCollapsed.value))
  }

  function setCollapsed(val) {
    menuCollapsed.value = val
    localStorage.setItem('menu_collapsed', String(val))
  }

  return { menuMode, menuCollapsed, setMenuMode, toggleCollapse, setCollapsed }
})
