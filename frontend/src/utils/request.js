import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import NProgress from 'nprogress'
import 'nprogress/nprogress.css'
import { useUserStore } from '@/store/user'
import router from '@/router'

NProgress.configure({ showSpinner: false })

const service = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

// 请求拦截器
service.interceptors.request.use(
  (config) => {
    NProgress.start()
    const userStore = useUserStore()
    if (userStore.token) {
      config.headers['Authorization'] = `Bearer ${userStore.token}`
    }
    return config
  },
  (error) => {
    NProgress.done()
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  (response) => {
    NProgress.done()
    const res = response.data
    // 文件下载直接返回
    if (response.config.responseType === 'blob') {
      return response
    }
    // 标准响应：{code, msg, success, data}
    if (res.code === 200 || res.success === true) {
      return res
    }
    // 401 未登录 / token 过期
    if (res.code === 401) {
      ElMessage.error(res.msg || '登录已过期')
      const userStore = useUserStore()
      userStore.logout()
      router.push('/login')
      return Promise.reject(new Error(res.msg || 'Unauthorized'))
    }
    // 403 无权限
    if (res.code === 403) {
      ElMessage.error(res.msg || '没有访问权限')
      return Promise.reject(new Error(res.msg || 'Forbidden'))
    }
    // 其他业务错误
    ElMessage.error(res.msg || '请求失败')
    return Promise.reject(new Error(res.msg || 'Error'))
  },
  (error) => {
    NProgress.done()
    let message = error.message || '网络异常'
    if (error.response) {
      const status = error.response.status
      if (status === 401) {
        message = '登录已过期，请重新登录'
        const userStore = useUserStore()
        userStore.logout()
        router.push('/login')
      } else if (status === 403) {
        message = '没有访问权限'
      } else if (status === 500) {
        message = '服务器内部错误'
      }
    }
    ElMessage.error(message)
    return Promise.reject(error)
  }
)

export default service
