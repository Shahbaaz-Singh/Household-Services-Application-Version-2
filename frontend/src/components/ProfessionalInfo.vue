<template>
  <div class="container mt-5">
    <h1 class="mb-4">Professional Info</h1>

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

    <search-bar @search="searchProfessionals" />

    <ul class="list-group mb-4">
      <li v-for="professional in professionals" :key="professional.id" class="list-group-item">
        {{ professional.username }}
        <button
          @click="toggleApproval(professional)"
          class="btn btn-sm me-2"
          :class="professional.is_approved ? 'btn-danger' : 'btn-success'"
        >
          {{ professional.is_approved ? 'Block' : 'Approve' }}
        </button>

        <a
          v-if="professional.documents"
          :href="getDocumentUrl(professional.documents)"
          target="_blank"
          class="btn btn-info btn-sm me-2"
        >
          View Document
        </a>
        <button @click="toggleInfo(professional)" class="btn btn-info btn-sm">View More Info</button>

        <div v-if="professional.showInfo" class="info-container">
          <ul>
            <li><strong>Expertise:</strong> {{ professional.expertise }}</li>
            <li><strong>Rating:</strong> {{ professional.rating }} ({{ professional.num_reviews }} reviews)</li>
            <li><strong>Location:</strong> {{ professional.location }}</li>
            <li><strong>Pin Code:</strong> {{ professional.pin_code }}</li>
            <li><strong>Phone:</strong> {{ professional.phone_number }}</li>
            <li><strong>Email:</strong> {{ professional.email }}</li>
            <li><strong>Address:</strong> {{ professional.address }}</li>
            <li><strong>Approval Status:</strong> {{ professional.is_approved ? 'Approved' : 'Pending' }}</li>
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
      professionals: []
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
    async searchProfessionals(query) {
      const response = await api.getProfessionals(query);
      this.professionals = response.data;
    },
    async toggleApproval(professional) {
      if (professional.is_approved) {
        await api.unapproveUser(professional.id);
      } else {
        await api.approveUser(professional.id);
      }
      professional.is_approved = !professional.is_approved;
    },
    toggleInfo(professional) {
      professional.showInfo = !professional.showInfo;
    },
    getDocumentUrl(filename) {
      if (!filename) return '';
      return `http://127.0.0.1:5000/api/documents/${encodeURIComponent(filename.replace(/\\/g, '/'))}`;
    }
  },
  mounted() {
    this.searchProfessionals();
  }
}
</script>

