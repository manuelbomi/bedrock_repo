import { useEffect, useRef, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Send, Loader2, Plus, AlertCircle } from 'lucide-react'
import { useMutation } from '@tanstack/react-query'
import { api } from '@/lib/api'
import { useChatStore } from '@/store/chatStore'
import ReactMarkdown from 'react-markdown'

export default function ChatPage() {
  const { sessionId } = useParams()
  const navigate = useNavigate()
  const [input, setInput] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const {
    messages,
    currentSessionId,
    isLoading,
    error,
    addMessage,
    setCurrentSessionId,
    setLoading,
    setError,
    clearMessages,
  } = useChatStore()

  const chatMutation = useMutation({
    mutationFn: api.sendMessage,
    onSuccess: (data) => {
      addMessage({
        id: `${Date.now()}-assistant`,
        role: 'assistant',
        content: data.response,
        timestamp: data.timestamp,
      })

      if (!currentSessionId) {
        setCurrentSessionId(data.session_id)
        navigate(`/chat/${data.session_id}`, { replace: true })
      }

      setLoading(false)
      setError(null)
    },
    onError: (error: any) => {
      setLoading(false)
      setError(error.response?.data?.detail || 'Failed to send message')
    },
  })

  useEffect(() => {
    if (sessionId && sessionId !== currentSessionId) {
      clearMessages()
      setCurrentSessionId(sessionId)
    }
  }, [sessionId, currentSessionId, clearMessages, setCurrentSessionId])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    const userMessage = {
      id: `${Date.now()}-user`,
      role: 'user' as const,
      content: input,
      timestamp: new Date().toISOString(),
    }

    addMessage(userMessage)
    setLoading(true)
    setInput('')

    chatMutation.mutate({
      prompt: input,
      session_id: currentSessionId || undefined,
    })
  }

  const handleNewChat = () => {
    clearMessages()
    navigate('/chat')
  }

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)] lg:h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Chat</h2>
            {currentSessionId && (
              <p className="text-sm text-gray-500 mt-1">
                Session: {currentSessionId.slice(0, 8)}...
              </p>
            )}
          </div>
          <button
            onClick={handleNewChat}
            className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
          >
            <Plus className="w-5 h-5" />
            <span className="hidden sm:inline">New Chat</span>
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-6 space-y-4 scrollbar-thin">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="bg-white rounded-2xl p-8 max-w-md shadow-sm border border-gray-200">
              <h3 className="text-2xl font-bold text-gray-900 mb-3">
                Welcome to AI Assistant
              </h3>
              <p className="text-gray-600 mb-6">
                I'm your AI support assistant powered by AWS Bedrock. I can help you with:
              </p>
              <ul className="text-left space-y-2 text-gray-700">
                <li className="flex items-start gap-2">
                  <span className="text-primary-600 font-bold">•</span>
                  <span>Answering product questions from our FAQ</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary-600 font-bold">•</span>
                  <span>Troubleshooting technical issues</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary-600 font-bold">•</span>
                  <span>Providing account and billing support</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary-600 font-bold">•</span>
                  <span>Remembering our conversation context</span>
                </li>
              </ul>
              <p className="text-gray-600 mt-6">
                Start by typing your question below!
              </p>
            </div>
          </div>
        ) : (
          <div className="max-w-4xl mx-auto space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${
                  message.role === 'user' ? 'justify-end' : 'justify-start'
                }`}
              >
                <div
                  className={`chat-message ${message.role} max-w-[85%] sm:max-w-[75%]`}
                >
                  {message.role === 'user' ? (
                    <p className="whitespace-pre-wrap">{message.content}</p>
                  ) : (
                    <div className="prose prose-sm max-w-none">
                      <ReactMarkdown>{message.content}</ReactMarkdown>
                    </div>
                  )}
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="chat-message assistant flex items-center gap-2">
                  <Loader2 className="w-5 h-5 animate-spin text-primary-600" />
                  <span className="text-gray-600">Thinking...</span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Error message */}
      {error && (
        <div className="px-6 py-3 bg-red-50 border-t border-red-200">
          <div className="flex items-center gap-2 text-red-800">
            <AlertCircle className="w-5 h-5" />
            <span>{error}</span>
          </div>
        </div>
      )}

      {/* Input */}
      <div className="bg-white border-t border-gray-200 px-4 py-4">
        <form onSubmit={handleSendMessage} className="max-w-4xl mx-auto">
          <div className="flex gap-3">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type your message..."
              disabled={isLoading}
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
            />
            <button
              type="submit"
              disabled={!input.trim() || isLoading}
              className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {isLoading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Send className="w-5 h-5" />
              )}
              <span className="hidden sm:inline">Send</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
