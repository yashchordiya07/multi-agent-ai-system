import axios from "axios";

const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

const http = axios.create({
  baseURL: BASE,
  timeout: 180_000,
  headers: { "Content-Type": "application/json" },
});

http.interceptors.response.use(
  (r) => r,
  (err) => {
    const msg =
      err.response?.data?.detail ||
      err.response?.data?.message ||
      err.message ||
      "Unknown error";
    return Promise.reject(new Error(msg));
  }
);

export const submitQuery  = (query, context = "") =>
  http.post("/api/query", { query, ...(context?.trim() ? { context } : {}) })
      .then((r) => r.data);

export const fetchMemory  = () => http.get("/api/memory").then((r) => r.data);
export const clearMemory  = () => http.delete("/api/memory").then((r) => r.data);
export const fetchCache   = () => http.get("/api/cache/stats").then((r) => r.data);
export const checkHealth  = () => http.get("/health").then((r) => r.data);
