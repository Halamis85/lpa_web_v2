<template>
  <div>
    <!-- KPI KARTY -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      <div class="bg-white p-4 rounded-lg shadow">
        <h4 class="text-gray-500">Celkem auditů</h4>
        <p class="text-2xl font-bold">{{ kpi.audits_count }}</p>
      </div>

      <div class="bg-green-100 p-4 rounded-lg shadow border-l-4 border-green-500">
        <h4 class="text-gray-700">OK odpovědi</h4>
        <p class="text-2xl font-bold">{{ kpi.ok }}</p>
      </div>

      <div class="bg-red-100 p-4 rounded-lg shadow border-l-4 border-red-500">
        <h4 class="text-gray-700">NOK odpovědi</h4>
        <p class="text-2xl font-bold">{{ kpi.nok }}</p>
      </div>

      <div class="bg-white p-4 rounded-lg shadow">
        <h4 class="text-gray-500">Úspěšnost</h4>
        <p class="text-2xl font-bold">{{ kpi.percent_ok }}%</p>
      </div>
    </div>

    <!-- SEKCE: POSLEDNÍ AUDITY -->
    <div class="bg-white p-4 rounded-lg shadow mb-6">
      <h3 class="text-lg font-semibold mb-3">📝 Poslední audity</h3>

      <table class="min-w-full border rounded-lg overflow-hidden">
        <thead class="bg-gray-200">
          <tr>
            <th class="px-4 py-2 text-left">ID</th>
            <th class="px-4 py-2 text-left">Měsíc</th>
            <th class="px-4 py-2 text-left">Linka</th>
            <th class="px-4 py-2 text-left">Oblast</th>
            <th class="px-4 py-2 text-left">Auditor</th>
            <th class="px-4 py-2 text-left">Stav</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="a in lastAudits"
            :key="a.id"
            class="border-b hover:bg-gray-50"
          >
            <td class="px-4 py-2">{{ a.id }}</td>
            <td class="px-4 py-2">{{ a.month }}</td>
            <td class="px-4 py-2">{{ a.line }}</td>
            <td class="px-4 py-2">{{ a.category }}</td>
            <td class="px-4 py-2">{{ a.auditor }}</td>
            <td class="px-4 py-2">
              <span
                class="px-2 py-1 rounded text-sm"
                :class="a.status === 'done' ? 'bg-green-200' : 'bg-yellow-200'"
              >
                {{ a.status }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
        <!-- GRAF OK vs NOK -->
    <div class="bg-white p-4 rounded-lg shadow mt-6">
      <h3 class="text-lg font-semibold mb-3">📈 OK vs NOK (posledních 6 měsíců)</h3>
      <canvas id="trendChart" class="w-full h-64"></canvas>
    </div>
  </div>
</template>

<script>
import Chart from "chart.js/auto";
import api from "../api";

export default {
  data() {
    return {
      kpi: {
        audits_count: 0,
        ok: 0,
        nok: 0,
        percent_ok: 0,
      },
      lastAudits: [],
    };
  },

  async mounted() {
    await this.loadKPI();
    await this.loadLastAudits();
    await this.loadTrend();
  },

  methods: {
    async loadKPI() {
      try {
        const res = await api.get("/dashboard/kpi");
        this.kpi = res.data;
      } catch {
        // fallback, pokud endpoint ještě neexistuje
        this.kpi = {
          audits_count: 0,
          ok: 0,
          nok: 0,
          percent_ok: 0,
        };
      }
    },

    async loadLastAudits() {
      try {
        const res = await api.get("/dashboard/last-audits");
        this.lastAudits = res.data;
      } catch {
        this.lastAudits = [];
      }
    },
    //gRAF
      async loadTrend() {
        const res = await api.get("/dashboard/trend");
        const data = res.data;

        const labels = data.map(d => d.month);
        const okData = data.map(d => d.ok);
        const nokData = data.map(d => d.nok);

      new Chart(document.getElementById("trendChart"), {
        type: "doughnut",
        data: {
          labels,
          datasets: [
            {
              label: "OK",
              data: okData,
              borderColor: "#22c55e",
              backgroundColor: "rgba(34,197,94,0.1)",
              tension: 0.3,
            },
            {
              label: "NOK",
              data: nokData,
              borderColor: "#ef4444",
              backgroundColor: "rgba(239,68,68,0.1)",
              tension: 0.3,
            },
          ],
        },
        options: {
          responsive: true,
          plugins: {
            legend: { position: "top" },
          },
          scales: {
            y: { beginAtZero: true },
          },
        },
      });
    },
  },
};
</script>
