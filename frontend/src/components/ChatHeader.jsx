export default function ChatHeader() {
  return (
    <header className="flex items-center gap-3 border-b border-slate-200 px-4 py-3 dark:border-slate-800">
      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-indigo-600 text-sm font-semibold text-white">
        CH
      </div>
      <div>
        <h1 className="text-base font-semibold text-slate-900 dark:text-slate-100">
          Chat with Chris Hsiao
        </h1>
        <p className="text-sm text-slate-500 dark:text-slate-400">
          AI assistant answering from Chris&apos;s CV
        </p>
      </div>
    </header>
  )
}
