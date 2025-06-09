import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor for auth (future use)
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized
      console.error("Unauthorized");
    }
    return Promise.reject(error);
  }
);

// API methods
export const api = {
  // Pull Requests
  getPullRequests: () => apiClient.get("/pull-requests"),
  getPullRequest: (id) => apiClient.get(`/pull-requests/${id}`),
  getPullRequestAnalysis: (id) =>
    apiClient.get(`/pull-requests/${id}/analysis`),
  triggerAnalysis: (id) => apiClient.post(`/analyze/${id}`),

  // Dashboard
  getDashboard: () => apiClient.get("/dashboard"),
  getStats: () => apiClient.get("/stats"),

  // Testing
  testCelery: () => apiClient.post("/test/celery"),
};

export default apiClient;
