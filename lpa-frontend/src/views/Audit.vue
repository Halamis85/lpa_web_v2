<template>
  <div class="max-w-6xl p-6 mx-auto">
    <!-- Hlavička -->
    <div class="mb-6">
      <h1 class="text-3xl font-bold text-gray-800">📋 Provedení auditu</h1>
      <p class="mt-2 text-gray-600">Vyplňte kontrolní checklist krok za krokem</p>
    </div>

    <!-- Výběr přidělení -->
    <div v-if="!executionId" class="space-y-6">
      <div class="p-6 bg-white rounded-lg shadow">
        <h2 class="mb-4 text-xl font-semibold text-gray-800">Vyberte audit k provedení</h2>
        
        <div v-if="assignments.length === 0" class="py-12 text-center text-gray-500">
          <div class="mb-4 text-6xl">📭</div>
          <p class="text-lg">Nemáte žádná přidělení k provedení</p>
        </div>

        <div v-else class="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
          <div
            v-for="assignment in assignments"
            :key="assignment.id"
            @click="selectAssignment(assignment)"
            class="p-6 transition border-2 border-gray-200 rounded-lg cursor-pointer hover:border-blue-500 hover:shadow-lg"
          >
            <div class="flex items-start justify-between mb-3">
              <div class="flex-1">
                <h3 class="font-semibold text-gray-800">{{ assignment.line_name }}</h3>
                <p class="text-sm text-gray-600">{{ assignment.category_name }}</p>
              </div>
              <span class="px-2 py-1 text-xs font-medium text-blue-800 bg-blue-100 rounded-full">
                {{ assignment.month }}
              </span>
            </div>
            <div class="pt-3 mt-3 border-t border-gray-200">
              <p class="text-sm text-gray-500">Termín: {{ formatDate(assignment.termin) }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Probíhající audit -->
    <div v-if="executionId" class="space-y-6">
      <!-- Progress bar -->
      <div class="p-6 bg-white rounded-lg shadow">
        <div class="flex items-center justify-between mb-2">
          <h2 class="text-xl font-semibold text-gray-800">{{ assignedCategoryName }}</h2>
          <span class="text-sm font-medium text-gray-600">
            {{ answeredCount }} / {{ totalQuestions }} odpovězeno
          </span>
        </div>
        <div class="relative w-full h-3 overflow-hidden bg-gray-200 rounded-full">
          <div
            class="absolute top-0 left-0 h-full transition-all duration-500 bg-linear-to-r from-blue-500 to-blue-600"
            :style="{ width: progressPercentage + '%' }"
          ></div>
        </div>
        <p class="mt-2 text-sm text-gray-500">
          {{ progressPercentage }}% dokončeno
        </p>
      </div>

      <!-- Otázky jako karty -->
      <div class="space-y-4">
        <div
          v-for="pos in maxPosition"
          :key="pos"
          class="p-6 transition bg-white rounded-lg shadow hover:shadow-md"
        >
          <div v-if="questionsByPosition[pos]">
            <div class="flex items-start justify-between mb-4">
              <div class="flex items-center gap-3">
                <div class="flex items-center justify-center w-10 h-10 text-white bg-blue-500 rounded-full">
                  {{ pos }}
                </div>
                <h3 class="text-lg font-medium text-gray-800">
                  {{ questionsByPosition[pos].question_text }}
                </h3>
              </div>
              <span
                v-if="answers[questionsByPosition[pos].id]"
                :class="[
                  'px-3 py-1 rounded-full text-sm font-medium',
                  answers[questionsByPosition[pos].id] === 'OK' 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-red-100 text-red-800'
                ]"
              >
                {{ answers[questionsByPosition[pos].id] }}
              </span>
            </div>

            <div class="flex gap-3">
              <button
                @click="saveAnswer(questionsByPosition[pos].id, 'OK')"
                :class="[
                  'flex-1 px-6 py-3 font-medium rounded-lg transition',
                  answers[questionsByPosition[pos].id] === 'OK'
                    ? 'bg-green-500 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-green-50 hover:text-green-700 border border-gray-300'
                ]"
              >
                <span class="mr-2">✓</span> OK
              </button>
              <button
                @click="saveAnswer(questionsByPosition[pos].id, 'NOK')"
                :class="[
                  'flex-1 px-6 py-3 font-medium rounded-lg transition',
                  answers[questionsByPosition[pos].id] === 'NOK'
                    ? 'bg-red-500 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-red-50 hover:text-red-700 border border-gray-300'
                ]"
              >
                <span class="mr-2">✗</span> NOK
              </button>
            </div>
          </div>

          <div v-else class="text-center text-gray-400">
            <p>Bez otázky</p>
          </div>
        </div>
      </div>

      <!-- Tlačítko dokončit -->
      <div class="sticky bottom-0 p-6 bg-white border-t rounded-lg shadow">
        <div class="flex items-center justify-between">
          <div>
            <p class="font-medium text-gray-800">
              {{ answeredCount === totalQuestions ? '✅ Všechny otázky zodpovězeny!' : '⚠️ Některé otázky ještě nejsou zodpovězeny' }}
            </p>
            <p class="text-sm text-gray-600">
              {{ answeredCount }} / {{ totalQuestions }} odpovězeno
            </p>
          </div>
          <button
            @click="showFinishConfirm = true"
            :disabled="answeredCount === 0"
            :class="[
              'px-8 py-3 font-semibold rounded-lg transition',
              answeredCount === 0
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-blue-600 text-white hover:bg-blue-700'
            ]"
          >
            🏁 Dokončit audit
          </button>
        </div>
      </div>
    </div>

    <!-- Modal pro NOK s fotkou -->
    <div
      v-if="nokQuestionId"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50"
      @click="cancelNok"
    >
      <div
        class="w-full max-w-2xl p-6 bg-white rounded-lg shadow-xl"
        @click.stop
      >
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-xl font-semibold text-gray-800">❌ NOK - Neshoda zjištěna</h3>
          <button
            @click="cancelNok"
            class="text-2xl text-gray-400 hover:text-gray-600"
          >
            ✕
          </button>
        </div>

        <div class="space-y-4">
          <div>
            <label class="block mb-2 text-sm font-medium text-gray-700">
              Popis neshody (volitelné)
            </label>
            <textarea
              v-model="nokComment"
              rows="4"
              placeholder="Popište, co bylo zjištěno..."
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            ></textarea>
          </div>

          <div>
            <label class="block mb-2 text-sm font-medium text-gray-700">
              Fotografie (volitelné)
            </label>
            <div class="relative">
              <input
                type="file"
                ref="fileInput"
                @change="handleFileChange"
                accept="image/*"
                capture="environment"
                class="hidden"
              />
              <button
                @click="$refs.fileInput.click()"
                class="flex items-center justify-center w-full px-4 py-8 transition border-2 border-gray-300 border-dashed rounded-lg hover:border-blue-500 hover:bg-blue-50"
              >
                <div class="text-center">
                  <span class="text-4xl">📷</span>
                  <p class="mt-2 text-sm text-gray-600">
                    {{ nokFile ? nokFile.name : 'Klikněte pro nahrání fotky nebo pořízení nové' }}
                  </p>
                </div>
              </button>
            </div>

            <!-- Náhled fotky -->
            <div v-if="previewUrl" class="mt-4">
              <img
                :src="previewUrl"
                alt="Náhled"
                class="max-w-50 rounded-lg shadow"
              />
              <button
                @click="removePhoto"
                class="px-3 py-1 mt-2 text-sm text-red-600 transition bg-red-100 rounded hover:bg-red-200"
              >
                🗑️ Odstranit fotku
              </button>
            </div>
          </div>

          <div class="flex justify-end gap-3 pt-4">
            <button
              @click="cancelNok"
              class="px-6 py-2 text-gray-700 transition bg-gray-100 border border-gray-300 rounded-lg hover:bg-gray-200"
            >
              Zrušit
            </button>
            <button
              @click="confirmNok"
              class="px-6 py-2 text-white transition bg-red-600 rounded-lg hover:bg-red-700"
            >
              💾 Potvrdit NOK
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Confirm dialog pro dokončení -->
    <div
      v-if="showFinishConfirm"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50"
      @click="showFinishConfirm = false"
    >
      <div
        class="w-full max-w-md p-6 bg-white rounded-lg shadow-xl"
        @click.stop
      >
        <h3 class="mb-4 text-xl font-semibold text-gray-800">🏁 Dokončit audit?</h3>
        
        <div class="mb-6 space-y-2">
          <div class="flex items-center justify-between p-3 bg-gray-50 rounded">
            <span class="text-gray-700">Celkem otázek:</span>
            <span class="font-semibold">{{ totalQuestions }}</span>
          </div>
          <div class="flex items-center justify-between p-3 bg-green-50 rounded">
            <span class="text-green-700">OK odpovědi:</span>
            <span class="font-semibold text-green-700">{{ okCount }}</span>
          </div>
          <div class="flex items-center justify-between p-3 bg-red-50 rounded">
            <span class="text-red-700">NOK odpovědi:</span>
            <span class="font-semibold text-red-700">{{ nokCount }}</span>
          </div>
          <div class="flex items-center justify-between p-3 bg-blue-50 rounded">
            <span class="text-blue-700">Úspěšnost:</span>
            <span class="font-semibold text-blue-700">{{ successRate }}%</span>
          </div>
        </div>

        <p v-if="answeredCount < totalQuestions" class="mb-6 text-sm text-orange-600">
          ⚠️ Upozornění: Nezodpověděli jste všechny otázky ({{ answeredCount }}/{{ totalQuestions }})
        </p>

        <div class="flex justify-end gap-3">
          <button
            @click="showFinishConfirm = false"
            class="px-6 py-2 text-gray-700 transition bg-gray-100 border border-gray-300 rounded-lg hover:bg-gray-200"
          >
            Pokračovat v auditu
          </button>
          <button
            @click="finishAudit"
            class="px-6 py-2 text-white transition bg-blue-600 rounded-lg hover:bg-blue-700"
          >
            ✓ Dokončit a uložit
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'

const router = useRouter()

// State
const assignments = ref([])
const selectedAssignmentId = ref(null)
const executionId = ref(null)
const assignedCategoryName = ref('')
const questionsByPosition = ref({})
const maxPosition = ref(4)
const answers = ref({})

// NOK dialog
const nokQuestionId = ref(null)
const nokComment = ref('')
const nokFile = ref(null)
const previewUrl = ref(null)
const fileInput = ref(null)

// Confirm dialog
const showFinishConfirm = ref(false)

// Computed
const totalQuestions = computed(() => {
  return Object.keys(questionsByPosition.value).length
})

const answeredCount = computed(() => {
  return Object.keys(answers.value).length
})

const progressPercentage = computed(() => {
  if (totalQuestions.value === 0) return 0
  return Math.round((answeredCount.value / totalQuestions.value) * 100)
})

const okCount = computed(() => {
  return Object.values(answers.value).filter(a => a === 'OK').length
})

const nokCount = computed(() => {
  return Object.values(answers.value).filter(a => a === 'NOK').length
})

const successRate = computed(() => {
  if (answeredCount.value === 0) return 0
  return Math.round((okCount.value / answeredCount.value) * 100)
})

// Lifecycle
onMounted(async () => {
  await loadAssignments()
  
  // Obnovit rozpracovaný audit
  const saved = localStorage.getItem('activeExecution')
  if (saved) {
    executionId.value = saved
    const exec = await api.get(`/executions/${saved}`)
    selectedAssignmentId.value = exec.data.assignment_id
    await loadExecution()
  }
})

// Methods
async function loadAssignments() {
  try {
    const res = await api.get('/assignments')
    assignments.value = res.data.filter(a => a.status !== 'done')
  } catch (error) {
    console.error('Chyba při načítání přidělení:', error)
  }
}

async function selectAssignment(assignment) {
  selectedAssignmentId.value = assignment.id
  await startAudit()
}

async function startAudit() {
  if (!selectedAssignmentId.value) return
  
  try {
    const res = await api.post(
      `/executions/start?assignment_id=${selectedAssignmentId.value}`
    )
    executionId.value = res.data.execution_id
    localStorage.setItem('activeExecution', executionId.value)
  } catch (err) {
    if (err.response?.status === 400) {
      const existing = await api.get(
        `/executions/by-assignment/${selectedAssignmentId.value}`
      )
      executionId.value = existing.data.execution_id
      localStorage.setItem('activeExecution', executionId.value)
    } else {
      alert('Nepodařilo se spustit audit')
      return
    }
  }
  
  await loadExecution()
}

async function loadExecution() {
  const res = await api.get(`/assignments/${selectedAssignmentId.value}`)
  const a = res.data
  
  assignedCategoryName.value = a.category_name
  
  await loadChecklist(a.template_id, a.category_id)
  await loadExistingAnswers()
}

async function loadChecklist(templateId, categoryId) {
  if (!templateId || !categoryId) return
  
  const res = await api.get(`/checklist/templates/${templateId}/questions`)
  const byPos = {}
  let max = 0
  
  res.data
    .filter(q => q.category_id === categoryId)
    .forEach(q => {
      byPos[q.position] = q
      if (q.position > max) max = q.position
    })
  
  questionsByPosition.value = byPos
  maxPosition.value = Math.max(max, 4)
}

async function loadExistingAnswers() {
  const res = await api.get(`/answers/execution/${executionId.value}`)
  answers.value = {}
  res.data.forEach(a => {
    answers.value[a.question_id] = a.odpoved
  })
}

async function saveAnswer(questionId, val) {
  if (val === 'NOK') {
    nokQuestionId.value = questionId
    return
  }
  await sendAnswer(questionId, val, null)
}

function handleFileChange(event) {
  const file = event.target.files[0]
  if (file) {
    nokFile.value = file
    previewUrl.value = URL.createObjectURL(file)
  }
}

function removePhoto() {
  nokFile.value = null
  previewUrl.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

async function confirmNok() {
  await sendAnswer(nokQuestionId.value, 'NOK', nokComment.value, nokFile.value)
  cancelNok()
}

function cancelNok() {
  nokQuestionId.value = null
  nokComment.value = ''
  removePhoto()
}

async function sendAnswer(questionId, value, comment = null, file = null) {
  const form = new FormData()
  form.append('audit_execution_id', executionId.value)
  form.append('question_id', questionId)
  form.append('odpoved', value)
  form.append('has_issue', value === 'NOK')
  
  if (comment) form.append('poznamka', comment)
  if (file) form.append('picture', file)
  
  try {
    await api.post('/answers', form, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    
    answers.value[questionId] = value
  } catch (error) {
    console.error('Chyba při ukládání odpovědi:', error)
    alert('Nepodařilo se uložit odpověď')
  }
}

async function finishAudit() {
  try {
    await api.post(`/executions/finish?execution_id=${executionId.value}`)
    localStorage.removeItem('activeExecution')
    
    // Zobrazit úspěch a přesměrovat
    alert(`✅ Audit dokončen!\n\nCelkem: ${totalQuestions.value}\nOK: ${okCount.value}\nNOK: ${nokCount.value}\nÚspěšnost: ${successRate.value}%`)
    
    router.push('/dashboard')
  } catch (error) {
    console.error('Chyba při dokončování auditu:', error)
    alert('Nepodařilo se dokončit audit')
  }
}

function formatDate(dateString) {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleDateString('cs-CZ')
}
</script>