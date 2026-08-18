<template>
  <!-- 渲染单个菜单项：含子菜单则用 sub-menu，否则用 menu-item -->
  <el-sub-menu
    v-if="item.children && item.children.length > 0"
    :index="resolvePath(item.path) || String(item.id)"
  >
    <template #title>
      <el-icon v-if="item.icon"><component :is="item.icon" /></el-icon>
      <span>{{ item.name }}</span>
    </template>
    <SidebarItem
      v-for="child in item.children"
      :key="child.path || child.id"
      :item="child"
      :base-path="resolvePath(item.path)"
    />
  </el-sub-menu>

  <!-- 外链：用 a 标签新窗口打开 -->
  <a
    v-else-if="item.is_external"
    :href="resolvePath(item.path)"
    target="_blank"
    rel="noopener"
    class="el-menu-item external-link"
  >
    <el-icon v-if="item.icon"><component :is="item.icon" /></el-icon>
    <span>{{ item.name }}</span>
  </a>

  <el-menu-item v-else :index="resolvePath(item.path)">
    <el-icon v-if="item.icon"><component :is="item.icon" /></el-icon>
    <template #title>{{ item.name }}</template>
  </el-menu-item>
</template>

<script setup>
import { defineProps } from 'vue'

const props = defineProps({
  item: { type: Object, required: true },
  basePath: { type: String, default: '' },
})

function resolvePath(routePath) {
  if (!routePath) return ''
  if (/^https?:\/\//.test(routePath)) return routePath
  // 绝对路径直接返回，不与 basePath 拼接
  if (routePath.startsWith('/')) return routePath
  // 相对路径与 basePath 拼接
  if (props.basePath.endsWith('/')) {
    return props.basePath + routePath
  }
  return props.basePath + '/' + routePath
}
</script>

<style scoped lang="scss">
.external-link {
  display: flex;
  align-items: center;
  height: 56px;
  line-height: 56px;
  font-size: 14px;
  color: #bfcbd9;
  padding: 0 20px;
  list-style: none;
  cursor: pointer;
  position: relative;
  transition: border-color .3s, background-color .3s, color .3s;
  box-sizing: border-box;
  white-space: nowrap;
  text-decoration: none;

  * {
    vertical-align: middle;
  }

  &:hover {
    background-color: #263445;
  }

  .el-icon {
    margin-right: 5px;
    width: 24px;
    text-align: center;
    font-size: 18px;
  }

  span {
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
  }
}
</style>
