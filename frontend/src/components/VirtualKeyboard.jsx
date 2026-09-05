import { Delete, CornerDownLeft } from 'lucide-react'
import { KEYBOARD_LANGUAGES, KEYBOARD_LAYOUTS } from '../lib/keyboardLayouts'

export default function VirtualKeyboard({ lang, setLang, onChar, onBackspace, onSpace, onEnter }) {
  const layout = KEYBOARD_LAYOUTS[lang]
  const isRtl = lang === 'ur'

  return (
    <div className="rounded-2xl border border-gray-100 bg-white p-3 shadow-lg">
      <div className="mb-2 flex flex-wrap gap-1.5">
        {KEYBOARD_LANGUAGES.map((l) => (
          <button
            key={l.code}
            type="button"
            onClick={() => setLang(l.code)}
            className={`rounded-full px-3 py-1 text-xs font-medium transition-colors ${
              lang === l.code
                ? 'bg-indigo-600 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {l.label}
          </button>
        ))}
      </div>

      <div
        dir={isRtl ? 'rtl' : 'ltr'}
        className={`flex flex-col gap-1.5 ${isRtl ? 'items-end' : 'items-start'}`}
      >
        {layout.rows.map((row, i) => (
          <div key={i} className="flex flex-wrap gap-1.5">
            {row.map((ch, j) => (
              <button
                key={j}
                type="button"
                onClick={() => onChar(ch)}
                className="min-w-[2.25rem] rounded-lg border border-gray-200 bg-gray-50 px-2.5 py-1.5 text-sm text-gray-800 transition-colors hover:border-indigo-200 hover:bg-indigo-50 active:bg-indigo-100"
              >
                {ch}
              </button>
            ))}
          </div>
        ))}
      </div>

      <div className="mt-2 flex gap-1.5">
        <button
          type="button"
          onClick={onSpace}
          className="flex-1 rounded-lg border border-gray-200 bg-gray-50 py-1.5 text-xs text-gray-500 hover:bg-gray-100"
        >
          Space
        </button>
        <button
          type="button"
          onClick={onBackspace}
          className="flex items-center justify-center rounded-lg border border-gray-200 bg-gray-50 px-3 py-1.5 text-gray-600 hover:bg-gray-100"
        >
          <Delete className="h-4 w-4" />
        </button>
        <button
          type="button"
          onClick={onEnter}
          className="flex items-center justify-center gap-1 rounded-lg bg-indigo-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-indigo-700"
        >
          <CornerDownLeft className="h-3.5 w-3.5" />
          Send
        </button>
      </div>
    </div>
  )
}
