<template>
  <div class="nok-audits">
    <div class="header">
      <h1>❌ NOK Audity</h1>
      <p class="subtitle">Přehled všech neshod zjištěných při auditech</p>
    </div>

    <!-- Filtry -->
    <div class="filters-card">
      <div class="filters-grid">
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
          <label>Datum od:</label>
          <input type="date" v-model="filters.date_from" />
        </div>

        <div class="filter-group">
          <label>Datum do:</label>
          <input type="date" v-model="filters.date_to" />
        </div>

        <div class="filter-group">
          <label>Stav:</label>
          <select v-model="filters.status">
            <option :value="null">Všechny stavy</option>
            <option value="open">Otevřené</option>
            <option value="assigned">Přiřazené</option>
            <option value="in_progress">V řešení</option>
            <option value="resolved">Vyřešené</option>
            <option value="closed">Uzavřené</option>
          </select>
        </div>

        <div class="filter-actions">
          <button @click="loadNokAudits" class="btn-primary">
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
      <p>Načítám NOK audity...</p>
    </div>

    <!-- Statistiky -->
    <div v-if="!loading && nokAudits.length > 0" class="stats-row">
      <div class="stat-card">
        <div class="stat-value">{{ nokAudits.length }}</div>
        <div class="stat-label">Celkem NOK</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ nokAudits.filter(a => a.neshoda_status === 'open').length }}</div>
        <div class="stat-label">Otevřené</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ nokAudits.filter(a => a.neshoda_status === 'assigned').length }}</div>
        <div class="stat-label">Přiřazené</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ nokAudits.filter(a => a.neshoda_status === 'resolved').length }}</div>
        <div class="stat-label">Vyřešené</div>
      </div>
    </div>

    <!-- Tabulka NOK auditů -->
    <div v-if="!loading && nokAudits.length > 0" class="nok-table-container">
      <table class="nok-table">
        <thead>
          <tr>
            <th>Fotka</th>
            <th>Otázka</th>
            <th>Linka</th>
            <th>Kategorie</th>
            <th>Auditor</th>
            <th>Datum</th>
            <th>Stav</th>
            <th>Řešitel</th>
            <th>Termín</th>
            <th>Akce</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="audit in nokAudits" :key="audit.id" class="nok-row">
            <!-- Fotka -->
            <td class="photo-cell">
              <img
                v-if="audit.picture_url"
                :src="getImageUrl(audit.picture_url)"
                alt="NOK fotka"
                class="nok-photo"
                @click="openImageModal(audit.picture_url)"
              />
              <span v-else class="no-photo">📷 Bez fotky</span>
            </td>

            <!-- Otázka -->
            <td class="question-cell">
              <div class="question-text">{{ audit.question_text }}</div>
              <div v-if="audit.neshoda_popis" class="comment">
                💬 {{ audit.neshoda_popis }}
              </div>
            </td>

            <!-- Linka -->
            <td>{{ audit.line_name }}</td>

            <!-- Kategorie -->
            <td>{{ audit.category_name }}</td>

            <!-- Auditor -->
            <td>{{ audit.auditor_name }}</td>

            <!-- Datum -->
            <td>{{ formatDate(audit.execution_date) }}</td>

            <!-- Stav -->
            <td>
              <span :class="['status-badge', `status-${audit.neshoda_status}`]">
                {{ getStatusText(audit.neshoda_status) }}
              </span>
            </td>

            <!-- Řešitel -->
            <td>
              <span v-if="audit.solver_id" class="solver-name">
                {{ getSolverName(audit.solver_id) }}
              </span>
              <span v-else class="no-solver">Nepřiřazen</span>
            </td>

            <!-- Termín -->
            <td>
              <span v-if="audit.termin" :class="{ 'deadline-warning': isDeadlineClose(audit.termin) }">
                {{ formatDate(audit.termin) }}
              </span>
              <span v-else class="no-deadline">-</span>
            </td>

            <!-- Akce -->
            <td class="actions-cell">
              <button
                v-if="canAssignSolver && !audit.solver_id"
                @click="openAssignDialog(audit)"
                class="btn-assign"
                title="Přiřadit řešitele"
              >
                👤 Přiřadit
              </button>
              <button
                @click="viewDetail(audit)"
                class="btn-detail"
                title="Detail"
              >
                👁️ Detail
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Prázdný stav -->
    <div v-if="!loading && nokAudits.length === 0" class="empty-state">
      <div class="empty-icon">✅</div>
      <h3>Žádné NOK audity</h3>
      <p>V tomto období nebyly nalezeny žádné neshody.</p>
    </div>

    <!-- Modal pro přiřazení řešitele -->
    <div v-if="showAssignDialog" class="modal-overlay" @click="closeAssignDialog">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>👤 Přiřadit řešitele</h3>
          <button @click="closeAssignDialog" class="close-btn">✕</button>
        </div>

        <div class="modal-body">
          <div class="form-group">
            <label>Otázka:</label>
            <p class="readonly-text">{{ selectedAudit?.question_text }}</p>
          </div>

          <div class="form-group">
            <label for="solver">Řešitel: *</label>
            <select v-model="assignForm.solver_id" id="solver" required>
              <option :value="null">-- Vyberte řešitele --</option>
              <option v-for="solver in solvers" :key="solver.id" :value="solver.id">
                {{ solver.jmeno }} ({{ solver.email }})
              </option>
            </select>
          </div>

          <div class="form-group">
            <label for="deadline">Termín nápravy:</label>
            <input
              type="date"
              v-model="assignForm.termin"
              id="deadline"
              :min="today"
            />
          </div>

          <div class="form-group">
            <label for="note">Poznámka:</label>
            <textarea
              v-model="assignForm.poznamka"
              id="note"
              rows="3"
              placeholder="Volitelná poznámka k nešhodě..."
            ></textarea>
          </div>
        </div>

        <div class="modal-footer">
          <button @click="closeAssignDialog" class="btn-secondary">Zrušit</button>
          <button
            @click="submitAssignment"
            class="btn-primary"
            :disabled="!assignForm.solver_id || submitting"
          >
            {{ submitting ? 'Přiřazuji...' : 'Přiřadit řešitele' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Modal pro zobrazení fotky -->
    <div v-if="showImageModal" class="modal-overlay" @click="closeImageModal">
      <div class="image-modal-content" @click.stop>
        <button @click="closeImageModal" class="close-btn">✕</button>
        <img :src="getImageUrl(selectedImage)" alt="NOK fotka" class="modal-image" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '../stores/user'
import api from '../api'

const userStore = useUserStore()

// State
const nokAudits = ref([])
const lines = ref([])
const categories = ref([])
const solvers = ref([])
const loading = ref(false)
const submitting = ref(false)

// Filtry
const filters = ref({
  line_id: null,
  category_id: null,
  date_from: null,
  date_to: null,
  status: null,
})

// Assign dialog
const showAssignDialog = ref(false)
const selectedAudit = ref(null)
const assignForm = ref({
  solver_id: null,
  termin: null,
  poznamka: null,
})

// Image modal
const showImageModal = ref(false)
const selectedImage = ref(null)

// Computed
const canAssignSolver = computed(() => {
  return userStore.userRole === 'admin' || userStore.userRole === 'auditor'
})

const today = computed(() => {
  return new Date().toISOString().split('T')[0]
})

// Načtení dat
async function loadNokAudits() {
  loading.value = true
  try {
    const params = {}
    if (filters.value.line_id) params.line_id = filters.value.line_id
    if (filters.value.category_id) params.category_id = filters.value.category_id
    if (filters.value.date_from) params.date_from = filters.value.date_from
    if (filters.value.date_to) params.date_to = filters.value.date_to

    const { data } = await api.get('/answers/nok-list', { params })
    nokAudits.value = data

    // Pokud je filtr stavu, aplikuj ho na klientovi
    if (filters.value.status) {
      nokAudits.value = nokAudits.value.filter(a => a.neshoda_status === filters.value.status)
    }
  } catch (error) {
    console.error('Chyba při načítání NOK auditů:', error)
    alert('Nepodařilo se načíst NOK audity')
  } finally {
    loading.value = false
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

async function loadSolvers() {
  try {
    const { data } = await api.get('/neshody/solvers')
    solvers.value = data
  } catch (error) {
    console.error('Chyba při načítání řešitelů:', error)
  }
}

function resetFilters() {
  filters.value = {
    line_id: null,
    category_id: null,
    date_from: null,
    date_to: null,
    status: null,
  }
  loadNokAudits()
}

// Přiřazení řešitele
function openAssignDialog(audit) {
  selectedAudit.value = audit
  assignForm.value = {
    solver_id: null,
    termin: null,
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
  try {
    await api.post(`/neshody/${selectedAudit.value.neshoda_id}/assign-solver`, {
      solver_id: assignForm.value.solver_id,
      termin: assignForm.value.termin,
      poznamka: assignForm.value.poznamka,
    })

    alert('✅ Řešitel byl úspěšně přiřazen')
    closeAssignDialog()
    loadNokAudits() // Reload
  } catch (error) {
    console.error('Chyba při přiřazení řešitele:', error)
    alert('❌ Nepodařilo se přiřadit řešitele')
  } finally {
    submitting.value = false
  }
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

function getStatusText(status) {
  const statusMap = {
    open: 'Otevřené',
    assigned: 'Přiřazené',
    in_progress: 'V řešení',
    resolved: 'Vyřešené',
    closed: 'Uzavřené',
  }
  return statusMap[status] || status
}

function getSolverName(solverId) {
  const solver = solvers.value.find(s => s.id === solverId)
  return solver ? solver.jmeno : 'Neznámý'
}

function isDeadlineClose(deadline) {
  if (!deadline) return false
  const deadlineDate = new Date(deadline)
  const today = new Date()
  const diffDays = Math.ceil((deadlineDate - today) / (1000 * 60 * 60 * 24))
  return diffDays <= 7 && diffDays >= 0
}

function viewDetail(audit) {
  // TODO: Navigate to detail view or show detail modal
  console.log('View detail:', audit)
}

onMounted(() => {
  loadNokAudits()
  loadLines()
  loadCategories()
  loadSolvers()
})
</script>

<style scoped>
.nok-audits {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.header {
  margin-bottom: 30px;
}

.header h1 {
  font-size: 32px;
  color: #d32f2f;
  margin-bottom: 5px;
}

.subtitle {
  color: #666;
  font-size: 16px;
}

/* Filtry */
.filters-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.filters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  align-items: end;
}

.filter-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 600;
  color: #333;
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

/* Statistiky */
.stats-row {
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

.stat-value {
  font-size: 36px;
  font-weight: 700;
  color: #d32f2f;
  margin-bottom: 5px;
}

.stat-label {
  color: #666;
  font-size: 14px;
}

/* Tabulka */
.nok-table-container {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.nok-table {
  width: 100%;
  border-collapse: collapse;
}

.nok-table thead {
  background: #f5f5f5;
}

.nok-table th {
  padding: 15px 10px;
  text-align: left;
  font-weight: 600;
  color: #333;
  border-bottom: 2px solid #ddd;
}

.nok-table td {
  padding: 15px 10px;
  border-bottom: 1px solid #eee;
}

.nok-row:hover {
  background: #f9f9f9;
}

/* Fotka */
.photo-cell {
  width: 120px;
}

.nok-photo {
  width: 100px;
  height: 75px;
  object-fit: cover;
  border-radius: 8px;
  cursor: pointer;
  transition: transform 0.3s;
}

.nok-photo:hover {
  transform: scale(1.05);
}

.no-photo {
  display: block;
  color: #999;
  font-size: 12px;
}

/* Otázka */
.question-cell {
  max-width: 300px;
}

.question-text {
  font-weight: 500;
  margin-bottom: 5px;
}

.comment {
  font-size: 12px;
  color: #666;
  font-style: italic;
}

/* Status badge */
.status-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.status-open {
  background: #ffebee;
  color: #c62828;
}

.status-assigned {
  background: #fff3e0;
  color: #e65100;
}

.status-in_progress {
  background: #e3f2fd;
  color: #1565c0;
}

.status-resolved {
  background: #e8f5e9;
  color: #2e7d32;
}

.status-closed {
  background: #f5f5f5;
  color: #616161;
}

/* Řešitel a termín */
.solver-name {
  font-weight: 500;
}

.no-solver {
  color: #999;
  font-style: italic;
}

.no-deadline {
  color: #999;
}

.deadline-warning {
  color: #d32f2f;
  font-weight: 600;
}

/* Akce */
.actions-cell {
  display: flex;
  gap: 5px;
}

.btn-assign, .btn-detail {
  padding: 6px 12px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.3s;
}

.btn-assign {
  background: #1976d2;
  color: white;
}

.btn-assign:hover {
  background: #1565c0;
}

.btn-detail {
  background: #f5f5f5;
  color: #333;
}

.btn-detail:hover {
  background: #e0e0e0;
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
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
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

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 600;
  color: #333;
}

.readonly-text {
  background: #f5f5f5;
  padding: 10px;
  border-radius: 6px;
  color: #666;
}

.form-group select,
.form-group input,
.form-group textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  font-family: inherit;
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
