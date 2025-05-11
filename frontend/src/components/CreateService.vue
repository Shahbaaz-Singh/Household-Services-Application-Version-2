<template>
    <div class="container mt-5">
      <h2>Create a New Service</h2>
  
      <div v-if="message" class="alert" :class="messageType">
        {{ message }}
      </div>
      
      <form @submit.prevent="createService">
        <div class="mb-3">
          <label for="name" class="form-label">Service Name</label>
          <input type="text" v-model="service.name" id="name" class="form-control" required>
        </div>
  
        <div class="mb-3">
          <label for="price" class="form-label">Price</label>
          <input type="number" v-model="service.price" id="price" class="form-control" required>
        </div>
  
        <div class="mb-3">
          <label for="time_required" class="form-label">Time Required (in hours)</label>
          <input type="number" v-model="service.time_required" id="time_required" class="form-control" required step="0.1">
        </div>
  
        <div class="mb-3">
          <label for="description" class="form-label">Description</label>
          <textarea v-model="service.description" id="description" class="form-control" rows="3" required></textarea>
        </div>
  
        <div class="mb-3">
          <label for="field_of_service" class="form-label">Field of Service</label>
          <select v-model="service.field_of_service" id="field_of_service" class="form-control" required>
            <option value="" disabled>Select a field of service</option>
            <option v-for="field in fieldsOfService" :key="field" :value="field">{{ field }}</option>
          </select>
        </div>
  
        <button type="submit" class="btn btn-primary">Create Service</button>
      </form>
      <div class="mt-3 text-center">
        <router-link to="/admin/services" class="text-decoration-none">Back to Services</router-link>
      </div>
    </div>
  </template>
  
  <script>
  import api from '../api';
  
  export default {
    name: 'CreateService',
    data() {
      return {
        service: {
          name: '',
          price: '',
          time_required: '',
          description: '',
          field_of_service: ''
        },
        fieldsOfService: [
          'Electrical', 'Plumbing', 'Cleaning', 'Landscaping', 'Handyman', 'Carpentry',
          'Pest Control', 'HVAC', 'Painting', 'Roofing', 'Masonry', 'Glass Repair',
          'Flooring', 'Furniture Assembly', 'Appliance Repair', 'Computer Repair', 
          'Window Cleaning', 'Gutter Cleaning', 'Moving Services', 'Security Services'
        ],
        message: '',
        messageType: ''
      };
    },
    methods: {
      async createService() {
        try {
          await api.createService(this.service);
          this.message = 'Service created successfully.';
          this.messageType = 'alert-success';
          
          this.service = {
            name: '',
            price: '',
            time_required: '',
            description: '',
            field_of_service: ''
          };
          
          setTimeout(() => {
            this.$router.push('/admin/services');
          }, 1500);
        } catch (error) {
          console.error('Error creating service:', error);
          this.message = 'Failed to create service. Please try again.';
          this.messageType = 'alert-danger';
        }
      }
    }
  };
  </script>
  