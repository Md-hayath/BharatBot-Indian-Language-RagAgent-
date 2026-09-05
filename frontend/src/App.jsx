import { useState } from 'react'
import Header from './components/Header'
import Sidebar from './components/Sidebar'
import ChatPanel from './components/ChatPanel'

function makeSessionId() {
  return typeof crypto.randomUUID === 'function' ? crypto.randomUUID() : `session-${Date.now()}`
}

export default function App() {
  const [sessionId] = useState(makeSessionId)
  const [messages, setMessages] = useState([])
  const [selectedDocument, setSelectedDocument] = useState('')

  return (
    <div className="flex h-screen flex-col overflow-hidden bg-gradient-to-b from-indigo-50/40 via-white to-white">
      <Header />
      <main className="mx-auto flex w-full max-w-6xl min-h-0 flex-1 flex-col gap-5 px-4 py-6 md:flex-row">
        <Sidebar selectedDocument={selectedDocument} onSelectDocument={setSelectedDocument} />
        <ChatPanel
          sessionId={sessionId}
          messages={messages}
          setMessages={setMessages}
          selectedDocument={selectedDocument}
        />
      </main>
    </div>
  )
}
