<script setup>
import GoogleIcon from './GoogleIcon.vue'

defineProps({
  loading: { type: Boolean, default: false },
  error: { type: String, default: '' },
})

defineEmits(['sign-in'])
</script>

<template>
  <div class="card">
    <h1>Welcome Back</h1>
    <p>Lorem ipsum dolor sit amet, consectetuer adipiscing elit</p>

    <button class="google-button" :disabled="loading" @click="$emit('sign-in')">
      <span class="google-icon">
        <GoogleIcon />
      </span>
      {{ loading ? 'Signing in…' : 'Sign in with Google' }}
    </button>

    <p v-if="error" class="error">{{ error }}</p>
  </div>
</template>

<style scoped>
.card {
  width: 100%;
  min-height: 100vh;
  padding: 48px 24px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border: 0;
  border-radius: 0;
  background: #fff;
  text-align: center;
}

h1 {
  margin: 0 0 12px;
  font-size: 18px;
  font-weight: 500;
  color: #444;
}

p {
  margin: 0 0 28px;
  font-size: 12px;
  color: #666;
}

.google-button {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 8px 14px 8px 8px;
  border: 0;
  border-radius: 4px;
  background: #4285f4;
  color: #fff;
  font-size: 13px;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.google-button:hover {
  background: #3b78dc;
}

.google-button:disabled {
  opacity: 0.7;
  cursor: wait;
}

.google-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 3px;
  background: #fff;
}

.error {
  margin: 16px 0 0;
  color: #c00;
}
</style>