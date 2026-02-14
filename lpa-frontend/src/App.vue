<template>
  <div class="flex h-screen bg-gray-100">
    <!-- Boční menu -->
    <aside v-if="userStore.isAuthenticated" class="flex flex-col w-64 p-5 text-white bg-gray-900">
      <h2 class="mb-6 text-xl font-bold">LPA AUDITY</h2>

      <nav class="flex-1 space-y-2">
        <router-link
          to="/dashboard"
          class="block px-3 py-2 rounded hover:bg-blue-600"
          active-class="bg-blue-600"
        >
          📊 Hlavní stránka
        </router-link>

        <router-link
          to="/nok-audits"
          class="block px-3 py-2 rounded hover:bg-red-600"
          active-class="bg-red-600"
        >
          🚨 NOK Audity
        </router-link>

        <router-link
          to="/issues"
          class="block px-3 py-2 rounded hover:bg-blue-600"
          active-class="bg-blue-600"
        >
          📑 Audity
        </router-link>

        <router-link
          to="/allocations"
          class="block px-3 py-2 rounded hover:bg-blue-600"
          active-class="bg-blue-600"
        >
          📋 Rozlosování
        </router-link>

        <router-link
          v-if="userStore.userRole === 'admin'"
          to="/admin"
          class="block px-3 py-2 rounded hover:bg-blue-600"
          active-class="bg-blue-600"
        >
          🔧 Administrace
        </router-link>

        <router-link
          to="/audit"
          class="block px-3 py-2 rounded hover:bg-blue-600"
          active-class="bg-blue-600"
        >
          📝 Provést audit
        </router-link>
      </nav>

      <!-- Info uživatele -->
      <div class="pt-4 mt-4 border-t border-gray-700">
        <div class="px-3 py-2 mb-2 text-sm">
          <div class="flex items-center gap-2 mb-1">
            <span class="text-gray-400">👤</span>
            <span class="font-semibold">{{ userStore.userName }}</span>
          </div>
          <div class="text-xs text-gray-400">{{ userStore.userEmail }}</div>
          <div class="mt-1">
            <span 
              class="px-2 py-1 text-xs rounded"
              :class="getRoleBadgeClass(userStore.userRole)"
            >
              {{ getRoleLabel(userStore.userRole) }}
            </span>
          </div>
        </div>
      </div>

      <button
        @click="handleLogout"
        class="px-3 py-2 mt-2 text-white bg-red-600 rounded hover:bg-red-700"
      >
        Odhlásit
      </button>
    </aside>

    <!-- OBSAH -->
    <main class="flex-1 p-6 overflow-auto">
      <header 
        v-if="userStore.isAuthenticated" 
        class="flex items-center justify-between p-4 mb-6 bg-white rounded-lg shadow"
      >
        <span class="font-semibold">
          Vítej, {{ userStore.userName }}! 👋
        </span>
        <div class="text-sm text-gray-500">
          {{ currentDateTime }}
        </div>
      </header>

      <router-view />
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useAutoLogout } from '@/composables/useAutoLogout'

const router = useRouter()
const userStore = useUserStore()
const currentDateTime = ref('')

// Auto-odlhášeni
useAutoLogout(30)

// Aktualizace času
const updateDateTime = () => {
  const now = new Date()
  currentDateTime.value = now.toLocaleString('cs-CZ', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

let intervalId = null

onMounted(() => {
  updateDateTime()
  intervalId = setInterval(updateDateTime, 60000) // Aktualizace každou minutu
})

onUnmounted(() => {
  if (intervalId) {
    clearInterval(intervalId)
  }
})

const handleLogout = () => {
  userStore.logout()
  router.push('/')
}

const getRoleBadgeClass = (role) => {
  const classes = {
    'admin': 'bg-purple-200 text-purple-800',
    'auditor': 'bg-blue-200 text-blue-800',
    'solver': 'bg-green-200 text-green-800'
  }
  return classes[role] || 'bg-gray-200 text-gray-800'
}

const getRoleLabel = (role) => {
  const labels = {
    'admin': 'Administrátor',
    'auditor': 'Auditor',
    'solver': 'Řešitel'
  }
  return labels[role] || role
}
</script>