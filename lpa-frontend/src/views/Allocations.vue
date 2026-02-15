<template>
  <div class="max-w-7xl p-6 mx-auto space-y-6">
    <!-- Hlavička -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-800">📋 Rozlosování auditů</h1>
        <p class="mt-1 text-gray-600">Přehled přidělených auditů pro vybraný měsíc</p>
      </div>
    </div>

    <!-- Výběr měsíce a akce -->
    <div class="flex items-center gap-4 p-6 bg-white rounded-lg shadow">
      <div class="flex-1">
        <label class="block mb-2 text-sm font-medium text-gray-700">Vyberte měsíc</label>
        <input
          v-model="selectedMonth"
          type="month"
          class="w-48 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        />
      </div>
      
      <div class="flex gap-3 items-end">
        <button @click="loadData" class="px-5 py-2 text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition">
          🔍 Načíst
        </button>
        
        <button 
          v-if="userRole === 'admin'"
          @click="generateAssignments" 
          class="px-5 py-2 text-white bg-green-600 rounded-lg hover:bg-green-700 transition"
        >
          🪄 Vygenerovat přidělení
        </button>
      </div>
    </div>

    <!-- Statistiky -->
    <div v-if="stats" class="grid grid-cols-2 gap-4 md:grid-cols-6">
      <div class="p-4 bg-white rounded-lg shadow">
        <div class="text-sm font-medium text-gray-500">Celkem</div>
        <div class="mt-1 text-2xl font-bold text-gray-900">{{ stats.total }}</div>
      </div>
      
      <div class="p-4 bg-green-50 rounded-lg shadow border-2 border-green-200">
        <div class="text-sm font-medium text-green-700">Splněno</div>
        <div class="mt-1 text-2xl font-bold text-green-900">{{ stats.completed }}</div>
      </div>
      
      <div class="p-4 bg-blue-50 rounded-lg shadow border-2 border-blue-200">
        <div class="text-sm font-medium text-blue-700">Probíhá</div>
        <div class="mt-1 text-2xl font-bold text-blue-900">{{ stats.in_progress }}</div>
      </div>
      
      <div class="p-4 bg-yellow-50 rounded-lg shadow border-2 border-yellow-200">
        <div class="text-sm font-medium text-yellow-700">Čeká</div>
        <div class="mt-1 text-2xl font-bold text-yellow-900">{{ stats.pending }}</div>
      </div>
      
      <div class="p-4 bg-red-50 rounded-lg shadow border-2 border-red-200">
        <div class="text-sm font-medium text-red-700">Po termínu</div>
        <div class="mt-1 text-2xl font-bold text-red-900">{{ stats.overdue }}</div>
      </div>
      
      <div class="p-4 bg-purple-50 rounded-lg shadow border-2 border-purple-200">
        <div class="text-sm font-medium text-purple-700">Splnitelnost</div>
        <div class="mt-1 text-2xl font-bold text-purple-900">{{ stats.completion_rate }}%</div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <div class="text-center">
        <div class="inline-block w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
        <p class="mt-4 text-gray-600">Načítám data...</p>
      </div>
    </div>

    <!-- Tabulka přidělení -->
    <div v-else-if="allocations.length > 0" class="bg-white rounded-lg shadow overflow-hidden">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Auditor
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Linka
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Oblast
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Termín
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Stav splnitelnosti
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Provedeno
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Akce
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr 
              v-for="allocation in allocations" 
              :key="allocation.assignment_id"
              class="hover:bg-gray-50 transition"
            >
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">{{ allocation.auditor_name }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">{{ allocation.line_name }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">{{ allocation.category_name }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">{{ formatDate(allocation.termin) }}</div>
                <div 
                  v-if="allocation.is_overdue" 
                  class="text-xs text-red-600 font-medium"
                >
                  Po termínu
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="getStatusClass(allocation.completion_status)">
                  {{ getStatusText(allocation.completion_status) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">
                  {{ allocation.datum_provedeni ? formatDate(allocation.datum_provedeni) : '-' }}
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm">
                <button
                  v-if="allocation.completion_status === 'completed'"
                  @click="viewReport(allocation.assignment_id)"
                  class="px-3 py-1 text-white bg-blue-600 rounded hover:bg-blue-700 transition"
                >
                  👁️ Zobrazit
                </button>
                <button
                  v-else-if="allocation.completion_status === 'in_progress' && canEdit(allocation)"
                  @click="continueAudit(allocation.assignment_id)"
                  class="px-3 py-1 text-white bg-yellow-600 rounded hover:bg-yellow-700 transition"
                >
                  🔁 Pokračovat
                </button>
                <button
                  v-else-if="canEdit(allocation)"
                  @click="startAudit(allocation.assignment_id)"
                  class="px-3 py-1 text-white bg-green-600 rounded hover:bg-green-700 transition"
                >
                  ▶️ Zahájit
                </button>
                <span v-else class="text-gray-400">-</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Prázdný stav -->
    <div v-else class="p-12 text-center bg-white rounded-lg shadow">
      <div class="text-6xl mb-4">📭</div>
      <h3 class="text-xl font-semibold text-gray-900 mb-2">Žádná přidělení</h3>
      <p class="text-gray-600">Pro vybraný měsíc {{ selectedMonth }} zatím nebyla vygenerována žádná přidělení.</p>
      <button 
        v-if="userRole === 'admin'"
        @click="generateAssignments" 
        class="mt-4 px-5 py-2 text-white bg-green-600 rounded-lg hover:bg-green-700 transition"
      >
        🪄 Vygenerovat přidělení pro tento měsíc
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api'

const router = useRouter()

// State
const selectedMonth = ref(new Date().toISOString().slice(0, 7))
const allocations = ref([])
const stats = ref(null)
const loading = ref(false)
const userRole = ref(localStorage.getItem('user_role') || 'auditor')
const currentUserId = ref(parseInt(localStorage.getItem('user_id') || '0'))

// Computed
const canEdit = computed(() => {
  return (allocation) => {
    // Admin může editovat vše, auditor jen své přidělení
    return userRole.value === 'admin' || allocation.auditor_id === currentUserId.value
  }
})

// Methods
async function loadData() {
  loading.value = true
  try {
    const response = await api.get(`/assignments/allocations/by-month/${selectedMonth.value}`)
    allocations.value = response.data.allocations
    stats.value = response.data.stats
  } catch (error) {
    console.error('Chyba při načítání dat:', error)
    alert('Nepodařilo se načíst data rozlosování')
    allocations.value = []
    stats.value = null
  } finally {
    loading.value = false
  }
}

async function generateAssignments() {
  if (!confirm(`Opravdu chcete vygenerovat nová přidělení pro měsíc ${selectedMonth.value}?`)) {
    return
  }
  
  try {
    await api.post(`/campaigns/${selectedMonth.value}/generate-assignments`)
    alert('Přidělení byla úspěšně vygenerována!')
    await loadData()
  } catch (error) {
    console.error('Chyba při generování:', error)
    alert(error.response?.data?.detail || 'Nepodařilo se vygenerovat přidělení')
  }
}

function getStatusClass(completionStatus) {
  const classes = {
    completed: 'px-3 py-1 text-xs font-semibold text-green-800 bg-green-100 rounded-full',
    in_progress: 'px-3 py-1 text-xs font-semibold text-blue-800 bg-blue-100 rounded-full',
    pending: 'px-3 py-1 text-xs font-semibold text-yellow-800 bg-yellow-100 rounded-full',
    overdue: 'px-3 py-1 text-xs font-semibold text-red-800 bg-red-100 rounded-full'
  }
  return classes[completionStatus] || classes.pending
}

function getStatusText(completionStatus) {
  const texts = {
    completed: '✅ Splněno',
    in_progress: '🔄 Probíhá',
    pending: '⏳ Čeká',
    overdue: '⚠️ Po termínu'
  }
  return texts[completionStatus] || 'Neznámý'
}

function formatDate(dateString) {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleDateString('cs-CZ')
}

function startAudit(assignmentId) {
  router.push({ path: '/audit', query: { assignment_id: assignmentId } })
}

function continueAudit(assignmentId) {
  router.push({ path: '/audit', query: { assignment_id: assignmentId } })
}

function viewReport(assignmentId) {
  router.push({ path: '/audit-report', query: { assignment_id: assignmentId } })
}

// Lifecycle
onMounted(() => {
  loadData()
})
</script>