<template>
  <div class="p-6 bg-white rounded-lg shadow">
    <div 
      class="flex items-center justify-between cursor-pointer"
      @click="isExpanded = !isExpanded"
    >
      <h3 class="flex items-center gap-2 text-lg font-semibold text-gray-800">
        <span>🔍</span>
        <span>Filtry</span>
      </h3>
      <button class="text-2xl text-gray-500 hover:text-gray-700">
        {{ isExpanded ? '▼' : '▶' }}
      </button>
    </div>

    <div v-if="isExpanded" class="mt-6">
      <div class="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
        <!-- Linka -->
        <div>
          <label class="block mb-2 text-sm font-medium text-gray-700">Linka</label>
          <select
            v-model="localFilters.line_id"
            @change="emitChange"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option :value="null">Všechny linky</option>
            <option v-for="line in lines" :key="line.id" :value="line.id">
              {{ line.name }}
            </option>
          </select>
        </div>

        <!-- Kategorie -->
        <div>
          <label class="block mb-2 text-sm font-medium text-gray-700">Kategorie</label>
          <select
            v-model="localFilters.category_id"
            @change="emitChange"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option :value="null">Všechny kategorie</option>
            <option v-for="cat in categories" :key="cat.id" :value="cat.id">
              {{ cat.name }}
            </option>
          </select>
        </div>

        <!-- Stav -->
        <div>
          <label class="block mb-2 text-sm font-medium text-gray-700">Stav</label>
          <select
            v-model="localFilters.status"
            @change="emitChange"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option :value="null">Všechny stavy</option>
            <option value="open">Otevřené</option>
            <option value="assigned">Přiřazené</option>
            <option value="in_progress">V řešení</option>
            <option value="resolved">Vyřešené</option>
            <option value="closed">Uzavřené</option>
          </select>
        </div>

        <!-- Řešitel -->
        <div>
          <label class="block mb-2 text-sm font-medium text-gray-700">Řešitel</label>
          <select
            v-model="localFilters.solver_id"
            @change="emitChange"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option :value="null">Všichni řešitelé</option>
            <option v-for="solver in solvers" :key="solver.id" :value="solver.id">
              {{ solver.jmeno }}
            </option>
          </select>
        </div>

        <!-- Datum od -->
        <div>
          <label class="block mb-2 text-sm font-medium text-gray-700">Datum od</label>
          <input
            type="date"
            v-model="localFilters.date_from"
            @change="emitChange"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        <!-- Datum do -->
        <div>
          <label class="block mb-2 text-sm font-medium text-gray-700">Datum do</label>
          <input
            type="date"
            v-model="localFilters.date_to"
            @change="emitChange"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        <!-- Vyhledávání -->
        <div class="md:col-span-2">
          <label class="block mb-2 text-sm font-medium text-gray-700">Vyhledávání</label>
          <input
            type="text"
            v-model="localFilters.search"
            @input="emitChange"
            placeholder="Hledat v otázkách a popisech..."
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
      </div>

      <!-- Akce -->
      <div class="flex justify-end mt-4">
        <button
          @click="resetFilters"
          class="flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 transition bg-gray-100 border border-gray-300 rounded-lg hover:bg-gray-200"
        >
          <span>🔄</span>
          <span>Resetovat filtry</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  filters: {
    type: Object,
    required: true
  },
  lines: {
    type: Array,
    default: () => []
  },
  categories: {
    type: Array,
    default: () => []
  },
  solvers: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:filters', 'reset'])

const isExpanded = ref(true)
const localFilters = ref({ ...props.filters })

watch(() => props.filters, (newFilters) => {
  localFilters.value = { ...newFilters }
}, { deep: true })

function emitChange() {
  emit('update:filters', { ...localFilters.value })
}

function resetFilters() {
  localFilters.value = {
    line_id: null,
    category_id: null,
    status: null,
    solver_id: null,
    date_from: null,
    date_to: null,
    search: '',
  }
  emit('reset')
  emit('update:filters', { ...localFilters.value })
}
</script>