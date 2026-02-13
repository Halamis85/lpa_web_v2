<template>
  <div>
    <h2 class="mb-4 text-2xl font-bold">📋 Rozlosování auditů</h2>

    <div class="flex items-center gap-3 mb-4">
      <input
        v-model="month"
        type="month"
        class="w-48 input"
      />
      <button @click="load" class="btn-primary">
        Načíst
      </button>
            <button @click="generate" class="btn-secondary">
         Vygenerovat  
      </button>
    </div>
    <div class="flex items-center gap-3 mb-4">

    </div>
    <div v-if="lines.length" class="overflow-auto">
      <table class="table">
        <thead>
          <tr>
            <th>Auditor</th>
            <th v-for="l in lines" :key="l">{{ l }}</th>
          </tr>
        </thead>

        <tbody>
          <tr v-for="a in auditors" :key="a">
            <td class="font-semibold">{{ a }}</td>

            <td
              v-for="l in lines"
              :key="l"
              class="text-center"
            >
              <span
                v-if="matrix[a][l]"
                class="px-2 py-1 text-blue-800 bg-blue-100 rounded"
              >
                {{ matrix[a][l] }}
              </span>
              <span v-else class="text-gray-300">—</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-else class="text-gray-500">
      Žádné rozlosování pro tento měsíc
    </div>
  </div>
</template>

<script>
import api from "../api";

export default {
  data() {
    return {
      month: new Date().toISOString().slice(0, 7),
      lines: [],
      auditors: [],
      matrix: {},
    };
  },

  mounted() {
    this.load();
  },

  methods: {
    async load() {
      const res = await api.get(`/allocations/matrix/${this.month}`);
      this.lines = res.data.lines;
      this.auditors = res.data.auditors;
      this.matrix = res.data.matrix;
    },
     async generate() {
     await api.post(`/campaigns/${this.month}/generate-assignments`);
     await this.load();
    }
  },
};
</script>
