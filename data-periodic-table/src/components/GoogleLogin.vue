<script setup>
import { ref, onMounted } from 'vue'

const user = ref(null)
const buttonEl = ref(null)

function parseJwt(token) {
  const base64 = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')
  const json = decodeURIComponent(
    atob(base64).split('').map(c => '%' + c.charCodeAt(0).toString(16).padStart(2, '0')).join('')
  )
  return JSON.parse(json)
}

function handleCredentialResponse(response) {
  user.value = parseJwt(response.credential)
  // In a real app, send response.credential to your backend to verify
}

function logout() {
  window.google.accounts.id.disableAutoSelect()
  user.value = null
}

onMounted(() => {
  const init = () => {
    window.google.accounts.id.initialize({
      client_id: import.meta.env.VITE_GOOGLE_CLIENT_ID,
      callback: handleCredentialResponse,
    })
    window.google.accounts.id.renderButton(buttonEl.value, {
      theme: 'outline',
      size: 'large',
    })
  }

  // The Google script loads async, so wait for it if needed
  if (window.google) init()
  else window.addEventListener('load', init)
})
</script>

<template>
  <div>
    <div v-if="!user">
      <h2>Login</h2>
      <div ref="buttonEl"></div>
    </div>

    <div v-else>
      <img :src="user.picture" width="80" style="border-radius: 50%" />
      <p>{{ user.name }}</p>
      <p>{{ user.email }}</p>
      <button @click="logout">Logout</button>
    </div>
  </div>
</template>