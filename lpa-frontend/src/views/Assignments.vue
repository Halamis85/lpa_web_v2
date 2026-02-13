<template>
  <div style="padding: 20px; max-width: 1000px; margin: auto;">
    <h2>📋 Moje přidělení (LPA audity)</h2>

    <button @click="loadAssignments">🔄 Obnovit</button>

    <table border="1" cellpadding="6" style="width: 100%; margin-top: 15px; text-align: center;">
      <thead>
        <tr>
          <th>ID</th>
          <th>Měsíc</th>
          <th>Linka</th>
          <th>Oblast</th>
          <th>Termín</th>
          <th>Stav</th>
          <th>Akce</th>
        </tr>
      </thead>

      <tbody>
        <tr v-for="a in assignments" :key="a.id">
          <td>{{ a.id }}</td>
          <td>{{ a.month }}</td>
          <td>{{ a.line_name }}</td>
          <td>{{ a.category_name }}</td>
          <td>{{ a.termin }}</td>
          <td>
            <span :style="{ fontWeight: 'bold' }">
              {{ a.status }}
              <select v-model="a.status" @change="changeStatus(a)">
                <option value="pending">pending</option>
                <option value="in_progress">in_progress</option>
                <option value="done">done</option>
              </select>
            </span>
          </td>
          <td>
            <button
              v-if="a.status === 'pending'"
              @click="goToAudit(a.id)"
            >
              ▶️ Zahájit audit
            </button>

            <button
              v-else-if="a.status === 'in_progress'"
              @click="goToAudit(a.id)"
            >
              🔁 Pokračovat
            </button>

            <button
              v-else
              @click="viewAudit(a.id)"
            >
              👁️ Zobrazit
            </button>
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
    return {
      assignments: [],
    };
  },

  async mounted() {
    await this.loadAssignments();
  },

  methods: {
    async loadAssignments() {
      const res = await api.get("/assignments");
      this.assignments = res.data;
    },

    goToAudit(assignmentId) {
      this.$router.push({
        path: "/audit",
        query: { assignment_id: assignmentId },
      });
    },

    viewAudit(assignmentId) {
  this.$router.push({
    path: "/audit-report",
    query: { assignment_id: assignmentId },
  });
  },
  async changeStatus(a) {
  await api.post(
    `/assignments/${a.id}/set-status?status=${a.status}`
  );
  alert("Stav aktualizován");
}
 }
}

</script>
