<template>
    <div class="container mt-5 text-center">
      <h1 class="text-primary">{{ title }}</h1>
      <p class="text-muted">{{ description }}</p>
      <div class="mt-4">
        <button
          v-for="action in actions"
          :key="action.label"
          :class="'btn btn-lg m-2 ' + getButtonClass(action.label)"
          @click="navigate(action.url)"
        >
          {{ action.label }}
        </button>
      </div>
    </div>
  </template>
  
  <script>
  import api from '../api';
  
  export default {
    data() {
      return {
        title: '',
        description: '',
        actions: []
      };
    },
    mounted() {
      api.getHomeData()
        .then(response => {
          this.title = response.data.title;
          this.description = response.data.description;
          this.actions = response.data.actions;
        })
        .catch(error => console.error('Error fetching home data:', error));
    },
    methods: {
      navigate(url) {
        this.$router.push(url);
      },
      getButtonClass(label) {
        if (label.includes('Admin')) return 'btn-primary';
        if (label.includes('Professional')) return 'btn-secondary';
        if (label.includes('Customer')) return 'btn-info';
        return 'btn-outline-primary';
      }
    }
  };
  </script>
  
  <style>
  @import 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css';
  </style>
  
