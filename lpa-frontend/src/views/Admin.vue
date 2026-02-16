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

    <!-- ===================== USERS - VYLEPŠENÁ SEKCE ===================== -->
    <div class="p-6 bg-white shadow rounded-xl">
      <h3 class="mb-4 text-lg font-semibold">👥 Správa uživatelů</h3>

      <!-- Add user -->
      <div class="p-4 mb-6 bg-gray-50 rounded-lg">
        <h4 class="mb-3 font-semibold">Přidat nového uživatele</h4>
        <div class="grid grid-cols-1 gap-3 md:grid-cols-5">
          <input
            v-model="newUser.jmeno"
            placeholder="Jméno"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <input
            v-model="newUser.email"
            placeholder="Email"
            type="email"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          
          <!-- Více rolí - checkboxy -->
          <div class="flex flex-col gap-2">
            <label class="text-sm font-medium text-gray-700">Role:</label>
            <div class="flex gap-3">
              <label class="flex items-center gap-1">
                <input
                  type="checkbox"
                  value="auditor"
                  v-model="newUser.roles"
                  class="rounded"
                />
                <span class="text-sm">Auditor</span>
              </label>
              <label class="flex items-center gap-1">
                <input
                  type="checkbox"
                  value="solver"
                  v-model="newUser.roles"
                  class="rounded"
                />
                <span class="text-sm">Řešitel</span>
              </label>
              <label class="flex items-center gap-1">
                <input
                  type="checkbox"
                  value="admin"
                  v-model="newUser.roles"
                  class="rounded"
                />
                <span class="text-sm">Admin</span>
              </label>
            </div>
          </div>

          <label class="flex items-center gap-2">
            <input
              type="checkbox"
              v-model="newUser.sendEmail"
              class="rounded"
            />
            <span class="text-sm">Poslat email</span>
          </label>

          <button @click="addUser" class="px-4 py-2 text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition">
            ➕ Přidat uživatele
          </button>
        </div>
      </div>

      <!-- Users table -->
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead class="bg-gray-100">
            <tr>
              <th class="px-4 py-3 font-semibold text-gray-700">ID</th>
              <th class="px-4 py-3 font-semibold text-gray-700">Jméno</th>
              <th class="px-4 py-3 font-semibold text-gray-700">Email</th>
              <th class="px-4 py-3 font-semibold text-gray-700">Role</th>
              <th class="px-4 py-3 font-semibold text-gray-700">Stav</th>
              <th class="px-4 py-3 font-semibold text-gray-700">Změna hesla</th>
              <th class="px-4 py-3 font-semibold text-gray-700">Akce</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="u in users" :key="u.id" class="hover:bg-gray-50" :class="{'opacity-60': !u.is_active}">
              <td class="px-4 py-3 border-t border-gray-200">{{ u.id }}</td>
              <td class="px-4 py-3 border-t border-gray-200">{{ u.jmeno }}</td>
              <td class="px-4 py-3 border-t border-gray-200">{{ u.email }}</td>
              <td class="px-4 py-3 border-t border-gray-200">
                <div class="flex flex-wrap gap-1">
                  <span
                    v-for="role in u.roles"
                    :key="role"
                    :class="getRoleBadgeClass(role)"
                    class="px-2 py-1 text-xs rounded"
                  >
                    {{ getRoleLabel(role) }}
                  </span>
                </div>
              </td>
              <td class="px-4 py-3 border-t border-gray-200">
                <span v-if="u.is_active" 
                      class="px-2 py-1 text-xs rounded bg-green-100 text-green-800">
                  ✓ Aktivní
                </span>
                <span v-else 
                      class="px-2 py-1 text-xs rounded bg-red-100 text-red-800">
                  ✗ Neaktivní
                </span>
              </td>
              <td class="px-4 py-3 border-t border-gray-200">
                <span v-if="u.force_password_change" class="text-xs text-orange-600">
                  ⚠️ Vyžadováno
                </span>
                <span v-else class="text-xs text-green-600">
                  ✓ OK
                </span>
              </td>
              <td class="px-4 py-3 border-t border-gray-200 space-x-2">
                <button
                  @click="editUser(u)"
                  class="px-3 py-1 text-sm text-white bg-blue-600 rounded hover:bg-blue-700"
                  title="Upravit uživatele"
                >
                  ✏️ Upravit
                </button>
                <button
                  @click="resetPassword(u)"
                  class="px-3 py-1 text-sm text-white bg-orange-600 rounded hover:bg-orange-700"
                  title="Reset hesla"
                >
                  🔐 Reset
                </button>
                <button v-if="u.is_active"
                        @click="deactivateUser(u)" 
                        class="px-3 py-1 text-sm bg-red-500 text-white rounded hover:bg-red-600">
                  Deaktivovat
                </button>
                <button v-else
                        @click="activateUser(u)" 
                        class="px-3 py-1 text-sm bg-green-500 text-white rounded hover:bg-green-600">
                  Aktivovat
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modal pro editaci uživatele -->
    <div
      v-if="editingUser"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50"
      @click.self="closeEditModal"
    >
      <div class="w-full max-w-md p-6 bg-white rounded-lg shadow-xl">
        <h3 class="mb-4 text-xl font-semibold">Upravit uživatele</h3>
        
        <div class="space-y-4">
          <div>
            <label class="block mb-1 text-sm font-medium text-gray-700">Jméno</label>
            <input
              v-model="editingUser.jmeno"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Jméno"
            />
          </div>

          <div>
            <label class="block mb-1 text-sm font-medium text-gray-700">Email</label>
            <input
              v-model="editingUser.email"
              type="email"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Email"
            />
          </div>

          <div>
            <label class="block mb-2 text-sm font-medium text-gray-700">Role</label>
            <div class="flex flex-col gap-2">
              <label class="flex items-center gap-2">
                <input
                  type="checkbox"
                  value="auditor"
                  v-model="editingUser.roles"
                  class="rounded"
                />
                <span>Auditor</span>
              </label>
              <label class="flex items-center gap-2">
                <input
                  type="checkbox"
                  value="solver"
                  v-model="editingUser.roles"
                  class="rounded"
                />
                <span>Řešitel</span>
              </label>
              <label class="flex items-center gap-2">
                <input
                  type="checkbox"
                  value="admin"
                  v-model="editingUser.roles"
                  class="rounded"
                />
                <span>Admin</span>
              </label>
            </div>
          </div>
        </div>

        <div class="flex gap-3 mt-6">
          <button @click="saveUser" class="flex-1 px-4 py-2 text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition">
            💾 Uložit změny
          </button>
          <button @click="closeEditModal" class="flex-1 px-4 py-2 text-gray-700 bg-gray-200 rounded-lg hover:bg-gray-300 transition">
            ❌ Zrušit
          </button>
        </div>
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

      // Vylepšená správa uživatelů
      users: [],
      newUser: {
        jmeno: '',
        email: '',
        roles: [],
        sendEmail: true,
      },
      editingUser: null,

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
      this.areas = (await api.get("/areas/")).data;
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

    // ==================== VYLEPŠENÉ METODY PRO USERS ====================
    async loadUsers() {
      try {
        const res = await api.get('/users')
        this.users = res.data
      } catch (err) {
        console.error('Chyba při načítání uživatelů:', err)
        alert('❌ Nepodařilo se načíst uživatele')
      }
    },

    async addUser() {
      if (!this.newUser.jmeno || !this.newUser.email) {
        alert('⚠️ Vyplňte jméno a email')
        return
      }

      if (this.newUser.roles.length === 0) {
        alert('⚠️ Vyberte alespoň jednu roli')
        return
      }

      try {
        await api.post('/users', {
          jmeno: this.newUser.jmeno,
          email: this.newUser.email,
          roles: this.newUser.roles,
          send_email: this.newUser.sendEmail,
        })
        
        alert(`✅ Uživatel ${this.newUser.jmeno} byl vytvořen`)
        
        this.newUser = {
          jmeno: '',
          email: '',
          roles: [],
          sendEmail: true,
        }
        
        await this.loadUsers()
      } catch (err) {
        const errorMsg = err.response?.data?.detail || 'Chyba při vytváření uživatele'
        alert('❌ ' + errorMsg)
        console.error('Error creating user:', err)
      }
    },

    editUser(user) {
      this.editingUser = {
        id: user.id,
        jmeno: user.jmeno,
        email: user.email,
        roles: [...user.roles],
      }
    },

    async saveUser() {
      if (!this.editingUser.jmeno || !this.editingUser.email) {
        alert('⚠️ Vyplňte jméno a email')
        return
      }

      if (this.editingUser.roles.length === 0) {
        alert('⚠️ Vyberte alespoň jednu roli')
        return
      }

      try {
        await api.put(`/users/${this.editingUser.id}`, {
          jmeno: this.editingUser.jmeno,
          email: this.editingUser.email,
          roles: this.editingUser.roles,
        })
        
        alert('✅ Uživatel byl aktualizován')
        this.closeEditModal()
        await this.loadUsers()
      } catch (err) {
        const errorMsg = err.response?.data?.detail || 'Chyba při aktualizaci uživatele'
        alert('❌ ' + errorMsg)
        console.error('Error updating user:', err)
      }
    },

    closeEditModal() {
      this.editingUser = null
    },

    async deactivateUser(user) {
      if (!confirm(`Deaktivovat ${user.jmeno}?\n\nData zůstanou zachovaná.`)) return
      
      try {
        await api.delete(`/users/${user.id}`)
        alert(`✅ ${user.jmeno} deaktivován`)
        await this.loadUsers()
      } catch (err) {
        alert('❌ ' + (err.response?.data?.detail || 'Chyba'))
      }
    },

    async activateUser(user) {
      if (!confirm(`Aktivovat ${user.jmeno}?`)) return
      
      try {
        await api.post(`/users/${user.id}/activate`)
        alert(`✅ ${user.jmeno} aktivován`)
        await this.loadUsers()
      } catch (err) {
        alert('❌ ' + (err.response?.data?.detail || 'Chyba'))
      }
    },

    async resetPassword(user) {
      if (!confirm(`Opravdu chcete resetovat heslo pro ${user.jmeno}?`)) {
        return
      }

      try {
        const res = await api.post(`/users/${user.id}/reset-password`)
        alert(`✅ ${res.data.message}`)
        await this.loadUsers()
      } catch (err) {
        const errorMsg = err.response?.data?.detail || 'Chyba při resetování hesla'
        alert('❌ ' + errorMsg)
        console.error('Error resetting password:', err)
      }
    },

    getRoleBadgeClass(role) {
      const classes = {
        'admin': 'bg-purple-200 text-purple-800',
        'auditor': 'bg-blue-200 text-blue-800',
        'solver': 'bg-green-200 text-green-800',
      }
      return classes[role] || 'bg-gray-200 text-gray-800'
    },

    getRoleLabel(role) {
      const labels = {
        'admin': 'Admin',
        'auditor': 'Auditor',
        'solver': 'Řešitel',
      }
      return labels[role] || role
    },
    // ==================== KONEC VYLEPŠENÝCH METOD ====================

    async loadLines() {
      const res = await api.get("/lines/");
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
        
        const msg = res.data.message || "Kampaň vytvořena";
        const emails = res.data.emails_sent || 0;
        const failed = res.data.emails_failed || 0;
        
        let alertMsg = `✅ ${msg}\n\n`;
        alertMsg += `📧 Emaily odeslané: ${emails}\n`;
        if (failed > 0) {
          alertMsg += `❌ Emaily selhaly: ${failed}`;
        }
        
        alert(alertMsg);
      } catch (err) {
        alert(err.response?.data?.detail || "Chyba při generování kampaně");
      }
    }
  },
};
</script>