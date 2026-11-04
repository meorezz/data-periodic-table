import { auth } from './firebase'

const API_URL = import.meta.env.VITE_API_URL

export async function apiRequest(path, options = {}) {
  const token = await auth.currentUser.getIdToken()
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: { ...options.headers, Authorization: `Bearer ${token}` },
  })
  const body = await response.json().catch(() => ({}))

  if (!response.ok) {
    throw new Error(body.detail || `Request failed (${response.status})`)
  }
  return body
}