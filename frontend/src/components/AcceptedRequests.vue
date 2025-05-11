<template>
    <div class="container mt-5">
      <h1 class="mb-4">Accepted Requests</h1>
  
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
  
      <h2>Accepted Service Requests</h2>
      <ul class="list-group">
        <li v-for="request in acceptedRequests" :key="request.id" class="list-group-item">
          <strong>Service Request Name:</strong> {{ request.associated_service.name }} <br>
          <strong>Status:</strong> {{ request.service_status }} <br>
          <strong>Remarks:</strong> {{ request.remarks }} <br>
          <strong>Date of Request:</strong> {{ formatDate(request.date_of_request) }} <br>
          <p><strong>Date of Acceptance:</strong> 
            <span v-if="request.date_of_acceptance">{{ formatDate(request.date_of_acceptance) }}</span>
            <span v-else>Not yet accepted</span>
          </p>
  
          <div class="d-inline">
            <select v-model="statusUpdates[request.id]">
              <option value="in_progress" :selected="request.service_status === 'in_progress'">
                In Progress
              </option>
              <option value="completed" :selected="request.service_status === 'completed'">
                Completed
              </option>
            </select>
            <button @click="updateStatus(request.id)" class="btn btn-sm me-2 btn-primary">Update Status</button>
          </div>
      
          <button class="btn btn-sm btn-secondary" type="button" @click="toggleDetails(request.id, 'customer')">
            {{ detailsVisible[request.id]?.customer ? 'Hide Customer Info' : 'View Customer Info' }}
          </button>
  
          <button class="btn btn-sm btn-secondary" type="button" @click="toggleDetails(request.id, 'service')">
            {{ detailsVisible[request.id]?.service ? 'Hide Service Request Details' : 'View Service Request Details' }}
          </button>
  
          <div v-if="detailsVisible[request.id]?.customer" class="mt-2">
            <div class="card card-body">
              <ul>
                <li><strong>Username:</strong> {{ request.customer.username }}</li>
                <li><strong>Location:</strong> {{ request.customer.location }}</li>
                <li><strong>Pin Code:</strong> {{ request.customer.pin_code }}</li>
                <li><strong>Phone Number:</strong> {{ request.customer.phone_number }}</li>
                <li><strong>Email:</strong> {{ request.customer.email }}</li>
                <li><strong>Address:</strong> {{ request.customer.address }}</li>
              </ul>
            </div>
          </div>
  
          <div v-if="detailsVisible[request.id]?.service" class="mt-2">
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
    name: 'AcceptedRequests',
    data() {
      return {
        acceptedRequests: [],
        detailsVisible: {},
        statusUpdates: {},
        message: '',
        alertType: 'success'
      };
    },
    methods: {
      async fetchAcceptedRequests() {
        try {
          const response = await api.getAcceptedRequests();
          this.acceptedRequests = response.data.accepted_requests;
          
          this.acceptedRequests.forEach(request => {
            this.detailsVisible[request.id] = { customer: false, service: false };
            this.statusUpdates[request.id] = request.service_status;
          });
        } catch (error) {
          console.error('Error fetching accepted requests:', error);
          this.message = 'Failed to load accepted requests. Please try again.';
          this.alertType = 'danger';
        }
      },
      toggleDetails(requestId, section) {
        if (!this.detailsVisible[requestId]) {
          this.detailsVisible[requestId] = { customer: false, service: false };
        }
        this.detailsVisible[requestId][section] = !this.detailsVisible[requestId][section];
      },
      async updateStatus(requestId) {
        try {
          await api.updateServiceStatus(requestId, this.statusUpdates[requestId]);
          this.message = 'Service status updated successfully.';
          this.alertType = 'success';
          this.fetchAcceptedRequests();
        } catch (error) {
          console.error('Error updating service status:', error);
          this.message = 'Failed to update service status. Please try again.';
          this.alertType = 'danger';
        }
      },
      formatDate(dateString) {
        if (!dateString) return '';
        const date = new Date(dateString);
        return date.toLocaleString('en-IN', {
          day: '2-digit',
          month: '2-digit',
          year: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        });
      },
      navigateTo(section) {
        window.location.href = `/professional/${section}`;
      },
      logout() {
        api.professionalLogout();
      }
    },
    mounted() {
      this.fetchAcceptedRequests();
    }
  };
  </script>
  
  <style scoped>
  .card {
    transition: all 0.3s ease;
  }
  .card:hover {
    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
  }
  .btn-info, .btn-secondary {
    margin-right: 5px;
    margin-top: 5px;
  }
  select {
    padding: 5px;
    margin-right: 5px;
    border-radius: 4px;
    border: 1px solid #ced4da;
  }
  </style>