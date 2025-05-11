<template>
    <div class="container mt-5 login-container">
      <h1 class="mb-4 text-center">Customer Login</h1>
    
      <div v-if="message" class="alert" :class="'alert-' + alertType">
          {{ message }}
      </div>
    
      <form @submit.prevent="login" class="border p-4 rounded bg-light shadow-sm">
          <input v-model="username" placeholder="Username" class="form-control mb-3" required />
          <input v-model="password" type="password" placeholder="Password" class="form-control mb-3" required />
          <button type="submit" class="btn btn-primary w-100">Login</button>
      </form>
    
      <div class="mt-3 text-center">
          <a href="/" class="text-decoration-none">Back to Home</a>
      </div>
    </div>
    </template>
    
    <script>
    import api from '../api';
    
    export default {
    data() {
      return {
          username: '',
          password: '',
          message: '',
          alertType: 'danger'
      };
    },
    methods: {
      async login() {
          try {
              const response = await api.customerLogin({
                  username: this.username,
                  password: this.password
              });
        
              localStorage.setItem('customerToken', response.data.access_token);
        if (response.data.refresh_token) {
          localStorage.setItem('customerRefreshToken', response.data.refresh_token);
        }
        const token = localStorage.getItem('customerToken');
        
        this.message = 'Login Successful! Redirecting to dashboard...';
        this.alertType = 'success';

        setTimeout(() => {
            if (token) {
                window.location.href = '/customer/dashboard';
            } else {
                console.error('Token not found, redirect aborted.');
            }
        }, 1000);
    } catch (error) {
    console.error('Login Error:', error);

    const status = error.response?.status;

    if (status === 401) {
        this.message = 'Invalid username or password.';
    } else if (status === 403) {
        this.message = 'Your account is blocked. Please contact the admin.';
    } else {
        this.message = 'An unexpected error occurred. Please try again later.';
    }

    this.alertType = 'danger';
}

}
    }
    };
    </script>
    <style>
    @import 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css';
    .login-container { max-width:400px; margin:auto; }
    </style>    