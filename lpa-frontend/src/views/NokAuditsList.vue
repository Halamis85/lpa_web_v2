<template>
  <div class="space-y-6">
    <!-- Hlavička -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-800">NOK Audity</h1>
        <p class="mt-1 text-gray-600">Správa a přehled neshod</p>
      </div>
      <button
        @click="exportData"
        class="flex items-center gap-2 px-4 py-2 text-white transition bg-green-600 rounded-lg hover:bg-green-700"
      >
        <span>📥</span>
        <span>Export do Excel</span>
      </button>
    </div>

    <!-- Statistiky -->
    <NokStatsCards :stats="stats" />

    <!-- Filtry -->
    <NokFilters
      v-model:filters="filters"
      :lines="lines"
      :categories="categories"
      :solvers="solvers"
      @reset="handleResetFilters"
    />

    <!-- Tabulka -->
    <div class="overflow-hidden bg-white rounded-lg shadow">
      <div class="px-6 py-4 bg-gray-50">
        <p class="text-sm text-gray-600">
          Zobrazeno <span class="font-semibold">{{ paginatedAudits.length }}</span> 
          z <span class="font-semibold">{{ filteredAudits.length }}</span> záznamů
        </p>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="flex items-center justify-center py-20">
        <div class="w-12 h-12 border-4 border-blue-500 rounded-full border-t-transparent animate-spin"></div>
      </div>

      <!-- Tabulka -->
      <div v-else-if="filteredAudits.length > 0" class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-linear-to-r from-blue-600 to-blue-700">
            <tr>
              <th
                v-for="column in columns"
                :key="column.key"
                @click="column.sortable && sortBy(column.key)"
                :class="[
                  'px-6 py-4 text-left text-xs font-medium text-white uppercase tracking-wider',
                  column.sortable ? 'cursor-pointer hover:bg-blue-500' : ''
                ]"
              >
                <div class="flex items-center gap-2">
                  <span>{{ column.label }}</span>
                  <span v-if="column.sortable" class="text-xs opacity-70">
                    {{ getSortIcon(column.key) }}
                  </span>
                </div>
              </th>
              <th class="px-6 py-4 text-left text-xs font-medium text-white uppercase tracking-wider">
                Akce
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr
              v-for="audit in paginatedAudits"
              :key="audit.id"
              :class="[
                'transition hover:bg-gray-50 cursor-pointer',
                getOverdueClass(audit.termin, audit.neshoda_status)
              ]"
              @click="handleRowClick(audit)"
            >
              <td class="px-6 py-4 text-sm font-medium text-blue-600 whitespace-nowrap">
                #{{ audit.id }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <img
                  v-if="audit.picture_url"
                  :src="getImageUrl(audit.picture_url)"
                  alt="NOK"
                  class="object-cover w-16 h-12 rounded cursor-pointer hover:scale-110 transition"
                  @click.stop="openImageModal(audit.picture_url)"
                />
                <span v-else class="text-2xl text-gray-400">📷</span>
              </td>
              <td class="px-6 py-4 text-sm text-gray-900">
                {{ truncate(audit.question_text, 80) }}
              </td>
              <td class="px-6 py-4 text-sm text-gray-900 whitespace-nowrap">
                {{ audit.line_name }}
              </td>
              <td class="px-6 py-4 text-sm text-gray-900 whitespace-nowrap">
                {{ audit.category_name }}
              </td>
              <td class="px-6 py-4 text-sm text-gray-900 whitespace-nowrap">
                {{ audit.auditor_name }}
              </td>
              <td class="px-6 py-4 text-sm text-gray-900 whitespace-nowrap">
                {{ formatDate(audit.execution_date) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span
                  :class="['px-3 py-1 text-xs font-medium rounded-full', getStatusBadgeClass(audit.neshoda_status)]"
                >
                  {{ getStatusText(audit.neshoda_status) }}
                </span>
              </td>
              <td class="px-6 py-4 text-sm text-gray-900 whitespace-nowrap">
                <span v-if="audit.solver_id">
                  {{ getSolverName(audit.solver_id) }}
                </span>
                <span v-else class="text-gray-400 italic">Nepřiřazeno</span>
              </td>
              <td class="px-6 py-4 text-sm whitespace-nowrap">
                <span
                  v-if="audit.termin"
                  :class="[
                    'font-medium',
                    isOverdue(audit.termin, audit.neshoda_status) ? 'text-red-600' : 'text-gray-900'
                  ]"
                >
                  {{ formatDate(audit.termin) }}
                  <span v-if="isOverdue(audit.termin, audit.neshoda_status)" class="block text-xs text-red-500">
                    ⚠️ PO TERMÍNU
                  </span>
                </span>
                <span v-else class="text-gray-400">-</span>
              </td>
              <td class="px-6 py-4 text-sm whitespace-nowrap" @click.stop>
                <div class="flex gap-2">
                  <button
                    v-if="canAssignSolver && !audit.solver_id"
                    @click="openAssignDialog(audit)"
                    class="p-2 text-blue-600 transition hover:bg-blue-100 rounded"
                    title="Přiřadit řešitele"
                  >
                    👤
                  </button>
                  <button
                    @click="handleRowClick(audit)"
                    class="p-2 text-gray-600 transition hover:bg-gray-100 rounded"
                    title="Detail"
                  >
                    👁️
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Empty state -->
      <div v-else class="py-20 text-center text-gray-500">
        <div class="mb-4 text-6xl">📭</div>
        <h3 class="mb-2 text-xl font-semibold text-gray-700">Žádné NOK audity</h3>
        <p v-if="hasActiveFilters">Zkuste upravit filtry nebo je resetovat.</p>
        <p v-else>Zatím nebyly nalezeny žádné neshody.</p>
      </div>

      <!-- Pagination -->
      <div v-if="filteredAudits.length > 0" class="flex items-center justify-between px-6 py-4 bg-gray-50">
        <div class="flex items-center gap-4">
          <select
            v-model.number="itemsPerPage"
            @change="currentPage = 1"
            class="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option :value="10">10 / stránka</option>
            <option :value="25">25 / stránka</option>
            <option :value="50">50 / stránka</option>
            <option :value="100">100 / stránka</option>
          </select>
        </div>

        <div class="flex items-center gap-2">
          <button
            @click="currentPage = 1"
            :disabled="currentPage === 1"
            class="px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            ⏮️
          </button>
          <button
            @click="currentPage--"
            :disabled="currentPage === 1"
            class="px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            ◀️
          </button>
          <span class="px-4 py-2 text-sm text-gray-700">
            Stránka {{ currentPage }} z {{ totalPages }}
          </span>
          <button
            @click="currentPage++"
            :disabled="currentPage === totalPages"
            class="px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            ▶️
          </button>
          <button
            @click="currentPage = totalPages"
            :disabled="currentPage === totalPages"
            class="px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            ⏭️
          </button>
        </div>
      </div>
    </div>

    <!-- Modal pro přiřazení řešitele -->
    <div
      v-if="showAssignDialog"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50"
      @click="closeAssignDialog"
    >
      <div
        class="w-full max-w-md p-6 bg-white rounded-lg shadow-xl"
        @click.stop
      >
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-xl font-semibold text-gray-800">👤 Přiřadit řešitele</h3>
          <button
            @click="closeAssignDialog"
            class="text-2xl text-gray-400 hover:text-gray-600"
          >
            ✕
          </button>
        </div>

        <div class="space-y-4">
          <div>
            <label class="block mb-2 text-sm font-medium text-gray-700">Řešitel *</label>
            <select
              v-model="assignForm.solver_id"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option :value="null">-- Vyberte řešitele --</option>
              <option v-for="solver in solvers" :key="solver.id" :value="solver.id">
                {{ solver.jmeno }} ({{ solver.email }})
              </option>
            </select>
          </div>

          <div>
            <label class="block mb-2 text-sm font-medium text-gray-700">Termín odstranění *</label>
            <input
              type="date"
              v-model="assignForm.termin"
              :min="today"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label class="block mb-2 text-sm font-medium text-gray-700">Poznámka</label>
            <textarea
              v-model="assignForm.poznamka"
              rows="4"
              placeholder="Poznámky k řešení..."
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            ></textarea>
          </div>

          <div class="flex justify-end gap-3">
            <button
              @click="closeAssignDialog"
              class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-lg hover:bg-gray-200"
            >
              Zrušit
            </button>
            <button
              @click="submitAssignment"
              :disabled="!assignForm.solver_id || !assignForm.termin || submitting"
              class="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {{ submitting ? 'Přiřazuji...' : 'Přiřadit' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal pro zobrazení fotky -->
    <div
      v-if="showImageModal"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-75"
      @click="closeImageModal"
    >
      <div class="relative max-w-4xl max-h-screen p-4" @click.stop>
        <button
          @click="closeImageModal"
          class="absolute top-2 right-2 p-2 text-white bg-black bg-opacity-50 rounded-full hover:bg-opacity-75"
        >
          ✕
        </button>
        <img
          :src="getImageUrl(selectedImage)"
          alt="NOK"
          class="max-w-full max-h-screen rounded-lg"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useNokAuditsStore } from '@/stores/nokAudits'
import { useNokAuditHelpers } from '@/composables/useNokAuditHelpers'
import NokStatsCards from '@/components/NokStatsCards.vue'
import NokFilters from '@/components/NokFilters.vue'

const router = useRouter()
const userStore = useUserStore()
const store = useNokAuditsStore()
const {
  formatDate,
  getStatusText,
  getStatusBadgeClass,
  isOverdue,
  getOverdueClass,
  truncate,
  getImageUrl,
  exportToCSV,
} = useNokAuditHelpers()

// State
const filters = ref({
  line_id: null,
  category_id: null,
  status: null,
  solver_id: null,
  date_from: null,
  date_to: null,
  search: '',
})

const currentPage = ref(1)
const itemsPerPage = ref(25)
const sortColumn = ref('execution_date')
const sortDirection = ref('desc')

const showAssignDialog = ref(false)
const selectedAudit = ref(null)
const assignForm = ref({
  solver_id: null,
  termin: null,
  poznamka: null,
})
const submitting = ref(false)

const showImageModal = ref(false)
const selectedImage = ref(null)

const columns = [
  { key: 'id', label: 'ID', sortable: true },
  { key: 'picture_url', label: 'Fotka', sortable: false },
  { key: 'question_text', label: 'Otázka', sortable: true },
  { key: 'line_name', label: 'Linka', sortable: true },
  { key: 'category_name', label: 'Kategorie', sortable: true },
  { key: 'auditor_name', label: 'Auditor', sortable: true },
  { key: 'execution_date', label: 'Datum', sortable: true },
  { key: 'neshoda_status', label: 'Stav', sortable: true },
  { key: 'solver_id', label: 'Řešitel', sortable: false },
  { key: 'termin', label: 'Termín', sortable: true },
]

// Computed
const loading = computed(() => store.loading)
const stats = computed(() => store.stats)
const lines = computed(() => store.lines)
const categories = computed(() => store.categories)
const solvers = computed(() => store.solvers)

const canAssignSolver = computed(() => {
  return userStore.userRole === 'admin' || userStore.userRole === 'auditor'
})

const today = computed(() => {
  return new Date().toISOString().split('T')[0]
})

const filteredAudits = computed(() => {
  let result = [...store.audits]

  // Aplikuj filtry
  if (filters.value.status) {
    result = result.filter(a => a.neshoda_status === filters.value.status)
  }

  if (filters.value.solver_id) {
    result = result.filter(a => a.solver_id === filters.value.solver_id)
  }

  if (filters.value.search) {
    const search = filters.value.search.toLowerCase()
    result = result.filter(a =>
      a.question_text.toLowerCase().includes(search) ||
      a.neshoda_popis?.toLowerCase().includes(search)
    )
  }

  // Sorting
  result.sort((a, b) => {
    let aVal = a[sortColumn.value]
    let bVal = b[sortColumn.value]

    if (aVal === null || aVal === undefined) return sortDirection.value === 'asc' ? 1 : -1
    if (bVal === null || bVal === undefined) return sortDirection.value === 'asc' ? -1 : 1

    if (typeof aVal === 'string') {
      aVal = aVal.toLowerCase()
      bVal = bVal.toLowerCase()
    }

    if (aVal < bVal) return sortDirection.value === 'asc' ? -1 : 1
    if (aVal > bVal) return sortDirection.value === 'asc' ? 1 : -1
    return 0
  })

  return result
})

const paginatedAudits = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value
  const end = start + itemsPerPage.value
  return filteredAudits.value.slice(start, end)
})

const totalPages = computed(() => {
  return Math.ceil(filteredAudits.value.length / itemsPerPage.value)
})

const hasActiveFilters = computed(() => {
  return Object.values(filters.value).some(v => v !== null && v !== '')
})

// Methods
function sortBy(column) {
  if (sortColumn.value === column) {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortColumn.value = column
    sortDirection.value = 'asc'
  }
}

function getSortIcon(column) {
  if (sortColumn.value !== column) return '⇅'
  return sortDirection.value === 'asc' ? '▲' : '▼'
}

function handleRowClick(audit) {
  router.push(`/nok-audits/${audit.id}`)
}

function handleResetFilters() {
  currentPage.value = 1
  store.fetchAudits()
}

function openAssignDialog(audit) {
  selectedAudit.value = audit
  assignForm.value = {
    solver_id: audit.solver_id || null,
    termin: audit.termin || null,
    poznamka: audit.neshoda_popis || null,
  }
  showAssignDialog.value = true
}

function closeAssignDialog() {
  showAssignDialog.value = false
  selectedAudit.value = null
}

async function submitAssignment() {
  if (!assignForm.value.solver_id) {
    alert('Musíte vybrat řešitele')
    return
  }

  submitting.value = true
  const result = await store.assignSolver(
    selectedAudit.value.neshoda_id,
    assignForm.value
  )

  if (result.success) {
    alert('✅ Řešitel byl úspěšně přiřazen')
    closeAssignDialog()
  } else {
    alert('❌ Nepodařilo se přiřadit řešitele')
  }

  submitting.value = false
}

function openImageModal(imageUrl) {
  selectedImage.value = imageUrl
  showImageModal.value = true
}

function closeImageModal() {
  showImageModal.value = false
  selectedImage.value = null
}

function getSolverName(solverId) {
  return store.getSolverName(solverId)
}

function exportData() {
  const exportData = filteredAudits.value.map(audit => ({
    'ID': audit.id,
    'Otázka': audit.question_text,
    'Linka': audit.line_name,
    'Kategorie': audit.category_name,
    'Auditor': audit.auditor_name,
    'Datum': formatDate(audit.execution_date),
    'Stav': getStatusText(audit.neshoda_status),
    'Řešitel': audit.solver_id ? getSolverName(audit.solver_id) : 'Nepřiřazeno',
    'Termín': audit.termin ? formatDate(audit.termin) : '-',
    'Popis': audit.neshoda_popis || '',
  }))

  const filename = `NOK_audity_${new Date().toISOString().split('T')[0]}.csv`
  exportToCSV(exportData, filename)
}

// Lifecycle
onMounted(async () => {
  await store.initialize()
})
</script>