import { useEffect, useRef, useState } from 'react'
import { Send, MessageCircleQuestion } from 'lucide-react'
import MessageBubble from './MessageBubble'
import { sendChatMessage } from '../lib/api'

export default function ChatPanel({ sessionId, messages, setMessages }) {
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  async function handleSend() {
    const query = input.trim()
    if (!query || loading) return

    setInput('')
    setMessages((prev) => [...prev, { role: 'user', content: query }])
    setLoading(true)

    try {
      const data = await sendChatMessage(query, sessionId)
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: data.response, sources: data.sources, lang: data.detected_language },
      ])
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: `⚠️ ${err.message || 'Something went wrong. Please try again.'}` },
      ])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-0 flex-1 flex-col rounded-2xl border border-gray-100 bg-white shadow-sm">
      <div className="flex-1 space-y-4 overflow-y-auto px-5 py-6">
        {messages.length === 0 ? (
          <div className="flex h-full flex-col items-center justify-center gap-3 text-center text-gray-400">
            <MessageCircleQuestion className="h-10 w-10 text-indigo-200" />
            <p className="text-sm">Upload a document, then ask a question in any language.</p>
          </div>
        ) : (
          messages.map((m, i) => (
            <MessageBubble key={i} role={m.role} content={m.content} sources={m.sources} lang={m.lang} />
          ))
        )}

        {loading && (
          <div className="flex justify-start">
            <div className="flex items-center gap-1.5 rounded-2xl rounded-bl-sm border border-gray-100 bg-white px-4 py-3 shadow-sm">
              <span className="typing-dot h-1.5 w-1.5 rounded-full bg-indigo-400" style={{ animationDelay: '0ms' }} />
              <span className="typing-dot h-1.5 w-1.5 rounded-full bg-indigo-400" style={{ animationDelay: '150ms' }} />
              <span className="typing-dot h-1.5 w-1.5 rounded-full bg-indigo-400" style={{ animationDelay: '300ms' }} />
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="border-t border-gray-100 p-4">
        <div className="flex items-center gap-2 rounded-full border border-gray-200 bg-gray-50 px-2 py-1.5 focus-within:border-indigo-300 focus-within:ring-2 focus-within:ring-indigo-100">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Type in any language..."
            className="flex-1 bg-transparent px-3 py-1.5 text-sm text-gray-800 placeholder:text-gray-400 focus:outline-none"
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || loading}
            className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-indigo-600 to-violet-600 text-white shadow-sm transition-opacity disabled:opacity-40"
          >
            <Send className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  )
}
