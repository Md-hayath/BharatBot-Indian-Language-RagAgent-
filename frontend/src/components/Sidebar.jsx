import { useEffect, useRef, useState } from 'react'
import { UploadCloud, FileText, Loader2, CheckCircle2, AlertCircle, Check } from 'lucide-react'
import { uploadDocument, fetchDocuments } from '../lib/api'
import { LANGUAGE_CONFIG } from '../lib/languages'

export default function Sidebar({ selectedDocument, onSelectDocument }) {
  const [dragging, setDragging] = useState(false)
  const [status, setStatus] = useState(null) // { type: 'loading' | 'success' | 'error', message }
  const [documents, setDocuments] = useState([])
  const inputRef = useRef(null)

  async function loadDocuments() {
    try {
      const docs = await fetchDocuments()
      setDocuments(docs)
    } catch {
      // Leave the list as-is if the fetch fails; upload/chat errors surface separately.
    }
  }

  useEffect(() => {
    loadDocuments()
  }, [])

  async function handleFile(file) {
    if (!file) return
    setStatus({ type: 'loading', message: `Processing ${file.name}...` })
    try {
      const data = await uploadDocument(file)
      setStatus({ type: 'success', message: `${data.filename} — ${data.chunks_added} chunks indexed` })
      await loadDocuments()
      onSelectDocument(data.filename)
    } catch (err) {
      setStatus({ type: 'error', message: err.message || 'Upload failed' })
    }
  }

  return (
    <aside className="flex w-full flex-col gap-5 md:w-80 md:shrink-0">
      <div className="rounded-2xl border border-gray-100 bg-white p-5 shadow-sm">
        <h2 className="mb-3 text-sm font-semibold text-gray-900">📁 Upload Documents</h2>

        <div
          onDragOver={(e) => {
            e.preventDefault()
            setDragging(true)
          }}
          onDragLeave={() => setDragging(false)}
          onDrop={(e) => {
            e.preventDefault()
            setDragging(false)
            handleFile(e.dataTransfer.files?.[0])
          }}
          onClick={() => inputRef.current?.click()}
          className={`flex cursor-pointer flex-col items-center gap-2 rounded-xl border-2 border-dashed px-4 py-8 text-center transition-colors ${
            dragging
              ? 'border-indigo-400 bg-indigo-50'
              : 'border-gray-200 bg-gray-50 hover:border-indigo-300 hover:bg-indigo-50/50'
          }`}
        >
          <UploadCloud className="h-7 w-7 text-indigo-500" />
          <p className="text-sm font-medium text-gray-700">Drop a file or click to browse</p>
          <p className="text-xs text-gray-400">PDF, DOCX, or TXT — any language</p>
          <input
            ref={inputRef}
            type="file"
            accept=".pdf,.docx,.txt"
            className="hidden"
            onChange={(e) => handleFile(e.target.files?.[0])}
          />
        </div>

        {status && (
          <div
            className={`mt-3 flex items-start gap-2 rounded-lg px-3 py-2 text-xs ${
              status.type === 'error'
                ? 'bg-red-50 text-red-700'
                : status.type === 'success'
                ? 'bg-emerald-50 text-emerald-700'
                : 'bg-indigo-50 text-indigo-700'
            }`}
          >
            {status.type === 'loading' && <Loader2 className="mt-0.5 h-3.5 w-3.5 shrink-0 animate-spin" />}
            {status.type === 'success' && <CheckCircle2 className="mt-0.5 h-3.5 w-3.5 shrink-0" />}
            {status.type === 'error' && <AlertCircle className="mt-0.5 h-3.5 w-3.5 shrink-0" />}
            <span>{status.message}</span>
          </div>
        )}

        {documents.length > 0 && (
          <div className="mt-4">
            <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-gray-400">Ask about</p>
            <ul className="space-y-1">
              <li>
                <button
                  onClick={() => onSelectDocument('')}
                  className={`flex w-full items-center justify-between gap-2 rounded-lg px-2.5 py-1.5 text-left text-sm transition-colors ${
                    !selectedDocument
                      ? 'bg-indigo-50 font-medium text-indigo-700'
                      : 'text-gray-600 hover:bg-gray-50'
                  }`}
                >
                  All documents
                  {!selectedDocument && <Check className="h-3.5 w-3.5 shrink-0" />}
                </button>
              </li>
              {documents.map((doc) => (
                <li key={doc}>
                  <button
                    onClick={() => onSelectDocument(doc)}
                    className={`flex w-full items-center justify-between gap-2 rounded-lg px-2.5 py-1.5 text-left text-sm transition-colors ${
                      selectedDocument === doc
                        ? 'bg-indigo-50 font-medium text-indigo-700'
                        : 'text-gray-600 hover:bg-gray-50'
                    }`}
                  >
                    <span className="flex min-w-0 items-center gap-2">
                      <FileText className="h-3.5 w-3.5 shrink-0 text-indigo-400" />
                      <span className="truncate">{doc}</span>
                    </span>
                    {selectedDocument === doc && <Check className="h-3.5 w-3.5 shrink-0" />}
                  </button>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      <div className="rounded-2xl border border-gray-100 bg-white p-5 shadow-sm">
        <h2 className="mb-3 text-sm font-semibold text-gray-900">🌍 Supported Languages</h2>
        <div className="flex flex-wrap gap-1.5">
          {Object.entries(LANGUAGE_CONFIG).map(([code, info]) => (
            <span
              key={code}
              className="inline-flex items-center gap-1 rounded-full bg-gray-50 px-2.5 py-1 text-xs font-medium text-gray-600"
              title={info.native}
            >
              <span>{info.flag}</span>
              {info.name}
            </span>
          ))}
        </div>
      </div>
    </aside>
  )
}
