import { createRouter, createWebHistory } from "vue-router"
import { useUserStore } from "@/stores/user"
import Login from "../views/Login.vue"
import Dashboard from "../views/Dashboard.vue"
import Admin from "../views/Admin.vue"
import Assignments from "../views/Assignments.vue"
import Audit from "../views/Audit.vue"
import Neshody from "../views/Neshody.vue"
import AuditReport from "../views/AuditReport.vue"
import Allocations from "../views/Allocations.vue"
import Issues from "@/views/Issues.vue"
import NokAuditsList from "@/views/NokAuditsList.vue"
import NokAuditDetail from "@/views/NokAuditDetail.vue"
import Statistics from '../views/Statistics.vue'
import ChangePassword from '@/views/ChangePassword.vue'

const routes = [
  {
    path: "/",
    name: "Login",
    component: Login,
    meta: { requiresAuth: false }
  },
  {
    path: '/change-password',
    name: 'ChangePassword',
    component: ChangePassword,
    meta: { requiresAuth: true }
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
  {
    path: "/nok-audits",
    name: "NokAuditsList",
    component: NokAuditsList,
    meta: { requiresAuth: true }
  },
  {
    path: "/nok-audits/:id",
    name: "NokAuditDetail",
    component: NokAuditDetail,
    meta: { requiresAuth: true }
  },
  {
    path: "/statistics",
    name: "Statistics",
    component: Statistics,
    meta: { requiresAuth: true }
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Navigation guard
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token')
  const userRole = localStorage.getItem('user_role')

  // Pokud stránka vyžaduje přihlášení
  if (to.meta.requiresAuth && !token) {
    next('/')
    return
  }

  // Pokud stránka vyžaduje admin práva
  if (to.meta.requiresAdmin && userRole !== 'admin') {
    next('/home')
    return
  }

  next()
})

export default router