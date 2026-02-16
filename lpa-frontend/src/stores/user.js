import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import api from '@/api'

export const useUserStore = defineStore('user', () => {
  const user = ref(null)
  const loading = ref(false)
  const error = ref(null)

  const isAuthenticated = computed(() => !!user.value)
  const userName = computed(() => user.value?.jmeno || '')
  const userEmail = computed(() => user.value?.email || '')
  const userRole = computed(() => user.value?.role || '')

  // ✅ NOVÁ METODA: login
  function login(userData) {
    user.value = userData
  }

  async function fetchUser() {
    loading.value = true
    error.value = null
    try {
      const response = await api.get('/auth/me')
      user.value = response.data
    } catch (err) {
      error.value = err.message
      user.value = null
      // Pokud token není validní, odstraň ho
      if (err.response?.status === 401) {
        localStorage.removeItem('access_token')
        localStorage.removeItem('user_id')
        localStorage.removeItem('user_name')
        localStorage.removeItem('user_email')
        localStorage.removeItem('user_role')
        localStorage.removeItem('user_roles')
      }
    } finally {
      loading.value = false
    }
  }

  function logout() {
    user.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('user_id')
    localStorage.removeItem('user_name')
    localStorage.removeItem('user_email')
    localStorage.removeItem('user_role')
    localStorage.removeItem('user_roles')
  }

  return {
    user,
    loading,
    error,
    isAuthenticated,
    userName,
    userEmail,
    userRole,
    login,
    fetchUser,
    logout
  }
})