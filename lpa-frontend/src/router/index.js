import { createRouter, createWebHistory } from "vue-router";
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
  { path: "/", component: Login },
  { path: "/dashboard", component: Dashboard },
  { path: "/admin", component: Admin },
  { path: "/assignments", component: Assignments }, 
  { path: "/audit", component: Audit },
  { path: "/neshody", component: Neshody },
  { path: "/audit-report", component: AuditReport },
  { path: "/allocations", component: Allocations },
  { path: "/Issues", component: Issues},
  
  
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
