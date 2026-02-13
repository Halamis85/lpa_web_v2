<template>
  <div class="min-h-screen bg-gray-100 flex items-center justify-center">
    <div class="bg-white shadow-lg rounded-xl w-full max-w-md p-8">
      <h2 class="text-2xl font-bold text-center mb-2">LPA v2</h2>
      <p class="text-gray-500 text-center mb-6">Přihlášení do systému</p>

      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700">Email</label>
          <input
            v-model="email"
            type="email"
            placeholder="vas@email.cz"
            class="mt-1 w-full border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700">Heslo</label>
          <input
            v-model="password"
            type="password"
            placeholder="••••••••"
            class="mt-1 w-full border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
          />
        </div>

        <button
          @click="login"
          class="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 rounded-lg transition"
        >
          Přihlásit se
        </button>

        <p v-if="error" class="text-red-600 text-sm text-center mt-3">
          {{ error }}
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import api from "../api";

export default {
  data() {
    return {
      email: "",
      password: "",
      error: null,
    };
  },
  methods: {
    async login() {
      this.error = null;
      try {
        const form = new URLSearchParams();
        form.append("username", this.email);
        form.append("password", this.password);

        const res = await api.post("/token", form);

        localStorage.setItem("access_token", res.data.access_token);
        this.$router.push("/dashboard");
      } catch (e) {
        this.error = "Neplatné přihlašovací údaje";
      }
    },
  },
};
</script>
