import { createRouter, createWebHistory } from 'vue-router';
import Home from './components/HomePage.vue';
import AdminLogin from './components/AdminLogin.vue';
import AdminDashboard from './components/AdminDashboard.vue';
import Register from './components/RegisterRole.vue';
import ProfessionalLogin from './components/ProfessionalLogin.vue';
import CustomerLogin from './components/CustomerLogin.vue';
import CustomerDashboard from './components/CustomerDashboard.vue';
import CustomerInfo from './components/CustomerInfo.vue';
import ProfessionalInfo from './components/ProfessionalInfo.vue';
import Services from './components/ServicesInfo.vue';
import CreateService from './components/CreateService.vue';
import UpdateService from './components/UpdateService.vue';
import ProfessionalDashboard from './components/ProfessionalDashboard.vue';
import CreateRequest from './components/CreateRequest.vue';
import SearchResults from './components/SearchResults.vue';
import ServiceRequests from './components/ServiceRequests.vue';
import PendingRequests from './components/PendingRequests.vue';
import AcceptedRequests from './components/AcceptedRequests.vue';

const routes = [
    {
      path: '/', 
      redirect: '/home',
    },
    {
      path: '/home',
      name: 'Home',
      component: Home,
    },
    {
        path: '/admin/login',
        name: 'AdminLogin',
        component: AdminLogin,
    },
    {
      path: '/professional/login',
      name: 'ProfessionalLogin',
      component: ProfessionalLogin,
    },
    {
      path: '/customer/login',
      name: 'CustomerLogin',
      component: CustomerLogin,
    },
    {
        path: '/admin/dashboard',
        name: 'AdminDashboard',
        component: AdminDashboard,
    },
    {
      path: '/customer/dashboard',
      name: 'CustomerDashboard',
      component: CustomerDashboard,
    },
    {
        path: '/register',
        name: 'Register',
        component: Register,
    },
    {
      path: '/admin/customer-info',
      name: 'CustomerInfo',
      component: CustomerInfo,
    },
    {
      path: '/admin/professional-info',
      name: 'ProfessionalInfo',
      component: ProfessionalInfo,
    },
    {
      path: '/admin/services',
      name: 'Services',
      component: Services,
    },
    {
      path: '/admin/create-service',
      name: 'CreateService',
      component: CreateService,
    },
    {
      path: '/admin/update-service/:id',
      name: 'UpdateService',
      component: UpdateService,
    },
    {
      path: '/professional/dashboard',
      name: 'ProfessionalDashboard',
      component: ProfessionalDashboard,
    },
    {
      path: '/customer/create-request',
      name: 'CreateRequest',
      component: CreateRequest,
      meta: { requiresAuth: true, role: 'customer' }
    },
    {
      path: '/customer/search-results',
      name: 'SearchResults',
      component: SearchResults,
      meta: { requiresAuth: true, role: 'customer' }
    },
    {
      path: '/customer/service-requests',
      name: 'ServiceRequests',
      component: ServiceRequests,
      meta: { requiresAuth: true, role: 'customer' }
    },
    {
      path: '/professional/pending-requests',
      name: 'PendingRequests',
      component: PendingRequests,
      meta: { requiresAuth: true, role: 'professional' }
    },
    {
      path: '/professional/accepted-requests',
      name: 'AcceptedRequests',
      component: AcceptedRequests,
      meta: { requiresAuth: true, role: 'professional' }
    },
  ];
  

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;