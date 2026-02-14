<template>
  <div class="space-y-6">
    <!-- Hlavička s navigací zpět -->
    <div class="flex items-center gap-4">
      <button
        @click="$router.back()"
        class="px-4 py-2 text-gray-700 transition bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
      >
        ← Zpět
      </button>
      <div>
        <h1 class="text-3xl font-bold text-gray-800">
          Detail NOK auditu #{{ audit?.id }}
        </h1>
        <p class="mt-1 text-gray-600">Detailní informace o neshodě</p>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-20">
      <div class="w-16 h-16 border-4 border-blue-500 rounded-full border-t-transparent animate-spin"></div>
    </div>

    <!-- Not found -->
    <div v-else-if="!audit" class="py-20 text-center">
      <div class="mb-4 text-6xl">❌</div>
      <h2 class="mb-2 text-2xl font-bold text-gray-800">NOK audit nenalezen</h2>
      <p class="mb-6 text-gray-600">Audit s ID {{ route.params.id }} neexistuje.</p>
      <button
        @click="$router.push('/nok-audits')"
        class="px-6 py-3 text-white transition bg-blue-600 rounded-lg hover:bg-blue-700"
      >
        Zpět na přehled
      </button>
    </div>

    <!-- Detail -->
    <div v-else class="space-y-6">
      <!-- Základní informace -->
      <div class="p-6 bg-white rounded-lg shadow">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-xl font-semibold text-gray-800">📌 Základní informace</h2>
          <span
            :class="['px-4 py-2 text-sm font-medium rounded-full', getStatusBadgeClass(audit.neshoda_status)]"
          >
            {{ getStatusText(audit.neshoda_status) }}
          </span>
        </div>

        <div class="grid grid-cols-1 gap-6 md:grid-cols-2">
          <div>
            <label class="block text-xs font-medium text-gray-500 uppercase">Otázka</label>
            <p class="mt-1 text-gray-900">{{ audit.question_text }}</p>
          </div>

          <div>
            <label class="block text-xs font-medium text-gray-500 uppercase">Linka</label>
            <p class="mt-1 text-gray-900">{{ audit.line_name }}</p>
          </div>

          <div>
            <label class="block text-xs font-medium text-gray-500 uppercase">Kategorie</label>
            <p class="mt-1 text-gray-900">{{ audit.category_name }}</p>
          </div>

          <div>
            <label class="block text-xs font-medium text-gray-500 uppercase">Auditor</label>
            <p class="mt-1 text-gray-900">{{ audit.auditor_name }}</p>
          </div>

          <div>
            <label class="block text-xs font-medium text-gray-500 uppercase">Datum auditu</label>
            <p class="mt-1 text-gray-900">{{ formatDate(audit.execution_date) }}</p>
          </div>

          <div>
            <label class="block text-xs font-medium text-gray-500 uppercase">Měsíc</label>
            <p class="mt-1 text-gray-900">{{ audit.month }}</p>
          </div>
        </div>
      </div>

      <!-- Fotografie -->
      <div v-if="audit.picture_url" class="p-6 bg-white rounded-lg shadow">
        <h2 class="mb-6 text-xl font-semibold text-gray-800">📷 Fotografie neshody</h2>
        <div class="flex justify-center">
          <img
            :src="getImageUrl(audit.picture_url)"
            alt="NOK fotka"
            class="max-w-full rounded-lg shadow-lg cursor-pointer hover:scale-105 transition"
            @click="openImageModal(audit.picture_url)"
          />
        </div>
        <p class="mt-3 text-sm text-center text-gray-500">
          Klikněte na obrázek pro zvětšení
        </p>
      </div>

      <!-- Popis neshody -->
      <div v-if="audit.neshoda_popis" class="p-6 bg-white rounded-lg shadow">
        <h2 class="mb-6 text-xl font-semibold text-gray-800">💬 Popis neshody</h2>
        <div class="p-4 border-l-4 border-blue-500 rounded bg-blue-50">
          <p class="text-gray-800">{{ audit.neshoda_popis }}</p>
        </div>
      </div>

      <!-- Řešení -->
      <div class="p-6 bg-white rounded-lg shadow">
        <h2 class="mb-6 text-xl font-semibold text-gray-800">👤 Řešení</h2>

        <div class="grid grid-cols-1 gap-6 md:grid-cols-2">
          <div>
            <label class="block text-xs font-medium text-gray-500 uppercase">Řešitel</label>
            <p v-if="audit.solver_id" class="mt-1 font-medium text-gray-900">
              {{ getSolverName(audit.solver_id) }}
            </p>
            <p v-else class="mt-1 italic text-gray-400">Nepřiřazeno</p>
          </div>

          <div>
            <label class="block text-xs font-medium text-gray-500 uppercase">Termín</label>
            <p
              v-if="audit.termin"
              :class="[
                'mt-1 font-medium',
                isOverdue(audit.termin, audit.neshoda_status) ? 'text-red-600' : 'text-gray-900'
              ]"
            >
              {{ formatDate(audit.termin) }}
              <span v-if="isOverdue(audit.termin, audit.neshoda_status)" class="block text-sm">
                ⚠️ PO TERMÍNU ({{ getDaysOverdue(audit.termin) }} dní)
              </span>
            </p>
            <p v-else class="mt-1 text-gray-400">-</p>
          </div>
        </div>

        <!-- Tlačítko pro přiřazení (pouze admin/auditor) -->
        <div v-if="canAssignSolver && audit.neshoda_status !== 'closed'" class="mt-6">
          <button
            @click="openAssignDialog"
            class="px-6 py-3 text-white transition bg-blue-600 rounded-lg hover:bg-blue-700"
          >
            {{ audit.solver_id ? '✏️ Změnit řešitele' : '👤 Přiřadit řešitele' }}
          </button>
        </div>
      </div>

      <!-- Timeline / Historie (placeholder pro budoucí rozšíření) -->
      <div class="p-6 bg-white rounded-lg shadow">
        <h2 class="mb-6 text-xl font-semibold text-gray-800">📅 Historie</h2>
        <div class="space-y-4">
          <div class="flex gap-4">
            <div class="flex flex-col items-center">
              <div class="flex items-center justify-center w-10 h-10 bg-red-100 rounded-full">
                <span>🚨</span>
              </div>
              <div class="w-1 h-full bg-gray-200"></div>
            </div>
            <div class="pb-8">
              <p class="font-medium text-gray-800">Neshoda zjištěna</p>
              <p class="text-sm text-gray-600">{{ formatDateTime(audit.execution_date) }}</p>
              <p class="text-sm text-gray-600">Auditor: {{ audit.auditor_name }}</p>
            </div>
          </div>

          <div v-if="audit.solver_id" class="flex gap-4">
            <div class="flex flex-col items-center">
              <div class="flex items-center justify-center w-10 h-10 bg-blue-100 rounded-full">
                <span>👤</span>
              </div>
            </div>
            <div>
              <p class="font-medium text-gray-800">Přiřazeno řešiteli</p>
              <p class="text-sm text-gray-600">Řešitel: {{ getSolverName(audit.solver_id) }}</p>
              <p v-if="audit.termin" class="text-sm text-gray-600">
                Termín: {{ formatDate(audit.termin) }}
              </p>
            </div>
          </div>
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
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useNokAuditsStore } from '@/stores/nokAudits'
import { useNokAuditHelpers } from '@/composables/useNokAuditHelpers'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const store = useNokAuditsStore()
const {
  formatDate,
  formatDateTime,
  getStatusText,
  getStatusBadgeClass,
  isOverdue,
  getImageUrl,
} = useNokAuditHelpers()

// State
const loading = ref(true)
const showAssignDialog = ref(false)
const assignForm = ref({
  solver_id: null,
  termin: null,
  poznamka: null,
})
const submitting = ref(false)
const showImageModal = ref(false)
const selectedImage = ref(null)

// Computed
const audit = computed(() => {
  return store.getAuditById(parseInt(route.params.id))
})

const solvers = computed(() => store.solvers)

const canAssignSolver = computed(() => {
  return userStore.userRole === 'admin' || userStore.userRole === 'auditor'
})

const today = computed(() => {
  return new Date().toISOString().split('T')[0]
})

// Methods
function getSolverName(solverId) {
  return store.getSolverName(solverId)
}

function getDaysOverdue(termin) {
  if (!termin) return 0
  const today = new Date()
  const deadline = new Date(termin)
  const diff = Math.floor((today - deadline) / (1000 * 60 * 60 * 24))
  return diff > 0 ? diff : 0
}

function openAssignDialog() {
  assignForm.value = {
    solver_id: audit.value.solver_id || null,
    termin: audit.value.termin || null,
    poznamka: audit.value.neshoda_popis || null,
  }
  showAssignDialog.value = true
}

function closeAssignDialog() {
  showAssignDialog.value = false
}

async function submitAssignment() {
  if (!assignForm.value.solver_id) {
    alert('Musíte vybrat řešitele')
    return
  }

  submitting.value = true
  const result = await store.assignSolver(
    audit.value.neshoda_id,
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

// Lifecycle
onMounted(async () => {
  // Pokud ještě nemáme data, načti je
  if (store.audits.length === 0) {
    await store.initialize()
  }
  loading.value = false
})
</script>