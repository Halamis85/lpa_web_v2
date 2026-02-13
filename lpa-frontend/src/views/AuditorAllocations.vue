<template>
  <div style="padding: 20px;">
    <h2>📋 Rozlosování auditorů</h2>

    <table border="1" cellpadding="6">
      <thead>
        <tr>
          <th>Auditor</th>
          <th>Linka</th>
          <th>Oblast</th>
          <th>Měsíc</th>
          <th>Termín</th>
          <th>Stav</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="a in allocations" :key="a.auditor + a.line + a.month">
          <td>{{ a.auditor }}</td>
          <td>{{ a.line }}</td>
          <td>{{ a.category }}</td>
          <td>{{ a.month }}</td>
          <td>{{ a.termin }}</td>
          <td>{{ a.status }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import api from "../api";

export default {
  data() { return { allocations: [] }; },
  async mounted() {
    const res = await api.get("/assignments/allocations");
    this.allocations = res.data;
  }
};
</script>
