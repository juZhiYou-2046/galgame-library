import axios from 'axios'

const http = axios.create({
  baseURL: '/api',
})

export async function scanDirectory(directory, maxDepth = 3) {
  const response = await http.post('/scan', { directory, max_depth: maxDepth })
  return response.data
}