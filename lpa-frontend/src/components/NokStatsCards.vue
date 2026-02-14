<template>
  <div class="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-5">
    <!-- Celkem NOK -->
    <div class="p-6 transition-transform bg-white border-l-4 border-red-500 rounded-lg shadow hover:scale-105">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm text-gray-600">Celkem NOK</p>
          <p class="text-3xl font-bold text-red-600">{{ stats.total }}</p>
        </div>
        <div class="text-4xl">🚨</div>
      </div>
    </div>

    <!-- Otevřené -->
    <div class="p-6 transition-transform bg-white border-l-4 border-orange-500 rounded-lg shadow hover:scale-105">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm text-gray-600">Otevřené</p>
          <p class="text-3xl font-bold text-orange-600">{{ stats.open }}</p>
        </div>
        <div class="text-4xl">⚠️</div>
      </div>
    </div>

    <!-- Přiřazené -->
    <div class="p-6 transition-transform bg-white border-l-4 border-blue-500 rounded-lg shadow hover:scale-105">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm text-gray-600">Přiřazené</p>
          <p class="text-3xl font-bold text-blue-600">{{ stats.assigned }}</p>
        </div>
        <div class="text-4xl">👤</div>
      </div>
    </div>

    <!-- Vyřešené -->
    <div class="p-6 transition-transform bg-white border-l-4 border-green-500 rounded-lg shadow hover:scale-105">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm text-gray-600">Vyřešené</p>
          <p class="text-3xl font-bold text-green-600">{{ stats.resolved }}</p>
        </div>
        <div class="text-4xl">✅</div>
      </div>
    </div>

    <!-- Po termínu -->
    <div class="p-6 transition-transform bg-white border-l-4 border-purple-500 rounded-lg shadow hover:scale-105">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm text-gray-600">Po termínu</p>
          <p class="text-3xl font-bold text-purple-600">{{ stats.overdue }}</p>
        </div>
        <div class="text-4xl">⏰</div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  stats: {
    type: Object,
    required: true,
    default: () => ({
      total: 0,
      open: 0,
      assigned: 0,
      resolved: 0,
      overdue: 0,
    })
  }
})
</script>