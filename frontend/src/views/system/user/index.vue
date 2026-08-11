<template>
  <div class="page-placeholder">
    <el-card>
      <el-empty description="用户管理 - 开发中">
        <template #image>
          <el-icon :size="60" color="#909399"><User /></el-icon>
        </template>
      </el-empty>
    </el-card>
  </div>
</template>

<script setup>
import { User } from '@element-plus/icons-vue'
</script>
