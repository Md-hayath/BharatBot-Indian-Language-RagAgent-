export default function Header() {
  return (
    <header className="relative overflow-hidden bg-gradient-to-r from-indigo-600 via-violet-600 to-fuchsia-600 px-6 py-5 shadow-md">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_20%_20%,rgba(255,255,255,0.15),transparent_50%)]" />
      <div className="relative mx-auto flex max-w-6xl items-center gap-3">
        <span className="text-2xl">🇮🇳</span>
        <div>
          <h1 className="text-xl font-bold tracking-tight text-white">BharatBot</h1>
          <p className="text-sm text-indigo-100">Upload any document. Chat in any Indian language.</p>
        </div>
      </div>
    </header>
  )
}
