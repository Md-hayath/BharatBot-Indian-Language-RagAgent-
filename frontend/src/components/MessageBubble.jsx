import { FileText } from 'lucide-react'
import { getLanguageDisplay } from '../lib/languages'

export default function MessageBubble({ role, content, sources, lang }) {
  const isUser = role === 'user'

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`flex max-w-[80%] flex-col gap-1.5 ${isUser ? 'items-end' : 'items-start'}`}>
        <div
          className={`whitespace-pre-wrap rounded-2xl px-4 py-2.5 text-sm leading-relaxed shadow-sm ${
            isUser
              ? 'rounded-br-sm bg-gradient-to-br from-indigo-600 to-violet-600 text-white'
              : 'rounded-bl-sm border border-gray-100 bg-white text-gray-800'
          }`}
        >
          {content}
        </div>

        {!isUser && (sources?.length > 0 || lang) && (
          <div className="flex flex-wrap items-center gap-1.5 px-1">
            {lang && (
              <span className="inline-flex items-center rounded-full bg-indigo-50 px-2 py-0.5 text-xs font-medium text-indigo-700">
                {getLanguageDisplay(lang).flag} {getLanguageDisplay(lang).name}
              </span>
            )}
            {sources?.map((s, i) => (
              <span
                key={i}
                className="inline-flex items-center gap-1 rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-600"
              >
                <FileText className="h-3 w-3" />
                {s}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
