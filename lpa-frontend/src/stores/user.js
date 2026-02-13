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

  async function fetchUser() {
    loading.value = true
    error.value = null
    try {
      const response = await api.get('/me')
      user.value = response.data
    } catch (err) {
      error.value = err.message
      user.value = null
      // Pokud token není validní, odstraň ho
      if (err.response?.status === 401) {
        localStorage.removeItem('access_token')
      }
    } finally {
      loading.value = false
    }
  }

  function logout() {
    user.value = null
    localStorage.removeItem('access_token')
  }

  return {
    user,
    loading,
    error,
    isAuthenticated,
    userName,
    userEmail,
    userRole,
    fetchUser,
    logout
  }
})
