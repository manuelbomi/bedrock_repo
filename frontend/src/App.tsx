import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import ChatPage from './pages/ChatPage'
import SessionsPage from './pages/SessionsPage'
import Layout from './components/Layout'

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Navigate to="/chat" replace />} />
          <Route path="/chat" element={<ChatPage />} />
          <Route path="/chat/:sessionId" element={<ChatPage />} />
          <Route path="/sessions" element={<SessionsPage />} />
        </Routes>
      </Layout>
    </Router>
  )
}

export default App
