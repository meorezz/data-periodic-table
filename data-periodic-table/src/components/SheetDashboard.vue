<script setup>
import { ref, onMounted } from 'vue'
import { apiRequest } from '../api'

defineProps({
  user: { type: Object, required: true },
})

defineEmits(['sign-out'])

const headers = ref([])
const rows = ref([])
const loading = ref(false)
const error = ref('')

async function loadSheet() {
  error.value = ''
  loading.value = true
  try {
    const data = await apiRequest('/api/sheet')
    headers.value = data.headers
    rows.value = data.rows
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

onMounted(loadSheet)
</script>

<template>
  <div class="dashboard">
    <header class="header">
      <div class="profile">
        <img :src="user.picture" alt="" class="avatar" referrerpolicy="no-referrer" />
        <div>
          <strong>{{ user.name }}</strong>
          <div class="email">{{ user.email }}</div>
        </div>
      </div>

      <div class="actions">
        <button :disabled="loading" @click="loadSheet">
          {{ loading ? 'Loading…' : 'Refresh data' }}
        </button>
        <button @click="$emit('sign-out')">Sign out</button>
      </div>
    </header>

    <p v-if="error" class="error">{{ error }}</p>
    <p v-else-if="loading && !rows.length" class="message">Loading sheet data…</p>
    <p v-else-if="!rows.length" class="message">The sheet has no data rows.</p>

    <div v-if="rows.length" class="table-wrapper">
      <table>
        <thead>
          <tr>
            <th v-for="(header, index) in headers" :key="index">{{ header }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, rowIndex) in rows" :key="rowIndex">
            <td v-for="(_, columnIndex) in headers" :key="columnIndex">
              {{ row[columnIndex] }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.dashboard {
  align-self: flex-start;
  width: 100%;
  max-width: 960px;
  padding: 24px;
  border: 1px solid #eee;
  border-radius: 6px;
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.header {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 20px;
}

.profile {
  display: flex;
  align-items: center;
  gap: 12px;
}

.avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
}

.email,
.message {
  margin: 0;
  font-size: 12px;
  color: #666;
}

.actions button {
  margin-left: 8px;
  padding: 6px 14px;
  border: 1px solid #ccc;
  border-radius: 4px;
  background: none;
  cursor: pointer;
}

.actions button:disabled {
  opacity: 0.6;
  cursor: wait;
}

.error {
  margin: 12px 0 0;
  color: #c00;
}

.table-wrapper {
  max-height: 60vh;
  overflow: auto;
  border: 1px solid #eee;
  border-radius: 4px;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

th,
td {
  padding: 8px 12px;
  border-bottom: 1px solid #eee;
  text-align: left;
  white-space: nowrap;
}

th {
  position: sticky;
  top: 0;
  background: #f0f3fa;
}

tr:hover td {
  background: #fafbfe;
}
</style>