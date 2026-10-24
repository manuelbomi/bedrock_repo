import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { Clock, Trash2, MessageSquare, Loader2 } from 'lucide-react'
import { api } from '@/lib/api'
import { formatDistanceToNow } from 'date-fns'

export default function SessionsPage() {
  const queryClient = useQueryClient()

  const { data: sessions, isLoading } = useQuery({
    queryKey: ['sessions'],
    queryFn: api.getSessions,
  })

  const deleteMutation = useMutation({
    mutationFn: api.deleteSession,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sessions'] })
    },
  })

  const handleDelete = async (sessionId: string, e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()

    if (confirm('Are you sure you want to delete this session?')) {
      deleteMutation.mutate(sessionId)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4 sm:p-6 lg:p-8">
      <div className="max-w-6xl mx-auto">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <h1 className="text-2xl font-bold text-gray-900">Chat Sessions</h1>
            <p className="text-gray-600 mt-1">
              View and manage your conversation history
            </p>
          </div>

          <div className="p-6">
            {isLoading ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
              </div>
            ) : !sessions || sessions.length === 0 ? (
              <div className="text-center py-12">
                <MessageSquare className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  No sessions yet
                </h3>
                <p className="text-gray-600 mb-6">
                  Start a conversation to create your first session
                </p>
                <Link
                  to="/chat"
                  className="inline-flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
                >
                  <MessageSquare className="w-5 h-5" />
                  Start Chat
                </Link>
              </div>
            ) : (
              <div className="space-y-3">
                {sessions.map((session) => (
                  <Link
                    key={session.session_id}
                    to={`/chat/${session.session_id}`}
                    className="block"
                  >
                    <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:border-primary-300 hover:bg-primary-50 transition-colors group">
                      <div className="flex items-start gap-4 flex-1 min-w-0">
                        <div className="p-2 bg-primary-100 rounded-lg group-hover:bg-primary-200 transition-colors">
                          <MessageSquare className="w-5 h-5 text-primary-600" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <h3 className="text-sm font-semibold text-gray-900 truncate">
                            Session {session.session_id.slice(0, 8)}...
                          </h3>
                          <div className="flex items-center gap-4 mt-1 text-sm text-gray-600">
                            <div className="flex items-center gap-1">
                              <Clock className="w-4 h-4" />
                              <span>
                                {formatDistanceToNow(
                                  new Date(session.last_message_at),
                                  { addSuffix: true }
                                )}
                              </span>
                            </div>
                            <span className="text-gray-400">•</span>
                            <span>{session.message_count} messages</span>
                          </div>
                        </div>
                      </div>
                      <button
                        onClick={(e) => handleDelete(session.session_id, e)}
                        disabled={deleteMutation.isPending}
                        className="ml-4 p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors disabled:opacity-50"
                      >
                        <Trash2 className="w-5 h-5" />
                      </button>
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Stats card */}
        {sessions && sessions.length > 0 && (
          <div className="mt-6 bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Statistics
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="p-4 bg-primary-50 rounded-lg">
                <p className="text-sm text-primary-600 font-medium">
                  Total Sessions
                </p>
                <p className="text-2xl font-bold text-primary-900 mt-1">
                  {sessions.length}
                </p>
              </div>
              <div className="p-4 bg-green-50 rounded-lg">
                <p className="text-sm text-green-600 font-medium">
                  Total Messages
                </p>
                <p className="text-2xl font-bold text-green-900 mt-1">
                  {sessions.reduce((sum, s) => sum + s.message_count, 0)}
                </p>
              </div>
              <div className="p-4 bg-purple-50 rounded-lg">
                <p className="text-sm text-purple-600 font-medium">
                  Latest Activity
                </p>
                <p className="text-sm font-bold text-purple-900 mt-1">
                  {formatDistanceToNow(
                    new Date(
                      Math.max(
                        ...sessions.map((s) =>
                          new Date(s.last_message_at).getTime()
                        )
                      )
                    ),
                    { addSuffix: true }
                  )}
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
