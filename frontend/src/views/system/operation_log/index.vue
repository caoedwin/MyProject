<template>
  <div class="page-placeholder">
    <el-card>
      <el-empty description="操作日志 - 开发中">
        <template #image>
          <el-icon :size="60" color="#909399"><Document /></el-icon>
        </template>
      </el-empty>
    </el-card>
  </div>
</template>

<script setup>
import { Document } from '@element-plus/icons-vue'
</script>
