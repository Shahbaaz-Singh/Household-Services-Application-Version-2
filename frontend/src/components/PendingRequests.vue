<template>
    <div class="container mt-5">
      <h1 class="mb-4">Pending Requests</h1>
  
      <div v-if="message" class="alert" :class="'alert-' + alertType">
        {{ message }}
      </div>
      
      <div class="row mb-3">
        <div class="col">
          <button @click="navigateTo('dashboard')" class="btn btn-info w-100 mb-2">
            Dashboard
          </button>
        </div>
        <div class="col">
          <button @click="navigateTo('pending-requests')" class="btn btn-info w-100 mb-2">
            View Pending Requests
          </button>
        </div>
        <div class="col">
          <button @click="navigateTo('accepted-requests')" class="btn btn-info w-100 mb-2">
            View Accepted Requests
          </button>
        </div>
        <div class="col">
          <button @click="logout" class="btn btn-danger w-100 mb-2">
            Logout
          </button>
        </div>
      </div>
  
      <h2>Pending Service Requests</h2>
      <ul class="list-group">
        <li v-for="request in pendingRequests" :key="request.id" class="list-group-item">
          <strong>Service:</strong> {{ request.associated_service.name }} <br>
          <strong>Customer:</strong> {{ request.requesting_customer.username }} <br>
  
          <button @click="acceptService(request.id)" class="btn btn-success btn-sm">Accept Service</button>
          <button @click="rejectService(request.id)" class="btn btn-danger btn-sm">Reject Service</button>
  
          <button class="btn btn-sm btn-secondary" type="button" @click="toggleDetails(request.id)">
            {{ detailsVisible[request.id] ? 'Hide Service Request Details' : 'View Service Request Details' }}
          </button>
  
          <div v-if="detailsVisible[request.id]" class="mt-2">
            <div class="card card-body">
              <ul>
                <li><strong>Service Name:</strong> {{ request.associated_service.name }}</li>
                <li><strong>Service Price:</strong> {{ request.associated_service.price }}</li>
                <li><strong>Time Required:</strong> {{ request.associated_service.time_required }} minutes</li>
                <li><strong>Service Description:</strong> {{ request.associated_service.description }}</li>
                <li><strong>Field of Service:</strong> {{ request.associated_service.field_of_service }}</li>
              </ul>
            </div>
          </div>
        </li>
      </ul>
    </div>
  </template>
  
  <script>
  import api from '../api';
  
  export default {
    name: 'PendingRequests',
    data() {
      return {
        pendingRequests: [],
        detailsVisible: {},
        message: '',
        alertType: 'success'
      };
    },
    methods: {
      async fetchPendingRequests() {
        try {
          const response = await api.getPendingRequests();
          this.pendingRequests = response.data.pending_requests;
          
          this.pendingRequests.forEach(request => {
            this.detailsVisible[request.id] = false;
          });
        } catch (error) {
          console.error('Error fetching pending requests:', error);
          this.message = 'Failed to load pending requests. Please try again.';
          this.alertType = 'danger';
        }
      },
      toggleDetails(requestId) {
        this.detailsVisible[requestId] = !this.detailsVisible[requestId];
      },
      async acceptService(requestId) {
        try {
          await api.acceptServiceRequest(requestId);
          this.message = 'You have accepted the service request.';
          this.alertType = 'success';
          this.fetchPendingRequests();
        } catch (error) {
          console.error('Error accepting service request:', error);
          this.message = 'Failed to accept service request. Please try again.';
          this.alertType = 'danger';
        }
      },
      async rejectService(requestId) {
        try {
          await api.rejectServiceRequest(requestId);
          this.message = 'You have rejected the service request.';
          this.alertType = 'success';
          this.fetchPendingRequests();
        } catch (error) {
          console.error('Error rejecting service request:', error);
          this.message = 'Failed to reject service request. Please try again.';
          this.alertType = 'danger';
        }
      },
      navigateTo(section) {
        window.location.href = `/professional/${section}`;
      },
      logout() {
        api.professionalLogout();
      }
    },
    mounted() {
      this.fetchPendingRequests();
    }
  };
  </script>  