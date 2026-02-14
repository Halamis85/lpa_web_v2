<template>
  <div class="space-y-6">
    <!-- Hlavička -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-800">Dashboard</h1>
        <p class="mt-1 text-gray-600">Přehled NOK auditů a statistik</p>
      </div>
      <router-link
        to="/nok-audits"
        class="flex items-center gap-2 px-4 py-2 text-white transition bg-blue-600 rounded-lg hover:bg-blue-700"
      >
        <span>📋</span>
        <span>Zobrazit všechny NOK</span>
      </router-link>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-20">
      <div class="w-16 h-16 border-4 border-blue-500 rounded-full border-t-transparent animate-spin"></div>
    </div>

    <!-- Statistiky -->
    <NokStatsCards v-if="!loading" :stats="stats" />

    <!-- Rychlý přehled -->
    <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
      <!-- Nejnovější NOK -->
      <div class="p-6 bg-white rounded-lg shadow">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-xl font-semibold text-gray-800">📌 Nejnovější NOK</h2>
          <router-link
            to="/nok-audits"
            class="text-sm text-blue-600 hover:text-blue-800"
          >
            Zobrazit vše →
          </router-link>
        </div>

        <div v-if="recentAudits.length === 0" class="py-8 text-center text-gray-500">
          <div class="mb-2 text-4xl">📭</div>
          <p>Žádné NOK audity</p>
        </div>

        <div v-else class="space-y-3">
          <div
            v-for="audit in recentAudits"
            :key="audit.id"
            class="p-4 transition border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50 hover:border-blue-300"
            @click="$router.push(`/nok-audits/${audit.id}`)"
          >
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <p class="font-medium text-gray-800">{{ truncate(audit.question_text, 80) }}</p>
                <div class="flex gap-2 mt-2 text-sm text-gray-600">
                  <span>🏭 {{ audit.line_name }}</span>
                  <span>•</span>
                  <span>📅 {{ formatDate(audit.execution_date) }}</span>
                </div>
              </div>
              <span
                :class="['px-2 py-1 text-xs font-medium rounded-full', getStatusBadgeClass(audit.neshoda_status)]"
              >
                {{ getStatusText(audit.neshoda_status) }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- NOK po termínu -->
      <div class="p-6 bg-white rounded-lg shadow">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-xl font-semibold text-gray-800">⚠️ NOK po termínu</h2>
          <span class="px-3 py-1 text-sm font-medium text-red-800 bg-red-100 rounded-full">
            {{ overdueAudits.length }}
          </span>
        </div>

        <div v-if="overdueAudits.length === 0" class="py-8 text-center text-gray-500">
          <div class="mb-2 text-4xl">✅</div>
          <p>Žádné neshody po termínu</p>
        </div>

        <div v-else class="space-y-3">
          <div
            v-for="audit in overdueAudits.slice(0, 5)"
            :key="audit.id"
            class="p-4 transition border-l-4 border-red-500 rounded-lg cursor-pointer bg-red-50 hover:bg-red-100"
            @click="$router.push(`/nok-audits/${audit.id}`)"
          >
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <p class="font-medium text-gray-800">{{ truncate(audit.question_text, 60) }}</p>
                <div class="flex gap-2 mt-2 text-sm text-gray-600">
                  <span>🏭 {{ audit.line_name }}</span>
                  <span>•</span>
                  <span class="text-red-600">⏰ {{ formatDate(audit.termin) }}</span>
                </div>
              </div>
              <span class="text-xs text-red-600">
                {{ getDaysOverdue(audit.termin) }} dní
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Rozdělení podle linek -->
    <div class="p-6 bg-white rounded-lg shadow">
      <h2 class="mb-4 text-xl font-semibold text-gray-800">📊 Rozdělení podle linek</h2>

      <div v-if="Object.keys(auditsByLine).length === 0" class="py-8 text-center text-gray-500">
        <p>Žádná data k zobrazení</p>
      </div>

      <div v-else class="space-y-4">
        <div
          v-for="(audits, lineName) in auditsByLine"
          :key="lineName"
          class="p-4 border border-gray-200 rounded-lg"
        >
          <div class="flex items-center justify-between mb-2">
            <h3 class="font-medium text-gray-800">{{ lineName }}</h3>
            <span class="text-sm text-gray-600">{{ audits.length }} NOK</span>
          </div>
          
          <div class="flex gap-2">
            <div
              v-for="status in ['open', 'assigned', 'resolved']"
              :key="status"
              class="flex items-center gap-1 text-xs"
            >
              <span
                :class="['w-2 h-2 rounded-full', getStatusColor(status)]"
              ></span>
              <span>{{ getStatusCount(audits, status) }}</span>
            </div>
          </div>

          <!-- Progress bar -->
          <div class="w-full h-2 mt-3 overflow-hidden bg-gray-200 rounded-full">
            <div
              class="h-full bg-green-500"
              :style="{ width: getResolvedPercentage(audits) + '%' }"
            ></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useNokAuditsStore } from '@/stores/nokAudits'
import { useNokAuditHelpers } from '@/composables/useNokAuditHelpers'
import NokStatsCards from '@/components/NokStatsCards.vue'

const router = useRouter()
const store = useNokAuditsStore()
const { formatDate, getStatusText, getStatusBadgeClass, truncate, isOverdue } = useNokAuditHelpers()

// Computed
const loading = computed(() => store.loading)
const stats = computed(() => store.stats)
const auditsByLine = computed(() => store.auditsByLine)

const recentAudits = computed(() => {
  return [...store.audits]
    .sort((a, b) => new Date(b.execution_date) - new Date(a.execution_date))
    .slice(0, 5)
})

const overdueAudits = computed(() => {
  return store.audits.filter(audit => 
    isOverdue(audit.termin, audit.neshoda_status)
  ).sort((a, b) => new Date(a.termin) - new Date(b.termin))
})

// Methods
function getStatusColor(status) {
  const colorMap = {
    open: 'bg-red-500',
    assigned: 'bg-orange-500',
    in_progress: 'bg-blue-500',
    resolved: 'bg-green-500',
    closed: 'bg-gray-500',
  }
  return colorMap[status] || 'bg-gray-500'
}

function getStatusCount(audits, status) {
  return audits.filter(a => a.neshoda_status === status).length
}

function getResolvedPercentage(audits) {
  const resolved = audits.filter(a => a.neshoda_status === 'resolved' || a.neshoda_status === 'closed').length
  return Math.round((resolved / audits.length) * 100)
}

function getDaysOverdue(termin) {
  if (!termin) return 0
  const today = new Date()
  const deadline = new Date(termin)
  const diff = Math.floor((today - deadline) / (1000 * 60 * 60 * 24))
  return diff > 0 ? diff : 0
}

// Lifecycle
onMounted(async () => {
  await store.initialize()
})
</script>