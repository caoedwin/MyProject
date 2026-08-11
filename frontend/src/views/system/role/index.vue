<template>
  <div class="page-placeholder">
    <el-card>
      <el-empty description="角色管理 - 开发中">
        <template #image>
          <el-icon :size="60" color="#909399"><UserFilled /></el-icon>
        </template>
      </el-empty>
    </el-card>
  </div>
</template>

<script setup>
import { UserFilled } from '@element-plus/icons-vue'
</script>
