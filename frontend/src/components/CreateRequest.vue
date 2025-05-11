<template>
    <div class="container mt-5">
      <h1 class="mb-4">Create Service Request</h1>
  
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

      <form @submit.prevent="requestService" class="p-4 border rounded bg-white">
        <div class="mb-3">
          <label for="service_id" class="form-label"><strong>Service:</strong></label>
          <select id="service_id" v-model="serviceId" class="form-select" required @change="updateServiceInfo">
            <option value="" selected>Select a Service</option>
            <option v-for="service in services" :key="service.id" :value="service.id">
              {{ service.name }}
            </option>
          </select>
        </div>
  
        <div v-if="showServiceInfo" id="service-info" class="border p-1 rounded" style="line-height: 1.0; margin-bottom: 1rem;">
          <p><strong>Field of Service:</strong> {{ selectedService.field_of_service }}</p>
          <p><strong>Price:</strong> {{ selectedService.price }}</p>
          <p><strong>Description:</strong> {{ selectedService.description }}</p>
          <p><strong>Time Required:</strong> {{ selectedService.time_required }}</p>
        </div>
  
        <div class="mb-3">
          <label for="location" class="form-label"><strong>Location (optional):</strong></label>
          <select id="location" v-model="location" class="form-select">
            <option value="">-- Select Location --</option>
            <option v-for="loc in locations" :key="loc" :value="loc">{{ loc }}</option>
          </select>
        </div>
  
        <div class="mb-3">
          <label for="pin_code" class="form-label"><strong>Pin Code (optional):</strong></label>
          <select id="pin_code" v-model="pinCode" class="form-select">
            <option value="">-- Select Pin Code --</option>
            <option v-for="code in pincodes" :key="code" :value="code">{{ code }}</option>
          </select>
        </div>
  
        <button type="submit" class="btn btn-success w-100">Create Request</button>
      </form>
  
      <h2 class="text-center text-primary my-4">Search Service Requests</h2>
      <form @submit.prevent="searchServices" class="p-4 border rounded bg-white">
        <div class="mb-3">
          <label for="search_query" class="form-label"><strong>Search:</strong></label>
          <input type="text" id="search_query" v-model="searchQuery" class="form-control" placeholder="Enter request details">
        </div>
        <button type="submit" class="btn btn-primary w-100">Search</button>
      </form>
    </div>
  </template>
  
  <script>
  import api from '../api';
  
  export default {
    name: 'CreateRequest',
    data() {
      return {
        services: [],
        locations: [],
        pincodes: [],
        serviceId: '',
        location: '',
        pinCode: '',
        searchQuery: '',
        selectedService: {},
        showServiceInfo: false,
        message: '',
        alertType: 'success'
      };
    },
    methods: {
        navigateTo(section) {
      window.location.href = `/customer/${section}`;
    },
      async fetchData() {
        try {
          const response = await api.getCreateRequestData();
          console.log('API Response:', response);
          console.log('Response data:', response.data);
          this.services = response.data.services;
          this.locations = response.data.locations;
          this.pincodes = response.data.pincodes;
        } catch (error) {
          console.error('Error fetching data:', error);
          this.message = 'Failed to load data. Please try again.';
          this.alertType = 'danger';
        }
      },
      updateServiceInfo() {
        if (this.serviceId) {
          this.selectedService = this.services.find(s => s.id === parseInt(this.serviceId));
          this.showServiceInfo = true;
        } else {
          this.showServiceInfo = false;
        }
      },
      async requestService() {
        try {
          await api.requestService({
            service_id: this.serviceId,
            location: this.location,
            pin_code: this.pinCode
          });
          this.message = 'Service request submitted successfully!';
          this.alertType = 'success';
          
          this.serviceId = '';
          this.location = '';
          this.pinCode = '';
          this.showServiceInfo = false;
        } catch (error) {
          console.error('Error creating service request:', error);
          this.message = 'Failed to create service request. Please try again.';
          this.alertType = 'danger';
        }
      },
      searchServices() {
        this.$router.push({
          name: 'SearchResults',
          query: { search_query: this.searchQuery }
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
      this.fetchData();
    }
  };
  </script>  