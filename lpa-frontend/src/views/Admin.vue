<template>
  <div class="space-y-8">

    <h2 class="text-2xl font-bold">🔧 Administrace</h2>
    <!-- ======================== Rozdělení auditu ==========-->
    <div class="object-center p-6 bg-white shadow rounded-xl ">
     <div class="grid grid-cols-2 gap-2">
       <h3 class="mb-4 text-lg font-semibold">📅 Nový měsíc (rozlosování)</h3>

        <div class="">
         <button @click="autoGenerateMonth" class="btn-primary">
           🪄 Zahájit rozlosovat audity
         </button>
        </div>
     </div>
  </div>
    <!-- ===================== USERS ===================== -->
    <div class="p-6 bg-white shadow rounded-xl">
      <h3 class="mb-4 text-lg font-semibold">👥 Správa uživatelů</h3>

      <!-- Add user -->
      <div class="grid grid-cols-1 gap-3 mb-6 md:grid-cols-4">
        <input
          v-model="newName"
          placeholder="Jméno"
          class="input"
        />
        <input
          v-model="newEmail"
          placeholder="Email"
          class="input"
        />
        <select v-model="newRole" class="input">
          <option value="auditor">Auditor</option>
          <option value="solver">Řešitel</option>
          <option value="admin">Admin</option>
        </select>
        <button @click="addUser" class="btn-primary">
          Přidat
        </button>
      </div>

      <!-- Users table -->
      <div class="overflow-x-auto">
        <table class="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Jméno</th>
              <th>Email</th>
              <th>Role</th>
              <th>Akce</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="u in users" :key="u.id">
              <td>{{ u.id }}</td>
              <td>{{ u.jmeno }}</td>
              <td>{{ u.email }}</td>
              <td>
                <select
                  v-model="u.role"
                  @change="updateRole(u)"
                  class="input-sm"
                >
                  <option value="auditor">Auditor</option>
                  <option value="solver">Řešitel</option>
                  <option value="admin">Admin</option>
                </select>
              </td>
              <td>
                <button
                  @click="initPasswords"
                  class="btn-secondary"
                >
                  🔐 Reset hesel
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ===================== LINES ===================== -->
    <div class="p-6 bg-white shadow rounded-xl">
      <h3 class="mb-4 text-lg font-semibold">🏭 Linky</h3>

      <div class="flex gap-3 mb-4">
        <input
          v-model="lineName"
          placeholder="Např. Sklad"
          class="flex-1 input"
        />
        <button @click="addLine" class="btn-primary">
          Přidat linku
        </button>
      </div>

      <ul class="pl-6 text-gray-700 list-disc">
        <li v-for="l in lines" :key="l.id">
          {{ l.name }}
        </li>
      </ul>
    </div>

    <!-- ===================== CHECKLIST ===================== -->
    <div class="p-6 bg-white shadow rounded-xl">
      <h3 class="mb-4 text-lg font-semibold">📋 Checklist šablony</h3>

      <div class="grid grid-cols-1 gap-3 mb-4 md:grid-cols-3">
        <select v-model="selectedLineId" @change="loadOrCreateTemplate" class="input">
          <option :value="null">Vyber linku</option>
          <option v-for="l in lines" :key="l.id" :value="l.id">
            {{ l.name }}
          </option>
        </select>

        <select v-model="selectedCategoryId" class="input">
          <option :value="null">Vyber kategorii</option>
          <option v-for="c in categories" :key="c.id" :value="c.id">
            {{ c.name }}
          </option>
        </select>

        <input
          v-model="newPosition"
          type="number"
          placeholder="Pozice"
          class="input"
        />
      </div>

      <div class="flex gap-3 mb-6">
        <input
          v-model="newQuestionText"
          placeholder="Text otázky"
          class="flex-1 input"
        />
        <button @click="addQuestion" class="btn-primary">
          Přidat otázku
        </button>
      </div>

      <!-- Matrix -->
      <div v-if="templateId" class="overflow-x-auto">
        <table class="table">
          <thead>
            <tr>
              <th>Pozice</th>
              <th v-for="c in categories" :key="c.id">
                {{ c.name }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="pos in maxPosition" :key="pos">
              <td class="font-semibold">{{ pos }}</td>
              <td v-for="c in categories" :key="c.id">
                <span v-if="questionsMatrix[c.name]?.[pos]">
                  {{ questionsMatrix[c.name][pos].question_text }}
                </span>
                <span v-else class="text-gray-400">
                  –
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

  </div>
</template>

<script>
import router from "@/router";
import api from "../api";

export default {
  data() {
    return {
      areaName: "",
      areas: [],

      templateName: "",
      templates: [],
      selectedTemplate: null,

      questionText: "",
      questions: [],

      users: [],
      newName: "",
      newEmail: "",
      newRole: "auditor",

      lineName: "",
      lines: [],
      categories: [],
      selectedLineId: null,
      templateId: null,
      selectedCategoryId: null,
      newQuestionText: "",
      newPosition: 1,

      questionsMatrix: {},
      maxPosition: 4,
      campaignMonth: "",
      autoMonth: "",
    };
  },

  async mounted() {
    await this.loadAreas();
    await this.loadTemplates();
    await this.loadLines();
    await this.loadUsers();
    this.loadCategories();
    this.loadLines();
  },

  methods: {
    async loadAreas() {
      this.areas = (await api.get("/areas")).data;
    },

    async addArea() {
      if (!this.areaName) return;
      await api.post("/areas?name=" + encodeURIComponent(this.areaName));
      this.areaName = "";
      await this.loadAreas();
    },
    
    async addLine() {
     if (!this.lineName) return;
     await api.post("/lines?name=" + encodeURIComponent(this.lineName));
     this.lineName = "";
    await this.loadLines();
    },

    async loadTemplates() {
      // zatím backend nemá GET /checklist/templates → přidáme za chvíli
      try {
        this.templates = (await api.get("/checklist/templates")).data;
      } catch {
        this.templates = [];
      }
    },

    async addTemplate() {
      if (!this.templateName) return;
      await api.post("/checklist/templates?name=" + encodeURIComponent(this.templateName));
      this.templateName = "";
      await this.loadTemplates();
    },

    async selectTemplate(t) {
      this.selectedTemplate = t;
      await this.loadQuestions();
    },

    async loadQuestions() {
      this.questions = (
        await api.get(`/checklist/${this.selectedTemplate.id}/questions`)
      ).data;
    },

    //Uživatele 
    async loadUsers() {
    this.users = (await api.get("/users")).data;
    },

    async addUser() {
    if (!this.newName || !this.newEmail) return;

    await api.post(
    `/users?jmeno=${encodeURIComponent(this.newName)}&email=${encodeURIComponent(
      this.newEmail
    )}&role=${this.newRole}`
    );

    this.newName = "";
    this.newEmail = "";
    this.newRole = "auditor";
    await this.loadUsers();
    },

    async updateRole(user) {
    await api.patch(`/users/${user.id}/role?role=${user.role}`);
    await this.loadUsers();
    },

    async initPasswords() {
    await api.post("/users/init-passwords");
    alert("Hesla byla nastavena = email");
    },
    async loadLines() {
    const res = await api.get("/lines");
    this.lines = res.data;
    },

    async loadCategories() {
    const res = await api.get("/checklist/categories");
    this.categories = res.data;
    },

    async loadOrCreateTemplate() {
      if (!this.selectedLineId) return;

    const res = await api.post(
      `/checklist/templates/for-line?line_id=${this.selectedLineId}`
    );

    this.templateId = res.data.id;

    await this.loadQuestionsMatrix();
    },

    async addQuestion() {
      if (!this.templateId || !this.selectedCategoryId) {
      alert("Vyberte linku a kategorii");
      return;
      }
  

    await api.post("/checklist/questions", null, {
      params: {
      template_id: this.templateId,
      category_id: this.selectedCategoryId,
      question_text: this.newQuestionText,
      position: this.newPosition,
      },
    });

    alert("Otázka přidána");
    this.newQuestionText = "";
    await this.loadQuestionsMatrix();
     },
    

    async loadQuestionsMatrix() {
    if (!this.templateId) return;

    const res = await api.get(
    `/checklist/templates/${this.templateId}/questions`
    );
    const questions = res.data;

    // Inicializace prázdné matice podle kategorií
   const matrix = {};
    this.categories.forEach(c => {
    matrix[c.name] = {};
    });

    // Naplnění matice
    questions.forEach(q => {
      const category = this.categories.find(c => c.id === q.category_id);
    if (category) {
      matrix[category.name][q.position] = q;
    }
    });

    this.questionsMatrix = matrix;  
    },

    async deleteQuestion(id) {
     if (!confirm("Opravdu chcete tuto otázku smazat?")) return;

    await api.delete(`/checklist/questions/${id}`);
    await this.loadQuestionsMatrix();
    },
    async updateQuestion(q) {
    await api.patch(
      `/checklist/questions/${q.id}?question_text=${encodeURIComponent(q.question_text)}`
    );
    },
    async createCampaign() {
     if (!this.campaignMonth) return;
    await api.post(`/campaigns?month=${this.campaignMonth}`);
    alert("Kampaň vytvořena");
    },

    async generateAssignments() {
      if (!this.campaignMonth) {
    alert("Nejprve zadejte měsíc kampaně");
    return;
    }

    const res = await api.post(
      `/campaigns/${this.campaignMonth}/generate-assignments`
    );
    alert("Přidělení vygenerována");
    },

    async autoGenerateCurrentMonth() {
  try {
    const res = await api.post("/campaigns/auto-generate-current");
    alert(res.data.message);
  } catch (e) {
    alert(
      e.response?.data?.detail ||
      "Chyba při automatickém generování přidělení"
    );
   }
  },

    async autoGenerateMonth() {
    try {
      const res = await api.post("/campaigns/auto-generate-current");
      alert(res.data.message || "Kampaň vytvořena a audity rozlosovány");
    } catch (err) {
      alert(err.response?.data?.detail || "Chyba při generování kampaně");
    }
    }
  }
}
</script>
