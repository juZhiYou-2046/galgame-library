import axios from 'axios'

const http = axios.create({
  baseURL: '/api',
})

export async function getReviews(gameId) {
  const response = await http.get(`/games/${gameId}/reviews`)
  return response.data
}

export async function createReview(gameId, data) {
  const response = await http.post(`/games/${gameId}/reviews`, data)
  return response.data
}

export async function deleteReview(gameId, reviewId) {
  await http.delete(`/games/${gameId}/reviews/${reviewId}`)
}
