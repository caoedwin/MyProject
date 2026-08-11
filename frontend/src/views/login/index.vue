<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <h2>MyProject 管理系统</h2>
        <p>Python 3.14 + Django 6.1 + Vue 3</p>
      </div>

      <el-tabs v-model="activeTab" class="login-tabs">
        <el-tab-pane label="登录" name="login">
          <el-form
            ref="loginFormRef"
            :model="loginForm"
            :rules="loginRules"
            @keyup.enter="handleLogin"
          >
            <el-form-item prop="username">
              <el-input
                v-model="loginForm.username"
                placeholder="请输入用户名"
                :prefix-icon="User"
                size="large"
              />
            </el-form-item>
            <el-form-item prop="password">
              <el-input
                v-model="loginForm.password"
                type="password"
                placeholder="请输入密码"
                :prefix-icon="Lock"
                size="large"
                show-password
              />
            </el-form-item>
            <div class="login-options">
              <el-checkbox v-model="loginForm.rememberMe">记住密码</el-checkbox>
              <el-link type="primary" :underline="false" @click="activeTab = 'register'">
                没有账号？去注册
              </el-link>
            </div>
            <el-button
              type="primary"
              size="large"
              :loading="loginLoading"
              style="width: 100%; margin-top: 10px"
              @click="handleLogin"
            >
              登 录
            </el-button>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="注册" name="register">
          <el-form
            ref="registerFormRef"
            :model="registerForm"
            :rules="registerRules"
          >
            <el-form-item prop="username">
              <el-input v-model="registerForm.username" placeholder="用户名" :prefix-icon="User" size="large" />
            </el-form-item>
            <el-form-item prop="nickname">
              <el-input v-model="registerForm.nickname" placeholder="昵称" :prefix-icon="UserFilled" size="large" />
            </el-form-item>
            <el-form-item prop="password">
              <el-input v-model="registerForm.password" type="password" placeholder="密码（至少6位）" :prefix-icon="Lock" size="large" show-password />
            </el-form-item>
            <el-form-item prop="password_confirm">
              <el-input v-model="registerForm.password_confirm" type="password" placeholder="确认密码" :prefix-icon="Lock" size="large" show-password />
            </el-form-item>
            <el-form-item prop="email">
              <el-input v-model="registerForm.email" placeholder="邮箱（选填）" :prefix-icon="Message" size="large" />
            </el-form-item>
            <el-form-item prop="phone">
              <el-input v-model="registerForm.phone" placeholder="手机号（选填）" :prefix-icon="Phone" size="large" />
            </el-form-item>
            <el-button
              type="primary"
              size="large"
              :loading="registerLoading"
              style="width: 100%; margin-top: 10px"
              @click="handleRegister"
            >
              注 册
            </el-button>
            <el-link type="info" :underline="false" style="margin-top: 10px" @click="activeTab = 'login'">
              已有账号？去登录
            </el-link>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, UserFilled, Message, Phone } from '@element-plus/icons-vue'
import { useUserStore } from '@/store/user'
import { register as registerApi } from '@/api'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const activeTab = ref('login')
const loginLoading = ref(false)
const registerLoading = ref(false)
const loginFormRef = ref()
const registerFormRef = ref()

// 登录表单：用户名/密码从 localStorage 还原（记住密码场景）
const savedCredentials = JSON.parse(localStorage.getItem('saved_credentials') || 'null')
const loginForm = reactive({
  username: savedCredentials?.username || '',
  password: savedCredentials?.password || '',
  rememberMe: !!savedCredentials,
})

const loginRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

const registerForm = reactive({
  username: '',
  nickname: '',
  password: '',
  password_confirm: '',
  email: '',
  phone: '',
})

const registerRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' },
  ],
  password_confirm: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (rule, value, cb) => {
        if (value !== registerForm.password) cb(new Error('两次密码不一致'))
        else cb()
      },
      trigger: 'blur',
    },
  ],
}

// 登录
async function handleLogin() {
  await loginFormRef.value.validate()
  loginLoading.value = true
  try {
    await userStore.login(loginForm)
    // 记住密码：本地保存用户名密码（仅用于回填表单，真正的免登由 remember_token 完成）
    if (loginForm.rememberMe) {
      localStorage.setItem('saved_credentials', JSON.stringify({
        username: loginForm.username,
        password: loginForm.password,
      }))
    } else {
      localStorage.removeItem('saved_credentials')
    }
    ElMessage.success('登录成功')
    const redirect = route.query.redirect || '/'
    router.push(redirect)
  } catch (e) {
    // 错误已由拦截器处理
  } finally {
    loginLoading.value = false
  }
}

// 注册
async function handleRegister() {
  await registerFormRef.value.validate()
  registerLoading.value = true
  try {
    await registerApi(registerForm)
    ElMessage.success('注册成功，请登录')
    activeTab.value = 'login'
    loginForm.username = registerForm.username
    loginForm.password = registerForm.password
  } catch (e) {
    // 错误已由拦截器处理
  } finally {
    registerLoading.value = false
  }
}
</script>

<style scoped lang="scss">
.login-container {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-box {
  width: 420px;
  padding: 40px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
}

.login-header {
  text-align: center;
  margin-bottom: 24px;
  h2 {
    font-size: 24px;
    color: #303133;
    margin-bottom: 8px;
  }
  p {
    font-size: 12px;
    color: #909399;
  }
}

.login-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.login-tabs {
  :deep(.el-tabs__nav) {
    width: 100%;
    .el-tabs__item {
      width: 50%;
      text-align: center;
    }
  }
}
</style>
