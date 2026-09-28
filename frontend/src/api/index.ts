import api from './client'

export const login = (email: string, password: string) =>
  api.post('/auth/login', { email, password })

export const register = (email: string, password: string, full_name: string) =>
  api.post('/auth/register', { email, password, full_name })

export const getMe = () => api.get('/auth/me')

export const getObjectTypes = () => api.get('/objects/')
export const getObjectType = (slug: string) => api.get(`/objects/${slug}`)
export const getDemoData = (slug: string) => api.get(`/objects/${slug}/demo-data`)

export const getCategories = () => api.get('/catalog/categories')
export const getSolutions = (params?: any) => api.get('/catalog/solutions', { params })
export const getSolution = (id: number) => api.get(`/catalog/solutions/${id}`)
export const compareSolutions = (ids: string) => api.get('/catalog/solutions/compare/list', { params: { ids } })
export const createSolution = (data: any) => api.post('/catalog/solutions', data)
export const updateSolution = (id: number, data: any) => api.put(`/catalog/solutions/${id}`, data)
export const deleteSolution = (id: number) => api.delete(`/catalog/solutions/${id}`)

export const getProjects = () => api.get('/projects/')
export const getProject = (id: number) => api.get(`/projects/${id}`)
export const createProject = (data: any) => api.post('/projects/', data)
export const updateProject = (id: number, data: any) => api.put(`/projects/${id}`, data)
export const deleteProject = (id: number) => api.delete(`/projects/${id}`)
export const duplicateProject = (id: number) => api.post(`/projects/${id}/duplicate`)
export const uploadParams = (id: number, file: File) => {
  const formData = new FormData()
  formData.append('file', file)
  return api.post(`/projects/${id}/upload-params`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export const createScenario = (projectId: number, data: any) =>
  api.post(`/projects/${projectId}/scenarios`, data)
export const updateScenario = (id: number, data: any) => api.put(`/scenarios/${id}`, data)
export const deleteScenario = (id: number) => api.delete(`/scenarios/${id}`)
export const calculateScenario = (id: number) => api.post(`/scenarios/${id}/calculate`)
export const compareScenarios = (projectId: number) => api.get(`/projects/${projectId}/compare`)

export const matchSolutions = (data: any) => api.post('/recommendations/match', data)

export const exportPDF = (projectId: number) =>
  api.get(`/projects/${projectId}/export/pdf`, { responseType: 'blob' })
export const exportExcel = (projectId: number) =>
  api.get(`/projects/${projectId}/export/excel`, { responseType: 'blob' })

export const getSimulation = (projectId: number, scenarioId?: number) =>
  api.get(`/projects/${projectId}/simulation`, { params: scenarioId ? { scenario_id: scenarioId } : {} })
