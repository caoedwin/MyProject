import { useUserStore } from '@/store/user'

/**
 * 权限指令
 * 用法：
 *   v-permission="'system:user_add'"           // 单个权限
 *   v-permission="['system:user_add', 'system:user_edit']"  // 任一权限
 */
export const permissionDirective = {
  mounted(el, binding) {
    const userStore = useUserStore()
    const { value } = binding
    if (!value) return

    const required = Array.isArray(value) ? value : [value]
    const hasAny = required.some(perm => userStore.hasPermission(perm))

    if (!hasAny) {
      el.parentNode && el.parentNode.removeChild(el)
    }
  },
}
