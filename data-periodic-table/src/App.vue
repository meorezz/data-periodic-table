<script setup>
import { ref, onMounted } from 'vue'
import { signInWithPopup, signOut as firebaseSignOut, onAuthStateChanged } from 'firebase/auth'
import { auth, firebaseConfigError, googleProvider } from './firebase'
import { apiRequest } from './api'
import LoginCard from './components/LoginCard.vue'
import PeriodicTable from './components/PeriodicTable.vue'

const user = ref(null)
const sheetHeaders = ref([])
const sheetRows = ref([])
const error = ref('')
const loading = ref(false)
if (firebaseConfigError.length) {
  error.value = `Firebase is not configured. Add: ${firebaseConfigError.join(', ')}`
}

async function registerUser() {
  const data = await apiRequest('/api/login', { method: 'POST' })
  const sheet = await apiRequest('/api/sheet')
  user.value = data.user
  sheetHeaders.value = sheet.headers
  sheetRows.value = sheet.rows
}

async function signIn() {
  error.value = ''
  loading.value = true
  try {
    if (!auth) throw new Error('Firebase is not configured. Add the required VITE_FIREBASE_* values.')
    await signInWithPopup(auth, googleProvider)
    await registerUser()
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

async function signOut() {
  if (!auth) return
  await firebaseSignOut(auth)
  user.value = null
}

onMounted(() => {
  if (!auth) return
  onAuthStateChanged(auth, async (firebaseUser) => {
    if (!firebaseUser || user.value) return
    try {
      await registerUser()
    } catch (e) {
      error.value = e.message
    }
  })
})
</script>

<template>
  <div class="page">
    <LoginCard
      v-if="!user"
      :loading="loading"
      :error="error"
      @sign-in="signIn"
    />
    <PeriodicTable
      v-else
      :user="user"
      :headers="sheetHeaders"
      :rows="sheetRows"
      @sign-out="signOut"
    />
  </div>
</template>

<style scoped>
.page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  box-sizing: border-box;
  padding: 24px;
  background: #f5f6f8;
  font-family: Arial, sans-serif;
}
</style>