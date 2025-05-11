import axios from 'axios';

const API_URL = 'http://127.0.0.1:5000';

const api = axios.create({
  baseURL: API_URL
});

const excludedEndpoints = [
  "/api/admin/login",
  "/api/professional/login",
  "/api/customer/login",
  "/api/refresh-token",
  "/api/register"
];

api.interceptors.request.use(
  (config) => {

    if (excludedEndpoints.some(endpoint => config.url.includes(endpoint))) {
      return config;
    }

    let token;
    
    if (config.url.includes('/api/admin/')) {
      token = localStorage.getItem('adminToken');
    } else if (config.url.includes('/api/professional/')) {
      token = localStorage.getItem('professionalToken');
    } else if (config.url.includes('/api/customer/')) {
      token = localStorage.getItem('customerToken');
    } else {
      token = localStorage.getItem('adminToken') || 
              localStorage.getItem('professionalToken') || 
              localStorage.getItem('customerToken');
    }
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);



api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (excludedEndpoints.some(endpoint => originalRequest.url.includes(endpoint))) {
      return Promise.reject(error);
    }
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        let refreshToken;
        let tokenKey;
        
        if (originalRequest.url.includes('/api/admin/')) {
          refreshToken = localStorage.getItem('adminRefreshToken');
          tokenKey = 'adminToken';
        } else if (originalRequest.url.includes('/api/professional/')) {
          refreshToken = localStorage.getItem('professionalRefreshToken');
          tokenKey = 'professionalToken';
        } else if (originalRequest.url.includes('/api/customer/')) {
          refreshToken = localStorage.getItem('customerRefreshToken');
          tokenKey = 'customerToken';
        }
        
        if (refreshToken) {
          const response = await axios.post(`${API_URL}/api/refresh-token`, { refreshToken });
          const { token } = response.data;
          localStorage.setItem(tokenKey, token);
          return api(originalRequest);
        } else {
          throw new Error('No refresh token available');
        }
      } catch (refreshError) {
        if (originalRequest.url.includes('/api/admin/')) {
          localStorage.removeItem('adminToken');
          localStorage.removeItem('adminRefreshToken');
          window.location.href = '/admin/login';
        } else if (originalRequest.url.includes('/api/professional/')) {
          localStorage.removeItem('professionalToken');
          localStorage.removeItem('professionalRefreshToken');
          window.location.href = '/professional/login';
        } else if (originalRequest.url.includes('/api/customer/')) {
          localStorage.removeItem('customerToken');
          localStorage.removeItem('customerRefreshToken');
          window.location.href = '/customer/login';
        }
        return Promise.reject(refreshError);
      }
    }
    
    if (error.response?.status === 403) {
      console.error('Permission denied for this resource:', originalRequest.url);
      
      if (originalRequest.url.includes('/api/admin/')) {
        alert('You need admin privileges to access this resource. Please log in as an admin.');
        window.location.href = '/admin/login';
      } else if (originalRequest.url.includes('/api/professional/')) {
        alert('You need professional privileges to access this resource. Please log in as a professional.');
        window.location.href = '/professional/login';
      } else if (originalRequest.url.includes('/api/customer/')) {
        alert('You need customer privileges to access this resource. Please log in as a customer.');
        window.location.href = '/customer/login';
      }
    }
    
    return Promise.reject(error);
  }
);


export default {
  // Home API
  getHomeData() {
    return api.get('/api/home');
  },

  // Miscellaneous APIs
  registerRole(formData) {
    return api.post('/api/register', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },
  getDocument(filename) {
    return api.get(`/api/documents/${filename}`, {
      responseType: 'blob'
    });
  },

  // Admin APIs
  adminLogin(credentials) {
    return api.post('/api/admin/login', credentials);
  },
  getAdminDashboard() {
    return api.get('/api/admin/dashboard');
  },
  getCustomers(searchQuery = '') {
    return api.get('/api/admin/customer_info', { 
      params: { search_query: searchQuery }
    });
  },
  blockUser(id) {
    return api.post(`/api/admin/block_user/${id}`);
  },
  unblockUser(id) {
    return api.post(`/api/admin/unblock_user/${id}`);
  },
  getProfessionals(searchQuery = '') {
    return api.get('/api/admin/professional_info', { 
      params: { search_query: searchQuery }
    });
  },
  approveUser(id) {
    return api.post(`/api/admin/approve/${id}`);
  },
  unapproveUser(id) {
    return api.post(`/api/admin/unapprove/${id}`);
  },
  getServices() {
    return api.get('/api/admin/services');
  },
  createService(serviceData) {
    return api.post('/api/admin/create_service', serviceData);
  },
  updateService(id, serviceData) {
    return api.post(`/api/admin/update_service/${id}`, serviceData);
  },
  deleteService(id) {
    return api.post(`/api/admin/delete_service/${id}`);
  },
  adminLogout() {
    return api.post('/api/admin/logout').then(() => {
      localStorage.removeItem('adminToken');
      localStorage.removeItem('adminRefreshToken');
      window.location.href = '/admin/login';
    });
  },

  // Customer APIs
  customerLogin(credentials) {
    return api.post('/api/customer/login', credentials);
  },
  getCustomerDashboard() {
    return api.get('/api/customer/dashboard');
  },
  getCreateRequestData() {
    return api.get('/api/customer/create_request');
  },
  searchServices(query) {
    return api.get('/api/customer/search_services', { params: { search_query: query } });
  },
  requestService(data) {
    return api.post('/api/customer/request_service', data);
  },
  getServiceRequests() {
    return api.get('/api/customer/service_requests');
  },
  updateRequest(id, remarks) {
    return api.put(`/api/customer/update_request/${id}`, { remarks });
  },
  closeRequest(id, rating) {
    return api.post(`/api/customer/close_request/${id}`, { rating });
  },
  customerLogout() {
    return api.post('/api/customer/logout').then(() => {
      localStorage.removeItem('customerToken');
      localStorage.removeItem('customerRefreshToken');
      window.location.href = '/customer/login';
    });
  },

  // Professional APIs
  professionalLogin(credentials) {
    return api.post('/api/professional/login', credentials);
  },
  getProfessionalDashboard() {
    return api.get('/api/professional/dashboard');
  },
  exportPendingRequests() {
    return api.post('/api/professional/export_pending_requests');
  },
  downloadProfessionalExport() {
    return api.get('/api/professional/download_export', { responseType: 'blob' });
  },
  getPendingRequests() {
    return api.get('/api/professional/pending_requests');
  },
  acceptServiceRequest(id) {
    return api.post(`/api/professional/accept_service/${id}`);
  },
  rejectServiceRequest(id) {
    return api.post(`/api/professional/reject_service/${id}`);
  },
  getAcceptedRequests() {
    return api.get('/api/professional/accepted_requests');
  },
  updateServiceStatus(id, status) {
    return api.post(`/api/professional/update_service_status/${id}`, { service_status: status });
  },
  professionalLogout() {
    return api.post('/api/professional/logout').then(() => {
      localStorage.removeItem('professionalToken');
      localStorage.removeItem('professionalRefreshToken');
      window.location.href = '/professional/login';
    });
  },
};