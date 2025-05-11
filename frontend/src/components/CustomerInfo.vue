<template>
  <div class="container mt-5">
    <h1 class="mb-4">Customer Info</h1>

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
      <search-bar @search="searchCustomers" />
      <ul class="list-group mb-4">
        <li v-for="customer in customers" :key="customer.id" class="list-group-item">
          {{ customer.username }}
          <button @click="toggleBlock(customer)" class="btn btn-sm me-2" :class="customer.is_blocked ? 'btn-success' : 'btn-danger'">
            {{ customer.is_blocked ? 'Unblock' : 'Block' }}
          </button>
          <button @click="toggleInfo(customer)" class="btn btn-info btn-sm me-2">View More Info</button>
          <div v-if="customer.showInfo">
            <ul>
                <li><strong>Location:</strong> {{ customer.location }}</li>
                <li><strong>Pin Code:</strong> {{ customer.pin_code }}</li>
                <li><strong>Phone Number:</strong> {{ customer.phone_number }}</li>
                <li><strong>Email:</strong> {{ customer.email }}</li>
                <li><strong>Address:</strong> {{ customer.address }}</li>
            </ul>
          </div>
        </li>
      </ul>
    </div>
  </template>
  
  <script>
  import api from '../api';
  import SearchBar from './SearchBar.vue';
  
  export default {
    components: { SearchBar },
    data() {
      return {
        customers: []
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
      async searchCustomers(query) {
        const response = await api.getCustomers(query);
        this.customers = response.data;
      },
      async toggleBlock(customer) {
        if (customer.is_blocked) {
          await api.unblockUser(customer.id);
        } else {
          await api.blockUser(customer.id);
        }
        customer.is_blocked = !customer.is_blocked;
      },
      toggleInfo(customer) {
        customer.showInfo = !customer.showInfo;
      }
    },
    mounted() {
      this.searchCustomers();
    }
  }

  </script>