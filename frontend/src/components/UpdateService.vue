<template>
    <div class="container mt-5">
      <h1 class="mb-4">Update Service</h1>
      
      <div v-if="message" class="alert" :class="messageType">
        {{ message }}
      </div>
  
      <form @submit.prevent="updateService" class="border p-4 rounded bg-light shadow-sm">
        <div class="mb-3">
          <label for="name" class="form-label">Service Name</label>
          <input type="text" class="form-control" id="name" v-model="service.name" required>
        </div>
        <div class="mb-3">
          <label for="price" class="form-label">Service Price</label>
          <input type="number" step="0.01" class="form-control" id="price" v-model="service.price" required>
        </div>
        <div class="mb-3">
          <label for="time_required" class="form-label">Time Required (in hours)</label>
          <input type="number" step="0.1" class="form-control" id="time_required" v-model="service.time_required" required>
        </div>
        <div class="mb-3">
          <label for="description" class="form-label">Service Description</label>
          <textarea class="form-control" id="description" v-model="service.description" rows="4" required></textarea>
        </div>
  
        <div class="d-flex justify-content-between">
          <button type="submit" class="btn btn-primary">Update Service</button>
          <router-link to="/admin/services" class="btn btn-secondary">Cancel</router-link>
        </div>
      </form>
  
      <div class="mt-3 text-center">
        <router-link to="/admin/services" class="text-decoration-none">Back to Services</router-link>
      </div>
    </div>
  </template>
  
  <script>
  import api from '../api';
  
  export default {
    name: 'UpdateService',
    data() {
      return {
        service: {
          name: '',
          price: '',
          time_required: '',
          description: ''
        },
        message: '',
        messageType: ''
      };
    },
    methods: {
      async fetchService() {
        try {
          const serviceId = this.$route.params.id;
          const response = await api.getServices();
          const services = response.data;
          const service = services.find(s => s.id == serviceId);
          
          if (service) {
            this.service = {
              name: service.name,
              price: service.price,
              time_required: service.time_required,
              description: service.description
            };
          } else {
            this.message = 'Service not found.';
            this.messageType = 'alert-danger';
          }
        } catch (error) {
          console.error('Error fetching service:', error);
          this.message = 'Failed to load service data.';
          this.messageType = 'alert-danger';
        }
      },
      async updateService() {
        try {
          const serviceId = this.$route.params.id;
          await api.updateService(serviceId, this.service);
          this.message = 'Service updated successfully.';
          this.messageType = 'alert-success';
          
          setTimeout(() => {
            this.$router.push('/admin/services');
          }, 1500);
        } catch (error) {
          console.error('Error updating service:', error);
          this.message = 'Failed to update service. Please try again.';
          this.messageType = 'alert-danger';
        }
      }
    },
    mounted() {
      this.fetchService();
    }
  };
  </script>  