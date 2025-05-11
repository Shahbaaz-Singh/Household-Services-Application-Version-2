<template>
    <div class="search-container">
      <div class="input-group">
        <input 
          type="text" 
          class="form-control" 
          placeholder="Search by username" 
          v-model="searchQuery"
          @input="emitSearch"
        >
        <button class="btn btn-primary" @click="emitSearch">Search</button>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: 'SearchBar',
    props: {
      initialQuery: {
        type: String,
        default: ''
      }
    },
    data() {
      return {
        searchQuery: this.initialQuery
      };
    },
    methods: {
      emitSearch() {
        this.$emit('search', this.searchQuery);
      }
    }
  };
  </script>
  
  <style scoped>
  .search-container {
    margin-bottom: 1rem;
  }
  </style>
  