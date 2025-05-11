<template>
    <div class="container mt-5">
      <h1 class="mb-4">Professional Dashboard</h1>

      <div class="row mb-3">
        <div class="col">
          <button @click="navigateTo('dashboard')" class="btn btn-info w-100 mb-2">
            Dashboard
          </button>
        </div>
        <div class="col">
          <button @click="navigateTo('pending-requests')" class="btn btn-info w-100 mb-2">
            View Pending Requests
          </button>
        </div>
        <div class="col">
          <button @click="navigateTo('accepted-requests')" class="btn btn-info w-100 mb-2">
            View Accepted Requests
          </button>
        </div>
        <div class="col">
          <button @click="logout" class="btn btn-danger w-100 mb-2">
            Logout
          </button>
        </div>
      </div>

      <div class="row mb-3">
        <div class="col">
          <button @click="exportPendingRequests" class="btn btn-warning w-100 mb-2">
        Export CSV for Service Requests
          </button>
        </div>
        <div class="col">
          <button @click="downloadExportedCsv" class="btn btn-success w-100 mb-2">
        Download Exported CSV
          </button>
        </div>
      </div>


      <h2>{{ professionalInfo.username }}'s Profile</h2>
      <h3>Rating: {{ professionalInfo.rating }} / 5</h3>
      <h4>Number of Reviews: {{ professionalInfo.num_reviews }}</h4>
  
      <div class="chart-container mt-4">
        <h2>Service Request Statistics</h2>
        <canvas id="requestStatsChart"></canvas>
      </div>
    </div>
  </template>
  
  <script>
  import api from '../api';
  import Chart from 'chart.js/auto';
  
  export default {
    name: 'ProfessionalDashboard',
    data() {
      return {
        professionalInfo: {
          username: '',
          rating: 0,
          num_reviews: 0,
          expertise: '',
          is_approved: false
        },
        requestStats: {
          rejected: 0,
          accepted: 0,
          completed: 0,
          pending: 0,
          in_progress: 0
        },
        chart: null
      };
    },
    methods: {
      async fetchDashboardData() {
        try {
  
          const response = await api.getProfessionalDashboard();
          
          this.professionalInfo = response.data.professional_info;
          this.requestStats = response.data.request_stats;
          
          this.renderChart();
        } catch (error) {
          console.error('Error fetching dashboard data:', error);
          alert('Unable to load dashboard data. Please try again.');
        }
      },
      async exportPendingRequests() {
  try {
    const response = await api.exportPendingRequests();

    if (response.data.success) {
      alert('Export job started! You will receive a notification when it’s done.');
    } else {
      alert('Failed to start export: ' + response.data.message);
    }
  } catch (error) {
    console.error('Error exporting pending requests:', error);
    console.log(error)
    alert('An error occurred while starting the export.');
  }
},
async downloadExportedCsv() {
      try {
        const response = await api.downloadProfessionalExport();
        if (response.status === 200) {
          const url = window.URL.createObjectURL(new Blob([response.data]));
          const link = document.createElement("a");
          link.href = url;
          link.setAttribute("download", "pending_requests.csv");
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
          alert("CSV file downloaded successfully!");
        } else {
          alert(response.data.message);
        }
      } catch (error) {
        console.error("Error downloading CSV:", error);
        alert("Failed to download CSV.");
      }
    },

      renderChart() {
        const ctx = document.getElementById('requestStatsChart').getContext('2d');
        
        if (this.chart) this.chart.destroy();
        
        this.chart = new Chart(ctx, {
          type: 'bar',
          data: {
            labels: ['Rejected', 'Accepted', 'Completed', 'Pending', 'In Progress'],
            datasets: [{
              label: '',
              data: [
                this.requestStats.rejected,
                this.requestStats.accepted,
                this.requestStats.completed,
                this.requestStats.pending,
                this.requestStats.in_progress
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
      },
      navigateTo(section) {
        window.location.href = `/professional/${section}`;
      },
      logout() {
        api.professionalLogout();
      }
    },
    mounted() {
      this.fetchDashboardData();
    }
  };
  </script>
  
  <style scoped>
  .chart-container {
    height: 400px;
  }
  </style>
  