export default function ServerBanner({ serverStatus }) {
  if (serverStatus === 'waking') {
    return (
      <div
        role="status"
        className="flex items-start gap-3 border-b border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900 dark:border-amber-900 dark:bg-amber-950 dark:text-amber-200"
      >
        <span className="mt-0.5 h-4 w-4 shrink-0 animate-spin rounded-full border-2 border-amber-500 border-t-transparent" />
        <p>
          <strong className="font-semibold">Waking up the server…</strong> The free
          hosting plan sleeps when idle, so the first load can take up to a minute.
          You can ask questions as soon as it&apos;s ready.
        </p>
      </div>
    )
  }

  if (serverStatus === 'unavailable') {
    return (
      <div
        role="alert"
        className="border-b border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800 dark:border-red-900 dark:bg-red-950 dark:text-red-200"
      >
        The server isn&apos;t responding right now. You can still try asking a
        question, or come back in a moment.
      </div>
    )
  }

  return null
}
