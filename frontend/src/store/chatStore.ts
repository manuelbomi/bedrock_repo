import { create } from 'zustand'

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: string
}

interface ChatState {
  messages: Message[]
  currentSessionId: string | null
  isLoading: boolean
  error: string | null

  addMessage: (message: Message) => void
  setMessages: (messages: Message[]) => void
  setCurrentSessionId: (sessionId: string | null) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  clearMessages: () => void
}

export const useChatStore = create<ChatState>((set) => ({
  messages: [],
  currentSessionId: null,
  isLoading: false,
  error: null,

  addMessage: (message) =>
    set((state) => ({
      messages: [...state.messages, message],
    })),

  setMessages: (messages) => set({ messages }),

  setCurrentSessionId: (sessionId) => set({ currentSessionId: sessionId }),

  setLoading: (loading) => set({ isLoading: loading }),

  setError: (error) => set({ error }),

  clearMessages: () => set({ messages: [], currentSessionId: null }),
}))
