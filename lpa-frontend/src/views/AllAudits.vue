<template>
  <div class="all-audits">
    <div class="header">
      <h1>📋 Všechny audity</h1>
      <p class="subtitle">Kompletní přehled provedených auditů</p>
    </div>

    <!-- Statistiky -->
    <div v-if="stats" class="stats-grid">
      <div class="stat-card">
        <div class="stat-value">{{ stats.total_audits }}</div>
        <div class="stat-label">Celkem auditů</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ stats.completed_audits }}</div>
        <div class="stat-label">Dokončené</div>
      </div>
      <div class="stat-card success">
        <div class="stat-value">{{ stats.ok_percent }}%</div>
        <div class="stat-label">OK odpovědi</div>
      </div>
      <div class="stat-card danger">
        <div class="stat-value">{{ stats.nok_answers }}</div>
        <div class="stat-label">NOK odpovědi</div>
      </div>
    </div>

    <!-- Filtry -->
    <div class="filters-card">
      <h3>🔍 Filtry</h3>
      <div class="filters-grid">
        <div class="filter-group">
          <label>Stav:</label>
          <select v-model="filters.status">
            <option :value="null">Všechny stavy</option>
            <option value="in_progress">Probíhající</option>
            <option value="done">Dokončené</option>
          </select>
        </div>

        <div class="filter-group">
          <label>Výsledek:</label>
          <select v-model="filters.result_filter">
            <option value="all">Všechny</option>
            <option value="ok">Pouze OK (bez NOK)</option>
            <option value="nok">Pouze s NOK</option>
          </select>
        </div>

        <div class="filter-group">
          <label>Linka:</label>
          <select v-model="filters.line_id">
            <option :value="null">Všechny linky</option>
            <option v-for="line in lines" :key="line.id" :value="line.id">
              {{ line.name }}
            </option>
          </select>
        </div>

        <div class="filter-group">
          <label>Kategorie:</label>
          <select v-model="filters.category_id">
            <option :value="null">Všechny kategorie</option>
            <option v-for="cat in categories" :key="cat.id" :value="cat.id">
              {{ cat.name }}
            </option>
          </select>
        </div>

        <div class="filter-group">
          <label>Auditor:</label>
          <select v-model="filters.auditor_id">
            <option :value="null">Všichni auditoři</option>
            <option v-for="auditor in auditors" :key="auditor.id" :value="auditor.id">
              {{ auditor.jmeno }}
            </option>
          </select>
        </div>

        <div class="filter-group">
          <label>Měsíc:</label>
          <select v-model="filters.month">
            <option :value="null">Všechny měsíce</option>
            <option v-for="m in months" :key="m" :value="m">
              {{ m }}
            </option>
          </select>
        </div>

        <div class="filter-group">
          <label>Datum od:</label>
          <input type="date" v-model="filters.date_from" />
        </div>

        <div class="filter-group">
          <label>Datum do:</label>
          <input type="date" v-model="filters.date_to" />
        </div>

        <div class="filter-actions">
          <button @click="loadAudits" class="btn-primary">
            🔍 Filtrovat
          </button>
          <button @click="resetFilters" class="btn-secondary">
            🔄 Reset
          </button>
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>Načítám audity...</p>
    </div>

    <!-- Tabulka auditů -->
    <div v-if="!loading && audits.length > 0" class="audits-table-container">
      <table class="audits-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Linka</th>
            <th>Kategorie</th>
            <th>Měsíc</th>
            <th>Auditor</th>
            <th>Datum</th>
            <th>Stav</th>
            <th>Celkem</th>
            <th>OK</th>
            <th>NOK</th>
            <th>OK %</th>
            <th>Akce</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="audit in audits" :key="audit.execution_id" class="audit-row">
            <td>{{ audit.execution_id }}</td>
            <td>{{ audit.line_name }}</td>
            <td>{{ audit.category_name }}</td>
            <td>{{ audit.month }}</td>
            <td>{{ audit.auditor_name }}</td>
            <td>{{ formatDate(audit.started_at) }}</td>
            <td>
              <span :class="['status-badge', `status-${audit.status}`]">
                {{ getStatusText(audit.status) }}
              </span>
            </td>
            <td class="text-center">{{ audit.stats.total }}</td>
            <td class="text-center ok-cell">{{ audit.stats.ok }}</td>
            <td class="text-center nok-cell">
              <span :class="{ 'has-nok': audit.stats.nok > 0 }">
                {{ audit.stats.nok }}
              </span>
            </td>
            <td class="text-center">
              <div class="progress-bar">
                <div
                  class="progress-fill"
                  :style="{ width: audit.stats.ok_percent + '%' }"
                  :class="{ 'low-score': audit.stats.ok_percent < 80 }"
                ></div>
                <span class="progress-text">{{ audit.stats.ok_percent }}%</span>
              </div>
            </td>
            <td class="actions-cell">
              <button @click="viewAudit(audit)" class="btn-view" title="Zobrazit detail">
                👁️
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Prázdný stav -->
    <div v-if="!loading && audits.length === 0" class="empty-state">
      <div class="empty-icon">📋</div>
      <h3>Žádné audity</h3>
      <p>V tomto období nebyly nalezeny žádné audity.</p>
    </div>

    <!-- Modal pro detail -->
    <div v-if="showDetailModal" class="modal-overlay" @click="closeDetailModal">
      <div class="modal-content large" @click.stop>
        <div class="modal-header">
          <h3>📋 Detail auditu #{{ selectedAudit?.execution_id }}</h3>
          <button @click="closeDetailModal" class="close-btn">✕</button>
        </div>

        <div class="modal-body">
          <div class="audit-info-grid">
            <div class="info-item">
              <strong>Linka:</strong>
              <span>{{ selectedAudit?.line_name }}</span>
            </div>
            <div class="info-item">
              <strong>Kategorie:</strong>
              <span>{{ selectedAudit?.category_name }}</span>
            </div>
            <div class="info-item">
              <strong>Auditor:</strong>
              <span>{{ selectedAudit?.auditor_name }}</span>
            </div>
            <div class="info-item">
              <strong>Datum:</strong>
              <span>{{ formatDateTime(selectedAudit?.started_at) }}</span>
            </div>
            <div class="info-item">
              <strong>Stav:</strong>
              <span :class="['status-badge', `status-${selectedAudit?.status}`]">
                {{ getStatusText(selectedAudit?.status) }}
              </span>
            </div>
            <div class="info-item">
              <strong>Výsledek:</strong>
              <span>
                {{ selectedAudit?.stats.ok }} OK / {{ selectedAudit?.stats.nok }} NOK
                ({{ selectedAudit?.stats.ok_percent }}%)
              </span>
            </div>
          </div>

          <div v-if="detailAnswers.length > 0" class="answers-section">
            <h4>Odpovědi na otázky:</h4>
            <div class="answers-list">
              <div
                v-for="answer in detailAnswers"
                :key="answer.id"
                :class="['answer-item', `answer-${answer.odpoved.toLowerCase()}`]"
              >
                <div class="answer-header">
                  <span class="answer-badge">{{ answer.odpoved }}</span>
                  <span class="category-tag">{{ answer.category }}</span>
                </div>
                <div class="answer-question">{{ answer.question_text }}</div>
                <div v-if="answer.picture_url" class="answer-photo">
                  <img
                    :src="getImageUrl(answer.picture_url)"
                    alt="Fotka z auditu"
                    @click="openImageModal(answer.picture_url)"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button @click="closeDetailModal" class="btn-secondary">Zavřít</button>
        </div>
      </div>
    </div>

    <!-- Image modal -->
    <div v-if="showImageModal" class="modal-overlay" @click="closeImageModal">
      <div class="image-modal-content" @click.stop>
        <button @click="closeImageModal" class="close-btn">✕</button>
        <img :src="getImageUrl(selectedImage)" alt="Fotka z auditu" class="modal-image" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'

// State
const audits = ref([])
const lines = ref([])
const categories = ref([])
const auditors = ref([])
const stats = ref(null)
const loading = ref(false)

// Filtry
const filters = ref({
  status: null,
  result_filter: 'all',
  line_id: null,
  category_id: null,
  auditor_id: null,
  month: null,
  date_from: null,
  date_to: null,
})

const months = ['2025-01', '2025-02', '2025-03', '2025-04', '2025-05', '2025-06',
                '2025-07', '2025-08', '2025-09', '2025-10', '2025-11', '2025-12']

// Detail modal
const showDetailModal = ref(false)
const selectedAudit = ref(null)
const detailAnswers = ref([])

// Image modal
const showImageModal = ref(false)
const selectedImage = ref(null)

// Načtení dat
async function loadAudits() {
  loading.value = true
  try {
    const params = {}
    if (filters.value.status) params.status = filters.value.status
    if (filters.value.result_filter && filters.value.result_filter !== 'all') {
      params.result_filter = filters.value.result_filter
    }
    if (filters.value.line_id) params.line_id = filters.value.line_id
    if (filters.value.category_id) params.category_id = filters.value.category_id
    if (filters.value.auditor_id) params.auditor_id = filters.value.auditor_id
    if (filters.value.month) params.month = filters.value.month
    if (filters.value.date_from) params.date_from = filters.value.date_from
    if (filters.value.date_to) params.date_to = filters.value.date_to

    const { data } = await api.get('/executions/list', { params })
    audits.value = data
  } catch (error) {
    console.error('Chyba při načítání auditů:', error)
    alert('Nepodařilo se načíst audity')
  } finally {
    loading.value = false
  }
}

async function loadStats() {
  try {
    const params = {}
    if (filters.value.date_from) params.date_from = filters.value.date_from
    if (filters.value.date_to) params.date_to = filters.value.date_to

    const { data } = await api.get('/executions/stats/summary', { params })
    stats.value = data
  } catch (error) {
    console.error('Chyba při načítání statistik:', error)
  }
}

async function loadLines() {
  try {
    const { data } = await api.get('/lines')
    lines.value = data
  } catch (error) {
    console.error('Chyba při načítání linek:', error)
  }
}

async function loadCategories() {
  try {
    const { data } = await api.get('/categories')
    categories.value = data
  } catch (error) {
    console.error('Chyba při načítání kategorií:', error)
  }
}

async function loadAuditors() {
  try {
    const { data } = await api.get('/users')
    auditors.value = data.filter(u => u.role === 'auditor' || u.role === 'admin')
  } catch (error) {
    console.error('Chyba při načítání auditorů:', error)
  }
}

function resetFilters() {
  filters.value = {
    status: null,
    result_filter: 'all',
    line_id: null,
    category_id: null,
    auditor_id: null,
    month: null,
    date_from: null,
    date_to: null,
  }
  loadAudits()
  loadStats()
}

// Detail auditu
async function viewAudit(audit) {
  selectedAudit.value = audit
  
  try {
    const { data } = await api.get(`/answers/execution/${audit.execution_id}`)
    detailAnswers.value = data
    showDetailModal.value = true
  } catch (error) {
    console.error('Chyba při načítání detailu:', error)
    alert('Nepodařilo se načíst detail auditu')
  }
}

function closeDetailModal() {
  showDetailModal.value = false
  selectedAudit.value = null
  detailAnswers.value = []
}

// Image modal
function openImageModal(imageUrl) {
  selectedImage.value = imageUrl
  showImageModal.value = true
}

function closeImageModal() {
  showImageModal.value = false
  selectedImage.value = null
}

// Helpers
function getImageUrl(path) {
  if (!path) return ''
  return `http://127.0.0.1:8000/${path}`
}

function formatDate(dateString) {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleDateString('cs-CZ')
}

function formatDateTime(dateString) {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('cs-CZ')
}

function getStatusText(status) {
  const statusMap = {
    in_progress: 'Probíhá',
    done: 'Dokončeno',
  }
  return statusMap[status] || status
}

onMounted(() => {
  loadAudits()
  loadStats()
  loadLines()
  loadCategories()
  loadAuditors()
})
</script>

<style scoped>
.all-audits {
  max-width: 1600px;
  margin: 0 auto;
  padding: 20px;
}

.header {
  margin-bottom: 30px;
}

.header h1 {
  font-size: 32px;
  color: #1976d2;
  margin-bottom: 5px;
}

.subtitle {
  color: #666;
  font-size: 16px;
}

/* Statistiky */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.stat-card {
  background: white;
  padding: 20px;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.stat-card.success .stat-value {
  color: #2e7d32;
}

.stat-card.danger .stat-value {
  color: #d32f2f;
}

.stat-value {
  font-size: 36px;
  font-weight: 700;
  color: #1976d2;
  margin-bottom: 5px;
}

.stat-label {
  color: #666;
  font-size: 14px;
}

/* Filtry */
.filters-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.filters-card h3 {
  margin: 0 0 15px 0;
  color: #333;
}

.filters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 15px;
  align-items: end;
}

.filter-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 600;
  color: #333;
  font-size: 14px;
}

.filter-group select,
.filter-group input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
}

.filter-actions {
  display: flex;
  gap: 10px;
}

.btn-primary, .btn-secondary {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
  white-space: nowrap;
}

.btn-primary {
  background: #1976d2;
  color: white;
}

.btn-primary:hover {
  background: #1565c0;
}

.btn-secondary {
  background: #f5f5f5;
  color: #333;
}

.btn-secondary:hover {
  background: #e0e0e0;
}

/* Loading */
.loading {
  text-align: center;
  padding: 60px 20px;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #1976d2;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Tabulka */
.audits-table-container {
  background: white;
  border-radius: 12px;
  overflow-x: auto;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.audits-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 1200px;
}

.audits-table thead {
  background: #f5f5f5;
}

.audits-table th {
  padding: 15px 10px;
  text-align: left;
  font-weight: 600;
  color: #333;
  border-bottom: 2px solid #ddd;
  font-size: 14px;
}

.audits-table td {
  padding: 12px 10px;
  border-bottom: 1px solid #eee;
  font-size: 14px;
}

.audit-row:hover {
  background: #f9f9f9;
}

.text-center {
  text-align: center;
}

.ok-cell {
  color: #2e7d32;
  font-weight: 600;
}

.nok-cell .has-nok {
  color: #d32f2f;
  font-weight: 700;
}

/* Status badge */
.status-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.status-in_progress {
  background: #e3f2fd;
  color: #1565c0;
}

.status-done {
  background: #e8f5e9;
  color: #2e7d32;
}

/* Progress bar */
.progress-bar {
  position: relative;
  width: 100%;
  height: 24px;
  background: #f5f5f5;
  border-radius: 12px;
  overflow: hidden;
}

.progress-fill {
  position: absolute;
  left: 0;
  top: 0;
  height: 100%;
  background: #4caf50;
  transition: width 0.3s;
}

.progress-fill.low-score {
  background: #ff9800;
}

.progress-text {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  font-size: 12px;
  font-weight: 600;
  color: #333;
  z-index: 1;
}

/* Actions */
.actions-cell {
  text-align: center;
}

.btn-view {
  background: #1976d2;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.btn-view:hover {
  background: #1565c0;
}

/* Empty state */
.empty-state {
  text-align: center;
  padding: 80px 20px;
  background: white;
  border-radius: 12px;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 20px;
}

.empty-state h3 {
  color: #333;
  margin-bottom: 10px;
}

.empty-state p {
  color: #666;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 800px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-content.large {
  max-width: 1000px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  margin: 0;
  font-size: 20px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999;
  padding: 0;
  width: 30px;
  height: 30px;
}

.close-btn:hover {
  color: #333;
}

.modal-body {
  padding: 20px;
}

.audit-info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
  margin-bottom: 30px;
  padding: 20px;
  background: #f5f5f5;
  border-radius: 8px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.info-item strong {
  font-size: 12px;
  color: #666;
  text-transform: uppercase;
}

.info-item span {
  font-size: 14px;
  color: #333;
}

.answers-section h4 {
  margin-bottom: 15px;
  color: #333;
}

.answers-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.answer-item {
  padding: 15px;
  border-radius: 8px;
  border-left: 4px solid #ddd;
}

.answer-item.answer-ok {
  background: #e8f5e9;
  border-left-color: #4caf50;
}

.answer-item.answer-nok {
  background: #ffebee;
  border-left-color: #f44336;
}

.answer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.answer-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  background: white;
}

.category-tag {
  font-size: 12px;
  color: #666;
  font-style: italic;
}

.answer-question {
  font-size: 14px;
  color: #333;
  line-height: 1.5;
}

.answer-photo {
  margin-top: 10px;
}

.answer-photo img {
  max-width: 300px;
  border-radius: 8px;
  cursor: pointer;
  transition: transform 0.3s;
}

.answer-photo img:hover {
  transform: scale(1.05);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 20px;
  border-top: 1px solid #eee;
}

/* Image modal */
.image-modal-content {
  position: relative;
  max-width: 90vw;
  max-height: 90vh;
}

.image-modal-content .close-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  background: rgba(0, 0, 0, 0.5);
  color: white;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  z-index: 10;
}

.modal-image {
  max-width: 100%;
  max-height: 90vh;
  border-radius: 8px;
}
</style>
