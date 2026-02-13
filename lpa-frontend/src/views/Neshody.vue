<template>
  <div style="padding: 20px; max-width: 1200px; margin: auto;">
    <h2>⚠️ Přehled neshod</h2>

    <button @click="loadNeshody">🔄 Obnovit</button>

    <table border="1" cellpadding="6" style="width: 100%; margin-top: 15px;">
      <thead>
        <tr>
          <th>ID</th>
          <th>Linka</th>
          <th>Oblast</th>
          <th>Popis</th>
          <th>Závažnost</th>
          <th>Stav</th>
          <th>Řešitel</th>
          <th>Akce</th>
        </tr>
      </thead>

      <tbody>
        <tr v-for="n in neshody" :key="n.id">
          <td>{{ n.id }}</td>
          <td>{{ n.line_name }}</td>
          <td>{{ n.category_name }}</td>
          <td>{{ n.popis }}</td>
          <td>{{ n.zavaznost }}</td>
          <td>{{ n.status }}</td>
          <td>
            {{ solverName(n.solver_id) || "—" }}
          </td>
          <td>
            <button @click="openDetail(n)">📄 Detail</button>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- MODAL DETAIL NESHODY -->
    <div
      v-if="showDetail"
      style="
        position: fixed;
        top: 10%;
        left: 25%;
        width: 50%;
        background: white;
        padding: 20px;
        border: 1px solid black;
        box-shadow: 0 0 10px rgba(0,0,0,.3);
      "
    >
      <h3>Detail neshody #{{ selected.id }}</h3>

      <p><strong>Linka:</strong> {{ selected.line_name }}</p>
      <p><strong>Oblast:</strong> {{ selected.category_name }}</p>
      <p><strong>Popis:</strong> {{ selected.popis }}</p>
      <p><strong>Závažnost:</strong> {{ selected.zavaznost }}</p>
      <p><strong>Stav:</strong> {{ selected.status }}</p>

      <div v-if="selected.picture_url" style="margin: 10px 0;">
        <strong>Fotka:</strong><br />
        <img
            :src="backendUrl + '/' + selected.picture_url"
            style="max-width: 100%; border: 1px solid #ccc;"
        />
      </div>

      <hr />

      <!-- Přidělení řešitele -->
      <div v-if="selected.status === 'open'">
        <h4>👤 Přidělit řešitele</h4>
        <select v-model="selectedSolverId">
          <option :value="null">-- vyber řešitele --</option>
          <option
            v-for="u in solvers"
            :key="u.id"
            :value="u.id"
          >
            {{ u.jmeno }}
          </option>
        </select>
        <button @click="assignSolver">Přidělit</button>
      </div>

      <!-- Řešení neshody -->
      <div v-if="selected.status === 'in_progress'">
        <h4>🛠️ Navrhnout řešení</h4>
        <textarea
          v-model="solutionNote"
          placeholder="Popis řešení..."
          style="width: 100%; height: 80px;"
        ></textarea>

        <div style="margin-top: 10px;">
          <label>Termín nápravy:</label>
          <input type="date" v-model="solutionDeadline" />
        </div>

        <button @click="resolveNeshoda">Označit jako vyřešené</button>
      </div>

      <!-- Uzavření neshody (jen admin) -->
      <div v-if="selected.status === 'resolved' && currentUser?.role === 'admin'">
        <h4>🔒 Uzavřít neshodu</h4>
        <button @click="closeNeshoda">Uzavřít</button>
      </div>

      <div style="text-align: right; margin-top: 15px;">
        <button @click="showDetail = false">Zavřít</button>
      </div>
    </div>
  </div>
</template>

<script>
import api from "../api";

export default {
  data() {
    return {
      neshody: [],
      solvers: [],
      currentUser: null,

      showDetail: false,
      selected: null,
      selectedSolverId: null,
      solutionNote: "",
      solutionDeadline: null,
      backendUrl: "http://127.0.0.1:8000",
    };
  },

  async mounted() {
    await this.loadNeshody();
    await this.loadSolvers();
    await this.loadMe();
  },

  methods: {
    async loadNeshody() {
      const res = await api.get("/neshody");
      this.neshody = res.data;
    },

    async loadSolvers() {
      const res = await api.get("/users");
      this.solvers = res.data.filter(u => u.role === "solver");
    },

    async loadMe() {
      const res = await api.get("/me");
      this.currentUser = res.data;
    },

    solverName(id) {
      const s = this.solvers.find(u => u.id === id);
      return s ? s.jmeno : null;
    },

    openDetail(n) {
      this.selected = n;
      this.selectedSolverId = n.solver_id || null;
      this.solutionNote = n.poznamka || "";
      this.solutionDeadline = n.termin || null;
      this.showDetail = true;
    },

    async assignSolver() {
      if (!this.selectedSolverId) {
        alert("Vyber řešitele");
        return;
      }

      await api.post(
        `/neshody/${this.selected.id}/assign?solver_id=${this.selectedSolverId}`
      );

      alert("Řešitel přidělen");
      this.showDetail = false;
      await this.loadNeshody();
    },

    async resolveNeshoda() {
      if (!this.solutionNote || !this.solutionDeadline) {
        alert("Vyplňte poznámku i termín");
        return;
      }

      await api.post(
        `/neshody/${this.selected.id}/resolve`,
        null,
        {
          params: {
            poznamka: this.solutionNote,
            termin: this.solutionDeadline,
          },
        }
      );

      alert("Neshoda označena jako vyřešená");
      this.showDetail = false;
      await this.loadNeshody();
    },

    async closeNeshoda() {
      await api.post(`/neshody/${this.selected.id}/close`);
      alert("Neshoda uzavřena");
      this.showDetail = false;
      await this.loadNeshody();
    },
  },
};
</script>
