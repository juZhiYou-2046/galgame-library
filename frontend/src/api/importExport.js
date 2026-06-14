import axios from 'axios'

const http = axios.create({
  baseURL: '/api',
})

export function getExportUrl(format) {
  return `/api/games/export?format=${format}`
}

export async function importGames(file, conflictStrategy = 'skip') {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('conflict_strategy', conflictStrategy)
  const response = await http.post('/games/import', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return response.data
}
