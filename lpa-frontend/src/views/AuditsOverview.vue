<template>
  <div style="padding: 20px;">
    <h2>📑 Přehled provedených auditů</h2>

    <table border="1" cellpadding="6">
      <thead>
        <tr>
          <th>ID</th>
          <th>Měsíc</th>
          <th>Linka</th>
          <th>Oblast</th>
          <th>Auditor</th>
          <th>Datum</th>
          <th>Akce</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="a in audits" :key="a.id">
          <td>{{ a.id }}</td>
          <td>{{ a.month }}</td>
          <td>{{ a.line }}</td>
          <td>{{ a.category }}</td>
          <td>{{ a.auditor }}</td>
          <td>{{ a.datum }}</td>
          <td>
            <button @click="viewSummary(a.id)">📊 Souhrn</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import api from "../api";

export default {
  data() { return { audits: [] }; },
  async mounted() {
    const res = await api.get("/assignments/completed");
    this.audits = res.data;
  },
  methods: {
    viewSummary(id) {
      this.$router.push({ path: "/audit-summary", query: { assignment_id: id }});
    }
  }
};
</script>
