<template>
  <div class="container mt-5">
    <h1 class="mb-4">Services</h1>
    <div v-if="message" class="alert" :class="'alert-' + alertType">
        {{ message }}
      </div>

    <div class="row mb-3">
      <div class="col">
        <button @click="navigateTo('dashboard')" class="btn btn-info w-100 mb-2">Dashboard</button>
      </div>
      <div class="col">
        <button @click="navigateTo('customer-info')" class="btn btn-info w-100 mb-2">View Customer Info</button>
      </div>
      <div class="col">
        <button @click="navigateTo('professional-info')" class="btn btn-info w-100 mb-2">View Professional Info</button>
      </div>
      <div class="col">
        <button @click="navigateTo('services')" class="btn btn-info w-100 mb-2">View Services</button>
      </div>
      <div class="col">
        <button @click="logout" class="btn btn-danger w-100 mb-2">Logout</button>
      </div>
    </div>
      <router-link to="/admin/create-service" class="btn btn-primary mb-3">Create New Service</router-link>
      <ul class="list-group mb-4">
        <li v-for="service in services" :key="service.id" class="list-group-item">
          {{ service.name }}
          <button @click="deleteService(service.id)" class="btn btn-danger btn-sm me-2">Delete</button>
          <router-link :to="`/admin/update-service/${service.id}`" class="btn btn-warning btn-sm me-2">Update Service</router-link>
          <button @click="toggleInfo(service)" class="btn btn-info btn-sm me-2">View More Info</button>
          <div v-if="service.showInfo">
            <ul>
                <li><strong>ID:</strong> {{ service.id }}</li>
                <li><strong>Name:</strong> {{ service.name }}</li>
                <li><strong>Price:</strong> {{ service.price }}</li>
                <li><strong>Time Required:</strong> {{ service.time_required }}</li>
                <li><strong>Description:</strong> {{ service.description }}</li>
                <li><strong>Field of Service:</strong> {{ service.field_of_service }}</li>
            </ul>
          </div>
        </li>
      </ul>
    </div>
  </template>
  
  <script>
  import api from '../api';
  
  export default {
    data() {
      return {
        services: []
      }
    },
    methods: {
      async logout() {
  try {
    await api.adminLogout();
  } catch (error) {
    console.error('Error logging out:', error);
  }
},
      navigateTo(section) {
      window.location.href = `/admin/${section}`;
    },
      async fetchServices() {
        const response = await api.getServices();
        this.services = response.data;
      },
      async deleteService(id) {
  if (confirm("Are you sure you want to delete this service?")) {
    try {
      const response = await api.deleteService(id);
      
      if (response.status === 200) {
        alert("Service deleted successfully");
        this.fetchServices();
      }
    } catch (error) {
      if (error.response) {
        if (error.response.status === 403) {
          alert("Unauthorized access");
        } else if (error.response.status === 400) {
          alert("Cannot delete service with active requests");
        } else {
          alert("An error occurred. Please try again later.");
        }
      } else {
        alert("Network error. Please check your connection.");
      }
    }
  }
},
      toggleInfo(service) {
        service.showInfo = !service.showInfo;
      }
    },
    mounted() {
      this.fetchServices();
    }
  }
  </script>