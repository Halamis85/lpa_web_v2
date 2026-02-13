<template>
  <div class="flex h-screen bg-gray-100">
    <!-- SIDEBAR -->
    <aside class="flex flex-col w-64 p-5 text-white bg-gray-900">
      <h2 class="mb-6 text-xl font-bold">LPA UDITY</h2>

      <nav class="flex-1 space-y-2">
        <router-link
          to="/dashboard"
          class="block px-3 py-2 rounded hover:bg-blue-600"
          active-class="bg-blue-600"
        >
          📊 Hlavní stránka
        </router-link>

        <router-link
          to="/issues"
          class="block px-3 py-2 rounded hover:bg-blue-600"
          active-class="bg-blue-600"
        >
          📑 Audity
        </router-link>

        <router-link
          to="/allocations"
          class="block px-3 py-2 rounded hover:bg-blue-600"
          active-class="bg-blue-600"
        >
          📋 Rozlosování
        </router-link>

        <router-link
          to="/admin"
          class="block px-3 py-2 rounded hover:bg-blue-600"
          active-class="bg-blue-600"
        >
          🔧 Administrace
        </router-link>

        <router-link
          to="/audit"
          class="block px-3 py-2 rounded hover:bg-blue-600"
          active-class="bg-blue-600"
        >
          📝 Provést audit
        </router-link>
      </nav>

      <button
        @click="logout"
        class="px-3 py-2 mt-auto text-white bg-red-600 rounded hover:bg-red-700"
      >
        Odhlásit
      </button>
    </aside>

    <!-- MAIN CONTENT -->
    <main class="flex-1 p-6 overflow-auto">
      <header class="flex items-center justify-between p-4 mb-6 bg-white rounded-lg shadow">
        <span class="font-semibold">Vítej </span>
      </header>

      <router-view />
    </main>
  </div>
</template>

<script>
export default {
  methods: {
    logout() {
      localStorage.removeItem("token");
      this.$router.push("/");
    },
  },
};
</script>
