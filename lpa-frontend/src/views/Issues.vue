<template>
  <div>
    <h2 class="mb-4 text-2xl font-bold">⚠️ Neshody</h2>

    <table class="table">
      <thead>
        <tr>
          <th>ID</th>
          <th>Popis</th>
          <th>Stav</th>
          <th>Termín</th>
          <th>Akce</th>
        </tr>
      </thead>

      <tbody>
        <tr v-for="i in issues" :key="i.id">
          <td>{{ i.id }}</td>
          <td>{{ i.popis }}</td>
          <td>
            <span class="px-2 py-1 bg-yellow-200 rounded">{{ i.status }}</span>
          </td>
          <td>{{ i.termin || "-" }}</td>

          <td class="space-x-2">
            <button v-if="i.status=='open'" @click="take(i.id)" class="btn-primary">Převzít</button>
            <button v-if="i.status=='in_progress'" @click="resolve(i.id)" class="btn-secondary">Vyřešeno</button>
            <button v-if="i.status=='resolved'" @click="close(i.id)" class="btn-secondary">Uzavřít</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import api from "../api";

export default {
  data() {
    return { issues: [] };
  },
  mounted() { this.load(); },

  methods: {
    async load() {
      this.issues = (await api.get("/neshody")).data;
    },
    async take(id) {
      await api.post(`/neshody/${id}/take`);
      this.load();
    },
    async resolve(id) {
      await api.post(`/neshody/${id}/resolve`);
      this.load();
    },
    async close(id) {
      await api.post(`/neshody/${id}/close`);
      this.load();
    },
  },
};
</script>
