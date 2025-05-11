<template>
    <div class="container mt-5 register-container">
      <h2 class="text-primary text-center">Register</h2>
  
      <div v-if="message" class="alert" :class="'alert-' + alertType">
        {{ message }}
      </div>
  
      <form @submit.prevent="register" enctype="multipart/form-data" class="border p-4 rounded bg-light shadow-sm">
        <div class="mb-3">
          <label for="username" class="form-label fw-bold">Username:</label>
          <input v-model="form.username" type="text" id="username" class="form-control" required />
        </div>
  
        <div class="mb-3">
          <label for="password" class="form-label fw-bold">Password:</label>
          <input v-model="form.password" type="password" id="password" class="form-control" required />
        </div>
  
        <div class="mb-3">
          <label for="confirm_password" class="form-label fw-bold">Confirm Password:</label>
          <input v-model="form.confirm_password" type="password" id="confirm_password" class="form-control" required />
        </div>
  
        <div class="mb-3">
          <label for="role" class="form-label fw-bold">Role:</label>
          <select v-model="form.role" id="role" class="form-select">
            <option value="" disabled>Select Role</option>
            <option value="customer">Customer</option>
            <option value="professional">Service Professional</option>
          </select>
        </div>
  
        <div v-if="form.role === 'professional'" class="mb-3">
          <label for="expertise" class="form-label fw-bold">Field of Expertise:</label>
          <select v-model="form.expertise" id="expertise" class="form-select">
            <option value="" disabled>Select Expertise</option>
            <option v-for="field in expertiseFields" :key="field.value" :value="field.value">
              {{ field.label }}
            </option>
          </select>
        </div>
  
        <div v-if="form.role === 'professional'" class="mb-3">
          <label for="documents" class="form-label fw-bold">Upload Documents:</label>
          <input @change="handleFileUpload" type="file" id="documents" class="form-control-file" />
        </div>
        
        <div class="mb-3">
          <label for="location" class="form-label fw-bold">Location:</label>
          <input v-model="form.location" type="text" id="location" class="form-control" required />
        </div>
  
        <div class="mb-3">
          <label for="pin_code" class="form-label fw-bold">Pin Code:</label>
          <input v-model="form.pin_code" type="text" id="pin_code" class="form-control" required />
        </div>
  
        <div class="mb-3">
          <label for="phone_number" class="form-label fw-bold">Phone Number:</label>
          <input v-model="form.phone_number" type="text" id="phone_number" class="form-control" required />
        </div>
  
        <div class="mb-3">
          <label for="email" class="form-label fw-bold">Email:</label>
          <input v-model="form.email" type="email" id="email" class="form-control" required />
        </div>
  
        <div class="mb-3">
          <label for="address" class="form-label fw-bold">Address:</label>
          <textarea v-model.trim.lazy="form.address" id="address" class="form-control" required></textarea>
        </div>
  
        <button type="submit" class="btn btn-primary">Register</button>
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
      form: {
        username: '',
        password: '',
        confirm_password: '',
        role: '',
        expertise: '',
        location: '',
        pin_code: '',
        phone_number: '',
        email: '',
        address: '',
        documents: null
      },
      message: '',
      alertType: '',
      expertiseFields: [
        { value: 'Electrical', label: 'Electrical' },
        { value: 'Plumbing', label: 'Plumbing' },
        { value: 'Cleaning', label: 'Cleaning' },
        { value: 'Landscaping', label: 'Landscaping' },
        { value: 'Handyman', label: 'Handyman' },
        { value: 'Carpentry', label: 'Carpentry' },
        { value: 'Pest Control', label: 'Pest Control' },
        { value: 'HVAC', label: 'HVAC' },
        { value: 'Painting', label: 'Painting' },
        { value: 'Roofing', label: 'Roofing' },
        { value: 'Masonry', label: 'Masonry' },
        { value: 'Glass Repair', label: 'Glass Repair' },
        { value: 'Flooring', label: 'Flooring' },
        { value: 'Furniture Assembly', label: 'Furniture Assembly' },
        { value: 'Appliance Repair', label: 'Appliance Repair' },
        { value: 'Computer Repair', label: 'Computer Repair' },
        { value: 'Window Cleaning', label: 'Window Cleaning' },
        { value: 'Gutter Cleaning', label: 'Gutter Cleaning' },
        { value: 'Moving Services', label: 'Moving Services' },
        { value: 'Security Services', label: 'Security Services' }
      ]
    };
  },
  methods: {
    handleFileUpload(event) {
      this.form.documents = event.target.files[0];
    },
    async register() {
      if (this.form.password !== this.form.confirm_password) {
        this.message = 'Passwords do not match';
        this.alertType = 'danger';
        window.scrollTo(0, 0);
        return;
      }

      const formData = new FormData();
      Object.keys(this.form).forEach(key => {
        if (this.form[key]) formData.append(key, this.form[key]);
      });

      try {
        const response = await api.registerRole(formData);
        this.message = response.data.message;
        this.alertType = 'success';
        window.scrollTo(0, 0);
        
        this.form = {
          username: '', password: '', confirm_password: '', role: '', expertise: '', location: '',
          pin_code: '', phone_number: '', email: '', address: '', documents: null
        };
      } catch (error) {
        this.message = error.response.data.message || 'Registration failed.';
        this.alertType = 'danger';
        window.scrollTo(0, 0);
      }
    }
  }
};

</script>
<style scoped>
.register-container {
  max-width: 550px;
  margin: auto;
  max-height: 90vh;
}
</style>