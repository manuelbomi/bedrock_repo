import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

export interface ChatRequest {
  prompt: string
  session_id?: string
}

export interface ChatResponse {
  response: string
  session_id: string
  timestamp: string
}

export interface SessionInfo {
  session_id: string
  user_id: string
  created_at: string
  last_message_at: string
  message_count: number
}

export interface UserInfo {
  user_id: string
  email: string
  created_at: string
  session_count: number
}

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add auth token to requests if available
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const api = {
  // Chat endpoints
  sendMessage: async (request: ChatRequest): Promise<ChatResponse> => {
    const { data } = await apiClient.post<ChatResponse>('/chat', request)
    return data
  },

  // Session endpoints
  getSessions: async (): Promise<SessionInfo[]> => {
    const { data } = await apiClient.get<SessionInfo[]>('/sessions')
    return data
  },

  deleteSession: async (sessionId: string): Promise<void> => {
    await apiClient.delete(`/sessions/${sessionId}`)
  },

  // User endpoints
  getUserInfo: async (): Promise<UserInfo> => {
    const { data } = await apiClient.get<UserInfo>('/user/info')
    return data
  },

  // Health check
  healthCheck: async (): Promise<{ status: string }> => {
    const { data } = await apiClient.get('/health')
    return data
  },
}
