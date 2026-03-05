import axios from 'axios';

const API_URL = 'http://localhost:8800/api';

const api = axios.create({
  baseURL: API_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

// Response interceptor for token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then(() => api(originalRequest))
          .catch((err) => Promise.reject(err));
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        await api.post('/user/refresh');
        processQueue(null);
        return api(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError, null);
        localStorage.removeItem('user');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: (credentials) => api.post('/user/login', credentials),
  register: (userData) => api.post('/user/register', userData),
  logout: () => api.post('/user/logout'),
  refresh: () => api.post('/user/refresh'),
};

// Task API
export const taskAPI = {
  getAll: (params = {}) => {
    const { stage = '', isTrashed = 'false', search = '' } = params;
    return api.get(`/task?stage=${stage}&isTrashed=${isTrashed}&search=${search}`);
  },
  getById: (id) => api.get(`/task/${id}`),
  create: (taskData) => api.post('/task/create', taskData),
  update: (id, taskData) => api.put(`/task/update/${id}`, taskData),
  delete: (id, actionType) => api.delete(`/task/delete-restore/${id}?actionType=${actionType}`),
  trash: (id) => api.put(`/task/${id}`),
  changeStage: (id, stage) => api.put(`/task/change-stage/${id}`, { stage }),
  complete: (id) => api.patch(`/task/complete/${id}`),
  archive: (id) => api.patch(`/task/archive/${id}`),
  getDashboard: () => api.get('/task/dashboard'),
  createSubTask: (id, subTaskData) => api.put(`/task/create-subtask/${id}`, subTaskData),
  postActivity: (id, activityData) => api.post(`/task/activity/${id}`, activityData),
};

// User API
export const userAPI = {
  getTeam: (search = '') => api.get(`/user/get-team?search=${search}`),
  updateProfile: (userData) => api.put('/user/profile', userData),
  changePassword: (passwordData) => api.put('/user/change-password', passwordData),
  getNotifications: () => api.get('/user/notifications'),
  getStatus: () => api.get('/user/get-status'),
};

// Analytics API
export const analyticsAPI = {
  getSummary: () => api.get('/analytics/summary'),
  getOverTime: () => api.get('/analytics/over-time'),
  getProductivity: () => api.get('/analytics/productivity'),
};

export default api;
