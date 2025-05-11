<template>
  <div class="container mt-5">
    <h1 class="mb-4">View Service Requests</h1>

    <div class="row mb-3">
      <div class="col">
        <button @click="navigateTo('dashboard')" class="btn btn-info w-100 mb-2">Dashboard</button>
      </div>
      <div class="col">
        <button @click="navigateTo('create-request')" class="btn btn-info w-100 mb-2">Create New Service Request</button>
      </div>
      <div class="col">
        <button @click="navigateTo('service-requests')" class="btn btn-info w-100 mb-2">View Your Service Requests</button>
      </div>
      <div class="col">
        <button @click="logout" class="btn btn-danger w-100 mb-2">Logout</button>
      </div>
    </div>

    <div v-if="message" class="alert" :class="'alert-' + alertType">
      {{ message }}
    </div>

    <h2>Your Service Requests</h2>
    <div v-if="serviceRequests.length">
      <div v-for="request in serviceRequests" :key="request.id" class="card mb-4">
        <div class="card-body">
          <strong>Service Request Name:</strong> {{ request.associated_service.name }} <br>
          <strong>Status:</strong>
          <span v-if="request.service_status === 'rejected'">Pending</span>
          <span v-else>{{ request.service_status }}</span>
          <br>

          <button class="btn btn-info btn-sm mt-2" type="button" @click="toggleDetails(request.id, 'service')">
            {{ detailsVisible[request.id]?.service ? 'Hide Service Request Details' : 'View Service Request Details' }}
          </button>

          <div v-if="detailsVisible[request.id]?.service" class="mt-2">
            <div class="card card-body">
              <ul>
                <li><strong>Service Name:</strong> {{ request.associated_service.name }}</li>
                <li><strong>Service Price:</strong> {{ request.associated_service.price }}</li>
                <li><strong>Time Required:</strong> {{ request.associated_service.time_required }} minutes</li>
                <li><strong>Service Description:</strong> {{ request.associated_service.description }}</li>
                <li><strong>Field of Service:</strong> {{ request.associated_service.field_of_service }}</li>
                <li><strong>Date of Request:</strong> {{ formatDate(request.date_of_request) }}</li>
                <li><strong>Date of Acceptance:</strong>
                  <span v-if="request.date_of_acceptance">{{ formatDate(request.date_of_acceptance) }}</span>
                  <span v-else>Not yet accepted</span>
                </li>
                <li><strong>Date of Completion:</strong>
                  <span v-if="request.date_of_completion">{{ formatDate(request.date_of_completion) }}</span>
                  <span v-else>Not yet completed</span>
                </li>
                <li><strong>Remarks:</strong> {{ request.remarks }}</li>
              </ul>
            </div>
          </div>

          <div v-if="request.assigned_professional">
            <button class="btn btn-info btn-sm mt-2" type="button" @click="toggleDetails(request.id, 'professional')">
              {{ detailsVisible[request.id]?.professional ? 'Hide Professional Details' : 'Show Professional Details' }}
            </button>
            <div v-if="detailsVisible[request.id]?.professional" class="mt-2">
              <div class="card card-body">
                <ul>
                  <li><strong>Accepted By:</strong> {{ request.assigned_professional.username }}</li>
                  <li><strong>Professional Rating:</strong> {{ request.assigned_professional.rating }} / 5</li>
                  <li><strong>Number of Reviews:</strong> {{ request.assigned_professional.num_reviews }}</li>
                  <li><strong>Phone Number:</strong> {{ request.assigned_professional.phone_number }}</li>
                  <li><strong>Email:</strong> {{ request.assigned_professional.email }}</li>
                </ul>
              </div>
            </div>
          </div>
          <div v-else>
            <p class="text-muted">This request is not yet accepted by a professional.</p>
          </div>

          <div class="mt-2">
            <label :for="'remarks-' + request.id" class="form-label">Update Remarks:</label>
            <input type="text" :id="'remarks-' + request.id" v-model="remarkUpdates[request.id]" 
                  class="form-control" placeholder="Enter remarks">
            <button @click="updateRequest(request.id)" class="btn btn-warning btn-sm mt-2">Update Remarks</button>
          </div>

          <div class="mt-2">
            <label :for="'rating-' + request.id" class="form-label">Rate Professional (1-5):</label>
            <input type="number" :id="'rating-' + request.id" v-model="ratingSubmissions[request.id]" 
                  class="form-control" min="1" max="5" placeholder="Enter rating">
            <button @click="closeRequest(request.id)" class="btn btn-danger btn-sm mt-2">Close Request</button>
          </div>
        </div>
      </div>
    </div>
    <p v-else class="text-muted">No service requests found.</p>
  </div>
</template>

<script>
import api from '../api';

export default {
  name: 'ServiceRequests',
  data() {
    return {
      serviceRequests: [],
      detailsVisible: {},
      remarkUpdates: {},
      ratingSubmissions: {},
      message: '',
      alertType: 'success'
    };
  },
  methods: {
    navigateTo(section) {
      window.location.href = `/customer/${section}`;
    },
    async fetchServiceRequests() {
      try {
        const response = await api.getServiceRequests();
        this.serviceRequests = response.data.service_requests;

        this.serviceRequests.forEach(request => {
          this.detailsVisible[request.id] = { service: false, professional: false };
          this.remarkUpdates[request.id] = request.remarks || '';
          this.ratingSubmissions[request.id] = '';
        });
      } catch (error) {
        console.error('Error fetching service requests:', error);
        this.message = 'Failed to load service requests. Please try again.';
        this.alertType = 'danger';
      }
    },
    toggleDetails(requestId, section) {
      if (!this.detailsVisible[requestId]) {
        this.detailsVisible[requestId] = { service: false, professional: false };
      }
      this.detailsVisible[requestId][section] = !this.detailsVisible[requestId][section];
    },
    async updateRequest(requestId) {
  try {
    await api.updateRequest(requestId, this.remarkUpdates[requestId]);
    this.message = 'Service request updated';
    this.alertType = 'success';
    await this.fetchServiceRequests();
  } catch (error) {
    console.error('Error updating request:', error);
    this.message = 'Failed to update request. Please try again.';
    this.alertType = 'danger';
  }
},
    async closeRequest(requestId) {
      try {
        const rating = parseInt(this.ratingSubmissions[requestId]);
        if (rating && (rating < 1 || rating > 5)) {
          this.message = 'Rating must be between 1 and 5';
          this.alertType = 'warning';
          return;
        }

        await api.closeRequest(requestId, rating);
        this.message = 'Service request closed.';
        this.alertType = 'success';
        this.fetchServiceRequests();
      } catch (error) {
        console.error('Error closing request:', error);
        this.message = 'Failed to close request. Please try again.';
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
    async logout() {
  try {
    await api.customerLogout();
  } catch (error) {
    console.error('Error logging out:', error);
  }
},
  },
  mounted() {
    this.fetchServiceRequests();
  }
};
</script>