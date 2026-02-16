<template>
  <div class="flex items-center justify-center min-h-screen bg-gray-100">
    <div class="w-full max-w-md p-8 bg-white rounded-lg shadow-xl">
      <div class="mb-6 text-center">
        <div class="mb-4 text-6xl">🔐</div>
        <h2 class="text-2xl font-bold text-gray-800">Změna hesla</h2>
        <p class="mt-2 text-sm text-gray-600">
          Pro pokračování je nutné změnit vaše dočasné heslo
        </p>
      </div>

      <form @submit.prevent="changePassword" class="space-y-4">
        <div>
          <label class="block mb-2 text-sm font-medium text-gray-700">
            Současné heslo
          </label>
          <input
            v-model="oldPassword"
            type="password"
            required
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Zadejte současné heslo"
          />
        </div>

        <div>
          <label class="block mb-2 text-sm font-medium text-gray-700">
            Nové heslo
          </label>
          <input
            v-model="newPassword"
            type="password"
            required
            minlength="6"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Minimálně 6 znaků"
          />
          <p class="mt-1 text-xs text-gray-500">
            Heslo musí mít alespoň 6 znaků
          </p>
        </div>

        <div>
          <label class="block mb-2 text-sm font-medium text-gray-700">
            Potvrzení nového hesla
          </label>
          <input
            v-model="confirmPassword"
            type="password"
            required
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Zadejte heslo znovu"
          />
        </div>

        <div v-if="error" class="p-3 text-sm text-red-700 bg-red-100 rounded-lg">
          {{ error }}
        </div>

        <button
          type="submit"
          :disabled="loading"
          class="w-full px-4 py-3 text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span v-if="loading">🔄 Změním heslo...</span>
          <span v-else>✅ Změnit heslo</span>
        </button>
      </form>

      <div class="mt-6 text-center">
        <button
          @click="logout"
          class="text-sm text-gray-600 hover:text-gray-800"
        >
          Odhlásit se
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const oldPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const error = ref('')
const loading = ref(false)

async function changePassword() {
  error.value = ''

  // Validace
  if (newPassword.value.length < 6) {
    error.value = 'Nové heslo musí mít alespoň 6 znaků'
    return
  }

  if (newPassword.value !== confirmPassword.value) {
    error.value = 'Hesla se neshodují'
    return
  }

  if (newPassword.value === oldPassword.value) {
    error.value = 'Nové heslo musí být odlišné od současného'
    return
  }

  loading.value = true

  try {
    await api.post('/auth/change-password', {
      old_password: oldPassword.value,
      new_password: newPassword.value,
    })

    alert('✅ Heslo bylo úspěšně změněno! Nyní budete přesměrováni.')
    
    // Přesměruj na domovskou stránku podle role
    const role = localStorage.getItem('user_role')
    if (role === 'admin') {
      router.push('/admin')
    } else if (role === 'solver') {
      router.push('/neshody')
    } else {
      router.push('/home')
    }
  } catch (err) {
    error.value = err.response?.data?.detail || 'Chyba při změně hesla'
    console.error('Error changing password:', err)
  } finally {
    loading.value = false
  }
}

function logout() {
  userStore.logout()
  router.push('/')
}
</script>