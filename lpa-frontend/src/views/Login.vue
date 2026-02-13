<template>
  <div class="flex items-center justify-center min-h-screen bg-gray-100">
    <div class="w-full max-w-md p-8 bg-white shadow-lg rounded-xl">
      <h2 class="mb-2 text-2xl font-bold text-center">LPA v2</h2>
      <p class="mb-6 text-center text-gray-500">Přihlášení do systému</p>

      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700">Email</label>
          <input
            v-model="email"
            type="email"
            placeholder="vas@email.cz"
            @keyup.enter="login"
            class="w-full p-2 mt-1 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700">Heslo</label>
          <input
            v-model="password"
            type="password"
            placeholder="••••••••"
            @keyup.enter="login"
            class="w-full p-2 mt-1 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
          />
        </div>

        <button
          @click="login"
          :disabled="loading"
          class="w-full py-2 font-semibold text-white transition bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {{ loading ? 'Přihlašování...' : 'Přihlásit se' }}
        </button>

        <p v-if="error" class="mt-3 text-sm text-center text-red-600">
          {{ error }}
        </p>
      </div>

      <!-- Info o výchozích účtech -->
      <div class="p-4 mt-6 rounded-lg bg-blue-50">
        <p class="mb-2 text-xs text-gray-600">
          <strong>Výchozí přihlašovací údaje:</strong>
        </p>
        <p class="text-xs text-gray-600">
          Email: admin@lpa.local<br>
          Heslo: admin
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import api from "@/api"

const router = useRouter()
const userStore = useUserStore()

const email = ref("")
const password = ref("")
const error = ref(null)
const loading = ref(false)

const login = async () => {
  error.value = null
  loading.value = true

  try {
    const form = new URLSearchParams()
    form.append("username", email.value)
    form.append("password", password.value)

    const res = await api.post("/token", form)
    
    localStorage.setItem("access_token", res.data.access_token)
    
    // Načti informace o uživateli
    await userStore.fetchUser()
    
    // Přesměruj na dashboard
    router.push("/dashboard")
  } catch (e) {
    error.value = "Neplatné přihlašovací údaje"
    console.error('Login error:', e)
  } finally {
    loading.value = false
  }
}
</script>
