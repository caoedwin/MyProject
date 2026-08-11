<template>
  <div class="page-placeholder">
    <el-card>
      <el-empty description="登录日志 - 开发中">
        <template #image>
          <el-icon :size="60" color="#909399"><Histogram /></el-icon>
        </template>
      </el-empty>
    </el-card>
  </div>
</template>

<script setup>
import { Histogram } from '@element-plus/icons-vue'
</script>
