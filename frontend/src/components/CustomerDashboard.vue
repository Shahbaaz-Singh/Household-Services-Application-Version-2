<template>
    <div class="container mt-5">
      <h1 class="mb-4">Customer Dashboard</h1>

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
  
      <div class="graph-container">
        <h2>Service Request Status Analysis</h2>
        <canvas id="dashboardChart"></canvas>
      </div>
    </div>
  </template>
  
  <script>
  import api from '../api';
  import Chart from 'chart.js/auto';
  
  export default {
    name: 'CustomerDashboard',
    data() {
      return {
        chart: null,
        serviceRequestStatusCounts: {}
      };
    },
    methods: {
      async fetchDashboardData() {
  try {
    const response = await api.getCustomerDashboard();
    console.log('Dashboard response:', response.data);
    this.serviceRequestStatusCounts = response.data.data.service_requests;
    console.log('Status counts:', this.serviceRequestStatusCounts);
    this.renderChart();
  } catch (error) {
    console.error('Error fetching dashboard data:', error);
    alert('Unable to load dashboard data.');
  }
},
      renderChart() {
  this.$nextTick(() => {
    const canvas = document.getElementById('dashboardChart');
    if (!canvas) {
      console.error('Canvas element not found');
      return;
    }
    
    const ctx = canvas.getContext('2d');
    if (this.chart) this.chart.destroy();

    console.log('Service request data:', this.serviceRequestStatusCounts);
    
    this.chart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: ['Pending', 'Accepted', 'In Progress', 'Completed', 'Closed'],
        datasets: [{
          label: 'Service Requests',
          data: [
            this.serviceRequestStatusCounts.pending || 0,
            this.serviceRequestStatusCounts.accepted || 0,
            this.serviceRequestStatusCounts.in_progress || 0,
            this.serviceRequestStatusCounts.completed || 0,
            this.serviceRequestStatusCounts.closed || 0,
          ],
          backgroundColor: ['red', 'green', 'blue', 'yellow', 'orange']
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false
          }
        }
      }
    });
  });
},
  
      navigateTo(section) {
        window.location.href = `/customer/${section}`;
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
      this.fetchDashboardData();
    }
  };
  </script>
  
  <style scoped>
  .graph-container {
  height: 400px;
  position: relative;
}
  </style>
  









  