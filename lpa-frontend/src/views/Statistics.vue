<template>
  <div class="max-w-7xl p-6 mx-auto space-y-6">
    <!-- Hlavička -->
    <div class="mb-8">
      <h1 class="text-4xl font-bold text-gray-800">📊 Statistiky a analytika</h1>
      <p class="mt-2 text-gray-600">Komplexní přehled výkonnosti auditů a trendů</p>
    </div>

    <!-- Celkové KPI -->
    <div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
      <div class="p-6 bg-linear-to-br from-blue-500 to-blue-600 rounded-lg shadow-lg text-white">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm opacity-90">Celkem auditů</p>
            <p class="mt-2 text-4xl font-bold">{{ overallStats.total_audits }}</p>
          </div>
          <div class="text-5xl opacity-50">📋</div>
        </div>
      </div>

      <div class="p-6 bg-linear-to-br from-green-500 to-green-600 rounded-lg shadow-lg text-white">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm opacity-90">Úspěšnost</p>
            <p class="mt-2 text-4xl font-bold">{{ overallStats.success_rate }}%</p>
          </div>
          <div class="text-5xl opacity-50">✅</div>
        </div>
      </div>

      <div class="p-6 bg-linear-to-br from-yellow-500 to-yellow-600 rounded-lg shadow-lg text-white">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm opacity-90">Probíhá</p>
            <p class="mt-2 text-4xl font-bold">{{ overallStats.in_progress }}</p>
          </div>
          <div class="text-5xl opacity-50">🔄</div>
        </div>
      </div>

      <div class="p-6 bg-linear-to-br from-purple-500 to-purple-600 rounded-lg shadow-lg text-white">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm opacity-90">Tento měsíc</p>
            <p class="mt-2 text-4xl font-bold">{{ overallStats.recent_month_success_rate }}%</p>
            <p class="text-xs opacity-75 mt-1">{{ overallStats.recent_month_audits }} auditů</p>
          </div>
          <div class="text-5xl opacity-50">📈</div>
        </div>
      </div>
    </div>

    <!-- Grafy - Řada 1 -->
    <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
      <!-- Graf 1: Provedené audity za měsíce -->
      <div class="p-6 bg-white rounded-lg shadow-lg">
        <h3 class="mb-4 text-lg font-semibold text-gray-800">📅 Provedené audity po měsících</h3>
        <div class="h-80">
          <canvas ref="monthlyAuditsChart"></canvas>
        </div>
      </div>

      <!-- Graf 2: Trend úspěšnosti -->
      <div class="p-6 bg-white rounded-lg shadow-lg">
        <h3 class="mb-4 text-lg font-semibold text-gray-800">📈 Trend úspěšnosti</h3>
        <div class="h-80">
          <canvas ref="successRateTrendChart"></canvas>
        </div>
      </div>
    </div>

    <!-- Grafy - Řada 2 -->
    <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
      <!-- Graf 3: Statistiky podle linek -->
      <div class="p-6 bg-white rounded-lg shadow-lg">
        <h3 class="mb-4 text-lg font-semibold text-gray-800">🏭 Statistiky podle linek</h3>
        <div class="h-80">
          <canvas ref="byLineChart"></canvas>
        </div>
      </div>

      <!-- Graf 4: OK vs NOK rozdělení -->
      <div class="p-6 bg-white rounded-lg shadow-lg">
        <h3 class="mb-4 text-lg font-semibold text-gray-800">⚖️ Celkové rozdělení OK/NOK</h3>
        <div class="h-80">
          <canvas ref="okNokPieChart"></canvas>
        </div>
      </div>
    </div>

    <!-- Grafy - Řada 3 -->
    <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
      <!-- Graf 5: Statistiky podle auditorů -->
      <div class="p-6 bg-white rounded-lg shadow-lg">
        <h3 class="mb-4 text-lg font-semibold text-gray-800">👥 Výkonnost auditorů</h3>
        <div class="h-80">
          <canvas ref="byAuditorChart"></canvas>
        </div>
      </div>

      <!-- Graf 6: NOK podle kategorií -->
      <div class="p-6 bg-white rounded-lg shadow-lg">
        <h3 class="mb-4 text-lg font-semibold text-gray-800">📂 NOK podle kategorií</h3>
        <div class="h-80">
          <canvas ref="byCategoryChart"></canvas>
        </div>
      </div>
    </div>

    <!-- Loading overlay -->
    <div v-if="loading" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div class="p-8 text-center bg-white rounded-lg shadow-xl">
        <div class="inline-block w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
        <p class="mt-4 text-lg font-semibold text-gray-700">Načítám statistiky...</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { Chart, registerables } from 'chart.js'
import api from '@/api'

Chart.register(...registerables)

// Refs pro grafy
const monthlyAuditsChart = ref(null)
const successRateTrendChart = ref(null)
const byLineChart = ref(null)
const okNokPieChart = ref(null)
const byAuditorChart = ref(null)
const byCategoryChart = ref(null)

// Data
const loading = ref(true)
const overallStats = ref({
  total_audits: 0,
  in_progress: 0,
  total_answers: 0,
  ok_count: 0,
  nok_count: 0,
  success_rate: 0,
  recent_month_success_rate: 0,
  recent_month_audits: 0
})

// Chart instances
let charts = []

// Načtení dat
async function loadAllData() {
  loading.value = true
  try {
    // Paralelní načtení všech dat
    const [
      overallData,
      monthlyData,
      successData,
      lineData,
      auditorData,
      categoryData
    ] = await Promise.all([
      api.get('/dashboard/stats/overall'),
      api.get('/dashboard/stats/monthly-audits?months=6'),
      api.get('/dashboard/stats/success-rate-trend?months=6'),
      api.get('/dashboard/stats/by-line'),
      api.get('/dashboard/stats/by-auditor'),
      api.get('/dashboard/stats/by-category')
    ])

    overallStats.value = overallData.data

    await nextTick()
    
    // Vytvoření grafů
    createMonthlyAuditsChart(monthlyData.data)
    createSuccessRateTrendChart(successData.data)
    createByLineChart(lineData.data)
    createOkNokPieChart()
    createByAuditorChart(auditorData.data)
    createByCategoryChart(categoryData.data)

  } catch (error) {
    console.error('Chyba při načítání dat:', error)
    alert('Nepodařilo se načíst statistická data')
  } finally {
    loading.value = false
  }
}

// Graf 1: Provedené audity po měsících (sloupcový)
function createMonthlyAuditsChart(data) {
  const ctx = monthlyAuditsChart.value.getContext('2d')
  
  const chart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: data.map(d => d.month_label || d.month),
      datasets: [
        {
          label: 'Dokončeno',
          data: data.map(d => d.completed),
          backgroundColor: 'rgba(34, 197, 94, 0.8)',
          borderColor: 'rgb(34, 197, 94)',
          borderWidth: 1
        },
        {
          label: 'Probíhá',
          data: data.map(d => d.in_progress),
          backgroundColor: 'rgba(234, 179, 8, 0.8)',
          borderColor: 'rgb(234, 179, 8)',
          borderWidth: 1
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            stepSize: 1
          }
        }
      },
      plugins: {
        legend: {
          display: true,
          position: 'top'
        }
      }
    }
  })
  
  charts.push(chart)
}

// Graf 2: Trend úspěšnosti (čárový)
function createSuccessRateTrendChart(data) {
  const ctx = successRateTrendChart.value.getContext('2d')
  
  const chart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: data.map(d => d.month_label || d.month),
      datasets: [
        {
          label: 'Úspěšnost (%)',
          data: data.map(d => d.success_rate),
          borderColor: 'rgb(59, 130, 246)',
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          tension: 0.4,
          fill: true,
          pointRadius: 5,
          pointHoverRadius: 7
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          max: 100,
          ticks: {
            callback: value => value + '%'
          }
        }
      },
      plugins: {
        legend: {
          display: true,
          position: 'top'
        },
        tooltip: {
          callbacks: {
            label: (context) => {
              const index = context.dataIndex
              const item = data[index]
              return [
                `Úspěšnost: ${item.success_rate}%`,
                `OK: ${item.ok}`,
                `NOK: ${item.nok}`,
                `Celkem: ${item.total}`
              ]
            }
          }
        }
      }
    }
  })
  
  charts.push(chart)
}

// Graf 3: Statistiky podle linek (horizontální bar)
function createByLineChart(data) {
  const ctx = byLineChart.value.getContext('2d')
  
  const chart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: data.map(d => d.line_name),
      datasets: [
        {
          label: 'Počet auditů',
          data: data.map(d => d.audit_count),
          backgroundColor: 'rgba(99, 102, 241, 0.8)',
          borderColor: 'rgb(99, 102, 241)',
          borderWidth: 1
        }
      ]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          beginAtZero: true
        }
      },
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          callbacks: {
            label: (context) => {
              const index = context.dataIndex
              const item = data[index]
              return [
                `Audity: ${item.audit_count}`,
                `Úspěšnost: ${item.success_rate}%`,
                `OK: ${item.ok}`,
                `NOK: ${item.nok}`
              ]
            }
          }
        }
      }
    }
  })
  
  charts.push(chart)
}

// Graf 4: OK vs NOK (koláčový)
function createOkNokPieChart() {
  const ctx = okNokPieChart.value.getContext('2d')
  
  const chart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['OK', 'NOK'],
      datasets: [{
        data: [overallStats.value.ok_count, overallStats.value.nok_count],
        backgroundColor: [
          'rgba(34, 197, 94, 0.8)',
          'rgba(239, 68, 68, 0.8)'
        ],
        borderColor: [
          'rgb(34, 197, 94)',
          'rgb(239, 68, 68)'
        ],
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom'
        },
        tooltip: {
          callbacks: {
            label: (context) => {
              const label = context.label
              const value = context.parsed
              const total = overallStats.value.ok_count + overallStats.value.nok_count
              const percentage = ((value / total) * 100).toFixed(1)
              return `${label}: ${value} (${percentage}%)`
            }
          }
        }
      }
    }
  })
  
  charts.push(chart)
}

// Graf 5: Statistiky podle auditorů
function createByAuditorChart(data) {
  const ctx = byAuditorChart.value.getContext('2d')
  
  const chart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: data.map(d => d.auditor_name),
      datasets: [
        {
          label: 'Úspěšnost (%)',
          data: data.map(d => d.success_rate),
          backgroundColor: 'rgba(168, 85, 247, 0.8)',
          borderColor: 'rgb(168, 85, 247)',
          borderWidth: 1,
          yAxisID: 'y1'
        },
        {
          label: 'Počet auditů',
          data: data.map(d => d.audit_count),
          backgroundColor: 'rgba(14, 165, 233, 0.8)',
          borderColor: 'rgb(14, 165, 233)',
          borderWidth: 1,
          yAxisID: 'y'
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          type: 'linear',
          display: true,
          position: 'left',
          beginAtZero: true,
          title: {
            display: true,
            text: 'Počet auditů'
          }
        },
        y1: {
          type: 'linear',
          display: true,
          position: 'right',
          beginAtZero: true,
          max: 100,
          title: {
            display: true,
            text: 'Úspěšnost (%)'
          },
          grid: {
            drawOnChartArea: false
          }
        }
      },
      plugins: {
        legend: {
          display: true,
          position: 'top'
        }
      }
    }
  })
  
  charts.push(chart)
}

// Graf 6: NOK podle kategorií
function createByCategoryChart(data) {
  const ctx = byCategoryChart.value.getContext('2d')
  
  const chart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: data.map(d => d.category_name),
      datasets: [{
        label: 'Počet NOK',
        data: data.map(d => d.nok_count),
        backgroundColor: 'rgba(239, 68, 68, 0.8)',
        borderColor: 'rgb(239, 68, 68)',
        borderWidth: 1
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          beginAtZero: true
        }
      },
      plugins: {
        legend: {
          display: false
        }
      }
    }
  })
  
  charts.push(chart)
}

// Lifecycle
onMounted(() => {
  loadAllData()
})

// Cleanup
onBeforeUnmount(() => {
  charts.forEach(chart => chart.destroy())
})
</script>