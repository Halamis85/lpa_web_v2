import axios from "axios";
import router from "./router";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://127.0.0.1:8000",
});

// Přidání JWT tokenu do každého requestu
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Zachytávání chyb
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Pokud je 401 (Unauthorized), přesměruj na login
    if (error.response?.status === 401) {
      localStorage.removeItem("access_token");

      // Přesměruj jen pokud nejsme již na login stránce
      if (router.currentRoute.value.path !== '/') {
        router.push('/');
      }
    }

    return Promise.reject(error);
  }
);

export default api;
