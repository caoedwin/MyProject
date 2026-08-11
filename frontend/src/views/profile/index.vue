<template>
  <div class="profile">
    <el-card>
      <template #header>个人中心</template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="用户名">{{ user.username }}</el-descriptions-item>
        <el-descriptions-item label="昵称">{{ user.nickname }}</el-descriptions-item>
        <el-descriptions-item label="邮箱">{{ user.email }}</el-descriptions-item>
        <el-descriptions-item label="手机号">{{ user.phone }}</el-descriptions-item>
        <el-descriptions-item label="性别">{{ user.gender == 1 ? '男' : user.gender == 2 ? '女' : '未知' }}</el-descriptions-item>
        <el-descriptions-item label="状态">{{ user.status == 1 ? '正常' : '禁用' }}</el-descriptions-item>
        <el-descriptions-item label="注册时间">{{ user.date_joined }}</el-descriptions-item>
        <el-descriptions-item label="最后登录">{{ user.last_login }}</el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useUserStore } from '@/store/user'

const userStore = useUserStore()
const user = computed(() => userStore.userInfo || {})
</script>
