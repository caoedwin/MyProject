<template>
  <div class="page-placeholder">
    <el-card>
      <el-empty description="菜单管理 - 开发中">
        <template #image>
          <el-icon :size="60" color="#909399"><Menu /></el-icon>
        </template>
      </el-empty>
    </el-card>
  </div>
</template>

<script setup>
import { Menu } from '@element-plus/icons-vue'
</script>
