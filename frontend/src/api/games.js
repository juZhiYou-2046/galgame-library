import axios from 'axios'

const http = axios.create({
  baseURL: '/api',
})

export async function getGames(params = {}) {
  const response = await http.get('/games', { params })
  return response.data
}

export async function getGame(id) {
  const response = await http.get(`/games/${id}`)
  return response.data
}

export async function createGame(data) {
  const response = await http.post('/games', data)
  return response.data
}

export async function updateGame(id, data) {
  const response = await http.put(`/games/${id}`, data)
  return response.data
}

export async function deleteGame(id) {
  await http.delete(`/games/${id}`)
}

export async function uploadCover(gameId, file) {
  const formData = new FormData()
  formData.append('file', file)
  const response = await http.post(`/games/${gameId}/cover`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return response.data
}