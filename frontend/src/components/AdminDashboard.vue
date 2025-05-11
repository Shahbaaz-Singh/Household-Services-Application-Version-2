<template>
  <div class="container mt-5">
    <h1 class="mb-4">Admin Dashboard</h1>

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

    <div class="graph-container">
      <h2>Dashboard Analytics</h2>
      <canvas id="dashboardChart"></canvas>
    </div>
  </div>
</template>

<script>
import api from '../api';
import Chart from 'chart.js/auto';

export default {
  name: 'AdminDashboard',
  data() {
    return {
      chart: null,
      dashboardData: {}
    };
  },
  methods: {
    async fetchDashboardData() {
      try {
        const response = await api.getAdminDashboard();

        this.dashboardData = {
          active_customers: response.data.active_customers,
          blocked_customers: response.data.blocked_customers,
          active_professionals: response.data.active_professionals,
          inactive_professionals: response.data.inactive_professionals,
          total_services: response.data.total_services
        };

        this.renderChart();
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
        alert('Unable to load dashboard data.');
      }
    },
    renderChart() {
      const ctx = document.getElementById('dashboardChart').getContext('2d');

      if (this.chart) this.chart.destroy();

      this.chart = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: ['Active Customers', 'Blocked Customers', 'Active Professionals', 'Inactive Professionals', 'Total Services'],
          datasets: [{
            label: '',
            data: [
              this.dashboardData.active_customers,
              this.dashboardData.blocked_customers,
              this.dashboardData.active_professionals,
              this.dashboardData.inactive_professionals,
              this.dashboardData.total_services
            ],
            backgroundColor: ['green', 'red', 'blue', 'orange', 'purple']
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
    },

    navigateTo(section) {
      window.location.href = `/admin/${section}`;
    },

    async logout() {
      try {
        await api.adminLogout();
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
}
</style>
