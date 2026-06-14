import axios from 'axios'

const http = axios.create({
  baseURL: '/api',
})

export async function getTags() {
  const response = await http.get('/tags')
  return response.data
}

export async function getTagSuggestions(query = '') {
  const response = await http.get('/tags/suggestions', { params: { q: query } })
  return response.data
}
