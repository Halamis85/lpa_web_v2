<template>
  <div class="max-w-5xl p-6 mx-auto">
    <h2 class="mb-6 text-2xl font-bold">📋 Provedení auditu</h2>

    <!-- výběr přidělení -->
    <div v-if="!executionId" class="mb-6">
      <label class="font-semibold">Vyber přidělení:</label>
      <select v-model="selectedAssignmentId" @change="startAudit" class="px-3 py-2 ml-2 border rounded">
        <option :value="null">-- vyber --</option>
        <option v-for="a in assignments" :key="a.id" :value="a.id">
          {{ a.line_name }} — {{ a.category_name }} ({{ a.status }})
        </option>
      </select>
    </div>

    <!-- probíhající audit -->
    <div v-if="executionId">
      <div class="mb-4 text-lg font-semibold">
        {{ assignedCategoryName }} — checklist
      </div>

      <table class="w-full text-sm border">
        <thead class="bg-gray-100">
          <tr>
            <th class="w-16 p-2 border">#</th>
            <th class="p-2 border">Otázka</th>
            <th class="w-48 p-2 border">Odpověď</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="pos in maxPosition" :key="pos">
            <td class="p-2 text-center border">{{ pos }}</td>
            <td class="p-2 border">
              <span v-if="questionsByPosition[pos]">
                {{ questionsByPosition[pos].question_text }}
              </span>
              <span v-else class="text-gray-400">—</span>
            </td>
            <td class="p-2 text-center border">
              <div v-if="questionsByPosition[pos]">
                <button
                  class="px-3 py-1 mr-2 border rounded"
                  :class="answers[questionsByPosition[pos].id]==='OK' ? 'bg-green-200' : ''"
                  @click="saveAnswer(questionsByPosition[pos].id,'OK')">
                  OK
                </button>
                <button
                  class="px-3 py-1 border rounded"
                  :class="answers[questionsByPosition[pos].id]==='NOK' ? 'bg-red-200' : ''"
                  @click="saveAnswer(questionsByPosition[pos].id,'NOK')">
                  NOK
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>

      <div class="mt-6">
        <button
          :disabled="!canFinish"
          @click="finishAudit"
          class="px-4 py-2 text-white bg-blue-600 rounded disabled:opacity-40">
          Ukončit audit
        </button>
      </div>
    </div>

    <!-- NOK modal -->
    <div v-if="nokQuestionId" class="fixed inset-0 flex items-center justify-center bg-black/40">
      <div class="p-6 bg-white rounded shadow w-96">
        <h3 class="mb-3 font-bold">Popis neshody</h3>
        <input type="file" @change="e => nokFile = e.target.files[0]" />
        <textarea v-model="nokComment" class="w-full p-2 mb-3 border"></textarea>
        <div class="text-right">
          <button class="mr-2" @click="nokQuestionId=null">Zrušit</button>
          <button class="px-3 py-1 text-white bg-red-500 rounded" @click="confirmNok">Uložit</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../api'

export default {
  data(){
    return {
      assignments:[],
      selectedAssignmentId:null,
      executionId:null,
      questionsByPosition:{},
      assignedCategoryName:'',
      maxPosition:4,
      answers:{},
      nokQuestionId:null,
      nokComment:'',
      nokFile: null
    }
  },

  computed:{
    canFinish(){
      const q=Object.values(this.questionsByPosition)
      return q.length && q.every(x=>this.answers[x.id])
    }
  },

    async mounted(){
      await this.loadAssignments()

    const saved = localStorage.getItem("activeExecution");

    if (saved) {
      this.executionId = saved;

      const exec = await api.get(`/executions/${saved}`);
      this.selectedAssignmentId = exec.data.assignment_id;

      await this.loadExecution();
    }
  },


  methods:{
    async loadAssignments(){
      const res=await api.get('/assignments')
      this.assignments=res.data.filter(a=>a.status!=='done')
    },

   async startAudit() {
  if (!this.selectedAssignmentId) return;
  try {
    // zkusíme start
    const res = await api.post(
      `/executions/start?assignment_id=${this.selectedAssignmentId}`);
    this.executionId = res.data.execution_id;
    localStorage.setItem("activeExecution", this.executionId);
  } catch (err) {
    // pokud už existuje → backend vrací 400
    if (err.response?.status === 400) {

      // načteme existující execution
      const existing = await api.get( `/executions/by-assignment/${this.selectedAssignmentId}` );
      this.executionId = existing.data.execution_id; localStorage.setItem("activeExecution", this.executionId);
    } else { alert("Nepodařilo se spustit audit");
      return; }}
  await this.loadExecution();
},

    async loadExecution(){

    // vždy načti assignment z backendu (jistota)
    const res = await api.get(`/assignments/${this.selectedAssignmentId}`);
    const a = res.data;

    this.assignedCategoryName = a.category_name;

    await this.loadChecklist(a.template_id, a.category_id);
    await this.loadExistingAnswers();
  },

    async loadChecklist(templateId,categoryId){
    if (!templateId || !categoryId) return;
      const res=await api.get(`/checklist/templates/${templateId}/questions`)
      const byPos={}
      let max=0
      res.data.filter(q=>q.category_id===categoryId).forEach(q=>{
        byPos[q.position]=q
        if(q.position>max) max=q.position
      })
      this.questionsByPosition=byPos
      this.maxPosition=Math.max(max,4)
    },

    async loadExistingAnswers(){
      const res=await api.get(`/answers/execution/${this.executionId}`)
      this.answers={}
      res.data.forEach(a=>this.answers[a.question_id]=a.odpoved)
    },

    async saveAnswer(questionId,val){
      if(val==='NOK'){
        this.nokQuestionId=questionId
        return
      }
      await this.sendAnswer(questionId,val,null)
    },

    async confirmNok(){
      await this.sendAnswer(this.nokQuestionId,'NOK',this.nokComment,this.nokFile);
      this.nokQuestionId=null;
      this.nokComment='';
      this.nokFile 
    },

    async sendAnswer(questionId, value, comment = null, file = null) {

      const form = new FormData();
      form.append("audit_execution_id", this.executionId);
      form.append("question_id", questionId);
      form.append("odpoved", value);
      form.append("has_issue", value === "NOK");

    if (comment) form.append("poznamka", comment);
    if (file) form.append("picture", file);

      await api.post("/answers", form, {
      headers: { "Content-Type": "multipart/form-data" }
    });

    this.answers[questionId] = value;
  },

    async finishAudit(){
      await api.post(`/executions/finish?execution_id=${this.executionId}`)
      localStorage.removeItem('activeExecution')
      this.executionId=null
      this.selectedAssignmentId=null
      this.answers={}
      await this.loadAssignments()
    }
  }
}
</script>
