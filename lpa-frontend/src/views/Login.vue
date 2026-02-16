<template>
  <div class="flex items-center justify-center min-h-screen bg-linear-to-br from-blue-50 to-blue-100">
    <div class="w-full max-w-md p-8 bg-white rounded-lg shadow-xl">
      <div class="mb-8 text-center">
        <div class="mb-4 text-6xl">🏭</div>
        <h1 class="text-3xl font-bold text-gray-800">LPA Systém</h1>
        <p class="text-gray-600">Přihlášení do systému</p>
      </div>

      <form @submit.prevent="login" class="space-y-6">
        <div>
          <label class="block mb-2 text-sm font-medium text-gray-700">
            Email
          </label>
          <input
            v-model="email"
            type="email"
            required
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="vas.email@firma.cz"
          />
        </div>

        <div>
          <label class="block mb-2 text-sm font-medium text-gray-700">
            Heslo
          </label>
          <input
            v-model="password"
            type="password"
            required
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="••••••••"
          />
        </div>

        <div v-if="error" class="p-3 text-sm text-red-700 bg-red-100 rounded-lg">
          {{ error }}
        </div>

        <button
          type="submit"
          :disabled="loading"
          class="w-full px-4 py-3 text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed font-medium"
        >
          <span v-if="loading">🔄 Přihlašuji...</span>
          <span v-else>🔓 Přihlásit se</span>
        </button>
      </form>

      <div class="mt-6 text-center text-sm text-gray-600">
        <p>Máte potíže s přihlášením?</p>
        <p class="mt-1">Kontaktujte administrátora systému</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function login() {
  error.value = ''
  loading.value = true

  try {
    const formData = new FormData()
    formData.append('username', email.value)
    formData.append('password', password.value)

    const response = await fetch('http://localhost:8000/auth/token', {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
      throw new Error('Nesprávný email nebo heslo')
    }

    const data = await response.json()

    // Ulož token a uživatelská data
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('user_id', data.user.id)
    localStorage.setItem('user_name', data.user.jmeno)
    localStorage.setItem('user_email', data.user.email)
    localStorage.setItem('user_role', data.user.role)
    localStorage.setItem('user_roles', JSON.stringify(data.user.roles))

    userStore.login(data.user)

    // ⚠️ KONTROLA FORCE PASSWORD CHANGE
    if (data.force_password_change) {
      // Přesměruj na stránku pro změnu hesla
      router.push('/change-password')
      return
    }

    // Normální přesměrování podle role
    if (data.user.roles.includes('admin')) {
      router.push('/admin')
    } else if (data.user.roles.includes('solver')) {
      router.push('/neshody')
    } else {
      router.push('/home')
    }
  } catch (err) {
    error.value = err.message || 'Chyba při přihlašování'
    console.error('Login error:', err)
  } finally {
    loading.value = false
  }
}
</script>