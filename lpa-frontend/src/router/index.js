import { createRouter, createWebHistory } from "vue-router";
import { useUserStore } from "@/stores/user";
import Login from "../views/Login.vue";
import Dashboard from "../views/Dashboard.vue";
import Admin from "../views/Admin.vue";
import Assignments from "../views/Assignments.vue";
import Audit from "../views/Audit.vue";
import Neshody from "../views/Neshody.vue";
import AuditReport from "../views/AuditReport.vue";
import Allocations from "../views/Allocations.vue";
import Issues from "@/views/Issues.vue";

const routes = [
  {
    path: "/",
    name: "Login",
    component: Login,
    meta: { requiresAuth: false }
  },
  {
    path: "/dashboard",
    name: "Dashboard",
    component: Dashboard,
    meta: { requiresAuth: true }
  },
  {
    path: "/admin",
    name: "Admin",
    component: Admin,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: "/assignments",
    name: "Assignments",
    component: Assignments,
    meta: { requiresAuth: true }
  },
  {
    path: "/audit",
    name: "Audit",
    component: Audit,
    meta: { requiresAuth: true }
  },
  {
    path: "/neshody",
    name: "Neshody",
    component: Neshody,
    meta: { requiresAuth: true }
  },
  {
    path: "/audit-report",
    name: "AuditReport",
    component: AuditReport,
    meta: { requiresAuth: true }
  },
  {
    path: "/allocations",
    name: "Allocations",
    component: Allocations,
    meta: { requiresAuth: true }
  },
  {
    path: "/issues",
    name: "Issues",
    component: Issues,
    meta: { requiresAuth: true }
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Navigation guard
router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore();
  const token = localStorage.getItem('access_token');

  // Pokud jde na login a je přihlášený, přesměruj na dashboard
  if (to.path === '/' && token) {
    // Pokud ještě nemáme user data, načti je
    if (!userStore.user) {
      await userStore.fetchUser();
    }
    if (userStore.isAuthenticated) {
      return next('/dashboard');
    }
  }

  // Kontrola autentizace
  if (to.meta.requiresAuth) {
    if (!token) {
      return next('/');
    }

    // Načíst user data, pokud ještě nejsou
    if (!userStore.user) {
      await userStore.fetchUser();
    }

    // Pokud se načtení nezdařilo (např. neplatný token)
    if (!userStore.isAuthenticated) {
      return next('/');
    }

    // Kontrola admin oprávnění
    if (to.meta.requiresAdmin && userStore.userRole !== 'admin') {
      alert('Nemáte oprávnění pro přístup k této stránce');
      return next('/dashboard');
    }
  }

  next();
});

export default router;
