<template>
  <div style="padding: 20px; max-width: 1000px; margin: auto;">
    <h2>📄 Zobrazení hotového auditu</h2>

    <div v-if="report">
      <p><strong>Měsíc:</strong> {{ report.campaign_month }}</p>
      <p><strong>Linka:</strong> {{ report.line }}</p>
      <p><strong>Oblast:</strong> {{ report.category }}</p>
      <p><strong>Datum provedení:</strong> {{ report.assignment.datum_provedeni }}</p>

      <table border="1" style="width: 100%; margin-top: 10px;">
        <thead>
          <tr>
            <th>Pozice</th>
            <th>Otázka</th>
            <th>Odpověď</th>
            <th>Fotka</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="a in report.answers" :key="a.question_id">
            <td>{{ a.position }}</td>
            <td>{{ a.question_text }}</td>
            <td>
              <span :style="{ color: a.odpoved === 'nok' ? 'red' : 'green' }">
                {{ a.odpoved.toUpperCase() }}
              </span>
            </td>
            <td>
              <img
                v-if="a.picture_url"
                :src="backendUrl + '/' + a.picture_url"
                style="max-width: 150px;"
              />
              <span v-else>—</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <button @click="$router.back()">⬅️ Zpět</button>
  </div>
</template>

<script>
import api from "../api";

export default {
  data() {
    return {
      report: null,
      backendUrl: "http://127.0.0.1:8000",
    };
  },

  async mounted() {
    const assignmentId = this.$route.query.assignment_id;
    const res = await api.get(`/assignments/${assignmentId}/report`);
    this.report = res.data;
  },
};
</script>
