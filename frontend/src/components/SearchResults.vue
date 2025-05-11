<template>
    <div class="container mt-5">
      <h1 class="mb-4">Search Results</h1>
      
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
  
      <div v-if="results.length" class="row">
        <div v-for="service in results" :key="service.id" class="col-md-6 mb-4">
          <div class="card shadow-sm">
            <div class="card-body">
              <h3 class="card-title">{{ service.name }}</h3>
              <p class="card-text"><strong>Field of Service:</strong> {{ service.field_of_service }}</p>
              <p class="card-text"><strong>Price:</strong> {{ service.price }}</p>
              <p class="card-text"><strong>Description:</strong> {{ service.description }}</p>
              <p class="card-text"><strong>Time Required:</strong> {{ service.time_required }}</p>
  
              <form @submit.prevent="requestService(service.id)" class="mt-3">
                <div class="mb-3">
                  <label for="location" class="form-label"><strong>Location (optional):</strong></label>
                  <select :id="'location-' + service.id" v-model="locationSelections[service.id]" class="form-select">
                    <option value="">-- Select Location --</option>
                    <option v-for="loc in locations" :key="loc" :value="loc">{{ loc }}</option>
                  </select>
                </div>
                <div class="mb-3">
                  <label for="pin_code" class="form-label"><strong>Pin Code (optional):</strong></label>
                  <select :id="'pin_code-' + service.id" v-model="pinCodeSelections[service.id]" class="form-select">
                    <option value="">-- Select Pin Code --</option>
                    <option v-for="code in pincodes" :key="code" :value="code">{{ code }}</option>
                  </select>
                </div>
                <button type="submit" class="btn btn-primary w-100">Request Service</button>
              </form>
            </div>
          </div>
        </div>
      </div>
      <p v-else class="text-center text-danger">No services match your search criteria.</p>
      
      <div class="mt-3 text-center">
        <router-link to="/customer/create-request" class="text-decoration-none">Go Back</router-link>
      </div>
    </div>
  </template>
  
  <script>
  import api from '../api';
  
  export default {
    name: 'SearchResults',
    data() {
      return {
        results: [],
        locations: [],
        pincodes: [],
        locationSelections: {},
        pinCodeSelections: {},
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
          const searchQuery = this.$route.query.search_query || '';
          const response = await api.searchServices(searchQuery);
          this.results = response.data.results;
          
          this.results.forEach(service => {
            this.locationSelections[service.id] = '';
            this.pinCodeSelections[service.id] = '';
          });
          
          const locationsResponse = await api.getCreateRequestData();
          this.locations = locationsResponse.data.locations;
          this.pincodes = locationsResponse.data.pincodes;
        } catch (error) {
          console.error('Error fetching search results:', error);
          this.message = 'Failed to load search results. Please try again.';
          this.alertType = 'danger';
        }
      },
      async requestService(serviceId) {
        try {
          await api.requestService({
            service_id: serviceId,
            location: this.locationSelections[serviceId],
            pin_code: this.pinCodeSelections[serviceId]
          });
          this.message = 'Service request submitted successfully!';
          this.alertType = 'success';
          
          this.locationSelections[serviceId] = '';
          this.pinCodeSelections[serviceId] = '';
        } catch (error) {
          console.error('Error creating service request:', error);
          this.message = 'Failed to create service request. Please try again.';
          this.alertType = 'danger';
        }
      }
    },
    watch: {
      '$route.query.search_query': function() {
        this.fetchData();
      }
    },
    mounted() {
      this.fetchData();
    }
  };
  </script>  